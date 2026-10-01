# 冻结早期时序表示：绝对支持可读性诊断

## 决策

研究问题已经收缩为：**已见语义训练后的时序表示，是否含有可由固定小读出器迁移读出的、跨查询可比较的视频—文本支持？** 本次没有证明“信息可靠存在、只是原存在头没有读出”；也不能证明“任何读出都不可能、表示完全没有信息”。目前支持的较窄结论是：相对时间位置的信息仍可读，但受控线性读出未获得跨族稳定的无GT绝对视觉支持。追加均值敏感性显示，给定原GT位置后仍有条件支持，固定实际文本后open_close保留有限局部证据；因此缺口进一步落在无GT的局部证据选取、聚合标尺及其跨语义迁移，而非确定的表示信息消失。保持表示可读性/语义迁移未决，不继续候选几何变体，不启动全模型训练或正式U确认。

## 实际执行、冻结与成本

使用原throw/open_close/sit的seen-only best，原模型全部eval、requires_grad=False、inference_mode，无反向、无原模型参数更新。Throw/open_close原100轮；sit仍77轮账本、best11/latest76，不补训练。读取原train、seen和training-side pseudo，未读正式U/test。新增冻结前向28370条query呈现：train19162、原评估7345、固定文本canonical1863；不是重跑旧三族评测队列，未改原评测文件。

提取256维的文本交互后/时序编码前early，以及decoder前memory；另提取原存在头使用的decoder pooling、文本投影平均、视频投影（含TEF）平均和native saliency。模型saliency loss权重为0，故其失败不能解释为一个已训练相关性头失败。原时间有效位置按原mask取，原clip_length=1，保留原max_v_l=200与截断限制。

每族拟合六个相同容量的257参数仿射logistic读出器：early_global、memory_global、decoder_global、text_global、video_global、memory_window。前五者使用原视频存在标签、全时序平均；memory_window正例仅使用原GT窗内平均，负例全视频平均，额外使用原时间监督，单独解释。未把S+窗外标为负例。标准化只fit原train，C=1、L2、balanced、lbfgs、seed3407，无超参扫描、seen/pseudo选择。18次拟合全部收敛，拟合系数总数4626。**零新骨干/零原模型更新；并非所有参数都零更新，小读出器确实拟合了。** 标准化可折叠进仿射系数，不增加表示函数容量。

逐时间绝对logit a_t=w·h_t+b不作时间归一化；mean与max均冻结展示，不后选其中一个当方法。logit数值不是已验证的校准概率，不同族独立读出尺度不直接比较。原阈值、gate、checkpoint、raw/gated/FRR/RR与旧结果保持不变，没有新方法共同成功或独立VTG迁移声明。

共同原视频bootstrap，2302视频联合抽样，1000次seed3407，探索性95%区间，所有族/split使用共同乘数。AUROC为query加权、抽样单位视频；相对位置先query摘要再video等权；族等权汇总。seen与pseudo不同query，不称同样本因果变化。canonical相同实际文本输入的跨视频PairAcc先query组等权，端点视频权重相乘；与旧pair等权统计口径不同。非时序控制的GT指标NA，不能把有效bootstrap次数写成1000。全部覆盖与有效次数见RESULTS。

## 覆盖

|族/split|query|S+|S−|原视频|
|---|---:|---:|---:|---:|
|throw/train|7559|6252|1307|3324|
|throw/seen|1185|709|476|376|
|throw/pseudo|570|464|106|389|
|open_close/train|4625|4188|437|2442|
|open_close/seen|722|516|206|299|
|open_close/pseudo|2827|1888|939|1236|
|sit/train|6978|5920|1058|3253|
|sit/seen|1065|676|389|370|
|sit/pseudo|976|625|351|452|

train与pseudo原视频无重叠，train与seen qid无重叠；seen仍可能共享训练侧原视频，不把seen读出表现称作未见视频泛化。原时间mask/GT覆盖有效，无当前样本GT-center fallback、无丢弃正例。固定文本使用每混合标签query组字典序最小qid的实际特征和mask，重新冻结前向，不拼接旧候选或slot数组。

