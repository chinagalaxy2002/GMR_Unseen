#!/usr/bin/env python3
"""Package the validated v3 candidate without hashes or model artifacts."""
import json, shutil, datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; W=ROOT/'data/processed/semantic_existence_v3'; DST=ROOT/'data/release/semantic_existence_v3'
DST.mkdir(parents=True,exist_ok=True)
for name in ['ontology','selection','master','splits']:
 shutil.copytree(W/name,DST/name,dirs_exist_ok=True)
(DST/'review').mkdir(parents=True,exist_ok=True)
for name in ['decisions.jsonl','quarantine.jsonl','history.jsonl','second_pass_decisions.jsonl','second_pass_adjudications.jsonl','batch_assignments.json','second_pass_assignments.json','semantic_overrides.jsonl','a1_semantic_corrections.jsonl','a1_semantic_revision.json']:
 p=W/'review'/name
 if p.exists(): shutil.copy2(p,DST/'review'/name)
# Make explicit disposition ledgers.
rows=[json.loads(x) for x in open(DST/'review/decisions.jsonl') if x.strip()]
# Preserve the positive normalization ledger and an explicit unresolved-positive exclusion list.
shutil.copy2(W/'positives/dispositions.jsonl',DST/'review/positive_dispositions.jsonl')
with open(DST/'review/positive_unresolved_exclusions.jsonl','w') as f:
 for r in (json.loads(x) for x in open(W/'positives/dispositions.jsonl') if x.strip()):
  if r.get('semantic_review_status')!='resolved': f.write(json.dumps(r,ensure_ascii=False)+'\n')
for name,subset in [('exclusions.jsonl',[r for r in rows if r['decision']=='exclude']),('quarantine.jsonl',[r for r in rows if r['decision']=='quarantine']),('rewrites.jsonl',[])]:
 with open(DST/'review'/name,'w') as f:
  for r in subset:f.write(json.dumps(r,ensure_ascii=False)+'\n')
from collections import Counter
counts=Counter(r['decision'] for r in rows)
protocol={'source_plan':'docs/20261009_SEMANTIC_EXISTENCE_V3_DATA_CONSTRUCTION_PLAN.md','ontology_version':'v3-ontology-1.0.0','positive_normalization_rule_version':'v3-event-normalization-1.1.0','reviewed_legacy_candidate_qids':len(rows),'review_decisions':dict(counts),'second_pass_qids':372,'second_pass_disagreements_adjudicated':91,'random_seed':3407,'video_review_policy':'No per-video review; semantic query comparison and recorded same-video positive alignment only.','model_predictions_used':False,'preset_scale_gates':False}
json.dump(protocol,open(DST/'construction_protocol.json','w'),ensure_ascii=False,indent=2)
profile=json.load(open(W/'selection/data_profile.json'))
json.dump({'positive_input_qids':profile['positive_unique_qids'],'positive_resolved_qids':profile['positive_qids_resolved'],'positive_unresolved_qids':profile['positive_qids_unresolved'],'video_assignments':profile['video_assignments'],'source_inventory':str(W/'inputs/inventory.json'),'excluded_unresolved_positive_qids':profile['positive_qids_unresolved'],'legacy_candidate_qids':len(rows),'kept_negative_qids':counts['keep']},open(DST/'input_inventory.json','w'),ensure_ascii=False,indent=2)
summary=json.load(open(W/'splits/summary.json'))
json.dump({'release':'semantic_existence_v3','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'validated','positive_clean_qids':len([1 for _ in open(W/'master/positive_clean.jsonl')]),'negative_clean_qids':len([1 for _ in open(W/'master/negative_clean.jsonl')]),'legacy_decisions':dict(counts),'groups':summary,'checks':['all legacy qids have final decisions','released negatives are keep/distinct','video splits are disjoint','train contains S only','matched U pairs refer to same-video U+/U- rows']},open(DST/'release_info.json','w'),ensure_ascii=False,indent=2)
report={'legacy_decision_counts':dict(counts),'second_pass_qids':372,'adjudicated_conflicts':91,'positive_unresolved_excluded':profile['positive_qids_unresolved'],'group_statistics':{g:json.load(open(W/'splits'/g/'statistics.json')) for g in summary}}
json.dump(report,open(DST/'review/review_statistics.json','w'),ensure_ascii=False,indent=2)
(DST/'README.md').write_text('''# Semantic Existence v3\n\nThis release rebuilds five action and action-object generalization groups from resolved Charades-derived positive query events and individually reviewed legacy negative candidates. All videos use the persisted shared train/val/test assignment.\n\n## Groups\n\n- `A1_v3`: physical placement and taking actions held out.\n- `A2_v3`: drinking and pouring held out.\n- `A3_v3`: running and walking held out.\n- `C1_v3`: sitting on bed, chair, or couch held out. Sofa is normalized to couch.\n- `C2_v3`: opening/closing boxes and cabinets held out.\n\nEach group contains `train.jsonl`, `val.jsonl`, `val_seen.jsonl`, `test.jsonl`, and matched unseen pair files. Train contains S+/S- only. Rows keep their shared video split. `semantic_inventory.json` and `statistics.json` report actual group contents.\n\n## Review\n\nAll 6,976 unique legacy negative candidates have final decisions. Release negatives are only `keep` with `distinct` relation; excludes and quarantines are retained in `review/`. Positive qids unresolved after normalization are omitted from the clean pool. No model predictions, hashes, or preset scale gates were used. See `construction_protocol.json`, `review/review_statistics.json`, and `release_info.json`.\n''',encoding='utf-8')
for g in summary:
 (DST/'splits'/g/'HANDOFF.md').write_text(f'''# {g}\n\nSplit membership follows the shared video assignment in `selection` source records. Training contains S+/S- only. Validation and test retain seen and held event examples as available. See `semantic_inventory.json` and `statistics.json` for actual counts.\n''',encoding='utf-8')
print('packaged',DST)
revision_file=W/'review/a1_semantic_revision.json'
if revision_file.exists():
 revision=json.load(open(revision_file))
 for filename in ['construction_protocol.json','release_info.json','review/review_statistics.json']:
  path=DST/filename
  record=json.load(open(path))
  record['semantic_revision']=revision['revision']
  record['semantic_correction_qids']=revision['total_unique_qids']
  json.dump(record,open(path,'w'),ensure_ascii=False,indent=2)
 with open(DST/'README.md','a') as f:
  f.write(f"\n## A1 semantic repair\n\nRevision `{revision['revision']}`. See `review/a1_semantic_corrections.jsonl` and `review/a1_semantic_revision.json`. Queries, windows, existence labels and video splits are preserved; 29 ambiguous candidates remain pending. Existing runs on the prior version are not results on this revision.\n")
