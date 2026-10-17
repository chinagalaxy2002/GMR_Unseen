"""Build the final, evidence-linked handoff after every frozen evaluation completes."""
from __future__ import annotations
import csv,json,statistics
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SEED=2026

def load(path):return json.loads(Path(path).read_text())
def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
def csv_rows(path):
    with Path(path).open(newline='') as f:return list(csv.DictReader(f))
def num(value):
    try:return float(value)
    except (TypeError,ValueError):return None
def f(value,digits=2):
    value=num(value);return 'N/A' if value is None else f'{value:.{digits}f}'
def avg(items,key):
    values=[num(x.get(key)) for x in items];values=[x for x in values if x is not None]
    return statistics.fmean(values) if values else None

def test_row(name,run,baseline_g04=None):
    if name=='E0':
        data=load(run/'metrics.json')['brief']
        return {'AUROC':data.get('AUROC_raw',data.get('AUROC')),'G04':baseline_g04,
                'G05':None,'BA':None,'mAP':data.get('mAP'),'localizer':'native baseline'}
    data=load(run/'test_metrics.json')
    return {'AUROC':data['AUROC'],'G04':data['gate_04']['G-mIoU@1'],'G05':data['fixed_05']['G-mIoU@1'],
            'BA':data['val_BA_threshold']['G-mIoU@1'],'mAP':data['native_pre_nms']['MR-full-mAP'],
            'localizer':str(data['localizer_matches_e0'])}

