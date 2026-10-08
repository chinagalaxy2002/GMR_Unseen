# 发布验证：Seen Guard

本分支从原 DEC 提交 `06b0f59b83e0cd20de20b19041e4172be34582d2` 建立独立工作区，保留原算法与结果存档。发布代码不导入原实验目录，不需要后台训练任务。

## 已完成验证

1. **文本缓存重建。** 使用 spaCy 3.8.16 / en_core_web_sm 3.8.0，从五划分的 train/val/test 查询文本重新解析 82,490 条记录。输入解析器的只有字符串；训练/验证/测试标注不参与解析。
2. **校准重建。** 独立的 `calibrate_seen_guard.py` 只读取 train/Seen-val 与验证窗口 IoU。训练组合统计、15 项模式、融合超参数和阈值与冻结配置一致；数值容差内的最大校准差约 1.11e-16。
3. **全量复算。** 从输入与原窗口 JSON 复算 Baseline、原 DEC、Seen Guard。45 行逐设置与 9 行宏平均，共 54 行，最大指标差约 1.42e-14。
4. **六项保护。** 15/15 的当前点估计满足 Seen AUROC≥Baseline，Unseen AUROC≥DEC，G-mIoU/Rej-F1≥DEC，S+ FRR≤DEC，U+ FRR≤DEC。所有 Unseen 排序与决策实际保持原 DEC。
5. **决策核验。** 未覆盖的 Unseen 接受/拒绝逐样本相同；C2_alt/QD 的全部接受/拒绝逐样本相同。打分函数只接收 X、queries 与文本解析结果，无需目标标签、分区、语义图或标识符。
6. **统计复算。** 2,000 次共享视频聚类配对 bootstrap，seed=3407，全部有效；所有区间与最终探索结果相同。
7. **资产核验。** 25 个数据资产及冻结校准资产经过 SHA256 校验。验证窗口 IoU 新增来源见 `data/SEEN_GUARD_SOURCE_MANIFEST.json`。
8. **算法图。** SVG 保留可编辑文字，PDF 为矢量，PNG 为预览。两阶段分层与真实代码对应，校准箭头为虚线，覆盖/未覆盖分支有文字标注。按 7.2 英寸双栏宽使用时最小文字约 8 pt；图注明确 FRR、G、F 和数据耦合边界。

机器可读记录：[publication_verification.json](results/publication_verification.json)。原探索副本的历史独立审计：[exploration_verification.json](results/exploration_verification.json)，其中元数据资产哈希对应原探索快照；本分支当前资产以发布验证及 ASSET_MANIFEST 为准。

## 数值规范化

探索阶段少量训练标准差继承了 NumPy 2 中间值。发布包按 NumPy 1.24.4 重建正尺度，最大差 8.48e-9，保留原阈值及策略；这是正比例重缩放，不改变阈值零的决策。所有 54 行指标与 bootstrap 区间已重新核对。记录见 [numerical_normalization.json](calibration/numerical_normalization.json)。

## 不应扩大解释的边界

- 这是阈值协议变体，不是对最终分数重新最大化 Seen-BA。原协议版本四项主要指标是 14/15。
- 方法探索已查看过当前测试集；参数校准只用验证数据，不足以排除算法设计受到测试结果影响。这不是独立留出确认。
- 组合解析规则与数据构建一致，当前路由恰好对应 Seen/Unseen；需要独立构建的数据验证。
- 15/15 是当前点估计通过，不代表每项变化统计显著或新数据永不下降。固定校准 bootstrap 不覆盖方法搜索的不确定性。
- Seen 回升导致 Gap 增大；A1/A2_alt 的 Unseen<0.60 仍存在。RR 是拒绝比例，不按越高越好处理。
- 使用历史缓存与原始定位提交，不复训 backbone，不重新编码原始视频；没有新增训练权重，但包含冻结解析器、参考统计、验证超参数和阈值。
