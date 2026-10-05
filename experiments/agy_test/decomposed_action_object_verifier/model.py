#!/usr/bin/env python3
"""
Model Architecture for Decomposed Action-Object Verifier (DAO-Verifier).
Implements decomposed motion-action and appearance-object verification
with query-prior debiasing and detector confidence fusion.
Zero edits to original repo code.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class ActionVerificationStream(nn.Module):
    """
    Verifies kinetic motion dynamics against action verb semantics.
    Uses 3D SlowFast features inside candidate window and temporal flow.
    Includes explicit query prior subtraction to prevent language frequency bias.
    """
    def __init__(self, sf_dim=2304, text_dim=512, hidden_dim=256):
        super().__init__()
        self.proj_cand = nn.Sequential(
            nn.Linear(sf_dim, text_dim),
            nn.LayerNorm(text_dim),
            nn.GELU(),
            nn.Linear(text_dim, text_dim),
            nn.LayerNorm(text_dim)
        )
        self.proj_flow = nn.Sequential(
            nn.Linear(sf_dim, text_dim),
            nn.LayerNorm(text_dim),
            nn.GELU(),
            nn.Linear(text_dim, text_dim),
            nn.LayerNorm(text_dim)
        )
        # Prior MLP predicts expected score solely from action text token
        self.prior_mlp = nn.Sequential(
            nn.Linear(text_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1)
        )
        # Interaction MLP combines multi-view kinetic alignment features
        # Input features:
        # - inter_cand (text_dim)
        # - inter_flow (text_dim)
        # - cos_cand (1)
        # - cos_flow (1)
        # - cos_rel (1)
        # Total = text_dim * 2 + 3 = 1027
        self.action_mlp = nn.Sequential(
            nn.Linear(text_dim * 2 + 3, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )

    def forward(self, v_sf_cand, v_sf_start, v_sf_end, v_sf_glob, q_act):
        # 1. Flow trajectory: end minus start
        flow = v_sf_end - v_sf_start
        # 2. Relative motion: cand minus global video average
        rel = v_sf_cand - v_sf_glob

        m_cand = F.normalize(self.proj_cand(v_sf_cand), p=2, dim=-1)
        m_flow = F.normalize(self.proj_flow(flow), p=2, dim=-1)
        m_rel = F.normalize(self.proj_cand(rel), p=2, dim=-1)
        q_act_norm = F.normalize(q_act, p=2, dim=-1)

        # Similarities
        cos_cand = (m_cand * q_act_norm).sum(dim=-1, keepdim=True)
        cos_flow = (m_flow * q_act_norm).sum(dim=-1, keepdim=True)
        cos_rel = (m_rel * q_act_norm).sum(dim=-1, keepdim=True)

        inter_cand = m_cand * q_act_norm
        inter_flow = m_flow * q_act_norm

        feat = torch.cat([inter_cand, inter_flow, cos_cand, cos_flow, cos_rel], dim=-1)
        s_act_raw = self.action_mlp(feat)
        prior = self.prior_mlp(q_act_norm)

        # Debiased action evidence
        evidence_act = s_act_raw - prior
        return evidence_act, s_act_raw, prior


class ObjectVerificationStream(nn.Module):
    """
    Verifies visual appearance against object noun semantics using 2D CLIP features.
    Computes local candidate window match contrasted with global video background.
    """
    def __init__(self, clip_dim=512, hidden_dim=256):
        super().__init__()
        self.prior_mlp = nn.Sequential(
            nn.Linear(clip_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1)
        )
        # Input features:
        # - inter_obj (clip_dim)
        # - cos_cand (1)
        # - delta_cos (1)
        # Total = clip_dim + 2 = 514
        self.object_mlp = nn.Sequential(
            nn.Linear(clip_dim + 2, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 64),
            nn.GELU(),
            nn.Linear(64, 1)
        )

    def forward(self, v_clip_cand, v_clip_glob, q_obj):
        v_cand_norm = F.normalize(v_clip_cand, p=2, dim=-1)
        v_glob_norm = F.normalize(v_clip_glob, p=2, dim=-1)
        q_obj_norm = F.normalize(q_obj, p=2, dim=-1)

        cos_cand = (v_cand_norm * q_obj_norm).sum(dim=-1, keepdim=True)
        cos_glob = (v_glob_norm * q_obj_norm).sum(dim=-1, keepdim=True)
        delta_cos = cos_cand - cos_glob

        inter_obj = v_cand_norm * q_obj_norm
        feat = torch.cat([inter_obj, cos_cand, delta_cos], dim=-1)
        s_obj_raw = self.object_mlp(feat)
        prior = self.prior_mlp(q_obj_norm)

        # Debiased object evidence
        evidence_obj = s_obj_raw - prior
        return evidence_obj, s_obj_raw, prior


class DecomposedActionObjectVerifier(nn.Module):
    """
    Full Decomposed Action-Object Verifier (DAO-Verifier).
    Integrates:
    1. Detector confidence (baseline logit + foreground log-odds + slot features)
    2. Motion-Action Kinetic Verification (SlowFast + temporal flow)
    3. Appearance-Object Verification (CLIP local-vs-global contrast)
    """
    def __init__(self, sf_dim=2304, clip_dim=512, slot_dim=512, hidden_dim=256):
        super().__init__()
        self.action_stream = ActionVerificationStream(sf_dim=sf_dim, text_dim=clip_dim, hidden_dim=hidden_dim)
        self.object_stream = ObjectVerificationStream(clip_dim=clip_dim, hidden_dim=hidden_dim)
        
        # Detector confidence adapter
        self.mlp_slot = nn.Sequential(
            nn.Linear(slot_dim, 128),
            nn.GELU(),
            nn.Linear(128, 1)
        )
        self.w_base = nn.Parameter(torch.tensor(1.0))
        self.w_fg = nn.Parameter(torch.tensor(0.5))
        self.bias = nn.Parameter(torch.tensor(0.0))

        # Non-negative fusion weights for decomposed evidence
        self.raw_alpha_act = nn.Parameter(torch.tensor(0.5))
        self.raw_alpha_obj = nn.Parameter(torch.tensor(0.5))

    def forward(self, batch):
        """
        batch contains:
        - v_sf_cand, v_sf_start, v_sf_end, v_sf_glob
        - v_clip_cand, v_clip_glob
        - q_act, q_obj
        - h_pool (512-dim dual pooled slot hidden states)
        - orig_logits, fg_max
        """
        # 1. Action evidence
        ev_act, raw_act, prior_act = self.action_stream(
            batch["v_sf_cand"],
            batch["v_sf_start"],
            batch["v_sf_end"],
            batch["v_sf_glob"],
            batch["q_act"]
        )

        # 2. Object evidence
        ev_obj, raw_obj, prior_obj = self.object_stream(
            batch["v_clip_cand"],
            batch["v_clip_glob"],
            batch["q_obj"]
        )

        # 3. Detector confidence
        eps = 1e-4
        fg_clamped = torch.clamp(batch["fg_max"].unsqueeze(-1), eps, 1.0 - eps)
        fg_logit = torch.log(fg_clamped / (1.0 - fg_clamped))
        slot_adj = self.mlp_slot(batch["h_pool"])
        
        s_det = self.w_base * batch["orig_logits"].unsqueeze(-1) + self.w_fg * fg_logit + slot_adj + self.bias

        # 4. Joint fusion
        alpha_act = F.softplus(self.raw_alpha_act)
        alpha_obj = F.softplus(self.raw_alpha_obj)

        s_exist = s_det + alpha_act * ev_act + alpha_obj * ev_obj

        return {
            "s_exist": s_exist.squeeze(-1),
            "s_det": s_det.squeeze(-1),
            "ev_act": ev_act.squeeze(-1),
            "ev_obj": ev_obj.squeeze(-1),
            "raw_act": raw_act.squeeze(-1),
            "prior_act": prior_act.squeeze(-1),
            "raw_obj": raw_obj.squeeze(-1),
            "prior_obj": prior_obj.squeeze(-1),
            "alpha_act": alpha_act,
            "alpha_obj": alpha_obj
        }
