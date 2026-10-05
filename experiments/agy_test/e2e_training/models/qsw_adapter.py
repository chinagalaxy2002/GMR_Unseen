"""
Quality-Aware Slot Witness (QSW) Adapter for Generalized Moment Retrieval.
Replaces coordinate-wise max-pooling over decoder query slots with
independent per-slot existence scoring and grounded foreground confidence gating.
"""
from __future__ import annotations
import math
import torch
import torch.nn.functional as F
from torch import nn, Tensor

class QSWAdapter(nn.Module):
    """
    Quality-Aware Slot Witness Adapter.
    Instead of coordinate-wise max pooling (h_exist = max_i H_i) which artificially
    inflates feature magnitude under unseen diffuse slots, QSW:
    1. Scores each slot independently: e_i = MLP_slot(h_i).
    2. Weights slots by their grounded foreground detector probabilities: p_i.
    3. Aggregates via temperature-softmax attention across slots.
    """
    def __init__(self, input_dim: int = 256, hidden_dim: int = 256, temperature: float = 0.5):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.temperature = nn.Parameter(torch.tensor(temperature, dtype=torch.float32))
        
        # Per-slot existence scoring MLP
        self.slot_mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1),
        )
        
        # Cross-slot witness attention projection
        self.witness_proj = nn.Linear(input_dim + 1, hidden_dim // 2)
        self.witness_score = nn.Linear(hidden_dim // 2, 1)

    def forward(self, decoder_queries: Tensor, pred_logits: Tensor = None) -> Tensor:
        """
        Inputs:
            decoder_queries: [batch_size, num_queries, input_dim] (H^q)
            pred_logits: [batch_size, num_queries, 2] (class logits: 0=foreground, 1=background)
        Returns:
            existence_logits: [batch_size] scalar existence score per video-query pair
        """
        bsz, num_q, d = decoder_queries.shape
        
        # 1. Per-slot existence scores: e_i in R
        slot_scores = self.slot_mlp(decoder_queries).squeeze(-1) # [B, N]
        
        # 2. Foreground probabilities from detector: p_i in [0, 1]
        if pred_logits is not None:
            fg_prob = pred_logits.softmax(dim=-1)[..., 0] # [B, N]
        else:
            fg_prob = torch.ones_like(slot_scores) / num_q
            
        # 3. Grounded witness attention weights
        fg_feat = fg_prob.unsqueeze(-1) # [B, N, 1]
        joint_input = torch.cat([decoder_queries, fg_feat], dim=-1) # [B, N, D + 1]
        attn_logits = self.witness_score(F.relu(self.witness_proj(joint_input))).squeeze(-1) # [B, N]
        
        # Temperature-scaled gating by foreground probability
        tau = torch.clamp(self.temperature, min=0.1, max=2.0)
        fg_gate = torch.log(fg_prob.clamp(min=1e-5)) / tau
        combined_logits = attn_logits + fg_gate
        witness_weights = F.softmax(combined_logits, dim=-1) # [B, N]
        
        # 4. Aggregated video-level existence score
        # Combination of soft witness expectation and top-1 witness
        top1_idx = torch.argmax(fg_prob, dim=-1, keepdim=True) # [B, 1]
        top1_score = torch.gather(slot_scores, 1, top1_idx).squeeze(-1) # [B]
        soft_score = torch.sum(witness_weights * slot_scores, dim=-1) # [B]
        
        existence_logits = 0.5 * top1_score + 0.5 * soft_score
        return existence_logits


def compute_qsw_existence_loss(
    pred_exist_logits: Tensor,
    exist_labels: Tensor,
    pairwise_vids: list[str] = None,
    gamma: float = 0.5,
    pair_weight: float = 0.2,
) -> Tensor:
    """
    Computes binary cross entropy + optional same-video contrastive ranking loss.
    """
    logits = pred_exist_logits.view(-1)
    labels = exist_labels.float().view(-1)
    bce_loss = F.binary_cross_entropy_with_logits(logits, labels, reduction="mean")
    
    if pairwise_vids is None or pair_weight <= 0:
        return bce_loss
        
    # Same-video pairwise ranking: s(V, Q+) > s(V, Q-) + gamma
    vid_to_idx = {}
    for i, v in enumerate(pairwise_vids):
        vid_to_idx.setdefault(v, []).append(i)
        
    pair_losses = []
    for v, idxs in vid_to_idx.items():
        pos = [i for i in idxs if labels[i] == 1]
        neg = [i for i in idxs if labels[i] == 0]
        for p in pos:
            for n in neg:
                diff = logits[p] - logits[n]
                pair_losses.append(F.relu(gamma - diff))
                
    if pair_losses:
        pairwise_loss = torch.stack(pair_losses).mean()
        return bce_loss + pair_weight * pairwise_loss
    return bce_loss
