"""Export English DETR text diagnostics and aggregates to a dedicated artifact branch."""
import argparse
import collections
import hashlib
import json
import math
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
REL=Path('experiments/agy_test/publication_degradation_diagnostics_20261013')
CJK=re.compile('[\u4e00-\u9fff]')
CREDENTIAL=re.compile(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(8*1024*1024),b''):h.update(data)
    return h.hexdigest()


def clean(text):
    # Paths refer to the local capture machine, not executable publication defaults.
    text=text.replace(str(REPO)+'/','<LOCAL_REPOSITORY>/')
    text=re.sub(r'/home/guoxiangyu/paper/[^\s\"\']*?[\u4e00-\u9fff][^\s\"\']*', '<LOCAL_VIDEO_FEATURE_ROOT>', text)
    text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',text).replace('\r','\n')
    return text


def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


class Export:
    def __init__(self,dest):
        self.dest=dest;self.entries=[];self.derived=[]
    def copy(self,source,relative):
        dest=self.dest/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        text=clean(source.read_text())
        if CJK.search(text):raise RuntimeError('Non-English CJK content: '+str(source))
        if CREDENTIAL.search(text):raise RuntimeError('Potential credential: '+str(source))
        dest.write_text(text)
        self.entries.append(dict(path=str(relative),source=str(source.relative_to(REPO)),source_sha256=sha(source),sha256=sha(dest),bytes=dest.stat().st_size,
            normalization='local absolute paths replaced; ANSI control sequences removed; CR progress rewritten as lines'))
    def generated(self,path,data):
        dest=self.dest/path;dump(dest,data)
        self.derived.append(dict(path=str(path),sha256=sha(dest),bytes=dest.stat().st_size))


class Aggregate:
    def __init__(self):self.n=0;self.values={};self.enums={}
    def add(self,row,skip):
        self.n+=1
        for k,v in row.items():
            if k in skip or v is None:continue
            if isinstance(v,(bool,int,float)) and math.isfinite(float(v)):
                s=self.values.setdefault(k,[0,0.,None,None]);s[0]+=1;s[1]+=float(v);s[2]=float(v) if s[2] is None else min(s[2],float(v));s[3]=float(v) if s[3] is None else max(s[3],float(v))
            elif isinstance(v,list) and v and all(isinstance(x,(int,float)) and math.isfinite(float(x)) for x in v):
                key=k+'_mean_over_slots';self.add_scalar(key,sum(v)/len(v))
                if k=='pool_owner_counts':
                    total=sum(v);p=[x/total for x in v if x>0] if total else []
                    if p:
                        self.add_scalar('pool_max_owner_fraction',max(p));self.add_scalar('pool_effective_owner_slots',math.exp(-sum(x*math.log(x) for x in p)))
                    for index,value in enumerate(v):self.add_scalar('pool_owner_count_slot_'+str(index),value)
                if k.startswith('leave_one_unit_out_'):
                    self.add_scalar(k+'_max',max(v));self.add_scalar(k+'_min',min(v))
            elif isinstance(v,str) and k.endswith('_status'):
                self.enums.setdefault(k,collections.Counter())[v]+=1
    def add_scalar(self,k,v):
        s=self.values.setdefault(k,[0,0.,None,None]);s[0]+=1;s[1]+=float(v);s[2]=float(v) if s[2] is None else min(s[2],float(v));s[3]=float(v) if s[3] is None else max(s[3],float(v))
    def finish(self):return dict(n=self.n,statistics={k:dict(n=v[0],mean=v[1]/v[0],min=v[2],max=v[3]) for k,v in self.values.items()},status_counts={k:dict(v) for k,v in self.enums.items()})


