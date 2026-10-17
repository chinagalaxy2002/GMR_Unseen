"""Paired E0 -> A3 mechanism analysis; diagnostics are never used for selection."""
from __future__ import annotations
import csv,json,math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'reports'/'mechanism'

def load(path):return json.loads(Path(path).read_text())
def mean(values):
    x=[float(v) for v in values if v is not None and math.isfinite(float(v))]
    return float(np.mean(x)) if x else None

def main():
    OUT.mkdir(parents=True,exist_ok=True);paired=[];summary=[];three_way=[]
    for seed in (2026,):
        e0=ROOT/'baseline'/'runs'/f'E0_s{seed}';a3=ROOT/'minneg'/'runs'/f'minneg_s{seed}'
        selected=load(e0/'selected.json')['epoch']
        e0_rows=load(e0/'diagnostics'/'pool_sources'/'validation'/f'epoch_{selected:04d}'/'SUMMARY.json')['per_query']
        e0_by={str(r['qid']):r for r in e0_rows}
        for folder in sorted((a3/'monitor'/'auroc_mechanisms'/'pool_sources'/'validation').glob('epoch_*')):
            epoch=int(folder.name.split('_')[-1]);a3_rows=load(folder/'summary.json')['per_query']
            for ar in a3_rows:
                er=e0_by[str(ar['qid'])]
                for k in (1,2,3):
                    if not er[f'top{k}_gt_hit']:continue
                    row={'seed':seed,'a3_epoch':epoch,'baseline_selected_epoch':selected,'qid':str(ar['qid']),
                         'vid':ar['vid'],'topk':k,'e0_score':er['existence_score'],'a3_score':ar['existence_score'],
                         'score_delta':ar['existence_score']-er['existence_score'],
                         'e0_actual_mean_abs_contribution_fraction':er[f'top{k}_actual_mean_abs_contribution_fraction'],
                         'e0_actual_mean_dominant_dimension_fraction':er[f'top{k}_actual_mean_dominant_dimension_fraction'],
                         'e0_actual_mean_ablation_logit_drop':er[f'top{k}_actual_mean_ablation_logit_drop'],
                         'a3_actual_attention_mass_final':ar[f'top{k}_gt_hit_attention_mass_final'],
                         'a3_actual_remove_hit_logit_drop':ar.get(f'top{k}_actual_remove_hit_logit_drop'),
                         'a3_actual_only_hit_logit':ar.get(f'top{k}_actual_only_hit_logit'),
                         'a3_mismatched_text_logit_drop':ar.get('actual_mismatched_text_logit_drop'),
                         'e0_counterfactual_max_owner_fraction':er[f'top{k}_counterfactual_max_owner_fraction'],
                         'a3_counterfactual_max_owner_fraction':ar[f'top{k}_gt_hit_pool_fraction']}
                    for threshold in (.4,.5):
                        before=er['existence_score']<threshold;after=ar['existence_score']<threshold
                        row[f'e0_false_reject_{threshold}']=before;row[f'a3_false_reject_{threshold}']=after
                        row[f'rescued_{threshold}']=before and not after
                        row[f'regressed_{threshold}']=not before and after
                        row[f'quadrant_{threshold}']=('rescued' if before and not after else 'persistent_reject' if before else 'regressed' if after else 'persistent_accept')
                    paired.append(row)
            current=[r for r in paired if r['seed']==seed and r['a3_epoch']==epoch]
            for k in (1,2,3):
                group=[r for r in current if r['topk']==k]
                for threshold in (.4,.5):
                    rejected=[r for r in group if r[f'e0_false_reject_{threshold}']]
                    rescued=[r for r in rejected if r[f'rescued_{threshold}']]
                    summary.append({'seed':seed,'a3_epoch':epoch,'topk':k,'threshold':threshold,
                        'hit_queries':len(group),'e0_false_rejects':len(rejected),'rescued':len(rescued),
                        'rescue_rate':len(rescued)/len(rejected) if rejected else None,
                        'mean_score_delta':mean([r['score_delta'] for r in group]),
                        'rescued_a3_attention_mass':mean([r['a3_actual_attention_mass_final'] for r in rescued]),
                        'persistent_a3_attention_mass':mean([r['a3_actual_attention_mass_final'] for r in rejected if not r[f'rescued_{threshold}']]),
                        'rescued_a3_remove_hit_logit_drop':mean([r['a3_actual_remove_hit_logit_drop'] for r in rescued]),
                        'persistent_a3_remove_hit_logit_drop':mean([r['a3_actual_remove_hit_logit_drop'] for r in rejected if not r[f'rescued_{threshold}']])})
        control=ROOT/'minneg'/'runs'/f'no_minneg_s{seed}'
        control_epoch=int(load(control/'selected.json')['epoch']);a3_epoch=int(load(a3/'selected.json')['epoch'])
        control_rows=load(control/'monitor'/'auroc_mechanisms'/'pool_sources'/'validation'/f'epoch_{control_epoch:04d}'/'summary.json')['per_query']
        a3_selected_rows=load(a3/'monitor'/'auroc_mechanisms'/'pool_sources'/'validation'/f'epoch_{a3_epoch:04d}'/'summary.json')['per_query']
        control_by={str(r['qid']):r for r in control_rows};a3_by={str(r['qid']):r for r in a3_selected_rows}
        for qid,er in e0_by.items():
            cr,ar=control_by[qid],a3_by[qid]
            for k in (1,2,3):
                if not er[f'top{k}_gt_hit']:continue
                row={'seed':seed,'qid':qid,'vid':er['vid'],'topk':k,
                    'e0_selected_epoch':selected,'no_minneg_selected_epoch':control_epoch,'a3_selected_epoch':a3_epoch,
                    'e0_score':er['existence_score'],'no_minneg_score':cr['existence_score'],'a3_score':ar['existence_score'],
                    'readout_plus_standard_finetune_delta':cr['existence_score']-er['existence_score'],
                    'minneg_increment_delta':ar['existence_score']-cr['existence_score'],
                    'total_a3_delta':ar['existence_score']-er['existence_score'],
                    'no_minneg_attention_mass_final':cr[f'top{k}_gt_hit_attention_mass_final'],
                    'a3_attention_mass_final':ar[f'top{k}_gt_hit_attention_mass_final'],
                    'no_minneg_remove_hit_logit_drop':cr.get(f'top{k}_actual_remove_hit_logit_drop'),
                    'a3_remove_hit_logit_drop':ar.get(f'top{k}_actual_remove_hit_logit_drop')}
                for threshold in (.4,.5):
                    e=er['existence_score']>=threshold;c=cr['existence_score']>=threshold;a=ar['existence_score']>=threshold
                    row[f'e0_accept_{threshold}']=e;row[f'no_minneg_accept_{threshold}']=c;row[f'a3_accept_{threshold}']=a
                    row[f'rescued_by_readout_{threshold}']=(not e and c)
                    row[f'rescued_only_after_minneg_{threshold}']=(not e and not c and a)
                three_way.append(row)
    for name,data in [('paired_queries.csv',paired),('epoch_summary.csv',summary),('selected_three_way.csv',three_way)]:
        with (OUT/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]) if data else []);writer.writeheader();writer.writerows(data)
    (OUT/'MECHANISM_RESULTS.json').write_text(json.dumps({'protocol':{
        'comparison':'same seed and qid; E0 selected-by-Val-mAP checkpoint versus every A3 Val epoch',
        'selection_use':'none','actual_E0':'masked mean pool -> MLP','actual_A3':'sequential cross-attention EventReadout',
        'max_pool':'counterfactual representation diagnostic only','test_role':'post-freeze confirmation only'},
        'selected_three_way_summary':{
            'n_rows':len(three_way),
            'mean_readout_plus_standard_finetune_delta':mean([r['readout_plus_standard_finetune_delta'] for r in three_way]),
            'mean_minneg_increment_delta':mean([r['minneg_increment_delta'] for r in three_way]),
            'rescued_by_readout_at_0.5':sum(r['rescued_by_readout_0.5'] for r in three_way),
            'rescued_only_after_minneg_at_0.5':sum(r['rescued_only_after_minneg_0.5'] for r in three_way)},
        'epoch_summary':summary},indent=2)+'\n')
    try:
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(11,4.2))
        for seed in (2026,):
            x=[r for r in summary if r['seed']==seed and r['topk']==3 and r['threshold']==.5]
            axes[0].plot([r['a3_epoch'] for r in x],[np.nan if r['rescue_rate'] is None else r['rescue_rate'] for r in x],marker='o',label=str(seed))
            axes[1].plot([r['a3_epoch'] for r in x],[np.nan if r['rescued_a3_remove_hit_logit_drop'] is None else r['rescued_a3_remove_hit_logit_drop'] for r in x],marker='o',label=str(seed))
        axes[0].set(title='E0 false rejects rescued by A3',xlabel='A3 epoch',ylabel='Rescue rate @ 0.5',ylim=(0,1));axes[0].legend(title='seed')
        axes[1].set(title='Causal reliance on hit slots (rescued)',xlabel='A3 epoch',ylabel='Logit drop after masking Top-3 hit slots')
        for ax in axes:ax.grid(alpha=.25)
        fig.tight_layout();fig.savefig(OUT/'mechanism_trajectory.png',dpi=200);plt.close(fig)
    except Exception as exc:
        (OUT/'PLOT_ERROR.txt').write_text(repr(exc)+'\n')

if __name__=='__main__':main()
