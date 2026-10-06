# DDV 五划分实验整理与发布说明

日期：2026-10-06。结论来自已完成实验和独立审计；本次发布未新增训练或模型评测。

## 目标与判定

目标是相对 GMR 基线提高未见语义上的事件存在/拒绝判别 AUROC，并缩小 Seen−Unseen Gap。**DDV 达到了五划分宏平均目标；尚未实现所有未见动作和组合都稳定改善。**

DDV 使用 FlashVTG、Moment-DETR、QD-DETR 三骨干共识，融合对齐 CLIP 相似度和 SlowFast 特征变化标量。验证头约 400 参数，骨干/编码器冻结；各划分独立训练，seed 3407，400 epochs × 10 steps。模型和阈值仅在 Seen validation 选择。现有测试划分已被多轮方法开发查看，属于开发结果，尚非新语义盲评。

## 主要结果

| 方法 | Seen AUROC | Unseen AUROC | Gap | Matched PairAcc |
|---|---:|---:|---:|---:|
| HQ QD 原始 logit | 0.7511 | 0.5027 | 0.2484 | 0.5181 |
| 发布 QD 概率 | 0.7476 | 0.5144 | 0.2332 | 0.5294 |
| Flash 原始 logit | 0.7730 | 0.5714 | 0.2016 | 0.6140 |
| 三骨干融合控制，重新训练 | 0.7778 | 0.5523 | 0.2255 | 0.6014 |
| DDV | **0.7684** | **0.6134** | **0.1550** | **0.6608** |

共享 1,217 个测试视频的 paired cluster Bootstrap，共 2,000 次。相对 HQ QD，DDV ΔUnseen 为 +11.06 pp，95% CI [8.89, 13.47] pp，Gap 缩小 9.34 pp；相对三骨干融合控制，ΔUnseen 为 **+6.11 pp，CI [4.22, 8.21] pp**，同时 Seen **−0.94 pp，CI [−1.45, −0.44] pp**。控制只有三个共识权重，尚需匹配容量的检测器 MLP 与逐模态消融才能进一步归因。

## 各划分及运行点

| Split | 未见语义 | DDV Seen | DDV Unseen | DDV Gap | U+ 误拒率 | U− 拒绝率 |
|---|---|---:|---:|---:|---:|---:|
| A1 | put / take | 0.8239 | 0.5153 | 0.3087 | 18.71% | 23.68% |
| A2_alt | drink / pour | 0.7802 | 0.5651 | 0.2151 | 1.19% | 1.60% |
| A3 | run / walk | 0.7267 | 0.5818 | 0.1448 | 29.17% | 41.41% |
| C1 | sit + bed/chair/couch | 0.7828 | 0.7682 | 0.0146 | 0.00% | 2.59% |
| C2_alt | open/close + box/cabinet | 0.7282 | 0.6364 | 0.0918 | 62.61% | 74.80% |

A1 Gap 比 HQ QD 扩大 2.99 pp，Unseen 增益区间跨零。动作三组的平均 DDV Unseen 为 0.5541，Flash logit 为 0.5514，差值区间跨零；组合两组分别为 0.7023 和 0.6015，增益显著。A2_alt/C1 的 Seen 运行点几乎不拒绝未见负例；C2_alt 则大量误拒正例。因此 AUROC 的改善仍需配合校准和定位评价。

## 审计纠错

- 原自定义 G-mIoU 未奖励正确拒绝，还把多个预测窗口拼成外包区间；不符合 GMR 的集合匹配公式。按项目正确评测器、原发布候选和各自 Seen 阈值，DDV Unseen G-mIoU@1 为 **29.25%**，HQ QD 为 **24.55%**。另用统一 pre-existence 候选时分别为 29.21%、24.54%，增益 CI [3.34, 6.04] pp。它评价固定 QD 候选加存在门控，不代表定位坐标改善。
- Release QD PairAcc 修正为 **0.5294**；原报告误复制了 HQ 0.5181。
- DDV Unseen 点估计超过 0.60，但 CI **[0.5926, 0.6346]** 包含 0.60。原代码未计算 p 值，不引用 `p < 0.0001`。
- 路由实际按 split ID，未实现查询语义动态路由；`w_obj/w_kin/w_vis` 未参与 forward；A3 alpha 上限是 0.60。
- 无符号的特征变化/端点距离不能单独证明有向动作推理；输入也没有音频。400-epoch 的耗时仅针对冻结特征上的验证头。

完整证据与限制见 [DDV_AUDIT_REPORT.md](../../experiments/agy_test/ddv_audit_20261006/DDV_AUDIT_REPORT.md)。

## 后续实验顺序

1. 约 400 参数 detector-only MLP、CLIP-only、SlowFast-only、统一融合，以及固定/自由/有界 gate 的重训对照。
2. 只用 Seen 数据做运行点校准；共同报告 U+ FRR、U− RR、Rej-F1、正确 G-mIoU 和正例 raw/gated 定位。
3. 精确源反事实配对、固定 query 的视频置换、动作互换和时间反转诊断，再决定是否加入有向起止状态。
4. 冻结结构/路由/损失/阈值方案后，用至少三个种子和未参与方法开发的新语义划分确认。

## 文件入口与发布范围

- [DDV 代码及资源恢复说明](../../experiments/agy_test/decomposed_directional_verifier/README.md)。
- [修正指标汇总](../../experiments/agy_test/decomposed_directional_verifier/benchmark_audited.json)。
- [审计指标](../../experiments/agy_test/ddv_audit_20261006/audit_metrics.json)、[Bootstrap](../../experiments/agy_test/ddv_audit_20261006/bootstrap.json)、[输入/参数核查](../../experiments/agy_test/ddv_audit_20261006/source_checks.json)。
- [本次发布清单](../../experiments/agy_test/decomposed_directional_verifier/PUBLICATION_MANIFEST.json)。

按照仓库既有口径，发布源码、文档和小型指标 JSON。检查点、NPZ 特征、逐查询预测、Bootstrap 抽样数组及视频保留本地。原报告和原汇总保留作追溯；正式引用以修正汇总和独立审计为准。
