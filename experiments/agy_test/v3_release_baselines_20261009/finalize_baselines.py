"""Finalize high-precision Flash readout after the training queue exits."""
import datetime
import json
import time
from run_baselines import ROOT, GROUPS, BACKBONES, evaluate, report, save_json

while not (ROOT/'PIPELINE_EXIT.json').exists():
    time.sleep(20)
state=json.loads((ROOT/'PIPELINE_EXIT.json').read_text())
for group in GROUPS:
    task=ROOT/'groups'/group
    for bb in BACKBONES:
        pred=task/'runs'/bb/'test'/('hl_test_submission.jsonl' if bb=='flash' else bb+'_detr_gmr_test_submission.jsonl')
        val=task/'frozen_checkpoints'/bb/('best_charadesSTA_val_preds.jsonl' if bb=='flash' else 'best_charades_semantic_existence_val_preds.jsonl')
        if pred.exists() and val.exists():
            evaluate(group,bb,val,pred)
report()
save_json(ROOT/'FINAL_EVALUATION_STATUS.json',dict(training_state=state,score_readout='Moment/QD native 4-decimal sigmoid; Flash native 6-decimal logit',finalized_at=datetime.datetime.now().isoformat(),complete=state['complete']==15 and state['failed']==0))

import subprocess, sys
subprocess.run([sys.executable, str(ROOT.parents[2]/'scripts/summarize_gmr_degradation.py'), '--experiment', str(ROOT)], check=True)
