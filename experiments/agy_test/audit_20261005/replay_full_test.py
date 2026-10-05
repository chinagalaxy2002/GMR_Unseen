"""Replay all test queries from canonical QD checkpoints, at official batch size.

Both readouts see identical fresh decoder states. Final scalar weights, scaler,
and Seen-selected threshold stay frozen. No optimization or threshold retuning.
"""
from pathlib import Path
import json
import sys
import numpy as np
import torch
from easydict import EasyDict
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from models.qd_detr_gmr import build_model
from training.qd_detr_gmr.dataset import StartEndDataset, start_end_collate, prepare_batch_inputs
from audit_results import SPLITS, rows, signals, forward, metrics, prepared_auc

OUT = Path(__file__).resolve().parent
torch.set_num_threads(2)
report = {"protocol": "canonical QD checkpoints, official eval_bsz=16, fresh features; final scalar checkpoint/scaler/threshold frozen", "splits": {}}
boot_data = {}
for split in SPLITS:
    base = ROOT / "results/semantic_existence/multi_split_v2" / split / "qd"
    final = ROOT / "experiments/agy_test/e2e_training/results_final" / split
    ckpt = torch.load(base / "best.ckpt", map_location="cpu", weights_only=False)
    calibrator = torch.load(final / "best.ckpt", map_location="cpu", weights_only=False)
    opt = EasyDict(ckpt["opt"])
    opt.device = "cuda:0"
    model, _ = build_model(opt)
    model.load_state_dict(ckpt["model"])
    model.cuda().eval()
    captured = {}
    def hook(_m, _i, outputs):
        captured["hs"] = outputs[0][-1].detach()
    handle = model.transformer.register_forward_hook(hook)
    release = ROOT / "data/release/semantic_existence_v2" / split
    ds = StartEndDataset(dset_name=opt.dset_name, data_path=str(release / "test.jsonl"),
        v_feat_dirs=opt.v_feat_dirs, q_feat_dir=opt.t_feat_dir,
        q_feat_type="last_hidden_state", max_q_l=int(opt.max_q_l),
        max_v_l=int(opt.max_v_l), ctx_mode=opt.ctx_mode, clip_len=int(opt.clip_length),
        max_windows=int(opt.max_windows), span_loss_type=opt.span_loss_type,
        load_labels=False, mr_only=True, keep_empty_gt=True)
    loader = DataLoader(ds,batch_size=16,shuffle=False,num_workers=0,collate_fn=start_end_collate)
    sig_parts = {k:[] for k in ["orig_logits", "cos_disp", "slot_max_dev", "fg_max"]}
    metadata, spans_parts, fg_parts = [], [], []
    for bi,batch in enumerate(loader):
        inputs,_ = prepare_batch_inputs(batch[1], "cuda:0")
        with torch.no_grad():
            result = model(**inputs)
        data = {"hs":captured["hs"].cpu().numpy(),
                "orig_logits":result["pred_exist_logits"].cpu().numpy(),
                "fg":result["pred_logits"].softmax(-1)[...,0].cpu().numpy()}
        sg = signals(data)
        for k in sg:
            sig_parts[k].append(sg[k])
        spans_parts.append(result["pred_spans"].detach().cpu().numpy())
        fg_parts.append(data["fg"])
        metadata.extend(batch[0])
        if bi%100 == 0:
            print(split, 'batches',bi+1,'/',len(loader),flush=True)
    handle.remove()
    sig = {k:np.concatenate(x) for k,x in sig_parts.items()}
    original = sig["orig_logits"]
    new = forward(sig,calibrator)
    test = dict(qids=np.array([str(x["qid"]) for x in metadata]),
                labels=np.array([int(x["exist_label"]) for x in metadata]),
                partitions=np.array([x["partition"] for x in metadata]),
                vids=np.array([x["vid"] for x in metadata]))
    pairs = rows(release/"matched_u_pairs.jsonl")
    th = float(calibrator["metrics"]["Threshold"])
    old_diag = json.loads((base/"diagnostics.json").read_text())
    probability = torch.from_numpy(original).sigmoid().numpy().astype(float)
    rounded = np.array([float(f'{x:.4f}') for x in probability])
    pub = {str(x["qid"]):x for x in rows(base/"test/qd_detr_gmr_test_submission.jsonl")}
    pub_score = np.array([pub[q]["pred_exist_score"] for q in test["qids"]])
    cached = {str(x["qid"]):x["pred_score"] for x in rows(final/"predictions.jsonl")}
    old_scores = np.array([cached[q] for q in test["qids"]])
    r = dict(baseline_logit=metrics(original,test,pairs), final_logit=metrics(new,test,pairs,th),
        baseline_rounded_probability=metrics(rounded,test,pairs,old_diag["threshold"]),
        published_probability_max_abs_error=float(np.max(np.abs(rounded-pub_score))),
        final_vs_cached_score_max_abs_error=float(np.max(np.abs(new-old_scores))),
        final_vs_cached_score_diff_gt_001_n=int((np.abs(new-old_scores)>.01).sum()),
        signals={k:metrics(s,test,pairs) for k,s in sig.items()})
    sp,fg = np.concatenate(spans_parts),np.concatenate(fg_parts)
    hits=[]
    for i,row in enumerate(metadata):
        c,w = map(float,sp[i,int(fg[i].argmax())])
        a,b = np.clip([(c-w/2)*row['duration'],(c+w/2)*row['duration']],0,row['duration'])
        best=0.
        for g,e in row['relevant_windows']:
            inter=max(0.,min(b,e)-max(a,g));union=b-a+e-g-inter
            best=max(best,inter/union if union>0 else 0.)
        hits.append(best>=.5)
    hits=np.array(hits);pos=test['partitions']=='U+'
    r['U_pos_raw_R1_iou05']=float(hits[pos].mean())
    r['U_pos_final_gated_R1_iou05']=float((hits[pos] & (new[pos]>=th)).mean())
    report['splits'][split]=r
    np.savez(OUT/(split+'_fresh_test_signals.npz'),**test,**sig,final=new)
    with (OUT/(split+'_fresh_test_predictions.jsonl')).open('w') as f:
        for q,p,z,n in zip(test['qids'],test['partitions'],original,new):
            f.write(json.dumps(dict(qid=str(q),partition=str(p),baseline_logit=float(z),final_logit=float(n)))+'\n')
    boot_data[split]=dict(y=test['labels'],parts=test['partitions'],vids=test['vids'],original=original,final=new)
    print('RESULT',split,json.dumps({k:v for k,v in r.items() if k!='signals'}),flush=True)
    del model
