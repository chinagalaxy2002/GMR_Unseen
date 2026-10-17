"""Read-only heads that extend Task A while keeping the E0 localizer frozen."""
import torch
from torch import nn
from torch.nn import functional as F


class EvidenceRead(nn.Module):
    def __init__(self, width=256):
        super().__init__()
        self.attention = nn.MultiheadAttention(width, 8, dropout=0.1, batch_first=True)
        self.feedforward = nn.Sequential(
            nn.Linear(width, 512), nn.ReLU(), nn.Dropout(0.1), nn.Linear(512, width)
        )
        self.norm_attention = nn.LayerNorm(width)
        self.norm_feedforward = nn.LayerNorm(width)
        self.dropout = nn.Dropout(0.1)

    def forward(self, state, memory, valid):
        evidence, attention = self.attention(
            state, memory.detach(), memory.detach(), key_padding_mask=~valid,
            need_weights=True, average_attn_weights=False
        )
        state = self.norm_attention(state + self.dropout(evidence))
        state = self.norm_feedforward(state + self.dropout(self.feedforward(state)))
        return state, attention.mean(dim=1).squeeze(1)


class EventReadout(nn.Module):
    def __init__(self, depth, job):
        super().__init__()
        self.multigranularity = bool(job.get('multigranularity', False))
        self.cardinality = bool(job.get('cardinality', False))
        self.token = nn.Parameter(torch.randn(1, 1, 256) * 0.02)
        self.text_read = EvidenceRead()
        self.video_reads = nn.ModuleList([EvidenceRead() for _ in range(depth)])
        n_stages = depth + 1 if self.multigranularity else 1
        self.stage_heads = nn.ModuleList([nn.Linear(256, 1) for _ in range(n_stages)])
        self.stage_weight = nn.Parameter(torch.zeros(n_stages))
        self.plurality = None if self.cardinality else nn.Sequential(
            nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 2)
        )
        self.count = nn.Sequential(nn.Linear(256, 256), nn.ReLU(), nn.Linear(256, 4)) \
            if self.cardinality else None
        self.context = None

    def forward(self, _pooled_input):
        context = self.context
        assert context is not None and len(context['video']) == len(self.video_reads)
        state, text_attention = self.text_read(
            self.token.expand(context['text'].shape[0], -1, -1),
            context['text'],
            context['text_valid'],
        )
        text_state = state[:, 0]
        states = [text_state]
        video_attention = []
        for reader, memory in zip(self.video_reads, context['video']):
            state, attention = reader(state, memory, context['video_valid'])
            video_attention.append(attention)
            states.append(state[:, 0])

        selected = states if self.multigranularity else [states[-1]]
        stage_logits = torch.stack(
            [head(value).squeeze(-1) for head, value in zip(self.stage_heads, selected)], dim=1
        )
        weights = torch.softmax(self.stage_weight, dim=0)
        existence = (stage_logits * weights.unsqueeze(0)).sum(1)

        context['stage_logits'] = stage_logits
        context['readout_states'] = torch.stack(states, dim=1)
        context['text_attention'] = text_attention
        context['video_attention'] = torch.stack(video_attention, dim=1)
        context['native_exist_input'] = _pooled_input
        if self.count is not None:
            fused_state = sum(weight * value for weight, value in zip(weights, selected))
            count_logits = self.count(fused_state)
            context['count_logits'] = count_logits
            existence = torch.logsumexp(count_logits[:, 1:], dim=1) - count_logits[:, 0]
        else:
            context['plurality'] = self.plurality(text_state)
        context['event_logit'] = existence
        return existence.unsqueeze(-1)

    def diagnostic_replay(self, text, text_valid, video, video_valid):
        """Replay only the existence readout for causal masking diagnostics."""
        state, _ = self.text_read(self.token.expand(text.shape[0], -1, -1), text, text_valid)
        states = [state[:, 0]]; attentions = []
        for reader, memory in zip(self.video_reads, video):
            state, attention = reader(state, memory, video_valid)
            states.append(state[:, 0]); attentions.append(attention)
        selected = states if self.multigranularity else [states[-1]]
        stage_logits = torch.stack([head(value).squeeze(-1) for head, value in zip(self.stage_heads, selected)], 1)
        weights = torch.softmax(self.stage_weight, 0)
        if self.count is not None:
            fused = sum(weight * value for weight, value in zip(weights, selected))
            count = self.count(fused)
            existence = torch.logsumexp(count[:, 1:], 1) - count[:, 0]
        else:
            existence = (stage_logits * weights.unsqueeze(0)).sum(1)
        return existence, torch.stack(attentions, 1)


