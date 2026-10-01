"""Create documentation snapshot only; never imports training/evaluation entrypoints."""
import datetime,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=Path(__file__).resolve().parents[1]
OUT=Path('/tmp/gmr-diagnostic-publication-20261001');PREFIX=Path('experiments/correspondence_generalization');P=OUT/PREFIX/S.name;P.mkdir(parents=True,exist_ok=True)
D=S/'DETAILS';D.mkdir(exist_ok=True);now=datetime.datetime.now().astimezone().isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fence(x):return '```json\n'+json.dumps(x,ensure_ascii=False,indent=2)+'\n```\n'
def demote(t):return re.sub(r'^(#{1,5}) ',r'##\1 ',t,flags=re.M)
def embed(p):
 text=p.read_text();base=p.parent
 def sub(m):
  label,link=m.groups()
  if link.startswith(('http','app:','#')):return m.group(0)
  target=(base/link).resolve()
  try:relative=target.relative_to(S.resolve());return '['+label+']('+str(relative)+')'
  except ValueError:return m.group(0)
 return demote(re.sub(r'\[([^\]]+)\]\(([^)]+)\)',sub,text))
runs={'throw/baseline':ROOT/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1','throw/adapter':ROOT/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_adapter_s3407_attempt1','open_close/baseline':S/'runs/open_close_qd_gmr_baseline_s3407_attempt1','sit/baseline':S/'runs/sit_qd_gmr_baseline_s3407_attempt1'}
book='''# 存在与定位共同泛化：完整实验与发现记录

整理日期：'''+now+'''

本文件汇总2026年9月30日阶段及随后授权的全部诊断，关联前序六组正式实验。它是已执行事实的归档，不是新训练指令。主文保留各轮完整解释；[DETAILS](DETAILS/README.md)包含全部汇总指标、冻结定义、超参和逐epoch账本，原JSON、源码和日志随文发布。原checkpoint、特征和大型逐query张量不放入Git，路径/来源/hash与未上传范围均在发布清单列明；不能把文档包称为包含原视频或全部模型资产。

## 阅读导航

1. 研究问题、最终发现和总目标。
2. 实验全集、数据与训练账本。
3. 第一阶段六组正式参照。
4. 三族D0/D3/D1/D2机制诊断。
5. 固定模型定位与存在读出。
6. 候选rank、foreground与时间窗几何。
7. 候选支持桥接与普通控制。
8. 早期时序表示、容量一致探针与池化敏感性。
9. 失败、完整性、未运行项与贡献边界。
10. 详细指标、定义、源码与原资产入口。

## 1. 问题真正收缩到了什么

冻结总体目标是未见存在AUROC与raw R1@0.5共同改善，官方gated为关键最终指标，seen小幅不劣、FRR/RR无明显恶化；独立正例VTG用于界定迁移范围。没有任何后续诊断改变这些成功标准。

本阶段的证据链：普通adapter在独立VTG有定位收益、GMR未获共同收益 → raw错误与候选缺失/排序并存 → 原存在分数不是候选质量 → foreground同query排序不等于跨query存在 → 保存候选几何一致性的冻结支持公式被拒绝 → 早期时序表示还需区分GT条件局部证据与无GT绝对支持。

最新问题是：**怎样在无GT条件下选出局部视频—文本证据，再聚合成跨查询、跨未见语义可比较的绝对支持？** 小读出器未证明只修原存在头即可恢复，线性失败也未证明表示完全无信息。GT已知时window probe在三个pseudo族的条件均值AUROC为.6241/.6078/.6726；固定实际文本后只有open_close保留有限局部证据（query等权PairAcc=.5646 [.5339,.6263]）。相同读出的无GT全视频mean/max等权AUROC仅.5686/.5402。时间归一化的相对最高和跨query绝对存在必须分开。

既有候选一致性公式失败不否定全部局部支持机制。新的绝对支持场只是待设计训练候选：原S+要求GT窗内存在高支持、原S−要求整段低支持，不把S+窗外全标负。这里没有训练该目标，没有新算法共同成功；损失冲突、纯标尺问题、确定表示缺失均未获因果证明。

## 2. 实验全集与记账

|编号|实际工作|模型训练/拟合|结果状态与解释|
|---|---|---|---|
|H0|前序A1/QD三方法×GMR/VTG六组|六组各100轮，seed3407|正式已完成；VTG adapter收益没有成为GMR共同收益|
|T1|严格throw开发baseline/adapter|复用各100轮原模型|非本阶段新训练，best索引99/13|
|T2|open_close留族baseline|本阶段100轮，29000更新|best49/latest99，完成|
|T3|sit留族baseline|77轮账本，33649更新后用户停止|best11/latest76；补评测不等于补训练|
|D0/D3|来源/覆盖、错误分解、best/latest、gate审计|原模型更新0|三baseline与throw adapter完成|
|D1|固定实际文本、跨/同视频排序、遮蔽/乱序/分支屏蔽|原模型更新0，冻结前向|输入敏感性不能当反事实正确率|
|D2|exist/loc局部梯度，交集/full-block审计|autograd.grad，optimizer.step=0|稳定跨族冲突进入线未达到|
|R1|固定读出精度和定位质量关系|原模型更新0，冻结前向|原生logit无一致恢复；存在不是定位质量|
|C1|候选rank/topK、分数与IoU、几何|训练/新增前向0|4878 S+；排序与缺失并存|
|B1|foreground/几何/乘积/标量控制|训练/新增前向0|7345 query；冻结primary共同退化|
|P1|early/memory/decoder/text/video/window六种仿射probe×三族|原模型更新0；18次257参数拟合|拟合系数4626，冻结前向28370条query呈现|
|P2|GT均值敏感性与同句条件证据|新增拟合0/前向0|主结果后追加探索，独立记录冻结与核验范围|

模型epoch在checkpoint/selection里0起始，账本epoch是1起始。Sit停止时旧交接记seen评测完成76轮，后来status字段记77；二者均保留，不据字段差异伪造完成。本记录确认的是77条训练epoch账本、best11/latest76及独立补评测产物，不补训练、不改旧账本。

### 2.1 训练来源、配置、选择、运行成本

'''
configs='# 全部训练配置、超参与来源\n\n原记录快照；旧路径保留以追溯，不是恢复训练命令。\n'
epochs='# 逐轮训练账本\n\n账本epoch为1起始，checkpoint编号为0起始；记录原更新数、loss、时间与显存。未启用budget_audit的字段为null，不声称成对曝光或同预算核验。\n'
for name,run in runs.items():
 status=json.loads((run/'status.json').read_text());selection=json.loads((run/'selection.json').read_text());prov=json.loads((run/'provenance.json').read_text());config=prov['config'];rel=run.relative_to(ROOT)
 book+='\n#### '+name+'\n\n来源：`'+str(rel)+'`。配置/来源：[TRAINING_CONFIGS](DETAILS/TRAINING_CONFIGS.md)；原逐轮记录：[EPOCHS](DETAILS/EPOCHS.md)。\n\n'+f"状态={status['state']}；训练账本={status['epoch']}轮，更新={status['updates_total']}；best={selection['epoch']}（0-based），选择指标={selection['score_name']}，score={selection['score']}。\n"
 configs+='\n## '+name+'\n\n'+fence({'status':status,'selection':selection,'provenance':{k:v for k,v in prov.items() if k!='assets_sha256'},'config':config,'asset_hash_count':len(prov.get('assets_sha256',{})),'source_path':str(rel),'provenance_sha256':sha(run/'provenance.json')})
 es=[json.loads(t) for t in (run/'epochs.jsonl').read_text().splitlines()];assert len(es)==status['epoch'];assert [x['epoch'] for x in es]==list(range(1,len(es)+1))
 epochs+='\n## '+name+'\n\n|epoch|updates|rows|loss|训练秒|GPU峰值bytes|budget审计|\n|---:|---:|---:|---:|---:|---:|---|\n'
 for x in es:epochs+='|'+ '|'.join(str(x.get(k)) for k in ['epoch','updates','rows','loss','train_wall_seconds','gpu_peak_bytes','budget_audit_enabled'])+'|\n'
 epochs+='\n原账本逐行JSON：\n\n```jsonl\n'+(run/'epochs.jsonl').read_text()+'```\n'