keys=['Seen_AUROC','Unseen_AUROC','Gap','Matched_PairAcc']
report['macro_means']={name:{k:float(np.mean([r[name][k] for r in report['splits'].values()])) for k in keys} for name in ['baseline_logit','final_logit','baseline_rounded_probability']}
all_vids=sorted(set(np.concatenate([x['vids'] for x in boot_data.values()])))
vmap={v:i for i,v in enumerate(all_vids)}
funcs=[]
for d in boot_data.values():
    vi=np.array([vmap[v] for v in d['vids']]);group=[]
    for parts in [['S+','S-'],['U+','U-']]:
        mask=np.isin(d['parts'],parts)
        group.append([prepared_auc(d['y'][mask],d[k][mask],vi[mask]) for k in ['original','final']])
    funcs.append(group)
rng=np.random.default_rng(20261005);deltas=np.empty((2000,len(SPLITS),3))
for b in range(2000):
    counts=np.bincount(rng.integers(len(all_vids),size=len(all_vids)),minlength=len(all_vids)).astype(float)
    for i,group in enumerate(funcs):
        ds,du=[f[1](counts)-f[0](counts) for f in group]
        deltas[b,i]=[ds,du,du-ds]
names=['delta_seen_final_minus_baseline','delta_unseen_final_minus_baseline','gap_reduction_baseline_minus_final']
ci=lambda arr:{name:np.nanquantile(arr[:,j],[.025,.975]).tolist() for j,name in enumerate(names)}
report['paired_video_bootstrap']=dict(repeats=2000,seed=20261005,video_clusters=len(all_vids),note='joint shared-video paired resampling; frozen model; exploratory results; no training-seed or selection uncertainty',per_split={s:ci(deltas[:,i]) for i,s in enumerate(SPLITS)},macro=ci(np.nanmean(deltas,axis=1)))
(OUT/'fresh_test_replay_metrics.json').write_text(json.dumps(report,indent=2)+'\n')
print('MACRO',json.dumps(report['macro_means']),flush=True)
print('CI',json.dumps(report['paired_video_bootstrap']),flush=True)
