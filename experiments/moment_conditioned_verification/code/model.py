"""Moment-Conditioned Event Verification (MCEV) for Generalized Moment Retrieval.

Decouples event verification while leveraging localized candidate temporal proposals
as concrete hypothesis evidence, resolving false rejections of localized positive moments.
"""
import math
import torch
from torch import nn
from torch.nn import functional as F


class EvidenceRead(nn.Module):
    def __init__(self, width=256, n_heads=8, dropout=0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(width, n_heads, dropout=dropout, batch_first=True)
        self.feedforward = nn.Sequential(
            nn.Linear(width, width * 2), nn.ReLU(), nn.Dropout(dropout), nn.Linear(width * 2, width)
        )
        self.norm_attention = nn.LayerNorm(width)
        self.norm_feedforward = nn.LayerNorm(width)
        self.dropout = nn.Dropout(dropout)

    def forward(self, state, memory, valid=None):
        key_padding_mask = ~valid.bool() if valid is not None else None
        evidence, attention = self.attention(
            state, memory, memory, key_padding_mask=key_padding_mask,
            need_weights=True, average_attn_weights=False
        )
        state = self.norm_attention(state + self.dropout(evidence))
        state = self.norm_feedforward(state + self.dropout(self.feedforward(state)))
        attn_out = attention.mean(dim=1).squeeze(1) if attention.ndim == 4 else attention.mean(dim=1)
        return state, attn_out


class CandidateMomentExtractor(nn.Module):
    """Extracts top-K candidate moments from localizer proposals and encodes temporal RoI features."""
    def __init__(self, hidden_dim=256, top_k=8, clip_length=2.0, max_duration=150.0):
        super().__init__()
        self.top_k = top_k
        self.clip_length = clip_length
        self.max_duration = max_duration
        self.geom_mlp = nn.Sequential(
            nn.Linear(4, 64),
            nn.ReLU(),
            nn.Linear(64, hidden_dim),
            nn.LayerNorm(hidden_dim),
        )
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, final_video, video_mask, candidate_spans):
        """
        Args:
            final_video: (B, T, D), T <= 75
            video_mask: (B, T) bool
            candidate_spans: (B, K, 3) where each row is [st, ed, conf]
        Returns:
            moment_tokens: (B, K, D)
            moment_confs: (B, K)
            moment_spans: (B, K, 2) in seconds
        """
        bsz = candidate_spans.shape[0]
        K = candidate_spans.shape[1]
        device = candidate_spans.device
        
        st = candidate_spans[:, :, 0].clamp(min=0.0, max=self.max_duration)
        ed = candidate_spans[:, :, 1].clamp(min=0.0, max=self.max_duration)
        confs = candidate_spans[:, :, 2].clamp(min=0.0, max=1.0)
        spans_2d = torch.stack([st, ed], dim=-1) # (B, K, 2)
        
        # Temporal RoI pooling from final_video
        T = final_video.shape[1]
        frame_centers = (torch.arange(T, device=device, dtype=torch.float32) * self.clip_length + self.clip_length / 2.0) # (T,)
        
        cand_center = (st + ed).unsqueeze(-1) / 2.0 # (B, K, 1)
        cand_half_w = (ed - st).clamp(min=self.clip_length).unsqueeze(-1) / 2.0 # (B, K, 1)
        
        dist_sq = (frame_centers.view(1, 1, T) - cand_center).square()
        weights = torch.exp(-dist_sq / (2.0 * cand_half_w.square() + 1e-5))
        weights = weights * video_mask.unsqueeze(1).float()
        weights_sum = weights.sum(dim=-1, keepdim=True).clamp(min=1e-5)
        norm_weights = weights / weights_sum # (B, K, T)
        
        # RoI video feature: (B, K, D)
        roi_video = torch.bmm(
            norm_weights.view(bsz * K, 1, T),
            final_video.unsqueeze(1).expand(-1, K, -1, -1).reshape(bsz * K, T, -1)
        ).view(bsz, K, -1)
        
        # Geometry embedding: [st/150, ed/150, duration/150, conf]
        geom_in = torch.stack([
            st / self.max_duration,
            ed / self.max_duration,
            (ed - st) / self.max_duration,
            confs,
        ], dim=-1) # (B, K, 4)
        geom_emb = self.geom_mlp(geom_in) # (B, K, D)
        
        moment_tokens = self.norm(roi_video + geom_emb)
        return moment_tokens, confs, spans_2d