class TaskAEnhancement(nn.Module):
    def __init__(self, base, job):
        super().__init__()
        self.base = base
        self.job = dict(job)
        self.quality_fusion = bool(job.get('quality_fusion', False))
        base.exist_head = EventReadout(len(base.transformer.encoder.layers), job)
        self.fusion = nn.Sequential(
            nn.LayerNorm(7), nn.Linear(7, 32), nn.GELU(), nn.Dropout(0.1), nn.Linear(32, 1)
        ) if self.quality_fusion else None
        self.handles = [base.input_txt_proj.register_forward_hook(self._capture_text)]
        self.handles.extend(
            layer.register_forward_hook(self._capture_video) for layer in base.transformer.encoder.layers
        )
        self.handles.append(base.transformer.register_forward_hook(self._capture_transformer))

    def _capture_text(self, _module, _inputs, output):
        self.base.exist_head.context['text'] = output

    def _capture_video(self, _module, _inputs, output):
        self.base.exist_head.context['video'].append(output.transpose(0, 1))

    def _capture_transformer(self, _module, _inputs, output):
        context = self.base.exist_head.context
        context['final_video_units'] = output[0].transpose(0, 1)
        context['final_video_valid'] = ~output[1].bool()

    @staticmethod
    def _masked_stats(values, valid):
        values = values.float()
        valid = valid.bool()
        safe = values.masked_fill(~valid, -1e4)
        maximum = safe.max(1).values
        count = valid.sum(1).clamp(min=1).float()
        mean = (values * valid.float()).sum(1) / count
        centered = (values - mean.unsqueeze(1)) * valid.float()
        std = torch.sqrt(centered.square().sum(1) / count + 1e-6)
        return maximum, mean, std

    def forward(self, **inputs):
        head = self.base.exist_head
        assert head.context is None
        context = {
            'text_valid': inputs['src_txt_mask'].bool(),
            'video_valid': inputs['src_vid_mask'].bool(),
            'video': [],
        }
        head.context = context
        try:
            output = self.base(**inputs)
            logit = context['event_logit']
            if self.fusion is not None:
                valid = output['video_msk'].bool()
                sal_max, sal_mean, sal_std = self._masked_stats(output['saliency_scores'].detach(), valid)
                att_max, att_mean, att_std = self._masked_stats(output['t2vattnvalues'].detach(), valid)
                features = torch.stack(
                    [logit, sal_max, sal_mean, sal_std, att_max, att_mean, att_std], dim=1
                )
                logit = logit + self.fusion(features).squeeze(-1)
            output['pred_exist_logits'] = logit
            output['pred_stage_logits'] = context['stage_logits']
            output['diagnostic_readout_states'] = context['readout_states']
            output['diagnostic_video_attention'] = context['video_attention']
            output['diagnostic_text_memory'] = context['text']
            output['diagnostic_text_valid'] = context['text_valid']
            output['diagnostic_video_memories'] = torch.stack(context['video'], dim=1)
            output['diagnostic_native_exist_input'] = context['native_exist_input']
            output['diagnostic_video_units'] = context['final_video_units']
            output['diagnostic_video_valid'] = context['final_video_valid']
            if 'count_logits' in context:
                output['pred_count_logits'] = context['count_logits']
                output['pred_multi_logits'] = torch.stack([
                    torch.logsumexp(context['count_logits'][:, :2], dim=1),
                    torch.logsumexp(context['count_logits'][:, 2:], dim=1),
                ], dim=1)
            else:
                output['pred_multi_logits'] = context['plurality']
            if '_out' in output:
                output['_out']['pred_exist_score'] = torch.sigmoid(logit).detach().cpu()
            return output
        finally:
            head.context = None


def head_loss(output, metadata, targets, job):
    existence = targets['exist_label'].float().to(output['pred_exist_logits'].device)
    details = {}
    if job.get('cardinality', False):
        count = torch.tensor(
            [min(3, len(row.get('relevant_windows', []))) for row in metadata],
            device=existence.device,
            dtype=torch.long,
        )
        main = F.cross_entropy(output['pred_count_logits'], count)
        details['loss_count'] = main
    else:
        if job.get('focal', False):
            prob = torch.sigmoid(output['pred_exist_logits'])
            pt = prob * existence + (1.0 - prob) * (1.0 - existence)
            main = (-0.5 * (1.0 - pt).square() * torch.log(pt.clamp_min(1e-7))).mean()
        else:
            main = F.binary_cross_entropy_with_logits(output['pred_exist_logits'], existence)
        details['loss_exist'] = main
        positive = existence > 0.5
        if positive.any():
            plural = torch.tensor(
                [len(row.get('relevant_windows', [])) >= 2 for row in metadata],
                device=existence.device,
                dtype=torch.long,
            )
            multi = F.cross_entropy(output['pred_multi_logits'][positive], plural[positive])
            main = main + float(job.get('multi_weight', 0.1)) * multi
            details['loss_multi'] = multi

    if job.get('multigranularity', False) and not job.get('cardinality', False):
        target = existence.unsqueeze(1).expand_as(output['pred_stage_logits'])
        auxiliary = F.binary_cross_entropy_with_logits(output['pred_stage_logits'], target)
        main = main + float(job.get('stage_aux_weight', 0.2)) * auxiliary
        details['loss_stage_aux'] = auxiliary
    details['loss_total'] = main
    return main, details
