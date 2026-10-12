# 三骨干 baseline 完整机制监控

正式队列：`experiments/baseline_full_diagnostics_20261013`（相对于本文件目录）。
33 个原生 baseline 设置：Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR × 11 个划分（clean_v3 五个、Soccer 五个、Charades-CG v2 一个）。另训练 Moment/QD 的 22 个去 decoder self-attention 配对设置，共 55 项，100 epochs，seed 3407，fresh initialization。每张 GPU 最多两个训练进程，优先跨数据集、跨骨干混排；不包含 QIVR。原 QIVR 与旧版监控队列已取消，已有结果保留。

本轮复现原生 baseline 架构和损失，所有模型参数参与训练；CLIP/SlowFast/文本特征为预提取输入。选择规则统一为 Seen validation AUROC 最大、并列取最早 epoch；阈值在 Seen validation 上按 BA 校准。**该选择规则不同于历史 baseline 的 Seen localization 最优选择规则**，历史比较是复现协议差异，不能宣称为新方法增益。训练仅用 S+/S−，冻结 checkpoint 与阈值后才读取 test 做最终 S/U 诊断。

## 记录范围

| 监控 | 训练 | 固定 Seen probe | 全量 Seen validation / 冻结 test |
|---|---|---|---|
| S+ 定位、S+／S− 存在分数、激活数量、正确覆盖与伪响应 | 每 batch 的响应汇总 | 每 epoch | 每 epoch／最终一次 |
| DETR 实际 Hungarian 匹配次数及样本归属变化 | 原生 criterion 的实际匹配，含训练随机性 | 固定样本、eval 模式，每 epoch 对照 | 不把额外匹配混入训练统计 |
| DETR 逐层 query 表征、余弦／距离／秩、槽间重叠、native self/cross attention | 首 batch＋每 50 steps；首 batch 保存 raw NPZ | 每 epoch 保存全部 probe raw | 完整候选／分数，层级 raw 以固定 probe 为主 |
| Flash 时序表征、多尺度 pyramid、候选边界、native cross attention、原生前景／回归监督目标 | 首 batch＋每 50 steps；首 batch raw | 每 epoch全部 probe raw（eval 无训练 target） | 完整原生候选及存在分数 |
| 共享表征上的定位／分类／存在梯度范数、余弦、冲突，分别 S+/S− | 首 batch＋每 50 steps；DETR 还保留原有共享参数梯度记录 | eval 不反传 | eval 不反传 |
| S+/S− 损失贡献、总梯度裁剪前范数／系数、学习率 | DETR 原生 final/aux 实际匹配拆分，每步；Flash 存在贡献按采样、定位／分类仅 S+ | — | — |
| 模块实际参数更新 | 每 epoch，包含 Flash pyramid／coord／class／conf／pooling | — | — |
| 池化所属槽位、正确／匹配槽贡献占比、逐槽移除后的 logit／概率变化、head ReLU 活跃率 | 首 batch＋每 50 steps | 每 epoch全部 probe | 全量每 epoch／最终一次 |
| 原始 logit、sigmoid 与原生舍入分数、饱和、ties、错排比例、极端反序对 | 采样 | 每 epoch | 全量每 epoch／最终一次 |
| 同视频正负排序、长度／GT 数／截断分层、定位与存在判别联合结果 | 采样 | 每 epoch | 全量每 epoch／最终一次 |
| S+ vs S−、U+ vs S−、S+ vs U−、U+ vs U− 的 2×2 AUROC 与对称 gap 分解 | 不接触 U | 不接触 U | 冻结 test；2000 次共享视频 cluster bootstrap |

Flash 没有 DETR decoder query 或 Hungarian 槽位，其 supervision 是原生中心／尺度范围的时序点目标。Flash 的 `leave_one_unit_out` 移除的是池化视频时序单元，不是多尺度候选；原生 query 表征保持固定。相关图和表不能直接混称为“DETR 槽位”。Flash 采用原生 SlowFast→CLIP 特征顺序、六位小数 logit；DETR 采用原生 CLIP→SlowFast、四位小数概率。sigmoid 概率、BCE 和 benchmark 原生 score 分开保存。

0.5 foreground／probability 及 IoU≥0.5 是预设描述阈值，不用于 Unseen 调参。LOO 为 head 局部干预；梯度冲突和 gap 分解为诊断证据，不能单独证明因果。训练 batch 有 dropout／GT 采样，归属变化应与固定 eval probe 对照。负样本没有定位 GT，正确覆盖／匹配 IoU 使用 NA，不当作 0 定位精度。

## 产物

队列 `STATUS.json`／`FULL_MONITORING.md`／`FULL_MONITOR_STATUS.json` 汇总进程与最新完整 Seen 验证；`MONITORING.md`／`RESPONSES.md` 保留原监控摘要。每项实验保留 `CONFIG.json`、`OPT.json`、日志、best/last checkpoint、`monitor/decoder_slots/` 或 `monitor/flash_temporal/`、`monitor/auroc_mechanisms/`、参数更新和响应轨迹。

最终提供冻结预测／校准元数据、S/U AUROC／实际 Rej-F1／G-mIoU@1 及有符号 Gap、总体 Rej-F1／RR／G-mIoU、S+/U+ FRR、子集样本计数及视频 bootstrap CI。历史 baseline 配对变化明确标为协议复现差异，SA 配对另报。Rej-F1／G-mIoU 的 Gap 依赖子集正负比例；未完成设置和不足五划分的汇总不得报正式五划分 macro。

`SOURCE_SNAPSHOT` 保存调度器、runner、监控与模型／数据集源码；SUITE/CONFIG 记录代码、release、checkpoint/prediction 哈希。smoke 与失败的工程检查目录单独保留，不混入正式结果。

验证：`FULL_MONITOR_TEST_RESULTS.json` 的四种 DETR 组合逐位输出／梯度／RNG 一致、S+/S− 原生损失精确可加；`FLASH_FULL_MONITOR_TEST_RESULTS.json` 通过同类检查，历史 checkpoint 的 16 条 Seen 样本 logit 最大误差 2e-6、set-IoU 误差 0。三数据集 smoke 为工程验证，不是性能结果。