def aggregate_queries(source,dest):
    groups={}
    with source.open() as stream:
        for line in stream:
            if not line.strip():continue
            row=json.loads(line);key=(row['epoch'],row['partition'])
            groups.setdefault(key,Aggregate()).add(row,{'epoch','step','batch','qid','vid','partition','pool_source_record','difficulty','foreground_scores','matched_foreground','unmatched_foreground'})
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w') as stream:
        for (epoch,partition),v in sorted(groups.items()):
            stream.write(json.dumps(dict(epoch=epoch,partition=partition,measurement_context='aggregate_of_native_observed_query_diagnostics',**v.finish()),allow_nan=False)+'\n')


def aggregate_decoder(source,dest):
    groups={}
    with source.open() as stream:
        for line in stream:
            if not line.strip():continue
            batch=json.loads(line)
            for row in batch['records']:
                key=(batch['epoch'],row['partition'],row['layer'])
                groups.setdefault(key,Aggregate()).add(row,{'qid','vid','partition','layer'})
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w') as stream:
        for (epoch,partition,layer),v in sorted(groups.items()):
            stream.write(json.dumps(dict(epoch=epoch,partition=partition,layer=layer,measurement_context='aggregate_of_native_returned_decoder_observations',**v.finish()),allow_nan=False)+'\n')


