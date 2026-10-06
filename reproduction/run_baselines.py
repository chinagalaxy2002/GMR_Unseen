"""Original baseline recipes with portable paths, one GPU, isolated outputs."""
from pathlib import Path
import argparse
import json
import os
import shlex
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SPLITS=['A1','A2_alt','A3','C1','C2_alt']
MODELS=['flash','moment','qd']

def launch(argv,env,log,dry):
    print(shlex.join(map(str,argv)),flush=True)
    if dry:return
    log.parent.mkdir(parents=True,exist_ok=True)
    (log.with_suffix('.command.json')).write_text(json.dumps({'argv':list(map(str,argv)),'CUDA_VISIBLE_DEVICES':env['CUDA_VISIBLE_DEVICES']},indent=2)+'\n')
    with log.open('w') as f:subprocess.run(list(map(str,argv)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)

def checkpoint(split,bb,base,frozen):
    if frozen:
        idx=json.loads((ROOT/'reproduction/baseline_checkpoint_index.json').read_text())
        return ROOT/idx[split][bb]
    if bb=='flash':
        candidates=list((base/split/bb).glob('charadesSTA-*/model_best.ckpt'))
        assert len(candidates)==1,'Expected one Flash best checkpoint in '+str(base/split/bb)
        return candidates[0]
    return base/split/bb/'best.ckpt'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stage',choices=['train','infer','train-and-infer'],required=True)
    p.add_argument('--splits',nargs='+',choices=SPLITS,default=SPLITS)
    p.add_argument('--models',nargs='+',choices=MODELS,default=MODELS)
    p.add_argument('--gpu',type=int,default=0)
    p.add_argument('--seed',type=int,default=3407)
    p.add_argument('--python',default=sys.executable)
    p.add_argument('--flash-python',default=None)
    p.add_argument('--output',type=Path,default=ROOT/'reproduction_outputs/baselines')
    p.add_argument('--predictions-output',type=Path,default=ROOT/'reproduction_outputs/baseline_predictions')
    p.add_argument('--published-checkpoints',action='store_true',help='Inference from 15 Drive checkpoints, not retraining.')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if a.published_checkpoints and a.stage!='infer':p.error('--published-checkpoints is only valid for --stage infer')
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(a.gpu)
    release=ROOT/'data/release/semantic_existence_v2'
    features=ROOT/'features/semantic_existence_v2'
    clip=ROOT/'features/charades_semantic_existence/clip'
    sf=ROOT/'features/charades_semantic_existence/slowfast'
    for sp in a.splits:
        for bb in a.models:
            py=(a.flash_python or a.python) if bb=='flash' else a.python
            out=a.output/sp/bb
            text=features/sp/'clip_text'
            if not a.dry_run:
                for path in [release/sp/'train.jsonl',release/sp/'test.jsonl',features/sp/'val_seen.jsonl',text,clip,sf]:
                    if not path.exists():raise FileNotFoundError('Restore Drive assets first: '+str(path))
            if a.stage in ['train','train-and-infer']:
                if out.exists() and any(out.iterdir()):raise FileExistsError('Choose an empty --output directory: '+str(out))
                common=['--train_path',release/sp/'train.jsonl','--eval_path',features/sp/'val_seen.jsonl','--t_feat_dir',text,
                        '--seed',a.seed,'--n_epoch',100,'--max_es_cnt',-1]
                if bb in ['moment','qd']:
                    cmd=[py,ROOT/f'training/{bb}_detr_gmr/train.py','--dataset','charades_semantic_existence',*common,
                         '--v_feat_dirs',clip,sf,'--results_dir',out,'--device','cuda' if bb=='moment' else 'cuda:0','--bsz',16,'--eval_bsz',16]
                else:
                    cmd=[py,'-m','training.flash_vtg_gmr.train',ROOT/'configs/flash_vtg_gmr/model.py',
                         '--dset_name','charadesSTA','--ctx_mode','video_tef',*common,'--eval_split_name','val',
                         '--v_feat_dirs',sf,clip,'--v_feat_dim',2816,'--t_feat_dim',512,'--max_q_l',40,'--max_v_l',200,
                         '--clip_length',1,'--max_windows',5,'--lr','3e-5','--lr_drop',400,'--wd','1e-4',
                         '--bsz',8,'--eval_bsz',1,'--eval_epoch',1,'--num_workers',0,'--device',0,
                         '--results_root',out,'--exp_id',f'seen_only_seed{a.seed}_100ep','--hidden_dim',256,'--dim_feedforward',1024,
                         '--enc_layers',3,'--t2v_layers',6,'--dummy_layers',2,'--nheads',8,'--num_dummies',40,
                         '--total_prompts',10,'--num_prompts',1,'--kernel_size',5,'--num_conv_layers',1,'--num_mlp_layers',5,
                         '--use_SRM','--input_dropout',.5,'--dropout',.1,'--span_loss_type','l1',
                         '--lw_reg',1,'--lw_cls',5,'--lw_sal',0,'--lw_saliency',0,'--lw_wattn',1,'--lw_ms_align',1,
                         '--mr_only','--eval_full_only','--use_exist_head','--exist_pool','mean','--exist_loss_coef',1,
                         '--exist_gate_thd',.5,'--nms_thd',-1]
                launch(cmd,env,a.output/sp/(bb+'_train.log'),a.dry_run)
            if a.stage in ['infer','train-and-infer']:
                ckpt=(a.output/sp/bb/'charadesSTA-<training-run>/model_best.ckpt'
                      if a.dry_run and bb=='flash' and not a.published_checkpoints
                      else checkpoint(sp,bb,a.output,a.published_checkpoints))
                if not a.dry_run and not ckpt.exists():raise FileNotFoundError(str(ckpt))
                for subset in ['val','test']:
                    target=a.predictions_output/sp/bb/subset
                    gt=features/sp/'val_seen.jsonl' if subset=='val' else release/sp/'test.jsonl'
                    if bb in ['moment','qd']:
                        cmd=[py,ROOT/f'training/{bb}_detr_gmr/evaluate.py','--dataset','charades_semantic_existence',
                             '--model_path',ckpt,'--split',subset,'--eval_path',gt,'--t_feat_dir',text,
                             '--v_feat_dirs',clip,sf,'--results_dir',target,'--device','cuda' if bb=='moment' else 'cuda:0']
                    else:
                        cmd=[py,'-m','training.flash_vtg_gmr.inference',ROOT/'configs/flash_vtg_gmr/model.py',
                             '--resume',ckpt,'--eval_split_name',subset,'--eval_path',gt,'--eval_results_dir',target,
                             '--t_feat_dir',text,'--v_feat_dirs',sf,clip,'--device',0,'--nms_thd',-1]
                    launch(cmd,env,a.predictions_output/sp/bb/(subset+'.log'),a.dry_run)
    print('Done. Model outputs:',a.output,'Prediction outputs:',a.predictions_output)

if __name__=='__main__':main()
