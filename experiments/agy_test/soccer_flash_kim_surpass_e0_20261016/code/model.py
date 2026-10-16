"""Event Query architecture with gradient control and decoupled plurality/presence heads."""
import torch
from torch import nn
from torch.nn import functional as F

def controlled_features(x, scale):
    if scale == 1.0:
        return x
    if scale == 0.0:
        return x.detach()
    return x.detach() + scale * (x - x.detach())

class EvidenceRead(nn.Module):
    def __init__(self, width=256):
        super().__init__()
        self.attention = nn.MultiheadAttention(width, 8, dropout=0.1, batch_first=True)
        self.feedforward = nn.Sequential(
            nn.Linear(width, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, width)
        )
        self.norm_attention = nn.LayerNorm(width)
        self.norm_feedforward = nn.LayerNorm(width)
        self.dropout = nn.Dropout(0.1)

    def forward(self, state, memory, valid):
        evidence, _ = self.attention(state, memory, memory, key_padding_mask=~valid, need_weights=False)
        state = self.norm_attention(state + self.dropout(evidence))
        return self.norm_feedforward(state + self.dropout(self.feedforward(state)))

class EventReadout(nn.Module):
    """Target Query reading text, then multi-layer video features.
    
    Decoupled heads following Kim et al. AAAI 2026:
    - Plurality Head attached to post-text state e0 (guided by linguistic plurality cues).
    - Presence Head attached to post-video state e3 (guided by joint multimodal context).
    - Gradient scale controls whether query gradients backpropagate into shared features.
      scale=0.0 completely detaches shared features, preserving pure localization optimization.
    """
    def __init__(self, depth, source, grad_scale):
        super().__init__()
        assert source in ('none', 'text', 'final') and 0.0 <= grad_scale <= 1.0
        self.source = source
        self.grad_scale = grad_scale
        self.token = nn.Parameter(torch.randn(1, 1, 256) * 0.02)
        self.text_read = EvidenceRead()
        self.video_reads = nn.ModuleList([EvidenceRead() for _ in range(depth)])
        self.existence = nn.Sequential(nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 1))
        if source != 'none':
            self.plurality = nn.Sequential(nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 2))
        self.context = None

    def read(self, text, features, text_valid, video_valid):
        state = self.text_read(
            self.token.expand(text.shape[0], -1, -1),
            controlled_features(text, self.grad_scale),
            text_valid
        )
        text_state = state[:, 0]
        for layer, memory in zip(self.video_reads, features):
            state = layer(state, controlled_features(memory, self.grad_scale), video_valid)
        final_state = state[:, 0]
        out = {'existence': self.existence(final_state)}
        if self.source != 'none':
            out['plurality'] = self.plurality(text_state if self.source == 'text' else final_state)
        return out

    def forward(self, pooled_input):
        c = self.context
        assert c is not None and len(c['video']) == len(self.video_reads)
        out = self.read(c['text'], c['video'], c['text_valid'], c['video_valid'])
        if 'plurality' in out:
            c['plurality'] = out['plurality']
        return out['existence']

class RetrievalModel(nn.Module):
    def __init__(self, base, job):
        super().__init__()
        self.base = base
        self.variant = job['variant']
        self.handles = []
        if self.variant == 'E0':
            return
        base.exist_head = EventReadout(
            len(base.transformer.encoder.layers),
            job.get('multi_source', 'none'),
            job.get('feature_grad_scale', 0.0)
        )
        self.handles.append(base.input_txt_proj.register_forward_hook(self._capture_text))
        for layer in base.transformer.encoder.layers:
            self.handles.append(layer.register_forward_hook(self._capture_video))

    def _capture_text(self, module, inputs, output):
        self.base.exist_head.context['text'] = output

    def _capture_video(self, module, inputs, output):
        self.base.exist_head.context['video'].append(output.transpose(0, 1))

    def forward(self, **inputs):
        if self.variant == 'E0':
            return self.base(**inputs)
        head = self.base.exist_head
        assert head.context is None, 'Overlapping forward passes not supported'
        c = {
            'text_valid': inputs['src_txt_mask'].bool(),
            'video_valid': inputs['src_vid_mask'].bool(),
            'video': []
        }
        head.context = c
        try:
            out = self.base(**inputs)
            if self.variant == 'E2M':
                out['pred_multi_logits'] = c['plurality']
            return out
        finally:
            head.context = None

def plurality_loss(output, metadata, exist_labels):
    logits = output['pred_multi_logits']
    counts = torch.tensor([len(r['relevant_windows']) for r in metadata], device=logits.device)
    positive = counts > 0
    assert torch.equal(positive, exist_labels.to(logits.device) > 0.5)
    if positive.any():
        targets = (counts[positive] >= 2).long()
        return F.cross_entropy(logits[positive], targets)
    return logits.sum() * 0.0
