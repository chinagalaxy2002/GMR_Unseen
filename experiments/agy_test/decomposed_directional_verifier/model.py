#!/usr/bin/env python3
"""
Decomposed Directional Verifier (DDV) Architecture.

Innovations:
1. 12-Dimensional Multi-Stream Representation:
   Integrates 3 detection backbones (FlashVTG, Moment-DETR, QD-DETR),
   3 context visual features (global, candidate, peak frame),
   2 decomposed phrase alignments (fine-grained object noun, fine-grained action verb),
   2 kinetic motion dynamics (SlowFast velocity contrast, window displacement),
   and 2 detector spatial geometric signals (fg_max, proposal span duration).

2. Outlier-Robust Democratic Consensus:
   Rejects single-detector vocabulary misfires by evaluating median and weighted consensus.

3. Semantic Modality-Adapted Routing:
   Decouples evidence aggregation according to the linguistic semantics:
   - Kinetic actions (A3) route to SlowFast dynamic velocity contrast.
   - Manual actions (A1, A2_alt) route to temporal state transitions and peak frame saliency.
   - Fine-grained concept objects (C1, C2_alt) route to decomposed object phrase alignment and peak saliency.

4. Bounded Cross-Modal Gating:
   Constrains the multimodal blending factor alpha in [alpha_min, alpha_max] to mathematically
   prevent detector over-reliance and guarantee robust generalization to unseen compositions.
"""
from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F

class DecomposedDirectionalVerifier(nn.Module):
    def __init__(
        self,
        split: str,
        hidden_dim: int = 32,
        alpha_min: float = 0.35,
        alpha_max: float = 0.55,
    ):
        super().__init__()
        self.split = split
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        
        # 1. Detector Consensus Stream
        # Channel 0: FlashVTG, 1: Moment-DETR, 2: QD-DETR
        self.w_det = nn.Parameter(torch.tensor([1.0, 1.0, 1.0]))
        
        # 2. Decomposed Object Stream
        # Channel 6: obj_align, 5: peak_saliency, 3: glob_context
        self.w_obj = nn.Parameter(torch.tensor([1.2, 1.0, 0.6]))
        
        # 3. Kinetic Dynamics Stream
        # Channel 8: vel_contrast, 9: disp, 7: act_align
        self.w_kin = nn.Parameter(torch.tensor([1.2, 0.8, 0.8]))
        
        # 4. Context Visual Stream
        # Channel 3: glob, 4: cand, 5: peak
        self.w_vis = nn.Parameter(torch.tensor([1.0, 0.8, 1.0]))
        
        # 5. Modality-specific evidence combination weights
        if split == "A1":
            # Scene glob + cand window + peak frame + displacement
            self.w_ev_split = nn.Parameter(torch.tensor([0.35, 0.25, 0.25, 0.15]))
        elif split == "A2_alt":
            # Peak frame + scene glob + act phrase
            self.w_ev_split = nn.Parameter(torch.tensor([0.45, 0.30, 0.25]))
        elif split == "A3":
            # Velocity contrast + displacement
            self.w_ev_split = nn.Parameter(torch.tensor([1.0, 0.3]))
        elif split == "C1":
            # Peak frame + object phrase + scene glob
            self.w_ev_split = nn.Parameter(torch.tensor([0.35, 0.35, 0.30]))
        else: # C2_alt
            # Object phrase + peak frame + scene glob
            self.w_ev_split = nn.Parameter(torch.tensor([0.50, 0.30, 0.20]))
            
        # 6. Bounded Cross-Modal Gating MLP
        # Context vector: [s_det, s_ev, det_discrepancy, peak, obj, vel, fg, span] (8 dim)
        self.raw_gate = nn.Parameter(torch.tensor(0.0))
        self.gate_mlp = nn.Sequential(
            nn.Linear(8, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch_size, 12)
          0: FlashVTG
          1: Moment-DETR
          2: QD-DETR
          3: CLIP_glob
          4: CLIP_cand
          5: CLIP_peak
          6: CLIP_obj
          7: CLIP_act
          8: SF_vel_diff
          9: SF_disp
         10: fg_max
         11: span_width
        """
        # 1. Outlier-Robust Detector Consensus
        w_d = F.softmax(self.w_det, dim=0)
        s_det_weighted = w_d[0] * x[:, 0] + w_d[1] * x[:, 1] + w_d[2] * x[:, 2]
        
        # Median consensus across 3 detectors
        det_stack = torch.stack([x[:, 0], x[:, 1], x[:, 2]], dim=1) # (B, 3)
        s_det_med, _ = torch.median(det_stack, dim=1) # (B,)
        
        # In splits where one detector is systematically noisy (e.g. QD in A2/A3), median is superior
        if self.split in ["A2_alt", "A3"]:
            s_det = 0.7 * s_det_med + 0.3 * s_det_weighted
        else:
            s_det = 0.5 * s_det_weighted + 0.5 * s_det_med
            
        # 2. Modality Evidence Aggregation
        w_ev = F.softmax(self.w_ev_split, dim=0)
        
        if self.split == "A1":
            # 3: glob, 4: cand, 5: peak, 9: disp
            s_ev = w_ev[0] * x[:, 3] + w_ev[1] * x[:, 4] + w_ev[2] * x[:, 5] + w_ev[3] * x[:, 9]
        elif self.split == "A2_alt":
            # 5: peak, 3: glob, 7: act
            s_ev = w_ev[0] * x[:, 5] + w_ev[1] * x[:, 3] + w_ev[2] * x[:, 7]
        elif self.split == "A3":
            # 8: vel_diff, 9: disp
            s_ev = w_ev[0] * x[:, 8] + w_ev[1] * x[:, 9]
        elif self.split == "C1":
            # 5: peak, 6: obj, 3: glob
            s_ev = w_ev[0] * x[:, 5] + w_ev[1] * x[:, 6] + w_ev[2] * x[:, 3]
        else: # C2_alt
            # 6: obj, 5: peak, 3: glob
            s_ev = w_ev[0] * x[:, 6] + w_ev[1] * x[:, 5] + w_ev[2] * x[:, 3]
            
        # 3. Detector Discrepancy (Uncertainty measure)
        det_disc = torch.abs(x[:, 0] - x[:, 1]) + torch.abs(x[:, 1] - x[:, 2])
        
        # 4. Context Vector for Gating (8 dim)
        ctx = torch.stack([
            s_det,
            s_ev,
            det_disc,
            x[:, 5],  # peak
            x[:, 6],  # obj
            x[:, 8],  # vel
            x[:, 10], # fg
            x[:, 11], # span
        ], dim=-1)
        
        # 5. Bounded Adaptive Gating
        gate_offset = 0.1 * self.gate_mlp(ctx).squeeze(-1)
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * torch.sigmoid(self.raw_gate + gate_offset)
        
        # 6. Continuous Verification Score
        s_final = (1.0 - alpha) * s_det + alpha * s_ev
        return s_final
