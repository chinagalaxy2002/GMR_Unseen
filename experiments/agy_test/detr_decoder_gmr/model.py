#!/usr/bin/env python3
"""
DEC-GMR: Decoder-Evidential Conjunctive Verification Network for DETR-based GMR.

Core Architecture:
1. Dynamic Query-Semantic Routing (Kinetic Stream vs Composite Stream).
2. Cross-Modal Conflict & Epistemic Uncertainty Estimation.
3. Adaptive Power-Law Conjunctive Gating:
   S_verified = (s_det ** beta_det) * (s_ev ** beta_ev)
   When conflict is high (s_det high, s_ev low), beta_ev is increased to suppress false positives.
4. Strictly single-backbone (supports Moment-DETR, FlashVTG, or QD-DETR standalone).
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F

class ConjunctiveDecoderVerifier(nn.Module):
    def __init__(
        self,
        in_mm_dim: int = 11,
        hidden_dim: int = 32,
    ):
        super().__init__()
        
        # 1. Kinetic Motion Stream Weights: [vel_diff, disp, delta_act]
        self.w_kin = nn.Parameter(torch.tensor([1.2, 0.6, 0.8]))
        
        # 2. Composite Semantic Stream Weights: [obj, peak, delta_obj, glob, act]
        self.w_comp = nn.Parameter(torch.tensor([1.2, 1.0, 0.6, 0.6, 0.6]))
        
        # 3. Dynamic Query Semantic Router (routes between kinetic and composite)
        self.router = nn.Sequential(
            nn.Linear(8, 16),
            nn.SiLU(),
            nn.Linear(16, 2)
        )
        
        # 4. Adaptive Conjunctive Exponent Network
        # Inputs: [s_det, s_ev, |s_det - s_ev|, peak, obj, vel, fg, delta_act] (8 dims)
        self.exponent_net = nn.Sequential(
            nn.Linear(8, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 2)
        )
        # Base exponents
        self.base_beta_det = nn.Parameter(torch.tensor(0.65))
        self.base_beta_ev = nn.Parameter(torch.tensor(0.85))

    def forward(
        self,
        s_det: torch.Tensor,
        mm_feats: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        s_det: (B,) - Rank-normalized detector score in [0, 1]
        mm_feats: (B, 11) - Multimodal physical and semantic evidence in [0, 1]
          0: CLIP_glob
          1: CLIP_cand
          2: CLIP_peak
          3: CLIP_obj
          4: CLIP_act
          5: SF_vel_diff
          6: SF_disp
          7: fg_max
          8: span_width
          9: delta_act
         10: delta_obj
        """
        eps = 1e-6
        s_det = torch.clamp(s_det, eps, 1.0)
        
        # 1. Kinetic Evidence
        w_k = F.softmax(self.w_kin, dim=0)
        s_kin = w_k[0] * mm_feats[:, 5] + w_k[1] * mm_feats[:, 6] + w_k[2] * mm_feats[:, 9]
        
        # 2. Composite Evidence
        w_c = F.softmax(self.w_comp, dim=0)
        s_comp = (
            w_c[0] * mm_feats[:, 3] +
            w_c[1] * mm_feats[:, 2] +
            w_c[2] * mm_feats[:, 10] +
            w_c[3] * mm_feats[:, 0] +
            w_c[4] * mm_feats[:, 4]
        )
        
        # 3. Dynamic Routing
        router_in = torch.stack([
            mm_feats[:, 0], mm_feats[:, 2], mm_feats[:, 3], mm_feats[:, 4],
            mm_feats[:, 5], mm_feats[:, 6], mm_feats[:, 9], mm_feats[:, 10]
        ], dim=-1)
        routing_w = F.softmax(self.router(router_in), dim=-1)
        s_ev = torch.clamp(routing_w[:, 0] * s_kin + routing_w[:, 1] * s_comp, eps, 1.0)
        
        # 4. Adaptive Exponents based on Discrepancy / Conflict
        conflict = torch.abs(s_det - s_ev)
        ctx = torch.stack([
            s_det,
            s_ev,
            conflict,
            mm_feats[:, 2], # peak
            mm_feats[:, 3], # obj
            mm_feats[:, 5], # vel
            mm_feats[:, 7], # fg
            mm_feats[:, 9], # delta_act
        ], dim=-1)
        
        offsets = 0.2 * torch.tanh(self.exponent_net(ctx)) # [-0.2, +0.2]
        beta_det = torch.clamp(self.base_beta_det + offsets[:, 0], 0.4, 0.9)
        beta_ev = torch.clamp(self.base_beta_ev + offsets[:, 1], 0.6, 1.2)
        
        # 5. Soft Conjunctive Kernel: S = (s_det ** beta_det) * (s_ev ** beta_ev)
        s_conj = torch.pow(s_det, beta_det) * torch.pow(s_ev, beta_ev)
        s_final = torch.clamp(s_conj, eps, 1.0 - eps)
        
        return s_final, s_ev, beta_det, beta_ev