(D/'TRAINING_CONFIGS.md').write_text(configs);(D/'EPOCHS.md').write_text(epochs)
book+='''
### 2.2 数据隔离与覆盖

原A1 S训练行、原标签和已有特征只读。Throw严格词形throw/toss/hurl/fling/lob审计排除5个额外视频、8条原训练行；strict train7559、pseudo570、seen1185。Open_close按open/close/shut及词形，sit按sit/seat及词形，排除包含该族标注或词形的整个训练视频。保留原行字节，不新增query/absence，不声称预训练未见语义或完整概念隔离。Seen可能与训练共享原视频；train与pseudo视频隔离。三个pseudo族共享原视频（throw–open_close62、throw–sit24、open_close–sit81），不能当独立重复试验。

'''
freeze=json.loads((S/'temporal_representation_analysis/FREEZE.json').read_text())
book+='|族/split|行|S+|S−|视频|\n|---|---:|---:|---:|---:|\n'
for g,c in freeze['coverage'].items():book+=f"|{g}|{c['rows']}|{c['positive']}|{c['negative']}|{c['videos']}|\n"
protocols='# 冻结定义与完整执行协议\n\n历史方案描述与后续停止状态分别保留；未来矩阵不代表执行事实。\n'
for p in [S/'plan/EXPERIMENT_PLAN.md',S/'plan/NEXT_TASK.md']:
 protocols+='\n## '+str(p.relative_to(S))+'\n\n'+demote(p.read_text())
