"""Clean V3 seen-only training, native inference and clustered baseline evaluation."""
import csv
import datetime
import fcntl
import json
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import numpy as np
from sklearn.metrics import roc_auc_score
from common import ROOT, REPO, RELEASE, NATIVE, GROUPS, BACKBONES, GMR, NUMERICAL, VIDEO, environment, read_rows, save_json, digest
sys.path.insert(0, str(NATIVE))
from eval.metrics import _clean_pred_windows, _compute_set_iou_score

LOCK = threading.Lock()
STATUS = {}
NAMES = {'moment':'Moment-DETR-GMR','qd':'QD-DETR-GMR','flash':'FlashVTG-GMR'}
KEYS = ('seen_auc','unseen_auc','gap','rej_f1','rr','s_frr','u_frr','gmiou1')


def update(key, **value):
    with LOCK:
        STATUS[key] = {**STATUS.get(key, {}), **value}
        save_json(ROOT/'QUEUE_STATUS.json', dict(updated=datetime.datetime.now().isoformat(), jobs=STATUS))


def prepare():
    prior = {r['qid']:r for r in json.loads((ROOT.parent/'v3_addseen_20261009/TEXT_FEATURE_MANIFEST.json').read_text())}
    shared = ROOT/'features/clip_text'; shared.mkdir(parents=True, exist_ok=True)
    inventory, records = {}, {}
    import hashlib
    for group in GROUPS:
        target = ROOT/'groups'/group/'release'/group
        target.mkdir(parents=True, exist_ok=True)
        source = RELEASE/'splits'/group
        for path in source.iterdir():
            if path.is_file():
                dest=target/path.name
                if dest.exists() and digest(dest)!=digest(path):
                    raise ValueError('Release changed since snapshot: '+str(path))
                shutil.copy2(path,dest)
        parts={part:read_rows(target/(part+'.jsonl')) for part in ('train','val','test')}
        assert all(r['partition'] in ('S+','S-') for r in parts['train'])
        assert read_rows(target/'val_seen.jsonl') == [r for r in parts['val'] if r['partition'].startswith('S')]
        for a,b in [('train','val'),('train','test'),('val','test')]:
            assert not ({r['vid'] for r in parts[a]} & {r['vid'] for r in parts[b]})
        for rows in parts.values():
            assert len({str(r['qid']) for r in rows}) == len(rows)
            for row in rows:
                assert bool(row['relevant_windows']) == bool(row['exist_label'])
                qid=str(row['qid']); query_hash=hashlib.sha256(row['query'].encode()).hexdigest()
                record=prior[qid]; assert record['query_sha256']==query_hash
                feature=__import__('pathlib').Path(record['source'])
                assert digest(feature)==record['feature_sha256']
                dest=shared/('qid'+qid+'.npz')
                if not dest.exists(): dest.symlink_to(feature)
                for folder in ('vid_clip','vid_slowfast'): assert (VIDEO/folder/(row['vid']+'.npz')).is_file()
                records[qid]=record
        feat=ROOT/'groups'/group/'features'/group; feat.mkdir(parents=True,exist_ok=True)
        for name, src in [('clip_text',shared),('val_seen.jsonl',target/'val_seen.jsonl')]:
            if not (feat/name).exists(): (feat/name).symlink_to(src)
        inventory[group]={p.name:digest(p) for p in target.iterdir() if p.is_file()}
    save_json(ROOT/'DATA_AUDIT.json', dict(release=str(RELEASE),groups=inventory,unique_queries=len(records),exact_query_feature_identity=True,video_disjoint=True,seen_only_train=True))
    save_json(ROOT/'TEXT_FEATURE_MANIFEST.json',list(records.values()))
    save_json(ROOT/'SOURCE_MANIFEST.json',{str(p.relative_to(NATIVE)):digest(p) for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in p.parts})


def metrics(y,p,sc,threshold,iou,weights):
    accept=sc>=threshold
    def mean(values, mask):
        return float(np.dot(weights[mask],values[mask])/weights[mask].sum()) if weights[mask].sum() else float('nan')
    def auc(mask):
        mask=mask & (weights>0)
        return float(roc_auc_score(y[mask],sc[mask],sample_weight=weights[mask])) if len(np.unique(y[mask]))==2 else float('nan')
    sa,ua=auc(np.char.startswith(p,'S')),auc(np.char.startswith(p,'U'))
    tn=weights[(y==0)&~accept].sum(); fp=weights[(y==0)&accept].sum(); fn=weights[(y==1)&~accept].sum()
    return dict(seen_auc=sa,unseen_auc=ua,gap=sa-ua,rej_f1=100*2*tn/(2*tn+fp+fn),rr=100*np.dot(weights,~accept)/weights.sum(),s_frr=100*mean(~accept,p=='S+'),u_frr=100*mean(~accept,p=='U+'),gmiou1=100*np.dot(weights,np.where(accept,iou,y==0))/weights.sum())