## 问题2：整段支持能区分S+/S−吗？

|组|原存在|early mean|memory mean|纯文本|纯视频+TEF|
|---|---|---|---|---|---|
|throw/seen|0.8048 [0.7726, 0.8360]|0.8204 [0.7913, 0.8487]|0.7746 [0.7369, 0.8098]|0.8505 [0.8276, 0.8728]|0.4982 [0.4591, 0.5364]|
|throw/pseudo|0.5662 [0.4910, 0.6376]|0.6283 [0.5569, 0.6927]|0.5691 [0.5035, 0.6324]|0.7077 [0.6402, 0.7634]|0.4854 [0.4185, 0.5456]|
|open_close/seen|0.8575 [0.8212, 0.8900]|0.8853 [0.8539, 0.9141]|0.8857 [0.8550, 0.9149]|0.8817 [0.8480, 0.9115]|0.4976 [0.4410, 0.5550]|
|open_close/pseudo|0.5371 [0.5197, 0.5562]|0.5459 [0.5271, 0.5660]|0.5384 [0.5190, 0.5579]|0.5233 [0.5027, 0.5455]|0.4983 [0.4802, 0.5164]|
|sit/seen|0.8432 [0.8194, 0.8652]|0.8313 [0.8095, 0.8525]|0.8371 [0.8156, 0.8588]|0.8415 [0.8176, 0.8648]|0.5498 [0.5134, 0.5870]|
|sit/pseudo|0.6543 [0.6110, 0.6977]|0.6648 [0.6237, 0.7031]|0.6498 [0.6058, 0.6933]|0.6483 [0.6125, 0.6857]|0.5080 [0.4798, 0.5363]|

|组|原存在|early mean|memory mean|纯文本|纯视频+TEF|
|---|---|---|---|---|---|
|seen族等权|0.8352 [0.8139, 0.8564]|0.8457 [0.8246, 0.8664]|0.8325 [0.8114, 0.8526]|0.8579 [0.8358, 0.8797]|0.5152 [0.4872, 0.5421]|
|pseudo族等权|0.5859 [0.5556, 0.6156]|0.6130 [0.5855, 0.6404]|0.5858 [0.5597, 0.6151]|0.6264 [0.6005, 0.6505]|0.4973 [0.4719, 0.5202]|

early mean的pseudo等权AUROC相对native原存在增益为0.0271 [0.0094, 0.0438]，但主要由throw贡献，open_close与sit差值区间包含0；纯文本等权AUROC更高。因此这点收益不能归为可靠的新增绝对视觉支持。memory mean与原头几乎相同，delta=-0.0001 [-0.0165, 0.0176]；没有简单换线性映射即可恢复的跨族证据。max池化不是补救：memory_global/max pseudo delta=-0.0252 [-0.0439, -0.0055]。固定mean/max全结果均保留，不挑选有利族/池化。

## 问题1：S+窗口内有绝对支持，还是只有相对峰值？

|组|window峰入GT|峰入GT−时长机会|GTmax vs S−全视频max AUC|
|---|---|---|---|
|throw/pseudo|0.3879 [0.3387, 0.4379]|0.1469 [0.1022, 0.1953]|0.3742 [0.3125, 0.4388]|
|open_close/pseudo|0.3024 [0.2770, 0.3276]|0.0594 [0.0357, 0.0830]|0.3402 [0.3194, 0.3594]|
|sit/pseudo|0.3680 [0.3195, 0.4091]|0.0825 [0.0382, 0.1237]|0.4529 [0.4125, 0.4921]|

memory_window的pseudo峰入GT族等权为0.3528 [0.3279, 0.3770]，超过GT所占有效时间质量的机会率；三族峰入GT−机会率区间均高于0，等权差为0.0962 [0.0725, 0.1188]。这表明在额外原时间监督下，相对时间位置仍可读。纯视频+TEF控制的pseudo峰入GT=.3090、超过机会率=.0524 [ .0269, .0770 ]，也有信号：高于均匀机会率不是严格的文本条件定位证明，动作/时间偏置可以解释部分表现。window相对纯视频的点差=.0438只是描述，尚无配对控制的因果结论。它不是窗口R1@.5，不能替代raw定位或共同收益。

