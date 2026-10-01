"""Publish diagnostic report/hand-off after validation, retaining previous revisions."""
from pathlib import Path
import json,datetime,shutil,hashlib
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis';now=datetime.datetime.now().astimezone().isoformat();assert json.loads((D/'VALIDATION.json').read_text())['state']=='passed';assert json.loads((D/'INTEGRITY.json').read_text())['all_original_assets_unchanged']
rev=S/'plan/handoff_revisions'/('temporal_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));rev.mkdir()
for p in [S/'DECISION.md',S/'README.md',S/'plan/HANDOFF.md',S/'plan/RECOVERY_PROMPT.txt',S/'plan/HANDOFF_STATUS.json',S/'plan/progress.md',S.parents[0]/'plan/EXPERIMENT_PLAN.md']:shutil.copy2(p,rev/('ROOT_EXPERIMENT_PLAN.md' if p.parent==S.parents[0]/'plan' else p.name))
pooling=json.loads((D/'POOLING_ROBUSTNESS.json').read_text())
conditional=json.loads((D/'CONDITIONAL_SUPPORT.json').read_text())
lines=['\n## 最大值搜索范围敏感性（看过主结果后追加，未重拟合）\n','S+ GT均值 vs 原S−全视频均值避免不同长度最大值搜索机会，但仍使用GT作正例诊断，不能当实际推理成绩。区间与主分析使用同一1000次seed3407视频权重，不把后加分析称为预登记。\n','|组|early GTmean AUC|memory GTmean AUC|window GTmean AUC|','|---|---|---|---|']
for g,metrics in pooling['metrics'].items():
 cells=[]
 for name in ['early_global','memory_global','memory_window']:
  m=metrics[name+'/GT_mean_vs_Sminus_video_mean_AUROC'];cells.append(f"{m['point']:.4f} [{m['ci95'][0]:.4f}, {m['ci95'][1]:.4f}]")
 lines.append('|'+g+'|'+'|'.join(cells)+'|')
lines+=['','敏感性结果必须与固定文本控制一起读：均值可缓解极值范围效应，但不能移除文本先验，也没有把GT变成可用推理输入。完整最大值−均值、两类有效时间长度分位数见[POOLING_ROBUSTNESS](POOLING_ROBUSTNESS.json)。','', '![固定读出诊断](REPRESENTATION_READOUT.png)','','[可导出图PDF](REPRESENTATION_READOUT.pdf)。','', '独立核验初次因逐行重复解压而主动终止，保留于../temporal_representation_failures/attempt_002_verifier_io；随后每组缓存一次重启核验，统计定义不变，主分析未重做。']
lines+=['','均值敏感性提示局部信息不能被判为消失：memory_window的GTmean正例诊断pseudo AUC为.6241/.6078/.6726，均高于随机；而同一读出的无GT整段mean/max等权AUC仅.5686/.5402。它使用额外原时间监督和GT位置，不能证明只修原存在头即可恢复。固定实际文本的GTmean PairAcc（另行看过主结果后冻结）如下：','|族|window GTmean同句PairAcc|','|---|---|']
for fam in ['throw','open_close','sit']:
 m=conditional['metrics'][fam]['memory_window'];lines.append(f"|{fam}|{m['point']:.4f} [{m['ci95'][0]:.4f}, {m['ci95'][1]:.4f}]|")
lines+=['','open_close保留有限的文本固定后、GT条件局部证据（PairAcc=.5646 [.5339,.6263]）；throw/sit覆盖有限且区间包含.5，不能扩展为三族稳定绝对支持。当前进一步收束为：**如何在无GT条件下选取这些局部证据，并聚合成可跨查询、跨语义比较的支持？** 仍不是已经证实的纯存在映射问题，也不是已经证实的表示完全缺失。详见[CONDITIONAL_SUPPORT](CONDITIONAL_SUPPORT.json)及其冻结/独立核验。']
with (D/'REPORT.md').open('a') as out:out.write('\n'.join(lines)+'\n')
summary='''
## 冻结时序表示绝对支持诊断已完成

用户将问题收束到跨查询可比较的绝对支持，已实际完成[时序表示诊断](temporal_representation_analysis/REPORT.md)。early mean的pseudo等权AUROC增益+.0271 [.0094,.0438]，但纯文本AUROC=.6264，高于early=.6130；固定实际文本控制未形成跨族稳定视觉判别。memory mean基本没有恢复增益。额外原GT监督的window probe保留相对峰值信号（pseudo峰入GT=.3528、机会率=.2566），但纯视频+TEF也有位置偏置，不能等同文本条件定位；更不能替代raw R1@.5。GTmax对整段S−max有搜索范围不等问题；追加均值诊断在GT已知时三族pseudo AUC=.6241/.6078/.6726，无GT同一读出mean/max仅.5686/.5402。固定实际文本后只有open_close的GTmean PairAcc=.5646 [.5339,.6263]支持有限局部证据；throw/sit未定。相关敏感性均后加探索、单列冻结。

结论：未支持“可靠绝对视觉支持已经在表示中，只需修原存在头”；也不能断言“表示完全没有支持信息”。当前缺口在无GT的局部证据选取、聚合标尺及其跨语义迁移之间，线性容量、监督和控制覆盖仍限制二选一判断。下一步不再围绕候选一致性扫变体；绝对支持场仅为待具体化研究候选，未启动新目标训练。

原模型更新0，新增骨干0；确实拟合18个257参数诊断读出器（合计4626参数），不是所有参数更新0。28370冻结前向query呈现、原train19162、原评估7345、canonical1863；1000次seed3407共同原视频探索95%区间。18次拟合收敛、独立核验通过、18230保护资产hash未变。原gate/阈值/主要指标/旧结果不变，无新raw/gated共同成功，无独立VTG新迁移结论；sit训练仍停止。RaTSG及Learning to Refuse近邻已核验，不能把局部证据判断存在写成首次贡献。详细范围/文献见报告。
'''
for name in ['DECISION.md','README.md']:
 with (S/name).open('a') as out:out.write('\n更新：'+now+'\n'+summary)
with (S/'plan/progress.md').open('a') as out:out.write('\n### '+now+' 冻结时序表示诊断收尾\n'+summary.replace('(temporal_representation_analysis/REPORT.md)','(../temporal_representation_analysis/REPORT.md)'))
head='''# 上下文恢复：冻结时序表示绝对支持诊断已完成

最新更新：'''+now+'''

先读根plan/EXPERIMENT_PLAN.md → 本HANDOFF → 阶段DECISION最新条目 → temporal_representation_analysis/REPORT.md、FREEZE/RESULTS/VALIDATION/INTEGRITY、POOLING_ROBUSTNESS → progress/HANDOFF_STATUS；NEXT_TASK为已完成的历史候选诊断，不是待执行命令。

'''+summary.replace('(temporal_representation_analysis/REPORT.md)','(../temporal_representation_analysis/REPORT.md)')+'''
本次授权诊断已完成，没有待运行任务。原训练队列保持停止，不启动全模型干预、正式U、75组、教师/window、多seed、同预算核验、第一阶段六组或sit补训练。若未来训练必须先具体化METHOD_SPEC与普通控制，并验证AUROC+raw共同路径，gated、seen、FRR/RR及独立VTG范围仍依原冻结标准。

恢复查看保存产物即可，不重复已完成collect/probe/verify；实现均在code/temporal_representation_*.py。两次失败/主动终止已保留在temporal_representation_failures，未改主统计定义。诊断读出拟合与全模型训练必须分别记账。

---
以下为历史交接，保留既有资产入口与此前决策：

'''
(S/'plan/HANDOFF.md').write_text(head+(S/'plan/HANDOFF.md').read_text())
rec='''最新恢复入口：先读temporal_representation_analysis/REPORT.md和阶段DECISION最新条目、plan/HANDOFF.md。用户授权的早期时序表示/固定小读出器诊断已经完成，原模型更新0，18个257参数probe确有拟合、总4626参数，28370冻结前向。独立核验通过，18230原资产hash不变。问题收束为跨查询绝对视觉支持的形成/迁移与聚合标尺；并未证明“只修存在头”，也未证明表示完全无信息。纯文本及固定实际文本控制限制global AUC解释；纯视频位置偏置与GT最大值搜索范围限制位置诊断。看保存敏感性结果，不重跑。没有待执行训练/正式U；sit保持77轮、best11/latest76。冻结总目标/阈值/gate/旧结果不变。不恢复任何旧队列。后续仅依据用户明确新范围继续，不能自动把待研究绝对支持场变成训练授权。

历史恢复说明：
'''
(S/'plan/RECOVERY_PROMPT.txt').write_text(rec+(S/'plan/RECOVERY_PROMPT.txt').read_text())
p=S/'plan/HANDOFF_STATUS.json';status=json.loads(p.read_text());status.update(updated_at=now,handoff_state='temporal_representation_diagnostic_completed_no_full_model_training',decision='relative position accessibility limited; transferable absolute visual support not established; readout versus representation unresolved',original_model_parameter_updates=0,diagnostic_probe_fits=18,diagnostic_probe_parameters_fitted=4626,temporal_representation_analysis='completed',active_processes=False,training_restarted=False)
# Existing parameter_updates=0 refers only to original model, clarify scope rather than rewriting history.
status['parameter_updates_scope']='original frozen model only; diagnostic probe fitting separately counted'
status['temporal_representation_summary']={'report':'temporal_representation_analysis/REPORT.md','new_frozen_forward_query_presentations':28370,'original_model_updates':0,'probe_fits':18,'probe_parameters':4626,'protected_paths':18230,'independent_validation':'passed','integrity':'passed','new_training_round_started':False,'bootstrap_video_union':2302,'bootstrap_resamples':1000,'bootstrap_seed':3407}
status['latest_authorized_task']={'state':'completed','name':'absolute_support_temporal_representation_diagnostic','result':'temporal_representation_analysis/REPORT.md','pending_action':None}
status['runtime_checked_at']=json.loads((D/'RUNTIME_AFTER.json').read_text())['at'];status['active_experiment_processes']=[];status['gpu_compute_process_snapshot']='';p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
p=S.parents[0]/'plan/EXPERIMENT_PLAN.md';t=p.read_text();t=t.replace('当前无已授权待执行任务。','随后[早期时序表示绝对支持诊断](../2026年9月30日_存在与定位共同泛化的机制诊断/temporal_representation_analysis/REPORT.md)已完成：相对位置可读性有有限支持，跨查询绝对视觉支持尚未证实，存在映射与表示迁移的归因仍未决；没有启动全模型训练。当前无已授权待执行任务。');p.write_text(t)
state=json.loads((D/'state.json').read_text());state.update(state='completed',active=False,finished_at=now,original_model_updates=0,probe_fits=18,fitted_probe_parameters=4626,independent_validation='passed',asset_integrity='passed',report='REPORT.md');(D/'state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
manifest={}
for path in list(D.iterdir())+list((S/'code').glob('temporal_representation_*.py')):
 if path.is_file() and path.name!='ARTIFACT_MANIFEST.json':
  h=hashlib.sha256()
  with path.open('rb') as stream:
   for chunk in iter(lambda:stream.read(8*1024*1024),b''):h.update(chunk)
  manifest[str(path.relative_to(S))]={'bytes':path.stat().st_size,'sha256':h.hexdigest()}
(D/'ARTIFACT_MANIFEST.json').write_text(json.dumps({'at':now,'files':manifest,'handoff_snapshot':str(rev.relative_to(S))},ensure_ascii=False,indent=2)+'\n')
print('diagnostic report and hand-off closed:',now)
