"""Render fixed representation diagnostic results without selecting a method."""
import json
from pathlib import Path
S=Path(__file__).resolve().parents[1];D=S/'temporal_representation_analysis'
r=json.loads((D/'RESULTS.json').read_text());f=json.loads((D/'FREEZE.json').read_text())
def fmt(m):
 if m['point'] is None:return 'NA'
 return f"{m['point']:.4f} [{m['ci95'][0]:.4f}, {m['ci95'][1]:.4f}]"
def table(groups,keys):
 lines=['|组|'+ '|'.join(name for name,key in keys)+'|','|---|'+ '|'.join('---' for _ in keys)+'|']
 for name,metrics in groups:lines.append('|'+name+'|'+ '|'.join(fmt(metrics[key]) for _,key in keys)+'|')
 return '\n'.join(lines)
text='''# 冻结早期时序表示：绝对支持可读性诊断

## 决策

研究问题已经收缩为：**已见语义训练后的时序表示，是否含有可由固定小读出器迁移读出的、跨查询可比较的视频—文本支持？** 本次没有证明“信息可靠存在、只是原存在头没有读出”；也不能证明“任何读出都不可能、表示完全没有信息”。目前支持的较窄结论是：相对时间位置的信息仍可读，但受控线性读出未获得跨族稳定的无GT绝对视觉支持。追加敏感性详见报告收尾部分，不据线性失败断言表示信息消失。保持表示可读性/语义迁移未决，不继续候选几何变体，不启动全模型训练或正式U确认。

## 实际执行、冻结与成本

使用原throw/open_close/sit的seen-only best，原模型全部eval、requires_grad=False、inference_mode，无反向、无原模型参数更新。Throw/open_close原100轮；sit仍77轮账本、best11/latest76，不补训练。读取原train、seen和training-side pseudo，未读正式U/test。新增冻结前向28370条query呈现：train19162、原评估7345、固定文本canonical1863；不是重跑旧三族评测队列，未改原评测文件。

提取256维的文本交互后/时序编码前early，以及decoder前memory；另提取原存在头使用的decoder pooling、文本投影平均、视频投影（含TEF）平均和native saliency。模型saliency loss权重为0，故其失败不能解释为一个已训练相关性头失败。原时间有效位置按原mask取，原clip_length=1，保留原max_v_l=200与截断限制。

每族拟合六个相同容量的257参数仿射logistic读出器：early_global、memory_global、decoder_global、text_global、video_global、memory_window。前五者使用原视频存在标签、全时序平均；memory_window正例仅使用原GT窗内平均，负例全视频平均，额外使用原时间监督，单独解释。未把S+窗外标为负例。标准化只fit原train，C=1、L2、balanced、lbfgs、seed3407，无超参扫描、seen/pseudo选择。18次拟合全部收敛，拟合系数总数4626。**零新骨干/零原模型更新；并非所有参数都零更新，小读出器确实拟合了。** 标准化可折叠进仿射系数，不增加表示函数容量。

逐时间绝对logit a_t=w·h_t+b不作时间归一化；mean与max均冻结展示，不后选其中一个当方法。logit数值不是已验证的校准概率，不同族独立读出尺度不直接比较。原阈值、gate、checkpoint、raw/gated/FRR/RR与旧结果保持不变，没有新方法共同成功或独立VTG迁移声明。

共同原视频bootstrap，2302视频联合抽样，1000次seed3407，探索性95%区间，所有族/split使用共同乘数。AUROC为query加权、抽样单位视频；相对位置先query摘要再video等权；族等权汇总。seen与pseudo不同query，不称同样本因果变化。canonical相同实际文本输入的跨视频PairAcc先query组等权，端点视频权重相乘；与旧pair等权统计口径不同。非时序控制的GT指标NA，不能把有效bootstrap次数写成1000。全部覆盖与有效次数见RESULTS。

## 覆盖

|族/split|query|S+|S−|原视频|
|---|---:|---:|---:|---:|
'''
for name,c in f['coverage'].items():text+=f"|{name}|{c['rows']}|{c['positive']}|{c['negative']}|{c['videos']}|\n"
text+='''
train与pseudo原视频无重叠，train与seen qid无重叠；seen仍可能共享训练侧原视频，不把seen读出表现称作未见视频泛化。原时间mask/GT覆盖有效，无当前样本GT-center fallback、无丢弃正例。固定文本使用每混合标签query组字典序最小qid的实际特征和mask，重新冻结前向，不拼接旧候选或slot数组。

## 问题2：整段支持能区分S+/S−吗？

'''
keys=[('原存在','original_native/AUROC'),('early mean','early_global/mean/AUROC'),('memory mean','memory_global/mean/AUROC'),('纯文本','text_global/mean/AUROC'),('纯视频+TEF','video_global/mean/AUROC')]
text+=table([(g,b['metrics']) for g,b in r['groups'].items() if not g.endswith('canonical')],keys)+'\n\n'
text+=table([(s+'族等权',r['equal_family'][s]) for s in ['seen','pseudo']],keys)+'\n\n'
text+='''early mean的pseudo等权AUROC相对native原存在增益为'''+fmt(r['equal_family']['pseudo']['early_global/mean/delta_AUROC_vs_native_exist'])+'''，但主要由throw贡献，open_close与sit差值区间包含0；纯文本等权AUROC更高。因此这点收益不能归为可靠的新增绝对视觉支持。memory mean与原头几乎相同，delta='''+fmt(r['equal_family']['pseudo']['memory_global/mean/delta_AUROC_vs_native_exist'])+'''；没有简单换线性映射即可恢复的跨族证据。max池化不是补救：memory_global/max pseudo delta='''+fmt(r['equal_family']['pseudo']['memory_global/max/delta_AUROC_vs_native_exist'])+'''。固定mean/max全结果均保留，不挑选有利族/池化。

## 问题1：S+窗口内有绝对支持，还是只有相对峰值？

'''
text+=table([(g,r['groups'][g]['metrics']) for g in ['throw/pseudo','open_close/pseudo','sit/pseudo']], [('window峰入GT','memory_window/peak_inside_GT'),('峰入GT−时长机会','memory_window/peak_minus_duration_chance'),('GTmax vs S−全视频max AUC','memory_window/GT_window_max_vs_Sminus_video_max_AUROC')])+'\n\n'
text+='''memory_window的pseudo峰入GT族等权为'''+fmt(r['equal_family']['pseudo']['memory_window/peak_inside_GT'])+'''，超过GT所占有效时间质量的机会率；三族峰入GT−机会率区间均高于0，等权差为'''+fmt(r['equal_family']['pseudo']['memory_window/peak_minus_duration_chance'])+'''。这表明在额外原时间监督下，相对时间位置仍可读。纯视频+TEF控制的pseudo峰入GT=.3090、超过机会率=.0524 [ .0269, .0770 ]，也有信号：高于均匀机会率不是严格的文本条件定位证明，动作/时间偏置可以解释部分表现。window相对纯视频的点差=.0438只是描述，尚无配对控制的因果结论。它不是窗口R1@.5，不能替代raw定位或共同收益。

相对高峰没有转化为绝对支持：memory_window的GT窗max对原S−全视频max pseudo AUC等权='''+fmt(r['equal_family']['pseudo']['memory_window/GT_window_max_vs_Sminus_video_max_AUROC'])+'''，memory_global同指标='''+fmt(r['equal_family']['pseudo']['memory_global/GT_window_max_vs_Sminus_video_max_AUROC'])+'''。**这个条件诊断的两类最大值搜索范围不等，负例有更大搜索机会；小于.5不能单独证明语义支持缺失。** GT仅用于诊断，实际mean/max推理不读取GT。所有GT均值、峰值、分位与范围效应保留。

## 固定实际文本的视觉控制

'''
text+=table([(g,r['groups'][g]['metrics']) for g in ['throw/canonical','open_close/canonical','sit/canonical']], [('原头PairAcc','original_native/max/same_query_PairAcc_query_equal'),('early max','early_global/max/same_query_PairAcc_query_equal'),('memory max','memory_global/max/same_query_PairAcc_query_equal'),('window max','memory_window/max/same_query_PairAcc_query_equal'),('纯文本','text_global/max/same_query_PairAcc_query_equal')])+'\n\n'
for fam in ['throw','open_close','sit']:text+=fam+'覆盖：'+str(r['groups'][fam+'/canonical']['coverage'])+'。\n\n'
text+='''纯文本控制各组准确为.5，说明相同实际文本控制成立；GPU浮点微小批次差异<1e−5按同组精确tie处理，未改变视觉分数。canonical各小读出器没有跨三族稳定的视觉判别支持；throw仅36行/10query组/37正负对，sit亦有限，区间宽，不能把控制不显著解释为表示绝对无信息。与普通pseudo全query的文本可区分性相比，这一控制更限制“只修存在标尺”的解释。

## 问题3与研究分支

- “可靠绝对支持可由同容量小读出器恢复，只是原头丢失”：本次未支持。early mean的小增益没有通过文本/固定文本控制形成跨族视觉证据。
- “任意读出均无信息，表示确定只学相对匹配”：本次不能证明。检查范围仅仿射读出、固定训练目标与池化，有容量/监督/优化及canonical覆盖限制。
- 当前可支持：相对时间位置可读，跨查询绝对视觉支持的可迁移可读性尚未证实。瓶颈范围从候选一致性收缩到**时序支持形成与跨语义迁移，及其无GT聚合标尺**；尚不能在表示信息缺失与更合适读出之间作因果二选一。

若未来明确进入训练，最小候选是用原S+窗口的存在性高支持和原S−整段缺席低支持学习未作时间归一化的支持场；不把S+窗外全标负，不依赖decoder候选槽。**本次未执行该训练，probe不是该新目标的训练验证。** 仍需具体METHOD_SPEC、容量/普通控制、共同AUROC+raw作用路径、gated与seen/FRR/RR护栏及独立VTG范围。不能用一次线性失败自动授权复杂表示重做。

## 近邻与创新边界

RaTSG已经使用帧/视频相关性反馈与多粒度相关性判别器：[NeurIPS 2024原论文](https://proceedings.neurips.cc/paper_files/paper/2024/hash/4b96695d9885f038110b8b16ef50e882-Abstract-Conference.html)。Learning to Refuse研究hard-irrelevant查询拒绝，采用refusal-aware强化微调与HI-VTG：[CVPR 2026原论文](https://openaccess.thecvf.com/content/CVPR2026/html/Lee_Learning_to_Refuse_Refusal-Aware_Reinforcement_Fine-Tuning_for_Hard-Irrelevant_Queries_in_CVPR_2026_paper.html)。不能宣称首次用局部相关性判断存在；潜在贡献须限定为原已见语义训练后、下游未见动作/组合上的同一绝对支持表示如何共同服务存在与定位。本次仅提供可读性诊断，没有新算法效果与新颖性通过声明。

## 复现与完整性

入口定义[FREEZE](FREEZE.json)、[probe代码冻结](PROBE_CODE_FREEZE.json)，已保存特征、系数、逐时间分数、[RESULTS](RESULTS.json)、共同bootstrap与日志。独立验证见[VALIDATION](VALIDATION.json)，原资产完整性见[INTEGRITY](INTEGRITY.json)。原12组forward中的seen/pseudo四位输出及canonical原存在控制均复现；三族冻结前后模型tensor hash一致。18230受保护原资产最终重新核hash。

首次import失败在前向/拟合前发生，保留于../temporal_representation_failures/attempt_001_import；改为直接import原数据集，不改冻结统计定义。无旧队列恢复、无原模型训练、无正式U确认。既有主要指标与门槛未变。
'''
(D/'REPORT.md').write_text(text)
print('report generated')