相对高峰没有转化为绝对支持：memory_window的GT窗max对原S−全视频max pseudo AUC等权=0.3891 [0.3628, 0.4143]，memory_global同指标=0.3918 [0.3658, 0.4204]。**这个条件诊断的两类最大值搜索范围不等，负例有更大搜索机会；小于.5不能单独证明语义支持缺失。** GT仅用于诊断，实际mean/max推理不读取GT。所有GT均值、峰值、分位与范围效应保留。

## 固定实际文本的视觉控制

|组|原头PairAcc|early max|memory max|window max|纯文本|
|---|---|---|---|---|---|
|throw/canonical|0.2522 [0.0000, 0.5164]|0.4189 [0.1333, 0.7388]|0.2639 [0.0000, 0.5601]|0.2756 [0.0499, 0.6200]|0.5000 [0.5000, 0.5000]|
|open_close/canonical|0.5094 [0.4742, 0.5614]|0.5395 [0.5035, 0.5901]|0.5079 [0.4726, 0.5584]|0.5110 [0.4767, 0.5673]|0.5000 [0.5000, 0.5000]|
|sit/canonical|0.5115 [0.4322, 0.6318]|0.5251 [0.4321, 0.6252]|0.4765 [0.3849, 0.6210]|0.4647 [0.3876, 0.6027]|0.5000 [0.5000, 0.5000]|

throw覆盖：{'same_query_pairs': 37, 'early_global/GTmax_eligible_Splus': 15, 'memory_global/GTmax_eligible_Splus': 15, 'decoder_global/GTmax_eligible_Splus': 0, 'text_global/GTmax_eligible_Splus': 0, 'video_global/GTmax_eligible_Splus': 15, 'memory_window/GTmax_eligible_Splus': 15, 'native_saliency/GTmax_eligible_Splus': 15, 'original_native/GTmax_eligible_Splus': 0, 'rows': 36, 'positive': 15, 'negative': 21, 'videos': 34, 'mixed_label_videos': 1, 'same_query_groups': 10, 'GT_fallback_Splus': 0, 'GT_no_valid_positions_Splus': 0}。

open_close覆盖：{'same_query_pairs': 7367, 'early_global/GTmax_eligible_Splus': 985, 'memory_global/GTmax_eligible_Splus': 985, 'decoder_global/GTmax_eligible_Splus': 0, 'text_global/GTmax_eligible_Splus': 0, 'video_global/GTmax_eligible_Splus': 985, 'memory_window/GTmax_eligible_Splus': 985, 'native_saliency/GTmax_eligible_Splus': 985, 'original_native/GTmax_eligible_Splus': 0, 'rows': 1598, 'positive': 985, 'negative': 613, 'videos': 814, 'mixed_label_videos': 423, 'same_query_groups': 158, 'GT_fallback_Splus': 0, 'GT_no_valid_positions_Splus': 0}。

sit覆盖：{'same_query_pairs': 359, 'early_global/GTmax_eligible_Splus': 131, 'memory_global/GTmax_eligible_Splus': 131, 'decoder_global/GTmax_eligible_Splus': 0, 'text_global/GTmax_eligible_Splus': 0, 'video_global/GTmax_eligible_Splus': 131, 'memory_window/GTmax_eligible_Splus': 131, 'native_saliency/GTmax_eligible_Splus': 131, 'original_native/GTmax_eligible_Splus': 0, 'rows': 229, 'positive': 131, 'negative': 98, 'videos': 122, 'mixed_label_videos': 69, 'same_query_groups': 45, 'GT_fallback_Splus': 0, 'GT_no_valid_positions_Splus': 0}。

