"""
QD-DETR model with Quality-Aware Slot Witness (QSW) Existence Head.
Constructed cleanly without modifying any files in the original codebase.
"""
from __future__ import annotations
import sys
from pathlib import Path
import torch
from torch import nn, Tensor

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from models.qd_detr_gmr import build_model as build_base_qd
from experiments.agy_test.e2e_training.models.qsw_adapter import QSWAdapter

class QSW_QDDETR(nn.Module):
    """
    Wraps standard QD-DETR, replacing the coordinate-wise max GMR adapter
    with the Quality-Aware Slot Witness (QSW) Adapter.
    """
    def __init__(self, base_model: nn.Module, hidden_dim: int = 256, temperature: float = 0.5):
        super().__init__()
        self.base_model = base_model
        # Disable the old existence head if present
        self.base_model.use_exist_head = False
        self.base_model.exist_head = None
        
        # New Quality-Aware Slot Witness Adapter
        self.qsw_adapter = QSWAdapter(input_dim=hidden_dim, hidden_dim=hidden_dim, temperature=temperature)

    def forward(self, src_txt, src_txt_mask, src_vid, src_vid_mask, src_aud=None, src_aud_mask=None):
        # 1. Forward through base QD-DETR
        outputs = self.base_model(
            src_txt=src_txt,
            src_txt_mask=src_txt_mask,
            src_vid=src_vid,
            src_vid_mask=src_vid_mask,
            src_aud=src_aud,
            src_aud_mask=src_aud_mask
        )
        
        # 2. Extract decoder slot representations and class logits
        # In base QD-DETR, self.transformer returns (hs, reference, memory, memory_global)
        # hs[-1] is the last decoder layer query embeddings [B, 10, 256]
        # outputs["pred_logits"] is [B, 10, 2]
        pred_logits = outputs["pred_logits"]
        hs_last = getattr(self.base_model, "_last_hs", None)
        
        # If _last_hs not saved, hook it from transformer
        if hs_last is None:
            # We can register hook on transformer to capture hs[-1]
            raise RuntimeError("Last decoder hidden state hs[-1] was not captured.")
            
        outputs["pred_exist_logits"] = self.qsw_adapter(hs_last, pred_logits)
        return outputs

def build_qsw_qd_model(opt, checkpoint_path=None, device="cuda:0"):
    """
    Builds the QD-DETR model, installs hook for hs[-1], attaches QSWAdapter,
    and optionally initializes backbone weights from canonical checkpoint.
    """
    base_model, base_criterion = build_base_qd(opt)
    
    # Store hs[-1] dynamically during transformer forward
    orig_forward = base_model.forward
    def forward_with_hs_capture(*args, **kwargs):
        # Patch forward to capture hs[-1]
        if kwargs.get("src_aud") is not None:
            src_vid = torch.cat([kwargs["src_vid"], kwargs["src_aud"]], dim=2)
        else:
            src_vid = kwargs["src_vid"]
            
        src_txt = kwargs["src_txt"]
        src_txt_mask = kwargs["src_txt_mask"]
        src_vid_mask = kwargs["src_vid_mask"]
        
        src_vid = base_model.input_vid_proj(src_vid)
        src_txt = base_model.input_txt_proj(src_txt)
        src = torch.cat([src_vid, src_txt], dim=1)
        mask = torch.cat([src_vid_mask, src_txt_mask], dim=1).bool()
        
        pos_vid = base_model.position_embed(src_vid, src_vid_mask)
        pos_txt = base_model.txt_position_embed(src_txt) if base_model.use_txt_pos else torch.zeros_like(src_txt)
        pos = torch.cat([pos_vid, pos_txt], dim=1)
        
        bsz = src.shape[0]
        mask_ = torch.ones((bsz, 1), dtype=torch.bool, device=mask.device)
        mask = torch.cat([mask_, mask], dim=1)
        
        src_ = base_model.global_rep_token.view(1, 1, base_model.hidden_dim).repeat(bsz, 1, 1)
        src = torch.cat([src_, src], dim=1)
        
        pos_ = base_model.global_rep_pos.view(1, 1, base_model.hidden_dim).repeat(bsz, 1, 1)
        pos = torch.cat([pos_, pos], dim=1)
        
        video_length = src_vid.shape[1]
        hs, reference, memory, memory_global = base_model.transformer(
            src, ~mask, base_model.query_embed.weight, pos, video_length=video_length
        )
        base_model._last_hs = hs[-1] # [B, 10, 256]
        
        from models.qd_detr_gmr.transformer import inverse_sigmoid
        outputs_class = base_model.class_embed(hs)
        reference_before_sigmoid = inverse_sigmoid(reference)
        tmp = base_model.span_embed(hs)
        outputs_coord = tmp + reference_before_sigmoid
        if base_model.span_loss_type == "l1":
            outputs_coord = outputs_coord.sigmoid()
            
        out = {
            "pred_logits": outputs_class[-1],
            "pred_spans": outputs_coord[-1],
        }
        out["pred_exist_logits"] = base_model.qsw_adapter(hs[-1], outputs_class[-1])
        return out
        
    base_model.forward = forward_with_hs_capture
    base_model.qsw_adapter = QSWAdapter(input_dim=opt.hidden_dim, hidden_dim=opt.hidden_dim)
    base_model.use_exist_head = True
    
    if checkpoint_path is not None and Path(checkpoint_path).exists():
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        state_dict = ckpt["model"]
        # Filter out old exist_head weights
        state_dict = {k: v for k, v in state_dict.items() if not k.startswith("exist_head.")}
        missing, unexpected = base_model.load_state_dict(state_dict, strict=False)
        print(f"Loaded backbone checkpoint from {checkpoint_path}")
        print(f"  Missing (expected for new QSWAdapter): {len(missing)}")
        print(f"  Unexpected: {len(unexpected)}")
        
    base_model.to(device)
    return base_model, base_criterion
