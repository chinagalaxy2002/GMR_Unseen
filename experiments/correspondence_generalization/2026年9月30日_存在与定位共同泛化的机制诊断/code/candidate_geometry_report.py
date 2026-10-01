"""Render completed candidate results and close out authorized documentation."""
import json,datetime,hashlib,shutil,subprocess
from pathlib import Path
S=Path(__file__).resolve().parents[1];D=S/'candidate_geometry_analysis';ROOT=S.parent
r=json.loads((D/'RESULTS.json').read_text());c=json.loads((D/'GEOMETRY_CONTRASTS.json').read_text());integ=json.loads((D/'INTEGRITY.json').read_text());stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def ci(x):
 if x['point'] is None:return 'NA'
 return f"{x['point']:.4f} [{x['ci95'][0]:.4f}, {x['ci95'][1]:.4f}]" if x['ci95'] else f"{x['point']:.4f} [NA]"
def metric(group,key,mode='video_equal'):return r['groups'][group]['metrics'][key][mode]
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,x))+' |' for x in rows])+'\n\n'
text=f'''# 零训练候选排序、置信度与时间窗几何诊断

完成：{stamp}。六组（three baseline seen-only best × seen/pseudo），4878条S+，原视频联合集2302个。新增训练、参数更新、模型前向均为0；正式真实U/test未读取。Throw/open_close完成100轮；sit保持用户停止、77轮账本、best 11/latest 76，不视作同预算100轮证据。

证据支持**分类排序缺口与窗几何缺失并存**，但两者与存在判别的共同机制仍未决。同query的二元正确/错误候选有可辨排序信号，不能据此把现有foreground称为连续定位质量分数，也不能承诺可学出oracle。GT依赖覆盖不是实际reranker性能或共同成功。没有方法比较，没有通过AUROC/raw联合门槛的声明。

## 冻结、聚合与复现

FREEZE.json在结果计算前保存输入路径、SHA256、qid/vid覆盖、指标与实现hash。该分析是在看过前轮结果后选择的探索分析。原raw列表顺序定义rank，四位小数score ties不重排；仅使用窗附带score，native decoder-slot概率未读取或拼接。GT最大IoU并列取原GT列表第一项；最高IoU候选并列取原rank第一项。最大IoU=0时几何匹配仍遵循同一规则，不能解释为语义对应的证据。

主要诊断聚合为每query摘要→视频内可用query均值→可用视频等权；同时保存query等权统计以复现旧指标。三族汇总等权，不按query数、视频数或pair数加权。以下区间均为共同原视频联合bootstrap 1000次、seed3407、探索性95%百分位区间，所有六组复用同一组乘数。零分母replicate为NA，并列在PairAcc中计.5；Spearman采用平均ties秩，score/IoU零方差不可用。分位数描述query分布，没有后验切点；连续均值区间使用视频聚合。候选/pair不是独立抽样单位。

六组K=1与原raw、K=10与旧任一候选oracle逐组精确复现，top1/oracle IoU还逐query匹配前轮。两个IoU阈值的rank质量守恒、三类错误分解、候选顺序/坐标、qid/vid均通过核验。独立验证器用显式pair枚举、平均秩Pearson重算Spearman、另写IoU公式、边界代数和共享bootstrap复核，4878条全部通过。{integ['protected_files']}个原保护资产hash未变。冻结输入没有修改原指标、阈值、gate、checkpoint、账本、停止队列和旧结果。

## 1. 覆盖与正确候选rank

所有输入query均有10个候选；不足10或空候选为0。GT非正长度、非正视频duration均为0。统计只在原S+ GT上进行，不创建任何新absence标签。

'''
text+=table(['组','S+ query/video','混合正误候选 query/video','组合pair数（非独立）','相关不可用query'],[[g,f"{b['coverage']['positive_queries']}/{b['coverage']['positive_videos']}",f"{b['coverage']['mixed_candidate_queries']}/{b['coverage']['mixed_candidate_videos']}",b['coverage']['candidate_pairs'],b['coverage']['unavailable_spearman_queries']] for g,b in r['groups'].items()])
text+='原query等权覆盖，用于与旧raw/oracle对照；数值为百分比，非实际无GT方法性能。\n\n'
text+=table(['组','IoU','K1','K2','K3','K5','K10'],[[g,t]+[f"{100*metric(g,f'R_at_{k}_iou_{t}','query_equal')['point']:.2f}" for k in [1,2,3,5,10]] for g in r['groups'] for t in [.5,.7]])
text+='主要视频等权覆盖及探索性95%区间：\n\n'
text+=table(['组','IoU','K1','K2','K3','K5','K10'],[[g,t]+[ci(metric(g,f'R_at_{k}_iou_{t}')) for k in [1,2,3,5,10]] for g in r['groups'] for t in [.5,.7]])
text+='K=1→K=2/3/5的新增覆盖（视频等权，百分点换算请乘100）：\n\n'
text+=table(['组','IoU','ΔK2','ΔK3','ΔK5'],[[g,t]+[ci(metric(g,f'gain_K{k}_minus_K1_iou_{t}')) for k in [2,3,5]] for g in r['groups'] for t in [.5,.7]])
rows=[json.loads(x) for x in (D/'CANDIDATE_ROWS.jsonl').read_text().splitlines()]
text+='第一正确rank原始query计数；无正确候选单列，分母是上表S+数。视频等权rank质量与区间完整保存在RESULTS.json。\n\n'
text+=table(['组','IoU']+[str(k) for k in range(1,11)]+['无正确'],[[g,t]+[sum(x['first_correct_rank'][str(t)]==k for x in rows if x['family']+'/'+x['split']==g) for k in range(1,11)]+[sum(x['first_correct_rank'][str(t)] is None for x in rows if x['family']+'/'+x['split']==g)] for g in r['groups'] for t in [.5,.7]])
text+='等权族pseudo汇总（video等权）：\n\n'
text+=table(['指标','点与95%区间'],[[k,ci(r['equal_family']['pseudo'][k]['video_equal'])] for k in ['R_at_1_iou_0.5','R_at_2_iou_0.5','R_at_3_iou_0.5','R_at_5_iou_0.5','R_at_10_iou_0.5','category_ranking_error','category_candidate_miss']])
text+='旧口径query等权族pseudo K1=29.36%、K10=70.60%、排序错误=41.23%、候选缺失=29.40%，本次精确复现。主要视频等权口径不同，不能用新口径替换原raw主要终点。三族排序缺口均明显，前5候选已覆盖大部分任一候选覆盖，但余下候选缺失仍无法靠现有集合重排消除。\n\n## 2. 同query内分类分数与IoU\n\n'
text+=table(['组','PairAcc（混合query）','Spearman（可用S+）','Spearman（混合）','混合正误pair score tie率','top1−最高IoU score'],[[g]+[ci(metric(g,k)) for k in ['PairAcc','spearman_score_iou','mixed_spearman_score_iou','mixed_pair_score_tie_rate','top1_minus_oracle_score']] for g in r['groups']])
text+=table(['组','score零方差query','IoU零方差query','有score ties query','相关不可用比例','gap p25/50/75'],[[g]+[sum(x[k] for x in rows if x['family']+'/'+x['split']==g) for k in ['score_zero_variance','iou_zero_variance','any_score_tie']]+[f"{metric(g,'spearman_unavailable_fraction','query_equal')['point']:.4f}",'/'.join(f'{v:.4f}' for v in r['geometry_query_distributions'][g]['top1_minus_oracle_score']['quantiles_p05_p25_p50_p75_p95'][1:4])] for g in r['groups']])
text+=f'''Pseudo等权族PairAcc={ci(r['equal_family']['pseudo']['PairAcc']['video_equal'])}。三个族seen/pseudo的PairAcc区间均高于.5，支持当前混合候选集合内有限的二元排序信号；它是每query正确候选与错误候选比较的均值，不是top1命中率，也不代表所有IoU取值都单调对应分数。连续相关性跨族不一致，open_close pseudo混合query Spearman略负，sit接近0，throw小正；不能把三族二元PairAcc支持扩写为稳定的连续质量排序。四位小数并列比例已显式计入，不补native映射，不用存在分数充当候选质量。

## 3. 窗几何：三类错误、长度、位置和边界

分类固定：top1正确（IoU≥.5）；排序错误（top1<.5且任一≥.5）；候选缺失（全部<.5）。每个窗匹配自身最大IoU的原GT；最高IoU窗是诊断oracle，不能用于无GT排序。GT匹配并列候选共0，oracle候选并列仅来自IoU完全相同的query（逐组见COVERAGE）；规则保持第一rank。

以下表是视频等权均值。中心绝对误差、起止误差以GT长度归一化；起止误差为pred−GT，负值为偏早，正值为偏晚。GT位置为中心/视频duration。完整秒误差、预测窗长度/位置、均值区间及p05/p25/p50/p75/p95在RESULTS的geometry_query_distributions与GEOMETRY_CONTRASTS中；不存在仅报告被挑选切点的问题。

'''
geomkeys=['gt_length_seconds','gt_center_video_fraction','abs_center_error_over_gt_length','prediction_gt_length_ratio','start_error_over_gt_length','end_error_over_gt_length','max_iou']
text+=table(['组','类','窗','GT秒','GT位置','|中心误差|/GT长','pred/GT长','起误差/GT长','止误差/GT长','IoU'],[[g,typ,w]+[f"{metric(g,typ+'/'+w+'/'+k)['point']:.3f}" for k in geomkeys] for g in r['groups'] for typ in ['top1_correct','ranking_error','candidate_miss'] for w in ['top1','oracle']])
text+='候选缺失−排序错误的主要几何描述差值（video等权；两类为不同输出分组，不能作因果差值）：\n\n'
text+=table(['组','GT秒差','oracle长度比差','oracle中心误差比差','GT位置差'],[[g]+[ci(c[g][f'candidate_miss_minus_ranking_error/oracle/{k}']) for k in ['gt_length_seconds','prediction_gt_length_ratio','abs_center_error_over_gt_length','gt_center_video_fraction']] for g in r['groups']])
text+='三族seen/pseudo都呈现候选缺失组GT更短、最高IoU窗更长且偏移更大的描述性趋势。Pseudo缺失组oracle长度比2.48/2.33/3.06，排序错误组1.42/1.39/1.25；相对GT过宽、中心偏离共同出现，现有集合内仅重排不能修复缺失组。与排序错误组相比，pseudo缺失组GT中心更早，但seen与三族的具体早晚边界方向并不一致，不能拟定一个通用边界平移或时长缩放。GT长度分母会放大短窗归一化误差，短窗、语义、数据构成混杂尚未排除。最高IoU的选择本身条件化了几何表现，这些差异支持覆盖内几何缺口的描述，不能证明回归训练因果失效。\n\n'
text+='连续分布核查：以下为query p25 / p50 / p75（绝非视频均值）；含三类及两种窗。其余分位数与每项最小/最大值见RESULTS.json。\n\n'
text+=table(['组','类','窗','GT秒','|中心误差|/GT长','pred/GT长','起误差/GT长','止误差/GT长'],[[g,typ,w]+[' / '.join(f'{v:.3f}' for v in r['geometry_query_distributions'][g][typ+'/'+w+'/'+k]['quantiles_p05_p25_p50_p75_p95'][1:4]) for k in ['gt_length_seconds','abs_center_error_over_gt_length','prediction_gt_length_ratio','start_error_over_gt_length','end_error_over_gt_length']] for g in r['groups'] for typ in ['top1_correct','ranking_error','candidate_miss'] for w in ['top1','oracle']])
text+='## 4. Seen/pseudo、跨族一致性与不确定性\n\nSeen与pseudo query不相同，以下共同视频乘数只处理数据复用的统计依赖，不构成同样本paired因果变化。\n\n'
text+=table(['族','pseudo−seen K1','pseudo−seen K10','pseudo−seen PairAcc','pseudo−seen Spearman'],[[f]+[ci(r['pseudo_minus_seen_descriptive'][f][k]['video_equal']) for k in ['R_at_1_iou_0.5','R_at_10_iou_0.5','PairAcc','spearman_score_iou']] for f in ['throw','open_close','sit','equal_family']])
text+='Throw/open_close的pseudo K1、K10更低，sit K1方向相反且区间跨0；二元PairAcc在open_close pseudo反而更高，另两族差异不明确。不存在一致的“pseudo分类排序全面退化”证据。候选几何缺失与排序缺口在seen/pseudo均存在，具体泛化差值仍受族和query构成影响。Sit训练截断单列，不据三族比较宣称同预算稳健性。\n\n'
valid=[z for g in r['groups'].values() for x in g['metrics'].values() for z in [x['video_equal']['valid_resamples'],x['query_equal']['valid_resamples']]]
text+=f'''所有逐组主/辅助均值指标有效bootstrap次数均为{min(valid)}至{max(valid)}；零分母replicate没有出现。不可用query相关性为throw seen/pseudo 5/3、open_close 2/19、sit 0/0，均如实排除并报告覆盖；未填.5。共同原视频全集包含全部输入（S+及S−）视频，指标只使用各自可用S+视频，乘数仍共同。视频交集、每项query/video分母与不可用数见COVERAGE和RESULTS。组合pair仅用于query摘要计算，未作独立样本。

## 5. 决定与共同机制缺口

本次支持分类排序缺口与候选几何缺失并存；连续候选质量排序跨族可靠性有限。现有正确候选经常落在top2/top3，缺失组在短GT、过宽预测与偏移上有一致描述线索。尚不能识别二者各自的训练原因、可修复比例或与存在判别共享的支持机制，不预设存在损失冲突。

与总目标之间仍缺：无GT候选质量是否同时能区分S+与原S−；它是否提供超出语义/query难度的视觉条件证据；一个具体机制对AUROC和raw定位共同影响的路径及普通控制。当前S+内部候选诊断没有回答存在AUROC，也没有独立VTG迁移新证据。前轮存在分数与定位质量弱关联不能补上这些缺口。

原共同门槛保持：AUROC与raw主要增益使用97.5%共同视频paired区间，gated关键最终指标及seen/FRR/RR护栏不变；本次探索95%区间不作确认通过判定。决定维持不启动复杂干预、正式U确认或其他训练；本任务完成于诊断与决策。下一步训练范围、METHOD_SPEC和普通控制均未授权/未形成，不自动启动PCGrad、loss重权、质量头、教师/window、多seed、同预算核验、旧75组或补sit。

可复核：FREEZE.json、COVERAGE.json、CANDIDATE_ROWS.jsonl、RESULTS.json、GEOMETRY_CONTRASTS.json、BOOTSTRAP_WEIGHTS.npz、VALIDATION.json、INTEGRITY.json、state.json及EXECUTION.log。实现：../code/candidate_geometry_analyze.py；独立复核：../code/candidate_geometry_verify.py。原三族评测和readout分析没有重跑。
'''
(D/'REPORT.md').write_text(text)
summary=f'''\n## 已完成候选级零训练诊断（{stamp}）

见[候选报告](candidate_geometry_analysis/REPORT.md)。固定六组共4878条S+，只读已有窗/GT，新增训练、参数更新与前向均0；1000次seed3407共同原视频探索性95%bootstrap。K1/K10逐组复现原raw/oracle，独立计算核验通过，117个保护资产hash未变。

证据支持**分类排序缺口和窗几何缺失并存**，与存在/定位共同机制仍未决。Pseudo同query候选PairAcc三族.6645/.6984/.5821（视频等权），区间均高于.5；连续IoU关联较弱且跨族不一致。任一候选与top1差距明确，但oracle仍为GT依赖诊断。候选缺失组相对排序错误组GT更短，最高IoU窗过宽、中心偏移更大，seen/pseudo均有描述线索；具体边界方向及seen→pseudo排序变化不一致，不支持直接给出通用几何修复。

原query等权pseudo raw=29.36%、oracle=70.60%保持；主要诊断视频等权为29.89%/69.98%，口径不同不替换旧指标。S+内PairAcc不能证明S+/S−存在判别或因果损失冲突，也没有独立VTG迁移新证据。总目标、冻结门槛与gate保持，不宣称共同成功。继续不进入复杂干预/正式U确认；具体共同机制、METHOD_SPEC、普通控制及新训练范围仍未形成。此次NEXT_TASK已完成，没有自动续跑队列。
'''
with (S/'DECISION.md').open('a') as f:f.write(summary)
readme=(S/'README.md').read_text();readme=readme[:readme.index('## 清空上下文后的下一项')]+'''## 候选级零训练诊断已完成

[NEXT_TASK](plan/NEXT_TASK.md)已完成，见[候选报告](candidate_geometry_analysis/REPORT.md)、[结果](candidate_geometry_analysis/RESULTS.json)、[独立核验](candidate_geometry_analysis/VALIDATION.json)和[完整性](candidate_geometry_analysis/INTEGRITY.json)。证据支持分类排序缺口与窗几何缺失并存，共同机制仍未决；没有新训练或方法联合收益。117个保护资产hash未变。

最新状态见[交接](plan/HANDOFF.md)及[恢复说明](plan/RECOVERY_PROMPT.txt)。当前没有已授权待运行任务，旧队列继续停止。
''';(S/'README.md').write_text(readme)
with (S/'plan/progress.md').open('a') as f:f.write(summary.replace('(candidate_geometry_analysis/','(../candidate_geometry_analysis/'))
nextp=S/'plan/NEXT_TASK.md';nx=nextp.read_text();nx=nx.replace('状态：planned，尚未执行。用户要求准备交接与恢复后开展后续工作；复制RECOVERY_PROMPT.txt后，直接执行此限定零训练诊断，不恢复历史训练授权。',f'状态：completed，{stamp}。用户已明确授权并实际完成限定零训练诊断。结果见[REPORT](../candidate_geometry_analysis/REPORT.md)，独立核验及原资产hash通过。以下保留执行前任务定义；不作为重复运行或训练授权。');nextp.write_text(nx)
handoff=f'''# 上下文恢复交接：候选级诊断已完成

更新：{stamp}。最新限定NEXT_TASK已实际完成；当前没有已授权待运行任务，不重复已有评测/分析，不恢复旧训练。

总目标见[根计划](../../plan/EXPERIMENT_PLAN.md)：未见存在AUROC和raw R1@.5共同改善，gated为关键最终指标，seen小幅不劣、FRR/RR护栏保持；独立VTG界定迁移范围。原冻结门槛不变，探索性95%诊断不能替代97.5%共同主要增益检验。

## 完成状态

第一阶段六组、第二阶段三族评测/机制诊断、固定读出分析及[候选级诊断](../candidate_geometry_analysis/REPORT.md)均完成。Throw/open_close完成100轮；sit停止、77轮训练账本、best 11/latest76，未补训练、未伪造训练result。queue_state/followup_state仍stopped_by_user。

候选诊断只读取三族原seen-selected best的seen/pseudo预测及GT，六组4878 S+，新增训练/更新/前向0。2302原视频共同bootstrap，1000次seed3407；原顺序rank、IoU .5/.7、K1/2/3/5/10、query→video聚合已冻结。K1/K10及逐query原IoU复现；117保护资产hash未变，独立pair/相关/IoU/权重核验通过。没有native slot→保存window的索引拼接。

## 证据与决定

分类排序缺口和窗几何缺失并存。Pseudo同query PairAcc（video等权）throw/open_close/sit=.6645/.6984/.5821，探索95%区间均高于.5，但连续score–IoU相关性跨族不一致。缺失组GT更短、oracle过宽且中心偏移更大，seen/pseudo均有描述支持；具体边界方向和seen/pseudo排序差值不一致。

原query等权pseudo raw29.36%/oracle70.60%保持，新video等权诊断29.89%/69.98%不替换原主要终点。Oracle、GT匹配/rank不能进入真实无GT推理；不能承诺学出oracle，不预设损失冲突。S+内部候选分析没有证明存在判别的共同机制或独立VTG迁移，未形成METHOD_SPEC/普通控制/新训练范围。维持不进入复杂训练及正式U确认。

## 恢复阅读与资产

依次阅读根计划→本交接→[DECISION](../DECISION.md)最新追加→[候选REPORT](../candidate_geometry_analysis/REPORT.md)与RESULTS/VALIDATION/INTEGRITY→NEXT_TASK（完成版，保留冻结定义）→readout报告→progress/HANDOFF_STATUS。原历史交接在handoff_revisions等快照保留。

原资产基目录：throw为根runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1；open_close为阶段runs/open_close_qd_gmr_baseline_s3407_attempt1；sit为diagnostics/sit/baseline/evaluation_bundle（原checkpoint/views链接）。每组原pred_relevant_windows_pre_exist按score排序，native数组按slot顺序，不能无映射拼接。FREEZE内记录输入路径、hash、定义和代码hash。

新产物：candidate_geometry_analysis/FREEZE.json、COVERAGE.json、CANDIDATE_ROWS.jsonl、RESULTS.json、GEOMETRY_CONTRASTS.json、BOOTSTRAP_WEIGHTS.npz、REPORT.md、VALIDATION.json、INTEGRITY.json、state.json、EXECUTION.log。独立实现code/candidate_geometry_analyze.py已有输出防覆盖；不运行其main重做，查看保存产物即可。

## 后续边界

没有待执行训练或正式确认；新工作需明确新范围。不得启动旧run_phase2/run_followup/根launch_queue，不恢复75组、教师/window、多seed、同预算核验、第一阶段六组或sit训练。训练前共同机制、具体METHOD_SPEC和普通控制仍有缺口；不能用新增训练代替诊断证据。当前真实运行核对见candidate_geometry_analysis/RUNTIME_BEFORE.json与RUNTIME_AFTER.json，无本阶段实验进程及GPU计算任务；另有无关目录历史监控，未操作。
''';(S/'plan/HANDOFF.md').write_text(handoff)
(S/'plan/RECOVERY_PROMPT.txt').write_text('''请恢复当前阶段上下文，先阅读根plan/EXPERIMENT_PLAN.md、阶段plan/HANDOFF.md、DECISION.md最新追加、candidate_geometry_analysis/REPORT.md及RESULTS/VALIDATION/INTEGRITY、plan/NEXT_TASK.md（已完成）、progress/HANDOFF_STATUS。

工作根：/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/correspondence_generalization
阶段：2026年9月30日_存在与定位共同泛化的机制诊断

三族评测、机制诊断、读出分析、候选rank/置信度/几何诊断都已实际完成，不重复运行。候选诊断4878 S+，117保护资产未变，1000次seed3407共同视频探索95%区间，新增训练/参数更新/前向0。证据支持排序缺口与几何缺失并存；与存在判别的共同机制仍未决，不预设损失冲突，不将GT oracle当方法性能。

总目标仍是未见AUROC和raw R1@.5共同改善，gated关键最终指标及seen/FRR/RR护栏不变，独立VTG界定迁移。当前没有已授权待运行任务；根据用户明确的新范围继续，不自行训练或正式U确认。Throw/open_close100轮；sit停止77轮账本、best11/latest76，不补训练。不恢复旧队列/75组/教师/window/多seed/同预算或第一阶段六组。原窗口score序和native slot序没有映射，不能按索引拼接。下一步如涉及训练，仍缺共同机制、具体METHOD_SPEC及普通控制，不自动启动。
''')
status=json.loads((S/'plan/HANDOFF_STATUS.json').read_text());status.update(updated_at=stamp,candidate_geometry_analysis='completed',handoff_state='all_authorized_zero_training_diagnostics_completed',active_processes=False,training_restarted=False,parameter_updates=0,new_training_epochs=0)
status['next_task'].update(state='completed',entry_point='code/candidate_geometry_analyze.py (already executed; no overwrite)',result='candidate_geometry_analysis/REPORT.md',start_instruction='no pending authorized task; do not rerun')
status['candidate_geometry_summary']={'positive_queries':4878,'protected_files':117,'integrity':'passed','independent_validation':'passed','conclusion':'ranking and geometry coexist; joint existence/localization mechanism unresolved','bootstrap_original_video_union':2302,'new_forward_passes':0}
(S/'plan/HANDOFF_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
rootplan=ROOT/'plan/EXPERIMENT_PLAN.md';rp=rootplan.read_text();rp=rp.replace('下一项为[候选排序/置信度/几何诊断](../2026年9月30日_存在与定位共同泛化的机制诊断/plan/NEXT_TASK.md)，尚未执行；只分析保存模型与预测，继续为共同机制提供依据。','[候选排序/置信度/几何诊断](../2026年9月30日_存在与定位共同泛化的机制诊断/candidate_geometry_analysis/REPORT.md)也已完成：排序缺口与窗几何缺失并存，与存在判别的共同机制仍未决；当前无已授权待执行任务。');rootplan.write_text(rp)
log=S/'code/candidate_geometry_execution.log'
if log.exists():shutil.move(str(log),str(D/'EXECUTION.log'))
print('report and stage handoff updated')