class MomentConditionedVerifier(nn.Module):
    """
    Moment-Conditioned Event Verification Module.
    Combines global contextual cross-attention with candidate moment verification.
    """
    def __init__(self, depth, job):
        super().__init__()
        self.job = dict(job)
        hidden_dim = 256
        self.use_moment_conditioning = bool(job.get('use_moment_conditioning', True))
        self.use_global_branch = bool(job.get('use_global_branch', True))
        self.top_k = int(job.get('top_k', 8))
        
        # Global Event Readout Branch
        self.token = nn.Parameter(torch.randn(1, 1, hidden_dim) * 0.02)
        self.text_read = EvidenceRead(hidden_dim)
        self.video_reads = nn.ModuleList([EvidenceRead(hidden_dim) for _ in range(depth)])
        self.global_head = nn.Linear(hidden_dim, 1)
        
        # Plurality Head on text
        self.plurality = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(), nn.Linear(hidden_dim, 2)
        )
        
        if self.use_moment_conditioning:
            # Local Candidate Moment Branch
            self.extractor = CandidateMomentExtractor(hidden_dim=hidden_dim, top_k=self.top_k)
            self.moment_cross_attn = nn.MultiheadAttention(hidden_dim, 8, dropout=0.1, batch_first=True)
            self.moment_match_mlp = nn.Sequential(
                nn.Linear(hidden_dim * 3 + 1, 128),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(128, 1),
            )
            self.local_head = nn.Sequential(
                nn.Linear(hidden_dim, 64),
                nn.ReLU(),
                nn.Linear(64, 1),
            )
            # Evidence Fusion Gate
            # Inputs: [global_logit, local_logit, v_max, v_top3, c_max, c_top3] -> 6 dims
            self.fusion_gate = nn.Sequential(
                nn.Linear(6, 32),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(32, 1),
            )
            nn.init.zeros_(self.fusion_gate[-1].weight)
            nn.init.zeros_(self.fusion_gate[-1].bias)

        self.context = None

    def forward(self, _pooled_input):
        context = self.context
        assert context is not None
        bsz = context['text'].shape[0]
        
        # 1. Global Readout Branch
        state, text_attention = self.text_read(
            self.token.expand(bsz, -1, -1),
            context['text'],
            context['text_valid'],
        )
        text_state = state[:, 0]
        for reader, memory in zip(self.video_reads, context['video']):
            state, _ = reader(state, memory, context['video_valid'])
        global_state = state[:, 0]
        global_logit = self.global_head(global_state).squeeze(-1) # (B,)
        
        context['text_state'] = text_state
        context['plurality'] = self.plurality(text_state)
        context['global_logit'] = global_logit
        
        if not self.use_moment_conditioning or 'candidate_spans' not in context:
            context['event_logit'] = global_logit
            return global_logit.unsqueeze(-1)
            
        # 2. Local Candidate Moment Verification Branch
        candidate_spans = context['candidate_spans'] # (B, K, 3)
        moment_tokens, moment_confs, moment_spans = self.extractor(
            final_video=context['final_video_units'],
            video_mask=context['final_video_valid'],
            candidate_spans=candidate_spans,
        )
        
        # Text query attends to candidate moments
        q_expanded = text_state.unsqueeze(1) # (B, 1, D)
        local_attended, _ = self.moment_cross_attn(q_expanded, moment_tokens, moment_tokens)
        local_logit = self.local_head(local_attended.squeeze(1)).squeeze(-1) # (B,)
        
        # Explicit match scoring between query and each candidate moment
        K = candidate_spans.shape[1]
        q_rep = text_state.unsqueeze(1).expand(-1, K, -1) # (B, K, D)
        elem_prod = q_rep * moment_tokens
        match_in = torch.cat([q_rep, moment_tokens, elem_prod, moment_confs.unsqueeze(-1)], dim=-1)
        match_scores = self.moment_match_mlp(match_in).squeeze(-1) # (B, K)
        
        v_max = match_scores.max(dim=1).values
        v_top3 = match_scores[:, :min(3, K)].mean(dim=1)
        c_max = moment_confs.max(dim=1).values
        c_top3 = moment_confs[:, :min(3, K)].mean(dim=1)
        
        # 3. Evidence Fusion
        if self.use_global_branch:
            gate_inputs = torch.stack([global_logit, local_logit, v_max, v_top3, c_max, c_top3], dim=1)
            residual = self.fusion_gate(gate_inputs).squeeze(-1)
            final_logit = global_logit + residual
        else:
            final_logit = local_logit + 0.5 * v_max
        
        context['local_logit'] = local_logit
        context['match_scores'] = match_scores
        context['moment_confs'] = moment_confs
        context['moment_spans'] = moment_spans
        context['event_logit'] = final_logit
        return final_logit.unsqueeze(-1)


