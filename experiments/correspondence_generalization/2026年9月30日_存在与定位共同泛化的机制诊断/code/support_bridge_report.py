"""Close out support-bridge research with evidence-driven conditional experiment decision."""
import datetime,hashlib,json,subprocess
from pathlib import Path
S=Path(__file__).resolve().parents[1];D=S/'support_bridge_analysis';ROOT=S.parent
r=json.loads((D/'RESULTS.json').read_text());v=json.loads((D/'VALIDATION.json').read_text());a=json.loads((D/'ATTRIBUTION.json').read_text());fs=json.loads((D/'TEXT_INPUT_DIFFERENCES.json').read_text());assert v['state']=='passed'
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def fmt(x):return 'NA (有效0/1000)' if x['point'] is None else f"{x['point']:.4f} [{x['ci'][0]:.4f}, {x['ci'][1]:.4f}]"
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])+'\n\n'
text=f'''# 下一步研究：候选支持是否连接存在与定位

完成：{stamp}。这是用户在候选诊断后授权继续研究、并在证据充分时新建实验阶段的下一步；原零训练候选任务没有被重跑。本次六组已有输出共7345 query（4878 S+、2467原S−），新增训练、参数更新、前向均0；正式U/test未读取。

**新发现：同query内foreground能排序正误窗，不代表跨query的事件存在证据。固定候选几何一致性也不能补上共同机制。** Primary的等权pseudo诊断AUROC较原存在读出下降.0558，raw R1@.5下降2.51个百分点；seen也退化。该具体共同支持假设被普通控制和现有数据否定，不进入新训练阶段。结论限于保存候选上的冻结公式，不宣布所有局部支持模型不可能、输入无信息或存在损失冲突成立。

## 1. 为什么选择这一步

前轮候选分析已证明排序缺口与候选缺失并存，但只分析S+，无法判断候选分数能否帮助存在AUROC。本次补上原S−，检验一个无新增参数、无需GT推理的具体共同路径，并以原foreground、纯几何及query标量几何控制区分信号来源。没有从oracle直接跳到训练，也没有后看结果搜索公式或系数。

原输入、原模型、原阈值和官方gate保留。诊断最大候选分数没有替换pred_exist_score，反事实rank仅作用于报告计算，不写回旧预测。因此没有新的官方gated、FRR/RR结果，更没有通过完整共同门槛的候选。原存在接受/拒绝与官方gated历史值仍原样有效，不能把raw选择变化解释为gate改进。

## 2. 计算前冻结的假设、普通控制与统计

窗口i的保存foreground为p_i；c_i为它与另外9个预测窗的平均temporal IoU（对角线排除，非GT IoU）。固定primary为s_i=p_i*c_i；存在诊断取max_i s_i，定位诊断取最高s_i的原窗。精确ties选择原列表第一rank。三项控制：p_i（原rank）、c_i（几何自身）、p_i*mean(c)（共享同一几何摘要，仅query标量，不改原候选rank）。总共4个事先冻结公式，没有拟合、重权扫描、阈值选择或新窗口。

共有2302原视频。1000次seed3407联合视频bootstrap的同一乘数用于所有族/split/readout，族汇总等权。全局AUROC和raw使用旧query等权目标并按视频聚类，S+候选PairAcc先query均值后video均值；同视频S+/S− PairAcc先每video汇总；同句跨video统计要求实际文本输入一致，按query组等权，端点乘数相乘。候选、pair和query组不作为独立抽样单位。基本区间是探索95%，另列共同主要读出差的97.5%辅助区间，不假装未见确认或种子稳健性。

单独冻结的“新研究进入证据”检查要求primary同时支持存在和raw、seen不劣、跨族与同文本视觉支持、优于纯几何普通控制；它是必要研究证据清单，不替换历史gated/FRR/RR完整成功门槛。条目失败则停止这个假设，不由更有利的族或后处理挽救。

首次计算在JSON序列化NumPy布尔值时失败，冻结/源码/日志完整保存在../support_bridge_analysis_failures/attempt_001；仅修正输出序列化后重算。独立核验确认两次冻结定义完全一致，没有修改公式或研究检查。执行源码内一个AUC检查字段历史命名误写30，实际是5读出×5权重=25/组；VALIDATION明确纠正且另按每组5读出全部1000权重独立复核。

## 3. Foreground的“相对排序”和“存在”证据分离

以下S+内部候选PairAcc为视频等权；存在AUROC为全部原S+/S−的query等权。它们是不同目标与不同覆盖，不将数值直接作为因果对比。

'''
text+=table(['组','原存在AUROC','max foreground存在AUROC','差值95%','S+内部foreground PairAcc'],[[g]+[fmt(b['metrics'][k]) for k in ['original_exist/existence_AUROC','foreground/existence_AUROC','foreground/existence_delta_vs_original','foreground/mixed_candidate_PairAcc_video_equal']] for g,b in r['groups'].items()])
text+='Pseudo等权foreground存在AUROC=.5037 [.4785,.5270]，相对原存在读出差−.0836 [−.1192,−.0552]；原等权存在AUROC=.5873。其S+内部候选PairAcc=.6483 [.6319,.6635]。因此已有候选foreground不能直接替代存在头或据此证明共用候选质量读出。它仍可能作为某个未来学习机制的一部分，但本次没有这一证据。\n\n## 4. 固定primary与全部普通控制\n\n'
text+=table(['组','读出','存在诊断AUROC 95%','raw R1@.5 95%','同视频S+/S− PairAcc 95%','混合候选PairAcc 95%'],[[g,k]+[fmt(b['metrics'][k+'/'+endpoint]) for endpoint in ['existence_AUROC','raw_R1_05','same_video_PairAcc_video_equal','mixed_candidate_PairAcc_video_equal']] for g,b in r['groups'].items() for k in ['foreground','agreement','foreground_agreement','scalar_geometry_control']])
text+='Primary对原读出的共同主要差值，辅助97.5%区间（探索、不作正式方法通过）：\n\n'
text+=table(['组','Δ存在AUROC','Δraw R1@.5'],[[g]+[fmt(b['metrics']['foreground_agreement/'+endpoint]) for endpoint in ['existence_delta_vs_original_975','raw_delta_vs_original_975']] for g,b in r['groups'].items()]+[['等权pseudo']+[fmt(r['equal_family']['pseudo']['foreground_agreement/'+k]) for k in ['existence_delta_vs_original_975','raw_delta_vs_original_975']],['等权seen']+[fmt(r['equal_family']['seen']['foreground_agreement/'+k]) for k in ['existence_delta_vs_original_975','raw_delta_vs_original_975']]])
text+='Pseudo等权primary AUROC=.5315、raw=26.85%；两项差值的97.5%区间均低于0。Throw pseudo小幅点升且两个区间均跨0，open_close/sit同时下降，不能挑throw宣布共同改善。Seen三族AUROC均下降，raw均下降，亦不支持seen小幅不劣。\n\n'
text+=table(['等权pseudo对照','Δ存在AUROC95%','Δraw95%'],[[k]+[fmt(r['equal_family']['pseudo']['primary_minus_'+k+'/'+ep]) for ep in ['existence_AUROC','raw_R1_05']] for k in ['foreground','agreement','scalar_geometry_control']])
text+='Primary虽然比纯geometry的raw更好，但不及原foreground；存在AUROC还不及query标量geometry控制。这不足以证明candidate-specific几何支持提供了所需共同信息。几何候选一致性可能反映重复/长度，而不是事实正确性；本次没有以这种可能解释代替实验证据。\n\n## 5. 排序改变的收益与损害归因\n\n'
text+=table(['组','读出','修复原raw错','破坏原raw对','净正确数','修复候选缺失'],[[g,k,z['repairs'],z['breaks'],z['net_correct_change'],z['repaired_candidate_misses']] for g,b in a.items() for k,z in b.items()])
text+='“修复−破坏”精确重构raw差值。原全部候选缺失的query无一能被这类集合内重排修复，候选几何缺失没有被隐藏。若以后研究更换候选生成/回归，只能形成新的假设和控制，本次不把该oracle差距认作可以实现的收益。分母、修复率/破坏率共同视频95%区间见ATTRIBUTION.json。\n\n## 6. 文本输入一致性、覆盖及未决项\n\n'
text+=table(['组','原S+/S−','原video数','同video混合数/pairs','同句混合组','实际文本完全一致组','同形状组','不同形状组'],[[g,f"{b['coverage']['positive']}/{b['coverage']['negative']}",b['coverage']['videos'],f"{b['coverage']['mixed_label_videos']}/{b['coverage']['same_video_pairs']}",b['coverage']['exact_query_label_mixed_groups'],b['coverage']['exact_feature_equal_groups'],fs[g]['shape_equal_groups'],fs[g]['shape_different_groups']] for g,b in r['groups'].items()])
text+='''所有同句混合组均未满足缓存文本输入完全一致（float32 last_hidden_state前32 token，norm+1e−5，与vendor相同，shape和数值均核对）。因此这次候选读出的同句视觉控制全部NA，有效bootstrap=0/1000，而不是填.5或标作视觉失败。原canonical存在头控制仍独立有效，本次不沿其存在分数拼接原窗口/slot score；它没有保存相同canonical输入下的完整候选，不能替代本项控制。原始同句特征不一致也不能证明视觉无信息或标签错误。

同形状输入的最大绝对归一化差值p0/p25/p50/p75/p100及每组shape核查见TEXT_INPUT_DIFFERENCES；不以容差放宽冻结的一致性条件。若一种未来候选出现共同改善，仍应保存新的canonical候选输出去补控制；本次primary已在共同读出和seen上失败，不追加无更新前向挽救它。

其余AUROC/raw/候选PairAcc/同视频统计均1000次有效；同句NA明确单列。低覆盖throw pseudo同视频只有32个混合视频、65pairs，组合数不当独立样本。跨族共享原视频、sit77轮截断及seen/pseudo构成差异，均限制推广性；不称为独立三次重复或同预算验证。

## 7. 是否足以新建训练实验阶段

'''
text+=table(['事先冻结的必要研究证据','结果'],[[k,'支持' if val else '未支持/无覆盖'] for k,val in r['entry_evidence_checks'].items()])
text+='结论：这一次共同候选支持假设证据不够，且primary在已观察数据上退化；**不新建训练阶段，不改旧训练代码，不恢复任何旧队列**。新增独立分析代码已经实际运行并核验，绝非只提方案。冻结结果仍支持“排序+几何问题并存”，但不支持简单的“slot预测一致就是真实证据”。\n\n'
text+='逐路径复核：\n\n'
text+=table(['路径','当前证据','决定'],[['直接把max foreground当存在分数','pseudo近随机且劣于原存在读出；raw不变','此直接读出拒绝'],['候选几何一致性/foreground×一致性','有普通控制；共同读出和seen退化','此冻结公式拒绝，不扫系数'],['IoU质量头或边界模型','已有近邻；S+定位质量证据不能说明原存在头如何共同受益','尚未形成可训练共同机制'],['PCGrad/固定损失重权','旧稳定共享块冲突未出现；本项没有新增因果证据','不恢复'],['保持预训练对应关系/教师','同维度不是共同空间；缓存仅token hidden，参考空间来源/可靠性未验证','不启用教师或旧window'],['共享的局部视觉支持','尚需无GT支持分数同时区分原S+/S−与定位，排除文本/长度偏置，并说明如何作用于原双头','保留研究问题，当前不因未决自动训练']])
text+='没有声称不存在其他可行方法。用户条件授权的“证据充分后新建目录并改代码做实验”在本次研究尚未触发；本次研究执行、独立核验与结果决策已完成。继续为总目标寻找机制需要一个不同于被拒绝公式的具体新问题，不能把追加训练作为默认下一步。\n\n## 8. 近邻文献核查与方法定位\n\n'
text+='候选质量排序、边界修正、query相互关系都已有先例，不能将它们或局部一致性本身写成创新。以下为本次核验的原始论文/作者仓库，不移用公开性能数字或把异任务结果当本项目证据。\n\n'
text+=table(['工作与作者/年份','已核验范围','与本次的区别'],[['[BAM-DETR](https://arxiv.org/abs/2312.00083)，Pilhyeon Lee、Hyeran Byun，ECCV2024','摘要：boundary-oriented formulation、双路径边界解码、质量排序','本次不改边界/网络；检验原S+/S−共同读出，不能以其正例TSG证明存在泛化'],['[RGTR](https://arxiv.org/abs/2406.00143)，Xiaolong Sun、Liushuai Shi、Le Wang等，AAAI2025（预印本2024）','摘要：region-guided anchors、多样性、IoU-aware scoring','本次只有已保存候选，无anchors/训练质量头；仅几何重复不等于真实支持'],['[Sim-DETR](https://arxiv.org/abs/2509.23867)，Jiajin Tang、Zhengxuan Wei等，ICCV2025','摘要：query关系注意力、query-to-frame alignment','本次非注意力/帧对齐；不能把该论文query冲突解释套成我方存在loss冲突'],['[Retrieving Any Relevant Moments](https://arxiv.org/abs/2605.02623)，Yiming Ding、Siyu Cao等，2026；[作者代码](https://github.com/dymm9977/generalized-moment-retrieval)','摘要：包含多/零相关窗的GMR、adapter及GRPO基线','本项目冻结Charades semantic开发族与原双头；异数据/异协议不能替代共同机制验证']])
text+='可复核产物：FREEZE、RESULTS、ROWS、COVERAGE、ATTRIBUTION、TEXT_FEATURE_AUDIT、TEXT_INPUT_DIFFERENCES、BOOTSTRAP_WEIGHTS、VALIDATION、INTEGRITY、state及执行日志。代码在../code/support_bridge_analyze.py、support_bridge_verify.py。输入SHA256保护2219个路径（包括缓存文本与原候选分析产物）；最终核验全部不变。\n'
(D/'REPORT.md').write_text(text)
evaltext=f'''# 候选共同支持方向评估

{stamp}。使用idea-evaluator，审查的是本次冻结的p_i×候选间平均IoU读出，而不是所有未来局部支持模型。

## 1. First impression

类型：共同存在/定位新设置中的方法假设，尚无新颖方法主张。一句话：检验已有候选的置信度与互相几何支持，能否无GT地同时服务存在判别和raw候选排序。原目标仍要求AUROC/raw共同改善、gated及seen/拒绝护栏，并用独立VTG界定迁移范围。

## 2. Fatal flaws

| 问题 | 严重性 | 证据 |
| --- | --- | --- |
| 冻结的核心共同支持机制被本项目数据与普通控制反驳（F6/data-refuted） | CRITICAL，仅限本实现 | 等权pseudo AUROC差−.0558、raw差−.0251；两项97.5%辅助区间均<0；seen双指标退化；primary还劣于保留原rank的标量控制 |

真实检索近邻：BAM-DETR（Lee/Byun，ECCV2024，边界与quality ranking），RGTR（Sun/Shi/Wang等，AAAI2025，region anchors/IoU scoring），Sim-DETR（Tang/Wei等，ICCV2025，query关系与frame alignment），GMR（Ding/Cao等，2026，多/零窗任务）。元信息和摘要经arXiv与作者仓库核验，完整链接见[REPORT](REPORT.md)。方法对象/机制与本诊断不同，不能据此声称绝对重复，也没有检索证明创新。

## 7. Verdict

**Reject and Pivot：停止这版候选几何一致性共同读出，不启动训练。** 按技能对data-refuted CRITICAL的短路规则，不再给五维高分或设计乐观挽救阈值。这不否定学习式视觉支持的全部可能，也不将原缓存同句控制不可用当作视觉否定。

已执行的动作：完成原S+/S−存在桥接及raw普通控制；独立重算所有7345条候选、全部1000视频权重的五读出AUC和修复/破坏归因；冻结拒绝该训练路线并保留共同机制未决。下一训练方案仍缺一个能作用于原存在/定位双头的机制与普通控制，不能只修定位或改变gate。
''';(D/'IDEA_EVALUATION.md').write_text(evaltext)
summary=f'''\n## 用户授权的下一步研究已完成（{stamp}）

见[支持桥接研究](support_bridge_analysis/REPORT.md)及[方向评估](support_bridge_analysis/IDEA_EVALUATION.md)。新增独立代码只分析7345条已有query/原S+/S−，未重跑旧评测，训练/更新/前向均0。完成固定foreground、候选几何一致性、二者乘积及query标量普通控制，1000次seed3407共同视频bootstrap。

新证据区分相对候选排序与存在：max foreground的pseudo等权AUROC=.5037，较原存在读出−.0836；S+内部PairAcc仍.6483。冻结primary p×平均预测窗IoU的等权pseudo AUROC=.5315（差−.0558，97.5%辅助区间[−.0934,−.0214]），raw=26.85%（差−2.51pp，[−4.20,−.69]pp），seen也退化，不能共同成功。保存候选内几何一致性不是已证实事实支持，该具体路线被拒绝，不扫系数挽救。

原缓存同句混合组没有实际文本完全一致组，本项候选视觉控制为NA而非.5；原canonical存在控制独立保留，不能拼接原候选替代。所有7345条候选/配对、完整bootstrap AUC及修复−破坏重构独立核验通过，2219保护路径hash未变。一项JSON序列化失败完整保留，两次冻结定义一致，修复未改统计口径。

按用户“发现充分才新建实验”的条件，**当前未触发新训练目录/训练代码修改**；实际下一步研究及拒绝决策已完成，继续保留存在/定位共同机制未决，不恢复旧队列、不正式U确认、不启用教师/window、多seed、同预算或补sit。冻结门槛、原gate/checkpoint/结果不变，独立VTG没有新迁移声明。
'''
with (S/'DECISION.md').open('a') as f:f.write(summary)
with (S/'plan/progress.md').open('a') as f:f.write(summary.replace('(support_bridge_analysis/','(../support_bridge_analysis/'))
readme=S/'README.md';readme.write_text(readme.read_text()+'''\n## 下一步共同支持研究已完成

用户随后授权继续研究、证据充分时另开实验。已实际完成[原S+/S−支持桥接与普通控制](support_bridge_analysis/REPORT.md)、[方向评估](support_bridge_analysis/IDEA_EVALUATION.md)和[独立核验](support_bridge_analysis/VALIDATION.json)。候选foreground的同query排序信号不能直接替代存在证据；冻结候选几何支持公式共同读出及seen退化，不触发新训练阶段。7345条输出，训练/更新/前向0；2219保护路径未变。共同机制继续未决。
''')
handoff=S/'plan/HANDOFF.md';hh=handoff.read_text();hh=hh.replace('最新限定NEXT_TASK已实际完成；当前没有已授权待运行任务，不重复已有评测/分析，不恢复旧训练。','NEXT_TASK及用户后来授权的下一步支持桥接研究均已完成；本次新研究未支持另开训练阶段，不重复已有评测/分析，不恢复旧训练。');hh+=summary.replace('(support_bridge_analysis/','(../support_bridge_analysis/');handoff.write_text(hh)
prompt=S/'plan/RECOVERY_PROMPT.txt';prompt.write_text(prompt.read_text()+'''\n用户随后授权继续研究、证据充分时另开实验；支持桥接研究已完成，不是待执行任务。恢复还需读support_bridge_analysis/REPORT.md、IDEA_EVALUATION.md、RESULTS/VALIDATION/INTEGRITY。7345条已有输出，候选foreground存在AUROC近随机，固定p×候选间平均IoU共同读出与seen退化，具体路线拒绝，未触发新训练阶段。原同句缓存特征没有完全一致组，本项候选视觉控制为NA；不据此宣布视觉无信息，不调用旧canonical存在分数拼接原候选。2219保护路径hash未变，训练/更新/前向0；不重复失败或已完成脚本。其他共同机制仍未决，后续依明确新问题继续，不自动扩大实验。
''')
hp=S/'plan/HANDOFF_STATUS.json';hs=json.loads(hp.read_text());hs.update(updated_at=stamp,support_bridge_analysis='completed',handoff_state='authorized_followup_research_completed_training_entry_not_supported',decision='fixed candidate agreement bridge rejected; joint mechanism unresolved; no new training round',active_processes=False);hs['support_bridge_summary']={'rows':7345,'new_forward_passes':0,'training_updates':0,'protected_paths':2219,'primary':'foreground_agreement','new_training_round_entry_supported':False,'report':'support_bridge_analysis/REPORT.md','independent_validation':'passed'};hp.write_text(json.dumps(hs,ensure_ascii=False,indent=2)+'\n')
rp=ROOT/'plan/EXPERIMENT_PLAN.md';root=rp.read_text();root=root.replace('下一项先做已有输出的零训练诊断','已完成候选诊断并补充原S+/S−支持桥接普通控制');root=root.replace('当前无已授权待执行任务。','随后授权的[支持桥接与普通控制研究](../2026年9月30日_存在与定位共同泛化的机制诊断/support_bridge_analysis/REPORT.md)也已完成；候选一致性未支持共同作用路径，未触发新训练阶段。当前无已授权待执行任务。');rp.write_text(root)
print('Bridge report, idea review and handoff documentation completed')