纯文本控制各组准确为.5，说明相同实际文本控制成立；GPU浮点微小批次差异<1e−5按同组精确tie处理，未改变视觉分数。canonical各小读出器没有跨三族稳定的视觉判别支持；throw仅36行/10query组/37正负对，sit亦有限，区间宽，不能把控制不显著解释为表示绝对无信息。与普通pseudo全query的文本可区分性相比，这一控制更限制“只修存在标尺”的解释。

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

## 最大值搜索范围敏感性（看过主结果后追加，未重拟合）

S+ GT均值 vs 原S−全视频均值避免不同长度最大值搜索机会，但仍使用GT作正例诊断，不能当实际推理成绩。区间与主分析使用同一1000次seed3407视频权重，不把后加分析称为预登记。

|组|early GTmean AUC|memory GTmean AUC|window GTmean AUC|
|---|---|---|---|
|throw/seen|0.8234 [0.7948, 0.8509]|0.7581 [0.7199, 0.7946]|0.8367 [0.8073, 0.8652]|
|throw/pseudo|0.6240 [0.5542, 0.6874]|0.5621 [0.4995, 0.6265]|0.6241 [0.5616, 0.6864]|
|throw/canonical|0.3968 [0.2143, 0.5914]|0.3873 [0.2055, 0.5844]|0.4000 [0.2148, 0.5920]|
|open_close/seen|0.8845 [0.8521, 0.9141]|0.8901 [0.8611, 0.9185]|0.8961 [0.8681, 0.9213]|
|open_close/pseudo|0.5557 [0.5374, 0.5766]|0.5526 [0.5321, 0.5736]|0.6078 [0.5883, 0.6281]|
|open_close/canonical|0.5829 [0.5613, 0.6102]|0.5701 [0.5463, 0.5965]|0.6315 [0.6089, 0.6570]|
|sit/seen|0.8336 [0.8101, 0.8566]|0.7846 [0.7565, 0.8090]|0.8669 [0.8449, 0.8859]|
|sit/pseudo|0.6537 [0.6143, 0.6898]|0.5487 [0.5058, 0.5932]|0.6726 [0.6286, 0.7167]|
|sit/canonical|0.5264 [0.4396, 0.6122]|0.4924 [0.4011, 0.5826]|0.5276 [0.4379, 0.6137]|

敏感性结果必须与固定文本控制一起读：均值可缓解极值范围效应，但不能移除文本先验，也没有把GT变成可用推理输入。完整最大值−均值、两类有效时间长度分位数见[POOLING_ROBUSTNESS](POOLING_ROBUSTNESS.json)。

![固定读出诊断](REPRESENTATION_READOUT.png)

[可导出图PDF](REPRESENTATION_READOUT.pdf)。

独立核验初次因逐行重复解压而主动终止，保留于../temporal_representation_failures/attempt_002_verifier_io；随后每组缓存一次重启核验，统计定义不变，主分析未重做。

均值敏感性提示局部信息不能被判为消失：memory_window的GTmean正例诊断pseudo AUC为.6241/.6078/.6726，均高于随机；而同一读出的无GT整段mean/max等权AUC仅.5686/.5402。它使用额外原时间监督和GT位置，不能证明只修原存在头即可恢复。固定实际文本的GTmean PairAcc（另行看过主结果后冻结）如下：

|族|window GTmean同句PairAcc|
|---|---|
|throw|0.3044 [0.0666, 0.6333]|
|open_close|0.5646 [0.5339, 0.6263]|
|sit|0.4948 [0.4103, 0.6416]|

open_close保留有限的文本固定后、GT条件局部证据（PairAcc=.5646 [.5339,.6263]）；throw/sit覆盖有限且区间包含.5，不能扩展为三族稳定绝对支持。当前进一步收束为：**如何在无GT条件下选取这些局部证据，并聚合成可跨查询、跨语义比较的支持？** 仍不是已经证实的纯存在映射问题，也不是已经证实的表示完全缺失。详见[CONDITIONAL_SUPPORT](CONDITIONAL_SUPPORT.json)及其冻结/独立核验。