for p in [S/'plan/EXECUTION_CONFIG.json',S/'views/open_close/view_manifest.json',S/'views/sit/view_manifest.json',ROOT/'runs/pseudo_unseen_a1_throw_strict/view_manifest.json']+[S/a/'FREEZE.json' for a in ['readout_analysis','candidate_geometry_analysis','support_bridge_analysis','temporal_representation_analysis']]+[S/'temporal_representation_analysis/PROBE_FITS.json',S/'temporal_representation_analysis/POOLING_ROBUSTNESS_FREEZE.json',S/'temporal_representation_analysis/CONDITIONAL_SUPPORT_FREEZE.json']:
 obj=json.loads(p.read_text());excluded={k:len(v) if hasattr(v,'__len__') else v for k,v in obj.items() if k in ['protected_files_sha256','feature_assets','protected_files','inputs_sha256']};obj={k:v for k,v in obj.items() if k not in excluded};protocols+='\n## '+str(p.relative_to(ROOT))+'\n\n'+fence(obj)
 if excluded:protocols+='\n大型逐资产hash表不重复展开，完整原JSON随文发布；省略表的字段/数量：'+str(excluded)+'。\n'
(D/'PROTOCOLS.md').write_text(protocols)
# Preserve every statistic, including geometry quantiles/flags/denominators and all fit/control results.
metric_files=[]
for folder in ['readout_analysis','candidate_geometry_analysis','support_bridge_analysis','temporal_representation_analysis']:
 parts=[]
 names={'RESULTS.json','GEOMETRY_CONTRASTS.json','ATTRIBUTION.json','COVERAGE.json','TEXT_INPUT_DIFFERENCES.json','POOLING_ROBUSTNESS.json','CONDITIONAL_SUPPORT.json'}
 for p in sorted((S/folder).iterdir()):
  if p.name in names:
   obj=json.loads(p.read_text());parts.append('\n## '+p.name+'\n\n完整机器可读结构如下。NA、有效次数、分母和辅助指标保留，不用缺值补.5。\n\n'+fence(obj))
 (D/(folder.upper()+'.md')).write_text('# '+folder+'：全部指标与覆盖\n'+''.join(parts));metric_files.append(folder.upper()+'.md')
# Large result appendix split by existing independent source to keep files readable.
main_reports=[('3. 前序六组正式实验（历史证据，不在本轮重跑）',ROOT/'2026年9月30日_正则化与残差适配的未见动作泛化实验/EXPERIMENT_RECORD.md'),('4. 多语义族机制诊断',S/'report/DIAGNOSTIC_REPORT.md'),('5. 固定模型定位与存在读出',S/'readout_analysis/REPORT.md'),('6. 候选rank、foreground与窗几何',S/'candidate_geometry_analysis/REPORT.md'),('7. 候选支持桥接与全部普通控制',S/'support_bridge_analysis/REPORT.md'),('8. 早期时序表示、容量一致读出与条件证据',S/'temporal_representation_analysis/REPORT.md')]
for title,p in main_reports:
 book+='\n## '+title+'\n\n'
 if p.is_relative_to(S):book+=embed(p)
 else:
  book+='原完整历史记录：[第一阶段EXPERIMENT_RECORD](../'+p.parent.name+'/EXPERIMENT_RECORD.md)。以下保留正文；其evidence链接以该原记录目录为基准。\n\n'+demote(p.read_text())