class MCEVModel(nn.Module):
    """Wraps FlashVTG with frozen localizer and MCEV existence head."""
    def __init__(self, base, job):
        super().__init__()
        self.base = base
        self.job = dict(job)
        self.depth = len(base.transformer.encoder.layers)
        self.top_k = int(job.get('top_k', 8))
        
        # Replace exist_head with MomentConditionedVerifier
        base.exist_head = MomentConditionedVerifier(self.depth, job)
        
        # Register hooks to capture intermediate representations without altering localizer computations
        self.handles = [
            base.input_txt_proj.register_forward_hook(self._capture_text),
            base.transformer.register_forward_hook(self._capture_transformer),
        ]
        self.handles.extend(
            layer.register_forward_hook(self._capture_video)
            for layer in base.transformer.encoder.layers
        )

    def _capture_text(self, _mod, _inp, output):
        self.base.exist_head.context['text'] = output.detach()

    def _capture_video(self, _mod, _inp, output):
        self.base.exist_head.context['video'].append(output.transpose(0, 1).detach())

    def _capture_transformer(self, _mod, _inp, output):
        context = self.base.exist_head.context
        context['final_video_units'] = output[0].transpose(0, 1).detach()
        context['final_video_valid'] = (~output[1].bool()).detach()

    def forward(self, **inputs):
        head = self.base.exist_head
        assert head.context is None, "Context re-entrancy error"
        
        context = {
            'text_valid': inputs['src_txt_mask'].bool(),
            'video_valid': inputs['src_vid_mask'].bool(),
            'video': [],
        }
        head.context = context
        try:
            output = self.base(**inputs)
            
            # Extract candidate moments from base output
            # In train: output['pred_spans'] is (B, 139, 3) where [st, ed, conf]
            # In eval:  output['_out']['boundary'] is (50, 3) where [st, ed, conf]
            if 'pred_spans' in output:
                spans = output['pred_spans'].detach() # (B, 139, 3)
                confs = spans[:, :, 2]
                _, top_idx = confs.topk(min(self.top_k, spans.shape[1]), dim=1)
                batch_idx = torch.arange(spans.shape[0], device=spans.device).unsqueeze(1).expand(-1, top_idx.shape[1])
                top_spans = spans[batch_idx, top_idx] # (B, K, 3)
            elif '_out' in output and 'boundary' in output['_out']:
                bnd = output['_out']['boundary'].detach() # (50, 3)
                top_spans = bnd[:self.top_k].unsqueeze(0) # (1, K, 3)
            else:
                top_spans = None
                
            context['candidate_spans'] = top_spans
            
            # Recompute existence logit with candidate spans
            logit = head(None).squeeze(-1)
            output['pred_exist_logits'] = logit
            output['pred_multi_logits'] = context['plurality']
            if '_out' in output:
                output['_out']['pred_exist_score'] = torch.sigmoid(logit).detach().cpu()
            return output
        finally:
            head.context = None


