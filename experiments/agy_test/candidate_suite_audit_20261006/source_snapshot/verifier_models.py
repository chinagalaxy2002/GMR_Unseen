#!/usr/bin/env python3
"""
Model Architectures for Independent Target Candidate Transfer and Ablation Benchmark.

Includes:
1. TargetCandidateVerifier: Full modular verifier with adaptive routing.
2. Ablation variants:
   - FixedPriorVerifier (frozen untrained initialization)
   - UnsignedDirectionVerifier (absolute value |delta|)
   - NoDirectionVerifier (delta zeroed out)
   - VisualOnlyVerifier (kinetic stream zeroed out)
   - KineticOnlyVerifier (visual stream zeroed out)
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F

class TargetCandidateVerifier(nn.Module):
    def __init__(
        self,
        hidden_dim: int = 32,
        alpha_min: float = 0.20,
        alpha_max: float = 0.50,
        ablation_mode: str = "none", # "none", "unsigned", "no_direction", "visual_only", "kinetic_only"
    ):
        super().__init__()
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.ablation_mode = ablation_mode
        
        # Multimodal Evidence Streams:
        # Kinetic Motion: [sf_vel, sf_disp, d_act]
        self.w_kin = nn.Parameter(torch.tensor([1.5, 0.5, 0.8]))
        
        # Composite Visual: [sim_cand, sim_obj, sim_peak, sim_act, sim_glob, d_obj]
        self.w_comp = nn.Parameter(torch.tensor([1.2, 1.0, 0.8, 0.6, 0.5, 0.5]))
        
        # Dynamic Modality Router
        # Inputs: [sim_glob, sim_cand, sim_peak, sim_obj, sim_act, sf_vel, sf_disp, d_act, d_obj] (9 dims)
        self.router = nn.Sequential(
            nn.Linear(9, 16),
            nn.SiLU(),
            nn.Linear(16, 2)
        )
        
        # Context Gating MLP:
        # [s_det, s_ev, sim_peak, sim_obj, sf_vel, fg_max, span_width, d_act] (8 dims)
        self.raw_gate = nn.Parameter(torch.tensor(-0.2)) # init towards lower alpha
        self.gate_mlp = nn.Sequential(
            nn.Linear(8, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, s_det: torch.Tensor, mm_feats: torch.Tensor) -> torch.Tensor:
        """
        s_det: (B,) detector score (quantile or prob in [0, 1])
        mm_feats: (B, 11)
          0: sim_glob
          1: sim_cand
          2: sim_peak
          3: sim_obj
          4: sim_act
          5: sf_vel
          6: sf_disp
          7: fg_max
          8: span_width
          9: d_act
         10: d_obj
        """
        # Apply ablations if requested
        feats = mm_feats.clone()
        if self.ablation_mode == "unsigned":
            feats[:, 9] = torch.abs(feats[:, 9])
            feats[:, 10] = torch.abs(feats[:, 10])
        elif self.ablation_mode == "no_direction":
            feats[:, 9] = 0.0
            feats[:, 10] = 0.0
        elif self.ablation_mode == "visual_only":
            feats[:, 5] = 0.0
            feats[:, 6] = 0.0
        elif self.ablation_mode == "kinetic_only":
            feats[:, 0] = 0.0
            feats[:, 1] = 0.0
            feats[:, 2] = 0.0
            feats[:, 3] = 0.0
            feats[:, 4] = 0.0
            feats[:, 10] = 0.0
            
        # 1. Kinetic Evidence Stream
        w_k = F.softmax(self.w_kin, dim=0)
        s_kin = w_k[0] * feats[:, 5] + w_k[1] * feats[:, 6] + w_k[2] * feats[:, 9]
        
        # 2. Composite Visual Stream
        w_c = F.softmax(self.w_comp, dim=0)
        s_comp = (
            w_c[0] * feats[:, 1] +
            w_c[1] * feats[:, 3] +
            w_c[2] * feats[:, 2] +
            w_c[3] * feats[:, 4] +
            w_c[4] * feats[:, 0] +
            w_c[5] * feats[:, 10]
        )
        
        # 3. Dynamic Router
        router_in = torch.stack([
            feats[:, 0], feats[:, 1], feats[:, 2], feats[:, 3], feats[:, 4],
            feats[:, 5], feats[:, 6], feats[:, 9], feats[:, 10]
        ], dim=-1)
        r_w = F.softmax(self.router(router_in), dim=-1)
        s_ev = r_w[:, 0] * s_kin + r_w[:, 1] * s_comp
        
        # 4. Contextual Adaptive Gate
        ctx = torch.stack([
            s_det,
            s_ev,
            feats[:, 2], # sim_peak
            feats[:, 3], # sim_obj
            feats[:, 5], # sf_vel
            feats[:, 7], # fg_max
            feats[:, 8], # span_width
            feats[:, 9], # d_act
        ], dim=-1)
        
        gate_offset = 0.1 * self.gate_mlp(ctx).squeeze(-1)
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * torch.sigmoid(self.raw_gate + gate_offset)
        
        # 5. Fused Output Score
        return (1.0 - alpha) * s_det + alpha * s_ev
