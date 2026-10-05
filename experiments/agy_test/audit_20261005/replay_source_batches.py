"""Replay first and most discrepant official test batches, without training."""
from pathlib import Path
import json
import sys
import numpy as np
import torch
from easydict import EasyDict
from scipy.special import expit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from models.qd_detr_gmr import build_model
from training.qd_detr_gmr.dataset import StartEndDataset, start_end_collate, prepare_batch_inputs
from audit_results import SPLITS, rows

torch.set_num_threads(2)
out = {}
for split in SPLITS:
    base = ROOT / "results/semantic_existence/multi_split_v2" / split / "qd"
    ckpt = torch.load(base / "best.ckpt", map_location="cpu", weights_only=False)
    opt = EasyDict(ckpt["opt"])
    opt.device = "cuda:0"
    model, _ = build_model(opt)
    model.load_state_dict(ckpt["model"])
    model.cuda().eval()
    cache = np.load(ROOT / "experiments/agy_test/cache/hq" / split / "test.npz")
    official = {str(x["qid"]): x for x in rows(base / "test/qd_detr_gmr_test_submission.jsonl")}
    truth = rows(ROOT / "data/release/semantic_existence_v2" / split / "test.jsonl")
    cache_index = {str(q):i for i,q in enumerate(cache["qids"])}
    pub = np.array([official[str(q)]["pred_exist_score"] for q in cache["qids"]])
    worst_q = str(cache["qids"][np.argmax(np.abs(expit(cache["orig_logits"].astype(float))-pub))])
    wi = next(i for i,x in enumerate(truth) if str(x["qid"]) == worst_q)
    ds = StartEndDataset(dset_name=opt.dset_name,
        data_path=str(ROOT / "data/release/semantic_existence_v2" / split / "test.jsonl"),
        v_feat_dirs=opt.v_feat_dirs, q_feat_dir=opt.t_feat_dir,
        q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
        max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
        max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
        load_labels=False, mr_only=True, keep_empty_gt=True)
    samples = []
    for start in sorted(set([0,wi//16*16])):
        batch = start_end_collate([ds[i] for i in range(start,min(start+16,len(ds)))])
        inputs,_ = prepare_batch_inputs(batch[1], "cuda:0")
        with torch.no_grad():
            score = model(**inputs)["pred_exist_logits"].cpu().numpy()
        for row,z in zip(batch[0],score):
            q=str(row["qid"])
            cz=float(cache["orig_logits"][cache_index[q]])
            p=float(official[q]["pred_exist_score"])
            samples.append(dict(qid=q, fresh_logit=float(z), cached_logit=cz,
                published_probability=p, fresh_probability=float(expit(float(z))),
                cached_probability=float(expit(cz))))
    out[split] = dict(worst_qid=worst_q, batch_size=16, rows=samples,
        fresh_cached_max_logit_error=max(abs(x["fresh_logit"]-x["cached_logit"]) for x in samples),
        fresh_published_max_probability_error=max(abs(round(x["fresh_probability"],4)-x["published_probability"]) for x in samples))
    print(split,{k:v for k,v in out[split].items() if k!='rows'},flush=True)
    del model
Path(__file__).with_name("source_batch_replay.json").write_text(json.dumps(out,indent=2)+"\n")
