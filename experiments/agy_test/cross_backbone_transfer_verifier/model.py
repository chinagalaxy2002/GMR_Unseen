#!/usr/bin/env python3
"""
Modular Backbone-Agnostic Verifier Architecture for Cross-Backbone Transfer Experiments.

Key Features:
1. Pure Modular Separation:
   Takes any single detector score s_det (FlashVTG, Moment-DETR, or QD-DETR)
   and fuses it with candidate multimodal grounding streams.
2. Dynamic Query Semantic Routing:
   Linguistic routing (kinetic motion vs composite interaction) without split ID.
3. Bounded Residual Adaptive Gating:
   Guarantees alpha in [0.35, 0.55] to prevent detector over-reliance.
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F

class SingleBackboneVerifier(nn.Module):
    def __init__(
        self,
        hidden_dim: int = 32,
        alpha_min: float = 0.35,
        alpha_max: float = 0.55,
    ):
        super().__init__()
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        
        # Multimodal Evidence Streams:
        # 1. Kinetic Motion (vel_contrast, disp, delta_act)
        self.w_kin = nn.Parameter(torch.tensor([1.4, 0.6, 0.8]))
        
        # 2. Composite Semantic Stream (obj_align, peak, delta_obj, scene_glob, act_align)
        self.w_comp = nn.Parameter(torch.tensor([1.2, 1.0, 0.6, 0.6, 0.6]))
        
        # Modality Router (routes between kinetic and composite)
        self.router = nn.Sequential(
            nn.Linear(8, 16),
            nn.SiLU(),
            nn.Linear(16, 2)
        )
        
        # Bounded Cross-Modal Gating MLP
        # Context: [s_det, s_ev, peak, obj, vel, fg, span, delta_act] (8 dims)
        self.raw_gate = nn.Parameter(torch.tensor(0.0))
        self.gate_mlp = nn.Sequential(
            nn.Linear(8, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, s_det: torch.Tensor, mm_feats: torch.Tensor) -> torch.Tensor:
        """
        s_det: (batch_size,) - detector score (rank-normalized in [0, 1])
        mm_feats: (batch_size, 11)
          0: CLIP_glob (index 3 in 14D)
          1: CLIP_cand (index 4 in 14D)
          2: CLIP_peak (index 5 in 14D)
          3: CLIP_obj (index 6 in 14D)
          4: CLIP_act (index 7 in 14D)
          5: SF_vel_diff (index 8 in 14D)
          6: SF_disp (index 9 in 14D)
          7: fg_max (index 10 in 14D)
          8: span_width (index 11 in 14D)
          9: delta_act (index 12 in 14D)
         10: delta_obj (index 13 in 14D)
        """
        # 1. Evidence Streams
        w_k = F.softmax(self.w_kin, dim=0)
        s_kin = w_k[0] * mm_feats[:, 5] + w_k[1] * mm_feats[:, 6] + w_k[2] * mm_feats[:, 9]
        
        w_c = F.softmax(self.w_comp, dim=0)
        s_comp = (
            w_c[0] * mm_feats[:, 3] +
            w_c[1] * mm_feats[:, 2] +
            w_c[2] * mm_feats[:, 10] +
            w_c[3] * mm_feats[:, 0] +
            w_c[4] * mm_feats[:, 4]
        )
        
        # 2. Dynamic Router
        router_in = torch.stack([
            mm_feats[:, 0], mm_feats[:, 2], mm_feats[:, 3], mm_feats[:, 4],
            mm_feats[:, 5], mm_feats[:, 6], mm_feats[:, 9], mm_feats[:, 10]
        ], dim=-1)
        routing_w = F.softmax(self.router(router_in), dim=-1)
        s_ev = routing_w[:, 0] * s_kin + routing_w[:, 1] * s_comp
        
        # 3. Context for Gating
        ctx = torch.stack([
            s_det,
            s_ev,
            mm_feats[:, 2], # peak
            mm_feats[:, 3], # obj
            mm_feats[:, 5], # vel
            mm_feats[:, 7], # fg
            mm_feats[:, 8], # span
            mm_feats[:, 9], # delta_act
        ], dim=-1)
        
        gate_offset = 0.1 * self.gate_mlp(ctx).squeeze(-1)
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * torch.sigmoid(self.raw_gate + gate_offset)
        
        # 4. Verified Score
        return (1.0 - alpha) * s_det + alpha * s_ev
