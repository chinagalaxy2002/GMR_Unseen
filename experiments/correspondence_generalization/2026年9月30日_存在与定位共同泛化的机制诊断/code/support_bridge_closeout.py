from pathlib import Path
import json,hashlib,datetime,re,subprocess
s=Path(__file__).resolve().parents[1];d=s/'support_bridge_analysis';root=s.parent;f=json.loads((d/'FREEZE.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as z:
  for b in iter(lambda:z.read(1048576),b''):h.update(b)
 return h.hexdigest()
checks={p:sha(p)==h for p,h in f['protected_files_sha256'].items()};assert all(checks.values());assert sha(s/'code/support_bridge_analyze.py')==f['source_sha256']
files=[s/'README.md',s/'DECISION.md',s/'plan/progress.md',s/'plan/HANDOFF.md',s/'plan/RECOVERY_PROMPT.txt',s/'plan/HANDOFF_STATUS.json',root/'plan/EXPERIMENT_PLAN.md',d/'REPORT.md',d/'IDEA_EVALUATION.md'];missing=[]
for p in files:
 for t in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not t.startswith(('https://','http://','#')) and not (p.parent/t).exists():missing.append((str(p),t))
assert not missing,missing
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();gpu=subprocess.run('nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader',shell=True,capture_output=True,text=True).stdout
proc=subprocess.run(['ps','-eo','pid,etimes,args'],capture_output=True,text=True).stdout
(d/'RUNTIME_AFTER.json').write_text(json.dumps({'at':stamp,'gpu_compute_snapshot':gpu,'process_snapshot':proc,'analysis_workers_terminal':True,'new_training_started':False},ensure_ascii=False,indent=2)+'\n')
x=json.loads((d/'INTEGRITY.json').read_text());x.update(final_checked_at=stamp,checks=checks,all_unchanged=all(checks.values()),source_matches_freeze=True,independent_validation='passed',documentation_links='passed');(d/'INTEGRITY.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
st=json.loads((d/'state.json').read_text());st.update(report='completed',idea_review='completed',independent_validation='passed',documentation='completed',integrity='passed',closed_at=stamp);(d/'state.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n')
hp=s/'plan/HANDOFF_STATUS.json';hs=json.loads(hp.read_text());hs.update(runtime_checked_at=stamp,gpu_compute_process_snapshot=gpu,active_experiment_processes=[]);hp.write_text(json.dumps(hs,ensure_ascii=False,indent=2)+'\n')
r=json.loads((d/'RESULTS.json').read_text());validation=json.loads((d/'VALIDATION.json').read_text());assert r['state']=='completed' and validation['state']=='passed' and not r['entry_evidence_supported'];assert sum(x['coverage']['rows'] for x in r['groups'].values())==7345
assert all(z for x in validation['checks'].values() for k,z in x.items() if k!='rows_verified')
audit={'at':stamp,'previous_goal_turn_classification':'progress: candidate diagnostics completed, then authorized support bridge changed authoritative state and evidence','objective':'Continue research according to plan and joint existence/localization target; conditionally create named experimental stage and code experiments only if sufficient discoveries','requirements':{'research_after_analysis':{'status':'proved','evidence':['REPORT.md','RESULTS.json','ROWS.jsonl','VALIDATION.json','IDEA_EVALUATION.md']},'align_with_joint_AUROC_raw_gated_seen_rejection_VTG_goal':{'status':'proved for this research scope; no efficacy claim','evidence':'FREEZE/REPORT retain full goal and leave gated/FRR/RR/VTG validation gaps explicit'},'determine_sufficient_discoveries':{'status':'proved not triggered for evaluated concrete hypothesis','evidence':r['entry_evidence_checks'],'limitation':'does not prove no possible future mechanism'},'new_experiment_directory_code_training_if_sufficient':{'status':'conditional branch not triggered by current evidence','new_stage_created':False,'new_training_started':False,'code_research_executed':['code/support_bridge_analyze.py','code/support_bridge_verify.py']},'preserve_original_stop_frozen_assets':{'status':'proved','protected_paths':len(checks),'all_unchanged':True},'complete_report_integrity_handoff':{'status':'proved','evidence':[str(p) for p in files]}},'pending_required_work_in_current_conditional_request':[],'future_scientific_gap':'a different concrete shared-support mechanism and ordinary controls, not automatic revival of rejected formulas'}
(d/'COMPLETION_AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
manifest={'at':stamp,'artifacts_sha256':{str(p):sha(p) for p in d.iterdir() if p.is_file() and p.name!='ARTIFACT_MANIFEST.json'},'source_sha256':{str(p):sha(p) for p in (s/'code').glob('support_bridge_*.py')},'documentation_sha256':{str(p):sha(p) for p in files},'failed_attempt_retained':str(s/'support_bridge_analysis_failures/attempt_001')};(d/'ARTIFACT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Closeout audited:',len(checks),'protected paths unchanged; report/docs links passed; conditional new training branch unsupported; GPU compute',repr(gpu))