book+='''
## 9. 失败、完整性与未运行项

|记录|实际发生|处理与结果|
|---|---|---|
|support_bridge_analysis_failures/attempt_001|NumPy bool JSON序列化失败|保留失败产物，修序列化后重算；冻结公式/统计定义未改|
|temporal_representation_failures/attempt_001_import|不必要的评估模块import引入standalone_eval依赖失败|发生在前向和probe拟合前；直接import原vendor数据集后成功，定义不变|
|temporal_representation_failures/attempt_002_verifier_io|独立核验每行重复解压，主动SIGTERM结束慢核验|每组缓存一次重启核验；主分析未重跑，统计定义未改|
|sit原训练停止|用户主动结束77轮运行|保持stopped_by_user，保留best/latest和补评测，不是失败后自动重训|

原三族补评测、读出、候选、支持桥接及表示诊断均保留各自独立state/log/冻结。候选/支持桥接/表示的独立核验通过；原资产保护路径分别117/2219/18230，固定读出81；模型tensor前后hash相同。早期表示独立核验对主memory/original全部1000次bootstrap作复核，其他读出检查点值与抽样replicate；追加条件PairAcc独立重算全部点值，区间未另完整复算，其验证范围在CONDITIONAL_SUPPORT_VALIDATION中明确。不能将“核验通过”扩大为每项都做了第二次完整bootstrap。

PCGrad、损失重权、绝对支持场全模型训练、IoU质量头/边界干预、教师/window、多seed、同预算核验、75组、正式U确认、重跑第一阶段六组、sit补训练均未运行。旧queue/followup历史状态保持停止；后来补评测是独立新授权，不改历史取消状态。

冻结共同门槛：AUROC及raw增益各双侧97.5%共同视频paired区间为正；gated点增益为正、95%下界≥−.01；seen AUROC/raw/gated允许下降.01；FRR增≤.03、RR降≤.03、raw-correct误拒增≤.05，分母<30低覆盖。跨界记不确定，探索95%不能替代正式共同通过；现有probe/条件GT诊断没有新gated/FRR/RR，也未验证独立VTG。

RaTSG和Learning to Refuse的局部相关性/视频存在/拒绝已有先例，不能声称首次使用局部证据判断存在。可能贡献仅能紧扣下游未见语义上的可迁移绝对支持与共同定位，需未来实证；目前是负结果与可读性机制诊断。

## 10. 所有细节与复现入口

- [训练完整配置](DETAILS/TRAINING_CONFIGS.md)、[逐epoch账本](DETAILS/EPOCHS.md)、[执行协议和定义](DETAILS/PROTOCOLS.md)。
- [固定读出全部指标](DETAILS/READOUT_ANALYSIS.md)、[候选几何全部指标](DETAILS/CANDIDATE_GEOMETRY_ANALYSIS.md)、[支持桥接全部指标](DETAILS/SUPPORT_BRIDGE_ANALYSIS.md)、[时序表示全部指标](DETAILS/TEMPORAL_REPRESENTATION_ANALYSIS.md)。
- [源码](code/)、[训练与补评测日志](logs/)、各analysis中的结果JSON/验证/状态和失败目录。
- [发布内容清单](PUBLICATION_MANIFEST.json)、[原本地资产清单](DETAILS/LOCAL_ASSET_INDEX.json)。未上传的模型/特征/逐query大数组不表示不存在，原本地目录保留。

本文合并历史报告，旧“下一步”属于当时建议。以本记录开头的最新结论及当前交接为准；没有自动继续训练的任务。
'''
(S/'EXPERIMENT_RECORD.md').write_text(book)
(D/'README.md').write_text('# 全部实验细节\n\n主入口：[完整实验记录](../EXPERIMENT_RECORD.md)。\n\n'+ '\n'.join('- ['+n+']('+n+')' for n in ['TRAINING_CONFIGS.md','EPOCHS.md','PROTOCOLS.md']+metric_files)+'\n')
# Snapshot text evidence; no checkpoint/features/large query outputs or accidental parent dirty files.
selected=[];excluded=[]
for p in S.rglob('*'):
 if not p.is_file() or p.is_symlink():continue
 rel=p.relative_to(S)
 if any(x in ['__pycache__','.git'] for x in rel.parts):continue
 include=p.suffix in ['.md','.json','.py','.txt','.log','.csv','.png','.pdf'] or p.name=='epochs.jsonl'
 if include:
  target=P/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);selected.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':sha(p)})
 else:excluded.append({'path':str(rel),'bytes':p.stat().st_size,'reason':'local original model/features/per-query arrays/row files; documentation-only publication'})