def make_readme(dest):
    root=str(REL);example=root+'/runs/clean_v3/A1_v3/moment/seed_3407'
    text=f'''# DETR Diagnostic Log Paths and Measurement Principles

`<ROOT>` denotes `{root}`. `<RUN>` denotes `<ROOT>/runs/<DATASET>/<SPLIT>/<BACKBONE>/seed_3407`. `<BACKBONE>` is `moment` (Moment-DETR-GMR) or `qd` (QD-DETR-GMR). `<DATASET>/<SPLIT>` is `charades_cg_v2/C3_CG` or `clean_v3/{{A1_v3,A2_v3,A3_v3,C1_v3,C2_v3}}`.

## Diagnostic log paths

| Diagnostic | Published paths under `<RUN>` | Measurement principle |
|---|---|---|
| Native training and protocol | `training/<BACKBONE>/console.log`, `train.log`, `val.log`, `opt.json`, `run_metadata.txt`; `CONFIG.json`, `PROVENANCE.json`, `STATUS.json` | Preserve native optimization and validation text. Record configuration, seed, feature order, source/data hashes and actual execution metadata. The explicit epoch cap is 26 completed epochs. |
| Checkpoint selection and calibration | `selection/trace.jsonl`, `selected.json`, `auroc_shadow.json`, `frozen.json`; `FROZEN_CALIBRATION.json` | Formal selection uses Seen-validation native MR-full-mAP, with QD's native non-numeric mAP fallback to mIoU. Strict improvement retains the earliest tie. AUROC is a diagnostic shadow. Calibration uses float32 native scores, 91 percentile candidates from 5 through 95, acceptance at score >= threshold and the first strict balanced-accuracy improvement. Freeze checkpoint/options/threshold hashes before test. |
| Existence scores and ranking | `monitor/auroc_mechanisms/{{probe,validation}}_epoch_*_scores.json`; `monitor/auroc_mechanisms/{{train,probe,validation}}_query_summary.jsonl`; `final/monitor/auroc_mechanisms/test_epoch_*_scores.json`, `test_query_summary.jsonl` | Keep raw logit, native sigmoid probability and four-decimal benchmark score distinct. Measure distributions, positive-negative pair errors and ties, same-video ranking, joint localization/existence outcomes and recorded strata. Query summaries aggregate observations by epoch and partition without publishing full per-query predictions. |
| Localization and responses | `monitor/train_responses.jsonl`, `epoch_responses.jsonl`, `probe_responses.jsonl`, `validation_responses.jsonl`; `final/test_responses.json` | A valid-span foreground probability >0.5 defines an active candidate. Top-1 IoU measures the leading candidate; oracle coverage checks whether any candidate overlaps GT at IoU >=0.5. Negative queries have no localization GT and retain N/A for GT-dependent measurements. These are distinct from end-to-end G-mIoU. |
| Actual matching and stability | `monitor/epochs.jsonl`, `fixed_probe.jsonl` | Capture the native criterion's first Hungarian call for final-decoder matches; exclude auxiliary calls from final-slot history. Track GT identity by query and normalized coordinates, exclude duplicate-coordinate GT from flips, and compare stochastic training assignment changes with a fixed evaluation-mode probe. |
| Decoder representations and attention | `monitor/decoder_slots/METADATA.json`, `train_slots_summary.jsonl`, `probe_slots_summary.jsonl` | Aggregate layer-wise cosine similarity, distances, effective centered rank, candidate overlap, foreground spread and native returned self/cross attention. Attention entropy normalizes rows; training dropout can change raw row sums. Published slot summaries aggregate scalar and per-slot summary measurements by epoch, partition and layer. |
| Loss and gradient interactions | `monitor/gradients.jsonl`, `representation_gradients.jsonl`; `monitor/auroc_mechanisms/shared_gradients.jsonl`, `objective_split.jsonl`, `existence_loss_contributions.jsonl`, `optimization.jsonl` | Reuse actual native final/aux matches for S+/S- loss attribution. Extra autograd reads task gradients with graph retention and without changing parameter `.grad`. Parameter-space localization/foreground versus existence gradients and shared-representation task gradients have separate definitions. Record pre-clipping global norms, clipping coefficients, weighted losses and numerical learning rates. |
| Pooling and existence head | `monitor/auroc_mechanisms/{{train,probe,validation}}_query_summary.jsonl`; `final/pooling_summary.json`; `<ROOT>/design/POOL_SOURCE_SCHEMA.json`; `<ROOT>/analysis/detr_20261014/DETR_ANALYSIS.json` | Observe the actual final-decoder feature tensor before native max pooling. Count feature owners separately from signed head components and actual leave-one-slot-out effects. Published summaries retain owner concentration, matched/correct owner fractions, ReLU activity and logit-removal statistics; final summaries additionally compare ownership, signed-component and removal leaders. |
| Parameter updates and stratification | `monitor/parameter_updates.jsonl`; score-report JSON under `monitor/auroc_mechanisms/` and `final/monitor/auroc_mechanisms/` | Compare module parameters before and after each epoch, including absolute and relative L2 changes. Record same-video ranking and behavior grouped by observed length, GT count and truncation. Stored strata use the legacy observation rules; they are descriptive diagnostics. |
| Frozen generalization and paired comparisons | `metrics.json`, `metrics.csv`, `METRICS.md`; `monitor/auroc_mechanisms/final_gap_decomposition.json`; `final/NATIVE_DIAGNOSTIC_PARITY.json` | Report Seen/Unseen AUROC, rejection F1 and G-mIoU@1 with signed Seen-minus-Unseen gaps; overall rates, positive false rejection and subset counts remain explicit. Use 2,000 shared target-video-cluster bootstrap draws for paired comparisons. Match each reference by split/backbone; reproduction deviations are not new-method gains. Rejection F1 and G-mIoU depend on class prevalence. |

Example records: [Moment training log]({example}/training/moment/console.log), [QD training log]({root}/runs/clean_v3/A1_v3/qd/seed_3407/training/qd/console.log), [Moment matching history]({example}/monitor/epochs.jsonl), [Moment gradient measurements]({example}/monitor/representation_gradients.jsonl), [Moment score report]({example}/monitor/auroc_mechanisms/validation_epoch_0018_scores.json), [Moment frozen metrics]({example}/metrics.json).

## Pooling provenance and local raw paths

The following paths are relative to the original local `<RUN>` and are documented for measurement provenance. They are local-only arrays, not downloadable files in this branch.

| Local raw path | Measurement principle |
|---|---|
| `monitor/auroc_mechanisms/pool_sources/{{train,probe,validation}}/epoch_*/batch_*_query_*.npz` | For each feature dimension, store native owner slot, signed selected value, distinct runner-up slot/value, top-two margin, exact-equality tie mask/count and the native first winning slot. Original decoder indices precede candidate ranking. |
| `final/monitor/auroc_mechanisms/pool_sources/test/epoch_*/batch_*_query_*.npz` | Apply the same capture to the frozen test checkpoint. Associate original slots with spans, foreground and GT IoU. Label native training/probe matcher identities separately from offline full-annotation matching in validation/test. |
| Pool-source NPZ fields `pool_logit_grad`, `pool_signed_logit_component`, `pool_head_bias_component`, `slot_positive_logit_component`, `slot_negative_logit_component` | For z = w2 ReLU(W1 p + b1) + b2, hold the observed ReLU mask a fixed: g = (w2 * a) W1, c[d] = p[d] g[d], bias = (w2 * a) b1 + b2. Sum dimension components plus explicit bias to reconstruct the logit within numerical tolerance. This local algebra is not a causal attribution. |
| Pool-source NPZ field `pool_source_changed_fraction` | Compare dimension-wise original slot indices for the same fixed Seen training probe in adjacent epochs. Slot-index agreement is not semantic identity tracking. |
| Pool-source NPZ field `slot_removal_logit_delta`; legacy query field `leave_one_unit_out_logit_drop` | Remove one slot, re-pool and recompute the native head, allowing the ReLU mask to change. New delta means removed minus original; legacy drop means original minus removed. Neither equals feature ownership or the fixed-mask signed component. |
| `monitor/decoder_slots/*_epoch_*_batch_*.npz` | Retain native layer outputs, returned attention and slot geometry at the legacy raw sampling frequency. |
| `monitor/assignments_epoch_*.npz`, `fixed_probe_epoch_*.npz`, `*_responses_epoch_*.npz` | Keep query/GT assignment and response arrays for local reanalysis and identity alignment. |
| `predictions.npz`, `candidate_cache.pt`, `bootstrap.npz`; `<ROOT>/analysis/detr_20261014/*_macro_bootstrap.npz` | Freeze per-query predictions, candidates and shared video-cluster resampling artifacts. Public metric JSON/CSV files retain point estimates and confidence intervals. |
| `training/<BACKBONE>/*.ckpt`, `local_only/checkpoints/*.pt` | Retain native selected/latest checkpoints and diagnostic anchors locally; weight files do not belong to this text-log branch. |

## Recording frequency

| Stage | Measurement principle |
|---|---|
| Native training, every step | Actual matching, response summaries, loss attribution, optimization and pre-clipping gradient norms. |
| Sampled native training | Preserve the legacy first-batch and every-50-global-step schedule for expensive representations, attention, task gradients, pooling and removals. Individual legacy observers retain their source-defined sampling predicates. |
| Fixed Seen training probe | Hash-ranked cohort of at most 64 queries per class; DETR excludes GT-truncated queries. Evaluate at epoch zero and every completed epoch while preserving RNG state. |
| Full Seen validation | Every epoch, including epoch zero: scores, ranking, localization and pooling/LOO diagnostics. Formal checkpoint eligibility starts at epoch one. |
| Final test | Evaluate only after native best/options/Seen threshold freezing. GT-based analysis is post-freeze diagnosis and does not select the checkpoint or threshold. |

## Aggregate result and implementation paths

| Path | Measurement principle |
|---|---|
| [Metric table with intervals]({root}/analysis/detr_20261014/DETR_METRICS_WITH_CI.csv) | Split/backbone point estimates and video-cluster intervals, including paired Unseen Net Gain, Seen Change and Gap Reduction. |
| [Full aggregate records]({root}/analysis/detr_20261014/DETR_ANALYSIS.json) | Collect frozen metrics, counts, score-shift decomposition, Seen trajectories, gradient summaries and final pooling summaries. |
| [English result tables]({root}/analysis/detr_20261014/DETR_RESULTS.md) | Render the same frozen split and five-split macro metrics; macro intervals use shared video-cluster draws across completed splits. |
| [Reference parity records]({root}/analysis/detr_20261014/REPRODUCTION_PARITY.json) | Compare model tensors, aligned native scores/IoUs, thresholds and reference checkpoint epochs. |
| `<ROOT>/native_source/{{mechanism_monitor,response_monitor,decoder_slot_monitor,auroc_mechanism_monitor}}.py` | Preserve the legacy nine diagnostic areas and native-process gradient/removal execution. |
| `<ROOT>/native_source/{{legacy_bridge,publication_monitor,pool_provenance,pool_algebra}}.py` | Connect native training to legacy observers and add detached pooling provenance/head algebra. |
| [Pool schema]({root}/design/POOL_SOURCE_SCHEMA.json), [scope and artifact index]({root}/PUBLICATION_SCOPE.json) | Define field layouts, labels, reference commits and the exact published artifact scope. |
| [Upload manifest](UPLOAD_MANIFEST.json) | List original/source and published SHA256 hashes, text normalization, derived summaries and explicit exclusions. |
'''
    (dest/'README.md').write_text(text)


