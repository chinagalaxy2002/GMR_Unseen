"""Evaluate the stopped sit best checkpoint in a separate diagnostic bundle."""
import json
import shutil
from phase2 import STAGE, dump, rows, sha


def main():
    import torch
    import queue_worker as w
    torch.set_num_threads(4)
    torch.manual_seed(3407)
    source=STAGE/'runs/sit_qd_gmr_baseline_s3407_attempt1'
    bundle=STAGE/'diagnostics/sit/baseline/evaluation_bundle'
    assert not bundle.exists(), 'Inspect incomplete existing evaluation; no automatic retry'
    bundle.mkdir(parents=True)
    for name in ('best.ckpt','latest.ckpt','views'):
        (bundle/name).symlink_to((source/name).resolve(),target_is_directory=name=='views')
    shutil.copyfile(source/'best_seen_predictions.jsonl',bundle/'best_seen_predictions.jsonl')
    ck=torch.load(source/'best.ckpt',map_location='cpu',weights_only=False)
    selection=json.loads((source/'selection.json').read_text())
    assert ck['epoch']==selection['epoch']==11
    seen=w.existence_summary(rows(source/'views/val_seen.jsonl'),rows(bundle/'best_seen_predictions.jsonl'))
    # Freeze the same seen-only Youden rule before any pseudo prediction is made.
    dump(bundle/'threshold_frozen.json',{'threshold':seen['threshold'],'source':'seen validation only; Youden J',
         'before_pseudo_evaluation':True,'checkpoint_sha256':sha(source/'best.ckpt'),
         'seen_prediction_sha256':sha(bundle/'best_seen_predictions.jsonl')})
    opt=ck['opt'];opt.device='cuda:0';opt.num_workers=0;opt.results_dir=str(bundle)
    ev,dsmod=w.modules('qd');model,criterion,*_=w.make_model(opt,ev,'baseline','qd')
    model.load_state_dict(ck['model']);model.eval()
    with torch.no_grad():
        official=w.official_eval(model,criterion,opt,ev,dsmod,source/'views/pseudo.jsonl','pseudo_predictions.jsonl','qd')
    pseudo=w.existence_summary(rows(source/'views/pseudo.jsonl'),rows(bundle/'pseudo_predictions.jsonl'),seen['threshold'])
    dump(bundle/'evaluation_result.json',{'state':'completed','training_updates':0,'new_training_epochs':0,
         'source_training_state':'stopped_by_user','source_training_epochs_logged':77,
         'checkpoint_epoch_zero_based':ck['epoch'],'checkpoint_sha256':sha(source/'best.ckpt'),
         'source_sha256':sha(__file__),'seen_selection':selection,'seen':seen,'pseudo':pseudo,'pseudo_official':official,
         'limitation':'Post-stop evaluation of saved seen-selected best; not completion of 100-epoch training; original run and checkpoints unchanged.'})
    print(json.dumps({'state':'completed','bundle':str(bundle),'pseudo':pseudo}))


if __name__=='__main__':main()