# Reused development runs are external to this stage; keep only configs/status/epochs/thresholds, not train/predictions.
for name,run in runs.items():
 if run.is_relative_to(S):continue
 for n in ['status.json','selection.json','provenance.json','result.json','epochs.jsonl','threshold_frozen.json','calibration_frozen.json','budget.json']:
  p=run/n
  if p.exists():target=OUT/PREFIX/run.relative_to(ROOT)/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
for p in [ROOT/'runs/pseudo_unseen_a1_throw_strict/view_manifest.json',ROOT/'code/queue_worker.py',ROOT/'code/methods.py']:
 target=OUT/PREFIX/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
# Local source metadata references not copied are explicitly distinguished from published files.
index={'stage':str(S),'generated_at':now,'excluded_from_github':excluded,'reused_runs':{k:str(v) for k,v in runs.items()},'hash_sources':['temporal_representation_analysis/FREEZE.json','temporal_representation_analysis/ARTIFACT_MANIFEST.json','candidate_geometry_analysis/FREEZE.json','support_bridge_analysis/FREEZE.json'],'note':'full original protected hashes in published JSON; excluded large artifacts remain local; no new compute'}
(D/'LOCAL_ASSET_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');shutil.copy2(D/'LOCAL_ASSET_INDEX.json',P/'DETAILS/LOCAL_ASSET_INDEX.json')
# Reference first-stage existing published file through its stable repo URL when embedding old local-relative links.
p=P/'EXPERIMENT_RECORD.md';t=p.read_text();start=t.index('## 3. 前序');end=t.index('## 4. 多语义');section=t[start:end];first=ROOT/'2026年9月30日_正则化与残差适配的未见动作泛化实验'
def historical(m):
 label,link=m.groups()
 if link.startswith(('http','#')):return m.group(0)
 resolved=(first/link).resolve()
 try:rp=resolved.relative_to(ROOT.resolve());return '['+label+'](https://github.com/chinagalaxy2002/GMR_Unseen/blob/main/'+str(PREFIX/rp)+')'
 except ValueError:return m.group(0)
section=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',historical,section);t=t[:start]+section+t[end:];p.write_text(t);(S/'EXPERIMENT_RECORD.md').write_text(t)
# Front-door link added without editing root research plan or old metrics.
readme=(S/'README.md').read_text();entry='\n## 全阶段完整实验归档\n\n[EXPERIMENT_RECORD.md](EXPERIMENT_RECORD.md)汇总全部已执行实验、发现、失败与解释边界；[DETAILS](DETAILS/README.md)保存所有汇总指标、协议、配置和逐轮账本。\n'
if '## 全阶段完整实验归档' not in readme:readme+=entry;(S/'README.md').write_text(readme)
(P/'README.md').write_text(readme)
# A supplementary diagnostics appendix retains every original diagnostic summary JSON.
diag=[]
for q in sorted((S/'diagnostics').rglob('*.json')):
 if q.name=='provenance.json' or 'evaluation_bundle' in str(q) or 'latest_predictions' in str(q):continue
 diag.append('\n## '+str(q.relative_to(S))+'\n\n'+fence(json.loads(q.read_text())))
(D/'MECHANISM_DIAGNOSTIC_DETAILS.md').write_text('# D0/D3/D1/D2全部诊断记录\n'+''.join(diag));shutil.copy2(D/'MECHANISM_DIAGNOSTIC_DETAILS.md',P/'DETAILS/MECHANISM_DIAGNOSTIC_DETAILS.md')
# Files are exact text snapshots except the new synthesized record and original readme entry.
files=[]
for p in sorted(OUT.rglob('*')):
 if p.is_file():files.append({'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'at':now,'repository':'chinagalaxy2002/GMR_Unseen','branch':'main','scope':'all performed stage experiments and diagnostics; historical first-stage record included and linked','documentation_only':True,'training_or_analysis_reruns':0,'files':files,'large_original_assets_remain_local':True,'raw_data_note':'source rows/checkpoints/features/per-time query arrays are indexed rather than uploaded','history_status_caveat':'sit seen-evaluation count fields differ;77 train ledger and best11/latest76 preserved'}
(S/'PUBLICATION_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');shutil.copy2(S/'PUBLICATION_MANIFEST.json',P/'PUBLICATION_MANIFEST.json')
print(json.dumps({'files':len(files)+1,'bytes':sum(x['bytes'] for x in files),'record_bytes':(S/'EXPERIMENT_RECORD.md').stat().st_size,'output':str(OUT),'excluded_large_files':len(excluded)},ensure_ascii=False))