def english_results(path,x):
    def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(v) for v in r)+' |' for r in rows])
    text=['# Frozen DETR Result Tables','','All rows use seed 3407, native Seen-localization checkpoint selection, a maximum of 26 completed epochs and Seen-only threshold calibration. Units are percentages and percentage-point gaps. Negative gaps are retained.','',
      table(['Dataset/split','Backbone','Selected epoch','AUROC Seen / Unseen / gap','Rej-F1 Seen / Unseen / gap','G-mIoU@1 Seen / Unseen / gap'],
      [[r['dataset']+'/'+r['split'],r['backbone'],r['best_epoch']]+[' / '.join(f"{r[s+'_'+m]:.2f}" for s in ('S','U','gap')) for m in ('auroc','rej_f1','gmiou1')] for r in x['runs']]),
      '','## Completed Clean five-split macro','','Each split has equal weight. Intervals use the same target-video cluster draws across splits to retain cross-split dependence.','',
      table(['Backbone','Metric','Seen [95% CI]','Unseen [95% CI]','Gap [95% CI]'],
      [[r['backbone'],metric]+[f"{r['metrics']['experiment/'+s+'/'+metric]['point']:.2f} [{r['metrics']['experiment/'+s+'/'+metric]['ci95'][0]:.2f}, {r['metrics']['experiment/'+s+'/'+metric]['ci95'][1]:.2f}]" for s in ('S','U','gap')] for r in x['macro'] for metric in ('auroc','rej_f1','gmiou1')]),
      '','## Overall operating-point records and subset sizes','',
      table(['Dataset/split','Backbone','S+ / S- / U+ / U-','Overall Rej-F1','Overall RR','S+ FRR','U+ FRR','U- false acceptance','Overall G-mIoU'],
      [[r['dataset']+'/'+r['split'],r['backbone'],' / '.join(str(r['n_'+p]) for p in ('S+','S-','U+','U-'))]+[f'{r[k]:.2f}' for k in ('overall_rej_f1','overall_rr','S+_frr','U+_frr','U-_false_acceptance','overall_gmiou1')] for r in x['runs']]),
      '','## Interpretation boundaries','','Rej-F1 and G-mIoU depend on subset class proportions. Reference differences describe 26-epoch reproduction deviations rather than algorithmic gains. AUROC shadow checkpoints are compared on Seen validation only. Pooling components, gradient conflicts and score-distribution decompositions are diagnostic associations rather than causal estimates. Full confidence intervals and paired changes for all three metrics are in `DETR_METRICS_WITH_CI.csv` and `DETR_ANALYSIS.json`.']
    path.write_text('\n'.join(text)+'\n')