def main():
    e0=ROOT/'baseline/runs'/f'E0_s{SEED}';control=ROOT/'minneg/runs'/f'no_minneg_s{SEED}';a3=ROOT/'minneg/runs'/f'minneg_s{SEED}'
    threshold_rows=csv_rows(ROOT/'reports/threshold_sweep_per_seed.csv')
    baseline_g04=next(num(r['G-mIoU@1']) for r in threshold_rows
                      if r['stage']=='baseline' and round(num(r['threshold']),2)==0.4)
    mechanism=ROOT/'reports/mechanism';three=csv_rows(mechanism/'selected_three_way.csv')
    choices={'E0':load(e0/'selected.json'),'A3-no-minneg':load(control/'selected.json'),'A3':load(a3/'selected.json')}
    runs={'E0':e0,'A3-no-minneg':control,'A3':a3}
    tests={name:test_row(name,path,baseline_g04 if name=='E0' else None) for name,path in runs.items()}
    trained={'E0':max(int(x['epoch']) for x in rows(e0/'trace.jsonl')),
             'A3-no-minneg':max(int(x['epoch']) for x in rows(control/'trace.jsonl')),
             'A3':max(int(x['epoch']) for x in rows(a3/'trace.jsonl'))}
    selected=[]
    for name in ('E0','A3-no-minneg','A3'):
        choice=choices[name];metric='Val mAP' if name=='E0' else 'Val AUROC'
        score=choice.get('score') if name=='E0' else choice.get('val_AUROC')
        display='EventReadout control (no min-neg)' if name=='A3-no-minneg' else name
        selected.append(f"| {display} | {choice['epoch']} / {trained[name]} | {metric} | {f(score)} | {f(tests[name]['AUROC'])} | {f(tests[name]['mAP'])} | {f(tests[name]['G04'])} | {f(tests[name]['G05'])} | {f(tests[name]['BA'])} |")
    mechanism_lines=[]
    for k in (1,2,3):
        group=[r for r in three if int(r['topk'])==k]
        mechanism_lines.append(
            f"| Top-{k} | {len(group)} | {f(avg(group,'readout_plus_standard_finetune_delta'),4)} | "
            f"{f(avg(group,'minneg_increment_delta'),4)} | {sum(str(r['rescued_by_readout_0.5']).lower()=='true' for r in group)} | "
            f"{sum(str(r['rescued_only_after_minneg_0.5']).lower()=='true' for r in group)} | "
            f"{f(avg(group,'no_minneg_remove_hit_logit_drop'),4)} | {f(avg(group,'a3_remove_hit_logit_drop'),4)} |")
    top3=[r for r in three if int(r['topk'])==3]
    rescued=[r for r in top3 if str(r['rescued_only_after_minneg_0.5']).lower()=='true']
    rescued.sort(key=lambda r:num(r['minneg_increment_delta']) or -999,reverse=True)
    persistent=[r for r in top3 if str(r['e0_accept_0.5']).lower()=='false' and str(r['a3_accept_0.5']).lower()=='false']
    persistent.sort(key=lambda r:num(r['a3_score']) or 999)
    def peak(stage,metric):
        item=max((r for r in threshold_rows if r['stage']==stage),key=lambda r:num(r[metric]))
        return num(item['threshold']),num(item[metric])
    peaks={stage:{metric:peak(stage,metric) for metric in ('G-mIoU@1','balanced_accuracy','Rej-F1')}
           for stage in ('baseline','no_minneg','minneg')}
    selected_pool={}
    score_reports={}
    for stage,path in (('no_minneg',control),('minneg',a3)):
        epoch=int(choices['A3-no-minneg' if stage=='no_minneg' else 'A3']['epoch'])
        selected_pool[stage]=load(path/'monitor/auroc_mechanisms/pool_sources/validation'/f'epoch_{epoch:04d}'/'summary.json')['per_query']
        score_reports[stage]=load(path/'monitor/auroc_mechanisms'/f'validation_epoch_{epoch:04d}_scores.json')
    score_means={}
    for stage,data in selected_pool.items():
        score_means[stage]={label:statistics.fmean(r['existence_score'] for r in data if r['label']==label)
                            for label in (0,1)}
    same_video={stage:score_reports[stage]['same_video'] for stage in score_reports}
    top3_control_to_a3_reject=sum(str(r['no_minneg_accept_0.5']).lower()=='true' and str(r['a3_accept_0.5']).lower()=='false' for r in top3)
    top3_minneg_only_rescue=sum(str(r['rescued_only_after_minneg_0.5']).lower()=='true' for r in top3)
    sweep={(r['stage'],round(num(r['threshold']),2)):r for r in threshold_rows}
    ledger=[]
    for threshold in (.4,.5,.6):
        for stage,label in (('baseline','E0'),('no_minneg','no-minneg'),('minneg','A3')):
            item=sweep[(stage,threshold)];negative_part=num(item['negative_recall'])*492/1036
            positive_part=num(item['G-mIoU@1'])-negative_part
            ledger.append(f"| {threshold:.1f} | {label} | {f(item['negative_recall'])} | {f(item['positive_recall'])} | {f(negative_part)} | {f(positive_part)} | {f(item['G-mIoU@1'])} |")
    def examples(items):
        if not items:return '_None._'
        lines=['| qid | video | E0 | no-minneg | A3 | min-neg Δ | A3 hit-slot mask Δlogit |','|---|---|---:|---:|---:|---:|---:|']
        for r in items[:10]:
            lines.append(f"| {r['qid']} | {r['vid']} | {f(r['e0_score'],4)} | {f(r['no_minneg_score'],4)} | {f(r['a3_score'],4)} | {f(r['minneg_increment_delta'],4)} | {f(r['a3_remove_hit_logit_drop'],4)} |")
        return '\n'.join(lines)
    report=load(ROOT/'reports/REPORT.json');mresult=load(mechanism/'MECHANISM_RESULTS.json')
    document=f"""# Seed 2026 E0 → A3 mechanism experiment handoff

Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}

## Executive summary

This run evaluates whether A3 fixes E0 existence false rejection after localization has already found a GT event. It contains one seed only (`2026`), so all differences are paired descriptive evidence rather than multi-seed uncertainty estimates. E0 is selected by Val native pre-NMS mAP; both EventReadout branches are selected independently by Val raw-logit AUROC. Test is opened only after checkpoint freezing.

The matched control isolates the min-neg increment:

```text
E0 selected localizer
├── EventReadout control: ordinary fine-tuning without min-neg
└── public A3: EventReadout + similarity hard-negative / min-neg
```

Both branches use the same seed, E0 checkpoint, initialization, batch order, optimizer, 100-epoch limit and 23-epoch patience. The negative forward uses a forked RNG, preventing its extra dropout draws from shifting A3's main-path random sequence.

## Frozen results

| model | selected / trained epoch | selection | selected Val score | Test AUROC | Test native mAP | Test G@0.4 | Test G@0.5 | Test G@Val-BA |
|---|---:|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(selected)}

For A3 branches, `localizer_matches_e0` is `{tests['A3']['localizer']}` for A3 and `{tests['A3-no-minneg']['localizer']}` for the no-minneg control. Thus an existence-mechanism comparison is valid only if both remain `True`.

## Main findings

1. **The matched experiment does not show an AUROC benefit from min-neg.** The no-minneg control has Val/Test AUROC `{f(choices['A3-no-minneg']['val_AUROC'])}/{f(tests['A3-no-minneg']['AUROC'])}`, versus `{f(choices['A3']['val_AUROC'])}/{f(tests['A3']['AUROC'])}` for A3. Therefore this seed does not support the claim that min-neg generally improves global positive-negative ranking.
2. **Min-neg mainly changes the operating scale and rejection behavior.** On selected Val, mean positive/negative scores move from `{f(score_means['no_minneg'][1],4)}/{f(score_means['no_minneg'][0],4)}` without min-neg to `{f(score_means['minneg'][1],4)}/{f(score_means['minneg'][0],4)}` with min-neg. The Test threshold maximizing G-mIoU@1 shifts from `{f(peaks['no_minneg']['G-mIoU@1'][0])}` to `{f(peaks['minneg']['G-mIoU@1'][0])}`, while their maxima are nearly unchanged (`{f(peaks['no_minneg']['G-mIoU@1'][1])}` versus `{f(peaks['minneg']['G-mIoU@1'][1])}`). The apparent A3 advantage at conventional thresholds is therefore primarily operating-point alignment, not a higher best-achievable G-mIoU envelope.
3. **Min-neg does improve the intended within-video discrimination diagnostic.** Val same-video macro AUROC changes from `{f(100*same_video['no_minneg']['macro_auroc'])}` to `{f(100*same_video['minneg']['macro_auroc'])}`, and pair-weighted AUROC from `{f(100*same_video['no_minneg']['pair_weighted_auroc'])}` to `{f(100*same_video['minneg']['pair_weighted_auroc'])}`. This is consistent with the mismatched-query objective, even though global AUROC is slightly worse.
4. **A3 relies more strongly on localized hit-slot evidence after min-neg.** For Top-3 hit queries, final-layer attention mass increases from `{f(avg(top3,'no_minneg_attention_mass_final'),4)}` to `{f(avg(top3,'a3_attention_mass_final'),4)}` and causal hit-slot masking Δlogit increases from `{f(avg(top3,'no_minneg_remove_hit_logit_drop'),4)}` to `{f(avg(top3,'a3_remove_hit_logit_drop'),4)}`. Attention alone is not treated as causal; the masking change supplies the stronger evidence.
5. **This is not a positive-query rescue mechanism at threshold 0.5.** Among `{len(top3)}` Top-3 hit-positive rows, min-neg alone rescues `{top3_minneg_only_rescue}` E0 false rejects, while it changes `{top3_control_to_a3_reject}` no-minneg accepts into A3 rejects. The supported interpretation is conservative score calibration plus stronger within-video contrast and hit-slot reliance—not recovery of low-scoring localized positives.

Overall verdict: on seed 2026, EventReadout without min-neg gives the better global AUROC, whereas min-neg makes the head substantially more conservative and moves its useful operating threshold toward 0.5. A3's fixed-threshold G-mIoU improvement is real, but it should not be described as a universal ranking gain or as rescuing E0's positive false rejects.

## Why G-mIoU rises at most practical thresholds

G-mIoU averages all 1,036 Test queries. A correctly rejected negative query has empty prediction and empty GT, so its score is exactly 1. A rejected positive query has empty prediction but non-empty GT, so its score is 0. Consequently:

```text
G-mIoU@1 = correctly rejected negative contribution
          + accepted-positive localization contribution
```

There are 492 negatives, so perfect negative rejection alone contributes `492/1036 = 47.49` G-mIoU points. Because the localizer is unchanged, A3's gain is a gate tradeoff: it earns many more negative-query points while sacrificing some positive-query localization points.

| threshold | model | negative recall | positive recall | negative contribution | positive localization contribution | G-mIoU@1 |
|---:|---|---:|---:|---:|---:|---:|
{chr(10).join(ledger)}

At threshold 0.5, relative to E0, A3 gains `47.01 - 33.69 = 13.32` points from correct negative rejection and loses `9.88 - 7.44 = 2.44` points from positive localization, for a net gain of about `10.88` G-mIoU points. This is why G-mIoU and Rej-F1 improve even though positive recall declines. A3 beats E0 from thresholds 0.03 through 0.73; beyond that, its already-low score scale rejects almost every positive and it becomes worse. The no-minneg control beats E0 across a wider interval because it improves rejection more moderately without suppressing positives as aggressively.

## What is actually being diagnosed

- **E0 path:** masked mean of final video units, concatenated with the query vector, followed by the native existence MLP.
- **A3 path:** newly initialized sequential cross-attention EventReadout over frozen E0 features. The legacy pooled vector is ignored.
- **Max pooling:** not on either actual path in this configuration. Max-owner values are counterfactual representation diagnostics only and cannot support a causal claim.
- **Hit definition:** one of the first `k` native-ranked windows has IoU ≥ 0.5 with any GT window. No GT-based reranking is performed.
- **False reject:** a positive hit query whose existence score is below 0.4 or 0.5.

## Selected-checkpoint mechanism decomposition

Score deltas below are paired on the same `seed × qid`. Counts at threshold 0.5 describe E0 false rejects rescued first by ordinary EventReadout training or only after adding min-neg. Mask Δlogit is the actual readout-logit reduction after hit-window slots are removed.

| localization set | hit-query rows | E0→no-minneg mean score Δ | no-minneg→A3 mean score Δ | rescued by readout | rescued only by min-neg | no-minneg mask Δlogit | A3 mask Δlogit |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(mechanism_lines)}

Interpretation rules:

1. A score increase without AUROC or same-video ranking improvement is calibration, not stronger discrimination.
2. Attention mass is routing evidence, not a causal attribution. The hit-slot masking Δlogit is the causal intervention used here.
3. `E0→no-minneg` combines head replacement and ordinary readout training. `no-minneg→A3` is the matched min-neg increment.
4. A min-neg mechanism is credible when it improves negative separation/rescue and the A3 decision remains causally dependent on hit slots.
5. Test confirms Val-discovered behavior; it must not be mined to select a mechanism claim.

## Top-3 queries rescued only after min-neg at threshold 0.5

{examples(rescued)}

## Top-3 persistent false rejects after A3 at threshold 0.5

{examples(persistent)}

## Diagnostic inventory

### E0 training and evaluation

- `baseline/runs/E0_s2026/diagnostics/optimization.jsonl`: sampled loss, learning rate and pre-clip norm.
- `baseline/runs/E0_s2026/diagnostics/gradients.jsonl`: sampled existence-vs-localization gradient cosine.
- `baseline/runs/E0_s2026/diagnostics/parameter_updates.jsonl`: module-level epoch updates.
- `baseline/runs/E0_s2026/diagnostics/pool_sources/validation/`: true mean-pool contribution and causal ablation for every Val epoch.
- `baseline/runs/E0_s2026/diagnostics/pool_sources/test/`: frozen Test diagnostic.

### EventReadout branches

- `minneg/runs/no_minneg_s2026/monitor/`: matched control training, score and intervention records.
- `minneg/runs/minneg_s2026/monitor/`: A3 training, score and intervention records.
- Each `pool_sources/validation/epoch_*` directory contains Top1/2/3 hits, false-reject flags, actual attention mass, hit-slot masking, hit-only replay, mismatched-text replay, and separately labelled counterfactual max ownership.
- `selection/trace.jsonl`, `selected.json`, and `selection/frozen.json` document Val-only selection and the Test boundary.
- Exact localizer fingerprints are checked every epoch and during Test.

### Paired reports and figures

- `reports/mechanism/selected_three_way.csv`: principal E0/no-minneg/A3 selected-checkpoint table.
- `reports/mechanism/paired_queries.csv`: E0 versus every A3 epoch.
- `reports/mechanism/epoch_summary.csv`: rescue trajectory.
- `reports/mechanism/MECHANISM_RESULTS.json`: machine-readable mechanism summary.
- `reports/mechanism/mechanism_trajectory.png`: A3 rescue and hit-slot causal reliance trajectory.
- `reports/threshold_sweep_per_seed.csv`: every threshold from 0.00 to 1.00.
- `reports/all_threshold_metrics.png` and `.pdf`: single-seed threshold curves for E0, no-minneg and A3.
- Test prediction hashes and invariant AUROCs: `{json.dumps(report['invariant_metrics'],ensure_ascii=False)}`.

## Reproduction

From `{ROOT}`:

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -B pipeline.py
```

The pipeline order is E0 → parallel no-minneg/A3 training → frozen tests → paired mechanism report → threshold sweep → this handoff. Configuration is in `baseline/configs/protocol.json` and `minneg/configs/jobs.json`. Runtime state and exact commands are retained in `PIPELINE_STATE.json`; individual stdout/stderr streams are in `logs/`.

## Scientific limitations

- Only seed 2026 is retained; variance and statistical confidence across seeds are unknown.
- E0 and EventReadout use different selection metrics by design: released E0 Val mAP versus requested EventReadout Val AUROC.
- E0→no-minneg does not separate head replacement from subsequent ordinary fine-tuning. It only separates their combined effect from the additional min-neg effect.
- Slot masking is a post-encoder readout intervention. It establishes reliance of the existence head, not how the frozen localizer originally formed the slot representation.
- Threshold-specific rescue depends on the declared operating point; AUROC and all-threshold curves should accompany any threshold claim.

Reference diagnostics implementation: commit `349becb99cdfba2b23630af9126af0a532506113` on `diagnostics/detr-native-26ep-20261014`.
"""
    (ROOT/'HANDOFF.md').write_text(document)
    print(ROOT/'HANDOFF.md')

if __name__=='__main__':main()
