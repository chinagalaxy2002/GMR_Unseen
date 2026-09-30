"""Frozen training-side diagnostic; all writes confined to this experiment."""
import hashlib,json,os,subprocess,sys,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE/'code'),str(ROOT),str(ROOT/'training/qd_detr_gmr')]
import torch

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    run=Path(sys.argv[1]).resolve()
    if not run.is_relative_to(HERE/'runs'):raise ValueError(run)
    run.mkdir(exist_ok=False,parents=True)
    start=time.monotonic()
    status={'state':'preflight','pid':os.getpid(),'start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    def update(**k):
        status.update(k);(run/'status.json').write_text(json.dumps(status,indent=2))
    update()
    try:
        view=HERE/'runs/pseudo_unseen_a1_throw'
        m=json.loads((view/'view_manifest.json').read_text())
        for v in m['derived'].values():assert sha(v['path'])==v['sha256']
        prior=json.loads((HERE/'runs/stage0/manifest.json').read_text())
        assets={}
        for split,v in prior['splits'].items():
            p=ROOT/'data/release/semantic_existence_v2'/split/'train.jsonl'
            assert sha(p)==v['train_sha256'];assets[str(p)]=sha(p)
            for b in v['baselines'].values():
                for p,h in zip(b['checkpoint_paths'],b['checkpoint_sha256']):
                    assert sha(p)==h;assets[p]=h
        assert torch.cuda.is_available()
        for i in range(torch.cuda.device_count()):assert torch.ones(4,device=f'cuda:{i}').sum().item()==4
        rows={n:[json.loads(l) for l in (view/n).read_text().splitlines()] for n in m['derived']}
        assert not {r['vid'] for r in rows['train.jsonl']}&{r['vid'] for r in rows['pseudo_unseen_dev.jsonl']}
        features=set()
        for rr in rows.values():
            for r in rr:
                features.add(ROOT/'features/semantic_existence_v2/A1/clip_text'/f"qid{r['qid']}.npz")
                for k in ('vid_clip','vid_slowfast'):
                    features.add(Path('/home/guoxiangyu/paper/新建文件夹/charades')/k/f"{Path(r['vid']).stem}.npz")
        for p in sorted(features):assert p.is_file();assets[str(p)]=sha(p)
        protocol={'purpose':'training-internal mechanism diagnostic; not official full-S experiment','seed':3407,'epochs':100,'batch_size':16,'workers':0,'expected_updates':47300,'expected_row_exposures':756700,'early_stop':False,'initialization':'from scratch; no old checkpoint or teacher','selection':'original seen-only MR-full-mAP; original fallback rule','official_gate':{'threshold':0.5,'hard':False},'stages':[0,1,10,30,100],'probe':{'dimensions':256,'fit_rows':'all 7567 development training rows','epochs':100,'batch_size':256,'optimizer':'AdamW lr=0.001 wd=0.0001','seed':3407,'views':['raw_joint','raw_video','raw_text','projection_joint','projection_video','projection_text','decoder_max','decoder_mean'],'selection':'final fixed-budget probe; no pseudo-U checkpoint/threshold selection','standardization':'fit only train; deterministic signed random projection to 256 for raw inputs','calibration':'train fitted scalar affine logistic; seen threshold only','bootstrap':'1000 paired resamples of videos seed=3407'},'mechanism_gate':'candidate hypothesis support requires >=0.03 paired pseudo-U AUROC gain over original head, paired video 95% CI lower bound >0, seen AUROC loss <=0.01; joint readout must beat both unimodal controls by >=0.03 with paired CI lower bound >0. Failure/inconclusive forbids claiming representation bottleneck. A readout gain alone is associative, not causal.','limitations':['single held action; training video distribution shifts','workers=0 differs from historical config; all future paired comparisons must share it','no true U access in development','flops not yet measured; forward counts/wall/memory recorded']}
        (run/'protocol.json').write_text(json.dumps(protocol,indent=2))
        provenance={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{str(p):sha(p) for d in ('models/qd_detr_gmr','training/qd_detr_gmr','configs/qd_detr_gmr') for p in (ROOT/d).rglob('*') if p.is_file() and p.suffix in ('.py','.yml')},'local_code_sha256':{str(p):sha(p) for p in (HERE/'code').rglob('*.py')},'assets_sha256':assets,'view_manifest_sha256':sha(view/'view_manifest.json'),'torch':torch.__version__,'devices':[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],'output':str(run),'protocol_sha256':sha(run/'protocol.json')}
        (run/'provenance.json').write_text(json.dumps(provenance,indent=2))
        from training.qd_detr_gmr.config import BaseOptions
        from vendor.qd_train import start_training
        c=BaseOptions('qd_detr','charades_semantic_existence','clip_slowfast');c.parse();opt=c.option
        opt.update(seed=3407,n_epoch=100,bsz=16,eval_bsz=16,max_es_cnt=-1,num_workers=0,device='cuda:0',train_path=str(view/'train.jsonl'),eval_path=str(view/'val_seen.jsonl'),t_feat_dir=str(ROOT/'features/semantic_existence_v2/A1/clip_text'),v_feat_dirs=[str(Path('/home/guoxiangyu/paper/新建文件夹/charades')/k) for k in ('vid_clip','vid_slowfast')],results_dir=str(run),mr_only=True,lw_saliency=0)
        for k,n in [('ckpt_filepath','ckpt_filename'),('train_log_filepath','train_log_filename'),('eval_log_filepath','eval_log_filename')]:opt[k]=str(run/opt[n])
        torch.set_num_threads(4)
        update(state='training',preflight_wall_seconds=time.monotonic()-start)
        start_training(opt)
        update(state='training_complete_diagnostics_pending',wall_seconds=time.monotonic()-start)
    except BaseException:
        update(state='failed',error=traceback.format_exc(),wall_seconds=time.monotonic()-start);raise
if __name__=='__main__':main()
