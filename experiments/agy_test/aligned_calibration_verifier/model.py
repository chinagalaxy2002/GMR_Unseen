#!/usr/bin/env python3
"""
Model Architecture for Aligned Calibration Verifier (AC-Verifier).

Key Principles:
1. P0 Control: Detector Adapter only (s_det = w_base * orig_logits + w_fg * fg_logit + mlp_slot(h_pool) + bias).
2. P1 Verifier: Aligned Reference-Centered CLIP Verifier.
   - Uses predefined unlabelled train-video reference centering: sim(q, v) = cos(q_proj, v) - cos(q_proj, v_ref).
   - Zero trainable text prior MLP: avoids language-frequency memorization.
   - Adaptive foreground gating: gates visual similarity based on candidate detector confidence.
   - Non-negative fusion weights: strictly additive visual grounding evidence.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class DetectorAdapter(nn.Module):
    """
    P0 Control Model: Adapts detector outputs without any new visual features.
    """
    def __init__(self, slot_dim=512):
        super().__init__()
        self.mlp_slot = nn.Sequential(
            nn.Linear(slot_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )
        self.w_base = nn.Parameter(torch.tensor(1.0))
        self.w_fg = nn.Parameter(torch.tensor(0.5))
        self.bias = nn.Parameter(torch.tensor(0.0))

    def forward(self, orig_logits, fg_max, h_pool):
        eps = 1e-4
        fg_clamped = torch.clamp(fg_max.unsqueeze(-1), eps, 1.0 - eps)
        fg_logit = torch.log(fg_clamped / (1.0 - fg_clamped))
        slot_adj = self.mlp_slot(h_pool)
        s_det = self.w_base * orig_logits.unsqueeze(-1) + self.w_fg * fg_logit + slot_adj + self.bias
        return s_det.squeeze(-1)


class AlignedCalibrationVerifier(nn.Module):
    """
    P1 Model: Aligned Calibration Verifier.
    Integrates detector adapter with reference-centered CLIP vision-language evidence.
    NO free text-only prior MLP.
    """
    def __init__(self, slot_dim=512):
        super().__init__()
        self.detector_adapter = DetectorAdapter(slot_dim=slot_dim)
        
        # Scaling parameters for reference-centered similarities
        self.raw_alpha_cand = nn.Parameter(torch.tensor(0.2))
        self.raw_alpha_glob = nn.Parameter(torch.tensor(0.1))
        
        # Temperature / scale factor for similarity alignment
        self.scale_sim = nn.Parameter(torch.tensor(10.0))

    def forward(self, batch):
        """
        batch contains:
        - orig_logits, fg_max, h_pool
        - sim_cand_sent: reference-centered candidate similarity
        - sim_glob_sent: reference-centered global video similarity
        """
        s_det = self.detector_adapter(batch["orig_logits"], batch["fg_max"], batch["h_pool"])
        
        alpha_cand = F.softplus(self.raw_alpha_cand)
        alpha_glob = F.softplus(self.raw_alpha_glob)
        
        # Foreground confidence gate: higher confidence -> higher trust in candidate window
        fg = batch["fg_max"]
        gate = torch.sigmoid(5.0 * (fg - 0.2))
        
        # Reference-centered visual evidence (already debiased by train video reference)
        v_evidence = self.scale_sim * (alpha_cand * batch["sim_cand_sent"] + alpha_glob * batch["sim_glob_sent"])
        
        s_exist = s_det + gate * v_evidence
        
        return {
            "s_exist": s_exist,
            "s_det": s_det,
            "v_evidence": v_evidence,
            "gate": gate,
            "alpha_cand": alpha_cand,
            "alpha_glob": alpha_glob
        }
