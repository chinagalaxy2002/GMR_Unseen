# A1/QD 六组双轨实验最终报告

冻结简单控制：adapter；候选 window 正式进入：False。真实 U 从未参与选择。

## GMR 逐组结果

| split | model | method | seed | S AUROC | U AUROC | gap | U+ FRR | U− RR | matched U PairAcc | raw U R1 .5/.7 | hard U R1 .5/.7 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| A1 | qd | baseline | 3407 | 0.7966 | 0.5309 | 0.2657 | 0.1505 | 0.1707 | 0.5817 | 0.2602/0.0903 | 0.2108/0.0796 |
| A1 | qd | regularized | 3407 | 0.8316 | 0.4954 | 0.3362 | 0.1269 | 0.1466 | 0.6442 | 0.2108/0.0817 | 0.1828/0.0688 |
| A1 | qd | adapter | 3407 | 0.7933 | 0.4771 | 0.3162 | 0.2430 | 0.2127 | 0.5865 | 0.2129/0.0882 | 0.1505/0.0645 |

## 独立正例 VTG（没有存在头，只有原 S+）

| split | model | method | seed | seen R1 .5/.7 | unseen R1 .5/.7 |
|---|---|---|---:|---|---|
| A1 | qd | baseline | 3407 | 0.3873/0.2124 | 0.2065/0.0839 |
| A1 | qd | regularized | 3407 | 0.3981/0.2299 | 0.1871/0.0753 |
| A1 | qd | adapter | 3407 | 0.4346/0.2457 | 0.2624/0.1097 |

## 完整性与机制限制

各组视频 paired bootstrap 区间保存为 *_video_ci.json；summary.json 为动作轴/组合轴等权摘要，本次仅 seed=3407，不进行或估计多种子变化。缺少组的摘要明确标 complete_axis=false。

冻结的 gate 仅支持关联，不证明因果。候选若被跳过，原因记录在 MECHANISM_GATE.json 和任务状态；不能宣称新算法或通用对应机制已成立。普通正则/适配层若同样有效，报告简洁控制结论。任何 U+ 接受提高但 U− RR 崩溃、U 不提高而 S 降低的现象均不计为泛化成功。

Flash 原评测对没有 proposal 的正例可能跳过 R1 分母；本报告 raw/hard R1 固定完整正例分母。原官方选 checkpoint 规则仍保留，官方指标另存各 test 报告。复制后的评测仅补齐空预测 qid，不造 proposal。

workers=0 与历史配置不同；历史报告不能混充当前比较。训练日志与来源记录保留，精确全部 FLOPs 与活跃 GPU 总时间未测量。

本次六组训练与评测无失败。failed_or_skipped.json 中的 3 个节点均为历史条件跳过：window 开发、teacher L2、teacher KL；不属于本次六组失败。机制分析见 MECHANISM_ANALYSIS.json。本次完成正式结果 6 个。

## 用户更新后的范围

仅 A1/QD，baseline/regularized/adapter × GMR/正例 VTG，共六组，seed=3407。其他正式训练及评测已取消。按用户要求不执行同预算核验，不声明初始化、batch 顺序、更新或曝光已通过成对核验。原已完成/运行任务的旧日志仅保留历史记录。

## 完成状态复核

2026-09-30T21:31:09+08:00 核对：六组训练均完成100/100 epoch，六组评测均完成，最终汇总完成。队列于2026-09-30 17:58:04（Asia/Shanghai）正常结束，汇总返回码为0。无本实验活动进程或待恢复任务；没有重新启动训练、评测或队列。逐组产物与 checkpoint 哈希核验见 [COMPLETION_VERIFIED.json](COMPLETION_VERIFIED.json)。未执行同预算成对核验。

| 轨道 | 方法 | 已完成 epoch | 训练 | 评测 |
| --- | --- | ---: | --- | --- |
| GMR | baseline | 100/100 | 完成 | 完成 |
| GMR | regularized | 100/100 | 完成 | 完成 |
| GMR | adapter | 100/100 | 完成 | 完成 |
| 正例 VTG | baseline | 100/100 | 完成 | 完成 |
| 正例 VTG | regularized | 100/100 | 完成 | 完成 |
| 正例 VTG | adapter | 100/100 | 完成 | 完成 |

Adapter 在正例 VTG 的 unseen R1@0.5 相对 baseline 提高约5.59个百分点，但在 GMR 的 unseen AUROC 下降约.0538，未提供双轨共同改善证据。当前结果仅支持 A1/QD 单 seed 下的描述性比较，不能证明通用对应机制或跨划分/架构一致性。