def compute_mcev_loss(output, metadata, targets, job, model=None, model_inputs=None):
    """
    Computes balanced loss for MCEV:
    - Base BCE on existence label
    - Plurality cross-entropy on positive queries
    - Balanced Margin Contrastive loss with semantic hard negatives (avoids score suppression!)
    """
    existence = targets['exist_label'].float().to(output['pred_exist_logits'].device)
    details = {}
    
    # 1. Primary existence classification loss
    if job.get('focal', False):
        prob = torch.sigmoid(output['pred_exist_logits'])
        pt = prob * existence + (1.0 - prob) * (1.0 - existence)
        loss_exist = (-0.5 * (1.0 - pt).square() * torch.log(pt.clamp_min(1e-7))).mean()
    else:
        loss_exist = F.binary_cross_entropy_with_logits(output['pred_exist_logits'], existence)
    
    details['loss_exist'] = loss_exist
    total_loss = loss_exist
    
    # 2. Plurality classification loss on positive queries
    positive = existence > 0.5
    if positive.any():
        plural = torch.tensor(
            [len(row.get('relevant_windows', [])) >= 2 for row in metadata],
            device=existence.device,
            dtype=torch.long,
        )
        loss_multi = F.cross_entropy(output['pred_multi_logits'][positive], plural[positive])
        multi_weight = float(job.get('multi_weight', 0.1))
        total_loss = total_loss + multi_weight * loss_multi
        details['loss_multi'] = loss_multi
        
    # 3. Hard negative contrastive loss
    if job.get('hard_negative', False) and model is not None and model_inputs is not None:
        batch_size = model_inputs['src_txt'].shape[0]
        if batch_size >= 2 and positive.any():
            # In-batch text embeddings
            pooled = (model_inputs['src_txt'] * model_inputs['src_txt_mask'].unsqueeze(-1)).sum(1)
            denom = model_inputs['src_txt_mask'].sum(1, keepdim=True).clamp(min=1)
            pooled = F.normalize(pooled / denom, dim=-1)
            
            sim_matrix = pooled @ pooled.t()
            sim_matrix.fill_diagonal_(-1e4)
            hard_neg_indices = sim_matrix.argmax(dim=1)
            
            neg_inputs = dict(model_inputs)
            neg_inputs['src_txt'] = model_inputs['src_txt'][hard_neg_indices]
            neg_inputs['src_txt_mask'] = model_inputs['src_txt_mask'][hard_neg_indices]
            
            device = model_inputs['src_txt'].device
            rng_devices = [device.index if device.index is not None else torch.cuda.current_device()] if device.type == 'cuda' else []
            with torch.random.fork_rng(devices=rng_devices):
                neg_output = model(**neg_inputs, targets={})
                
            pos_logits = output['pred_exist_logits'][positive]
            neg_logits = neg_output['pred_exist_logits'][positive]
            
            loss_mode = job.get('contrast_loss_mode', 'margin')
            if loss_mode == 'margin':
                # Balanced Margin Contrastive: enforces pos_logit >= neg_logit + margin
                # Does NOT push logits toward -inf! Pushes pos UP and neg DOWN symmetrically!
                margin = float(job.get('contrast_margin', 2.0))
                loss_contrast = F.relu(margin - (pos_logits - neg_logits)).mean()
            elif loss_mode == 'info_nce':
                # InfoNCE contrastive: -log(exp(pos/T) / (exp(pos/T) + exp(neg/T)))
                temp = float(job.get('contrast_temp', 0.5))
                pair_logits = torch.stack([pos_logits / temp, neg_logits / temp], dim=1) # (N_pos, 2)
                loss_contrast = F.cross_entropy(pair_logits, torch.zeros(len(pos_logits), dtype=torch.long, device=device))
            elif loss_mode == 'naive_bce':
                # A3's legacy asymmetric loss: forces neg_logits to 0
                loss_contrast = F.binary_cross_entropy_with_logits(neg_logits, torch.zeros_like(neg_logits))
            else:
                raise ValueError(f"Unknown contrast_loss_mode: {loss_mode}")
                
            contrast_weight = float(job.get('hard_negative_weight', 0.5))
            total_loss = total_loss + contrast_weight * loss_contrast
            details['loss_contrast'] = loss_contrast
            
    details['loss_total'] = total_loss
    return total_loss, details
