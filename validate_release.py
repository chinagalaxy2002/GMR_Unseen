"""Verify every published row, protection gate, rebuilt config and data asset."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from dec import SPLITS,BACKBONES,score
from seen_guard import score_seen_guard

def main():
    root=Path(__file__).resolve().parent;p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reproduced',type=Path,default=root/'reproduced_seen_guard');p.add_argument('--rebuilt',type=Path,default=root/'calibration/rebuilt_seen_guard.json');p.add_argument('--output',type=Path,default=root/'results/publication_verification.json');a=p.parse_args()
    expected={(r['split'],r['backbone'],r['method']):r for r in json.loads((root/'results/metrics.json').read_text())}
    actual={(r['split'],r['backbone'],r['method']):r for r in json.loads((a.reproduced/'metrics.json').read_text())}
    assert len(expected)==len(actual)==54 and set(expected)==set(actual)
    maximum=0.
    for key,r in actual.items():
        for name,value in r.items():
            if name in ('split','backbone','method'):continue
            if value is None:assert expected[key][name] is None
            else:maximum=max(maximum,abs(value-expected[key][name]));assert abs(value-expected[key][name])<1e-12,(key,name)
    config=json.loads((root/'calibration/seen_guard.json').read_text());rebuilt=json.loads(a.rebuilt.read_text());assert config['inventories']==rebuilt['inventories'];cal_error=0.
    assert len(config['settings'])==len(rebuilt['settings'])==15
    for x in config['settings']:
        y=next(y for y in rebuilt['settings'] if (y['split'],y['backbone'])==(x['split'],x['backbone']));assert x['mode']==y['mode'] and x['config']==y['config']
        for k,v in x['calibration'].items():
            if v is None:assert y['calibration'][k] is None
            else:cal_error=max(cal_error,abs(v-y['calibration'][k]));assert abs(v-y['calibration'][k])<1e-12,(x['split'],x['backbone'],k)
    gates=[];keys=json.loads((root/'calibration/query_keys.json').read_text());decisions=[]
    for sp in SPLITS:
        train,test=[dict(np.load(root/'data'/sp/(part+'.npz'),allow_pickle=False)) for part in ('train','test')];assert keys[sp]['test']['qids']==test['qids'].tolist()
        for bb in BACKBONES:
            b,d,n=[actual[sp,bb,m] for m in ('baseline','dec','seen_guard')]
            delta=dict(seen_vs_baseline_pp=100*(n['seen_auc']-b['seen_auc']),unseen_vs_dec_pp=100*(n['unseen_auc']-d['unseen_auc']),gmiou_vs_dec_pp=n['gmiou1']-d['gmiou1'],f1_vs_dec_pp=n['rej_f1']-d['rej_f1'],s_frr_improvement_pp=d['s_frr']-n['s_frr'],u_frr_improvement_pp=d['u_frr']-n['u_frr']);assert min(delta.values())>=-1e-9,(sp,bb,delta)
            gates.append(dict(split=sp,backbone=bb,all_six_pass=True,deltas=delta))
            setting=next(r for r in config['settings'] if r['split']==sp and r['backbone']==bb)
            # No target annotations or identifiers are available to the scorer.
            sc=score_seen_guard(train,{'X':test['X'],'queries':test['queries']},setting,keys[sp]['test']['keys'],config['inventories'][sp]);original=score(train,test,bb);unseen=np.char.startswith(test['partitions'],'U');old=original>=setting['calibration']['dec_threshold'];np.testing.assert_array_equal((sc>=0.)[unseen],old[unseen])
            if setting['mode']=='preserve_dec_decisions':np.testing.assert_array_equal(sc>=0.,old)
            decisions.append(dict(split=sp,backbone=bb,unseen_decisions_identical=True,mode=setting['mode'],annotations_not_required=True))
    assets=json.loads((root/'data/ASSET_MANIFEST.json').read_text())
    for asset in assets:assert hashlib.sha256((root/asset['path']).read_bytes()).hexdigest()==asset['sha256'],asset['path']
    frozen=json.loads((root/'calibration/ASSET_MANIFEST.json').read_text())
    for asset in frozen:assert hashlib.sha256((root/asset['path']).read_bytes()).hexdigest()==asset['sha256'],asset['path']
    bootstrap_path=a.reproduced/'bootstrap.json';same_ci=None;draws=None
    if bootstrap_path.exists():
        bc=json.loads(bootstrap_path.read_text());same_ci=bc==json.loads((root/'results/bootstrap.json').read_text());assert same_ci;draws=bc['valid_draws'];assert draws==2000
    report=dict(rows=54,settings=15,strict_six_gate_passes=15,max_point_error=maximum,max_calibration_error=cal_error,rebuilt_inventory_identical=True,data_assets_verified=len(assets),frozen_assets_verified=len(frozen),bootstrap_intervals_identical=same_ci,valid_bootstrap_draws=draws,gates=gates,decision_audit=decisions,threshold_protocol_changed=True,independent_test_confirmation=False)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS: 54 rows, 15 six-gate checks, rebuilt configuration, assets and decision isolation. Max errors:',maximum,cal_error)

if __name__=='__main__':main()