def main(dest):
    export=Export(dest);analysis=json.loads((ROOT/'analysis/detr_20261014/DETR_ANALYSIS.json').read_text());runs=[]
    safe_jsonl={'epochs.jsonl','fixed_probe.jsonl','gradients.jsonl','representation_gradients.jsonl','parameter_updates.jsonl','train_responses.jsonl','epoch_responses.jsonl','probe_responses.jsonl','validation_responses.jsonl','existence_loss_contributions.jsonl','shared_gradients.jsonl','objective_split.jsonl','optimization.jsonl'}
    for metric in sorted(ROOT.glob('runs/**/seed_3407/metrics.json')):
        run=metric.parent;bb=run.parent.name
        if bb not in ('moment','qd'):continue
        assert json.loads((run/'STATUS.json').read_text())['state']=='complete'
        relrun=REL/run.relative_to(ROOT)
        print('EXPORT_START',run.relative_to(ROOT),flush=True)
        for name in ['CONFIG.json','PROVENANCE.json','STATUS.json','FROZEN_CALIBRATION.json','metrics.json','metrics.csv','METRICS.md']:
            export.copy(run/name,relrun/name)
        for source in sorted((run/'selection').glob('*')):
            if source.suffix in ('.json','.jsonl'):export.copy(source,relrun/'selection'/source.name)
        for source in sorted((run/'training'/bb).glob('*')):
            if source.suffix in ('.log','.txt','.json') or source.name=='exit_code':export.copy(source,relrun/'training'/bb/source.name)
        for source in sorted((run/'monitor').rglob('*')):
            if source.is_file() and (source.suffix=='.json' or source.name in safe_jsonl):export.copy(source,REL/source.relative_to(ROOT))
        for source in sorted((run/'final').rglob('*.json')):
            export.copy(source,REL/source.relative_to(ROOT))
        for source in sorted((run/'final').glob('*.log')):export.copy(source,REL/source.relative_to(ROOT))
        for phase in ('train','probe','validation'):
            source=run/'monitor/auroc_mechanisms'/(phase+'_queries.jsonl')
            target=dest/relrun/'monitor/auroc_mechanisms'/(phase+'_query_summary.jsonl')
            aggregate_queries(source,target);export.derived.append(dict(path=str(target.relative_to(dest)),source=str(source.relative_to(REPO)),source_sha256=sha(source),sha256=sha(target),bytes=target.stat().st_size,derivation='epoch/partition aggregates; no full query records'))
        for phase in ('train','probe'):
            source=run/'monitor/decoder_slots'/(phase+'_slots.jsonl')
            target=dest/relrun/'monitor/decoder_slots'/(phase+'_slots_summary.jsonl')
            aggregate_decoder(source,target);export.derived.append(dict(path=str(target.relative_to(dest)),source=str(source.relative_to(REPO)),source_sha256=sha(source),sha256=sha(target),bytes=target.stat().st_size,derivation='epoch/partition/layer aggregates; no full query records'))
        source=run/'final/monitor/auroc_mechanisms/test_queries.jsonl';target=dest/relrun/'final/monitor/auroc_mechanisms/test_query_summary.jsonl'
        aggregate_queries(source,target);export.derived.append(dict(path=str(target.relative_to(dest)),source=str(source.relative_to(REPO)),source_sha256=sha(source),sha256=sha(target),bytes=target.stat().st_size,derivation='frozen test partition aggregates'))
        dataset=run.parents[2].name;split=run.parents[1].name
        export.generated(relrun/'final/pooling_summary.json',analysis['mechanisms'][dataset+'/'+split+'/'+bb]['pool_test'])
        runs.append(dict(dataset=dataset,split=split,backbone=bb,path=str(relrun),selected_epoch=json.loads((run/'selection/frozen.json').read_text())['epoch'],trained_epochs=26))
        print('EXPORT_DONE',run.relative_to(ROOT),flush=True)
    assert len(runs)==12
    for name in ['DETR_ANALYSIS.json','DETR_METRICS.csv','DETR_METRICS_WITH_CI.csv','REPRODUCTION_PARITY.json']:
        export.copy(ROOT/'analysis/detr_20261014'/name,REL/'analysis/detr_20261014'/name)
    english_results(dest/REL/'analysis/detr_20261014/DETR_RESULTS.md',analysis)
    for name in ['POOL_SCHEMA_VALIDATION.json','LEGACY_DIAGNOSTIC_PARITY_AUDIT.json']:
        export.copy(ROOT/name,REL/name)
    schema=json.loads((ROOT/'design/POOL_SOURCE_SCHEMA.json').read_text());schema['status']='implemented_and_validated';schema['flash_mean_pooling']={'status':'outside_this_publication_scope'}
    export.generated(REL/'design/POOL_SOURCE_SCHEMA.json',schema)
    export.generated(REL/'PUBLICATION_SCOPE.json',dict(captured_at=datetime.now().astimezone().isoformat(),backbones=['Moment-DETR-GMR','QD-DETR-GMR'],runs=runs,
        reference_diagnostics_branch='diagnostics/baseline-auroc-20261013',reference_diagnostics_commit='00a6d6b41f0ec21056f2d71207385f3a67b2d962',
        reference_publication_commit='2677cfecddd0101b187d0ab413f2b51fe09ea201',seed=3407,epoch_cap=26,published_reference_cap=100,
        formal_selection='native Seen-validation localization; AUROC diagnostic shadow only',bootstrap='2000 shared target-video cluster draws',
        excluded=['Flash runs','full per-query predictions and candidate caches','checkpoints','raw NPZ tensors and bootstrap arrays','features','videos','credentials'],
        validation='English-only added text; safe file extensions; SHA256 manifests; all 12 DETR final evaluations complete'))
    for source in sorted((ROOT/'native_source').rglob('*')):
        if not source.is_file() or source.suffix not in ('.py','.yml','.yaml'):continue
        rel=source.relative_to(ROOT/'native_source')
        if 'flash' in str(rel).lower() or '__pycache__' in rel.parts or source.name=='legacy_flash.py':continue
        export.copy(source,REL/'native_source'/rel)
    export.copy(Path(__file__),REL/'code'/Path(__file__).name)
    license_path=REPO/'LICENSE'
    if license_path.exists():export.copy(license_path,Path('LICENSE'))
    (dest/'.gitignore').write_text('*.ckpt\n*.pt\n*.npz\n*.npy\n__pycache__/\n.env*\nfeatures/\nvideos/\n')
    make_readme(dest)
    # Every exported file is readable text, English, below GitHub limits, and token-screened.
    files=[]
    for p in sorted(dest.rglob('*')):
        if not p.is_file() or p.name=='.git':continue
        text=p.read_text()
        if CJK.search(text):raise RuntimeError('CJK remains in '+str(p))
        if CREDENTIAL.search(text):raise RuntimeError('Credential-like content in '+str(p))
        if p.stat().st_size>=95*1024*1024:raise RuntimeError('File exceeds safe GitHub limit: '+str(p))
        if p.suffix in ('.json','.jsonl'):
            if p.suffix=='.json':json.loads(text)
            else:
                for line in text.splitlines():
                    if line.strip():json.loads(line)
        files.append(dict(path=str(p.relative_to(dest)),bytes=p.stat().st_size,sha256=sha(p)))
    manifest=dict(captured_at=datetime.now().astimezone().isoformat(),reference_branch='diagnostics/baseline-auroc-20261013',
        branch='diagnostics/detr-native-26ep-20261014',file_count=len(files),total_bytes=sum(p['bytes'] for p in files),
        files=files,copied_sources=export.entries,derived_records=export.derived,
        exclusions=['weights and raw arrays remain local','query/decoder raw JSONL replaced by aggregate summaries','no Flash artifacts','no dataset/feature/video/credential upload'],
        language='English; CJK scan passed',normalization='remove ANSI controls and replace local absolute paths without changing numeric measurements')
    dump(dest/'UPLOAD_MANIFEST.json',manifest)
    print(json.dumps(dict(files=len(files)+1,bytes=manifest['total_bytes'],runs=len(runs),destination=str(dest))),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();main(args.output.resolve())