def evaluate(group,bb,val_path,pred_path):
    task=ROOT/'groups'/group; release=task/'release'/group
    val=read_rows(release/'val_seen.jsonl'); vp={str(r['qid']):r for r in read_rows(val_path)}
    assert set(vp)=={str(r['qid']) for r in val}
    vy=np.array([r['exist_label'] for r in val]); vs=np.array([vp[str(r['qid'])]['pred_exist_logit' if bb=='flash' else 'pred_exist_score'] for r in val],np.float32)
    best_ba=-1.; threshold=.5
    for candidate in np.percentile(vs,np.linspace(5,95,91)):
        accept=vs>=candidate; ba=.5*(accept[vy==1].mean()+(~accept[vy==0]).mean())
        if ba>best_ba: best_ba=ba; threshold=float(candidate)
    out=task/'evaluation'/bb; out.mkdir(parents=True,exist_ok=True)
    save_json(out/'FROZEN_CALIBRATION.json',dict(threshold=threshold,seen_validation_ba=best_ba,validation_sha256=digest(release/'val_seen.jsonl'),prediction_sha256=digest(val_path)))
    rows=read_rows(release/'test.jsonl'); pred={str(r['qid']):r for r in read_rows(pred_path)}
    assert set(pred)=={str(r['qid']) for r in rows}
    y=np.array([r['exist_label'] for r in rows]); p=np.array([r['partition'] for r in rows]); vids=np.array([r['vid'] for r in rows])
    sc=np.array([pred[str(r['qid'])]['pred_exist_logit' if bb=='flash' else 'pred_exist_score'] for r in rows],np.float32)
    iou=np.array([_compute_set_iou_score([w[:2] for w in _clean_pred_windows(pred[str(r['qid'])]['pred_relevant_windows'],max_pred_windows=1)],r['relevant_windows']) for r in rows])
    point=metrics(y,p,sc,threshold,iou,np.ones(len(y)))
    np.savez_compressed(out/'predictions.npz',qids=np.array([str(r['qid']) for r in rows]),vids=vids,labels=y,partitions=p,scores=sc,threshold=threshold,accept_iou=iou)
    videos,vi=np.unique(vids,return_inverse=True); rng=np.random.RandomState(3407); draws=[]
    for _ in range(2000):
        weights=np.bincount(rng.randint(len(videos),size=len(videos)),minlength=len(videos))[vi]
        draws.append(list(metrics(y,p,sc,threshold,iou,weights).values()))
    draws=np.array(draws); valid=np.isfinite(draws).all(axis=1)
    assert valid.any()
    np.savez_compressed(out/'bootstrap_draws.npz',draws=draws,valid=valid,videos=videos,keys=np.array(KEYS))
    save_json(out/'bootstrap.json',dict(seed=3407,requested_draws=2000,valid_draws=int(valid.sum()),unit='video cluster',absolute={k:np.percentile(draws[valid,i],[2.5,97.5]).tolist() for i,k in enumerate(KEYS)}))
    save_json(out/'metrics.json',dict(split=group,backbone=bb,method='Baseline',threshold=threshold,**point))
    with LOCK: report()


def report():
    records=[]; intervals={}
    for group in GROUPS:
        for bb in BACKBONES:
            out=ROOT/'groups'/group/'evaluation'/bb
            if (out/'metrics.json').exists():
                records.append(json.loads((out/'metrics.json').read_text())); intervals[(group,bb)]=json.loads((out/'bootstrap.json').read_text())['absolute']
    for bb in BACKBONES:
        rr=[r for r in records if r['backbone']==bb]
        if len(rr)==5:
            records.append(dict(split='MACRO',backbone=bb,method='Baseline',threshold=None,**{k:float(np.mean([r[k] for r in rr])) for k in KEYS}))
            # The same seed and sorted shared video universe pair draws across groups.
            dd=[np.load(ROOT/'groups'/g/'evaluation'/bb/'bootstrap_draws.npz') for g in GROUPS]
            assert all(np.array_equal(dd[0]['videos'],d['videos']) for d in dd)
            macro=np.mean([d['draws'] for d in dd],axis=0); valid=np.isfinite(macro).all(axis=1)
            intervals[('MACRO',bb)]={k:np.percentile(macro[valid,i],[2.5,97.5]).tolist() for i,k in enumerate(KEYS)}
    out=ROOT/'evaluation'; out.mkdir(exist_ok=True)
    save_json(out/'metrics.json',records)
    save_json(out/'bootstrap.json',{'|'.join(k):v for k,v in intervals.items()})
    with (out/'metrics.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['split','backbone','method','threshold',*KEYS]); writer.writeheader();writer.writerows(records)
    lines=['# Clean Semantic Existence v3 baseline evaluation','',f'Completed settings: {sum(r["split"]!="MACRO" for r in records)}/15. Seed 3407; fresh Seen-only training; native Seen-validation checkpoint selection; threshold maximizes BA over 91 Seen-validation percentiles (5–95), earliest tie. AUROC 0–1; gap in pp. Absolute Unseen AUROC 95% CI: 2,000 video-cluster bootstrap draws, seed 3407; fixed checkpoint and threshold. Macro is equal-weight over all five groups, with shared-video draws. Gains/change/reduction are undefined for standalone baselines and shown as —.','', '| Evaluation Variant | Seen AUROC | Unseen AUROC | Performance Gap | Unseen Net Gain | 95% CI (Bootstrap) | Seen Change | Gap Reduction |','|---|---:|---:|---:|---:|---|---:|---:|']
    for r in records:
        lo,hi=intervals[(r['split'],r['backbone'])]['unseen_auc']
        lines.append(f"| {r['split']} / {NAMES[r['backbone']]} / Baseline | {r['seen_auc']:.4f} | {r['unseen_auc']:.4f} | {100*r['gap']:.2f} | — | [{lo:.4f}, {hi:.4f}] absolute | — | — |")
    lines+=['','| Backbone Model | Evaluation Branch | Actual Rejection F1 (Rej-F1) | Overall Rejection Rate (RR) | S+ False Rejection Rate (S+ FRR) | U+ False Rejection Rate (U+ FRR) | End-to-end Localization (G-mIoU@1) |','|---|---|---:|---:|---:|---:|---:|']
    for r in records:
        lines.append(f"| {NAMES[r['backbone']]} | {r['split']} / Baseline | {r['rej_f1']:.2f}% | {r['rr']:.2f}% | {r['s_frr']:.2f}% | {r['u_frr']:.2f}% | {r['gmiou1']:.2f}% |")
    lines+=['','Rej-F1 = 2TN/(2TN+FP+FN), treating rejection as positive. G-mIoU@1 uses the first valid native submitted window (no duration-bound skip), max IoU / number of GT windows; rejected negatives score 1, rejected positives score 0. Each backbone supplies its own localization. See DATA_AUDIT.json, SOURCE_MANIFEST.json, PROTOCOL.json and per-setting calibration, predictions and bootstrap artifacts.','']
    lines += ['', 'Seen/Unseen Rej-F1 and G-mIoU@1 gaps: [GENERALIZATION_DROP_COMPARISON.md](GENERALIZATION_DROP_COMPARISON.md).']
    (out/'STANDARD_EVALUATION.md').write_text('\n'.join(lines))


def job(group,bb,gpu):
    key=group+'/'+bb; task=ROOT/'groups'/group; run=task/'runs'/bb
    env=environment(gpu)
    env.update(V3_NATIVE_REPO=str(NATIVE),TRAIN_GPU=str(gpu),RUN_ROOT=str(task/'runs'),DATA_ROOT=str(task/'release'/group),FEATURE_ROOT=str(task/'features'/group),VIDEO_ROOT=str(VIDEO),GMR_PYTHON=GMR,FLASH_PYTHON=NUMERICAL,SEMANTIC_SEED='3407')
    exit_file=run/'exit_code'
    if not exit_file.exists():
        if run.exists() and list(run.rglob('*.ckpt')):
            import time
            active = lambda: any(str(task/'release'/group/'train.jsonl') in line and ('training.flash_vtg_gmr.train' in line or '/train.py' in line) for line in subprocess.check_output(['ps','-eo','args'],text=True).splitlines())
            if not active(): raise RuntimeError('Interrupted training requires explicit resume: '+key)
            update(key,stage='training',gpu=gpu,recovered_existing_process=True)
            while not exit_file.exists():
                if not active():
                    time.sleep(2)
                    if not exit_file.exists(): raise RuntimeError('Existing training ended without exit status: '+key)
                    break
                time.sleep(20)
        if not exit_file.exists():
            update(key,stage='training',gpu=gpu,started=datetime.datetime.now().isoformat())
            subprocess.run(['bash',str(ROOT/'launch_native.sh'),bb],cwd=NATIVE,env=env,check=True)
    assert exit_file.read_text().strip()=='0'
    source=run
    if bb=='flash':
        dirs=list(run.glob('charadesSTA-*')); assert len(dirs)==1; source=dirs[0]
        names=['model_best.ckpt','opt.json','best_charadesSTA_val_preds.jsonl']
    else: names=['best.ckpt','best_charades_semantic_existence_val_preds.jsonl']
    frozen=task/'frozen_checkpoints'/bb; frozen.mkdir(parents=True,exist_ok=True)
    for name in names: shutil.copy2(source/name,frozen/name)
    save_json(frozen/'MANIFEST.json',{name:digest(frozen/name) for name in names})
    output=run/'test'; output.mkdir(exist_ok=True)
    update(key,stage='inference')
    if bb=='flash':
        cmd=[NUMERICAL,'-m','training.flash_vtg_gmr.inference','configs/flash_vtg_gmr/model.py','--resume',str(frozen/names[0]),'--eval_split_name','test','--eval_path',str(task/'release'/group/'test.jsonl'),'--eval_results_dir',str(output),'--device','0','--nms_thd','-1']
        pred=output/'hl_test_submission.jsonl'
    else:
        cmd=[GMR,f'training/{bb if bb=="qd" else "moment"}_detr_gmr/evaluate.py','--dataset','charades_semantic_existence','--model_path',str(frozen/names[0]),'--split','test','--eval_path',str(task/'release'/group/'test.jsonl'),'--t_feat_dir',str(task/'features'/group/'clip_text'),'--v_feat_dirs',str(VIDEO/'vid_clip'),str(VIDEO/'vid_slowfast'),'--results_dir',str(output),'--device','cuda' if bb=='moment' else 'cuda:0']
        pred=output/(bb+'_detr_gmr_test_submission.jsonl')
    if not pred.exists():
        with (run/'inference.log').open('w') as stream: subprocess.run(cmd,cwd=NATIVE,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
    update(key,stage='bootstrap')
    evaluate(group,bb,frozen/names[-1],pred)
    update(key,stage='complete',finished=datetime.datetime.now().isoformat())


def worker(slot,jobs):
    while True:
        try: group,bb=jobs.get_nowait()
        except Empty: return
        try: job(group,bb,slot%2)
        except Exception as error:
            import traceback
            traceback.print_exc(); update(group+'/'+bb,stage='failed',error=str(error))


def main():
    prepare()
    save_json(ROOT/'PROTOCOL.json',dict(dataset=str(RELEASE),seed=3407,maximum_epochs=100,max_es_cnt=26,warm_start=False,training='S+/S- only',checkpoint_selection={'moment':'Seen validation MR-full-mAP','qd':'Seen validation MR-full-mAP','flash':'Seen validation mean R1@0.5 and R1@0.7'},threshold='full Seen validation BA, 91 percentile candidates 5..95, first tie',bootstrap_draws=2000,bootstrap_unit='video',workers=6,gpus=[0,1],variants=['Baseline'],score_readout='Moment/QD native 4-decimal sigmoid; Flash native 6-decimal logit avoids 3-decimal probability saturation'))
    report(); jobs=Queue()
    for group in GROUPS:
        for bb in BACKBONES: jobs.put((group,bb))
    with ThreadPoolExecutor(max_workers=6) as pool: list(pool.map(lambda slot:worker(slot,jobs),range(6)))
    save_json(ROOT/'PIPELINE_EXIT.json',dict(complete=sum(s['stage']=='complete' for s in STATUS.values()),failed=sum(s['stage']=='failed' for s in STATUS.values()),finished=datetime.datetime.now().isoformat()))
    if any(s['stage']=='failed' for s in STATUS.values()): sys.exit(1)

if __name__=='__main__':
    with (ROOT/'queue.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        main()
