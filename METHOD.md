# DEC-Power-CDF + Seen Guard

原 DEC 的全域证据乘法改善了 Unseen 排序，也会降低正常 Seen 查询的分数并改变其排序。Seen Guard 用训练查询的语义覆盖范围决定是否施加这类约束：训练覆盖的查询接受 Seen 验证保护，未覆盖查询保留原 DEC。没有新训练权重，但需要训练经验分布、验证校准和冻结的文本解析器。

![Algorithm overview](figures/algorithm_overview.svg)

[完整伪代码与图注](docs/ALGORITHM.md)；[原 DEC 证据定义及历史修正](docs/DEC_REFERENCE.md)。

## 1. 原 DEC

中点经验 CDF 为 `F_R(z)=(#{r<z}+#{r<=z})/(2|R|)`。分别用训练样本拟合检测器和证据的参考分布，令 `x=F_d(d)`、`y=F_E(E)`，则 `s_D=x^0.65*y^0.85`。

原证据 E 的有序子串路由、通道及固定权重保持原分支定义。它含场景、视觉显著性、物体对齐、速度对比和有符号状态变化，不是纯动态证据，也不是动作发生的因果证明。最终主方法只使用当前骨干自身的检测器分数，没有采用多骨干融合候选。

## 2. 查询覆盖路由

固定 `en_core_web_sm 3.8.0` 提取首个非辅助内容动词及其直接宾语或介词宾语，沿用 `shut→close` 与 take/put/pick 的小品词规则。训练正例建立动作—物体组合表 I；`covered(Q)=1[p(Q)∈I]`。缺失动作/物体时采用未覆盖分支。

推理只读取查询文本和训练统计，不读取目标 semantic_graph、存在性标签、Seen/Unseen 分区、留出名单或划分规范。解析器沿用了基准构建规则，在当前五个划分上路由恰好对应 Seen/Unseen；这不是独立验证过的通用 OOD 检测器。

## 3. 覆盖查询的冻结策略

**融合。** 搜索 41 个 `alpha∈{0,0.025,...,1}`：`f_alpha=(1-alpha)*x^0.65+alpha*s_D`。各候选采用原 91 个百分位的 Seen-BA 阈值。先要求 Seen AUROC≥Baseline，Seen G/F≥Baseline 与 DEC 两者；可行池中选择与原 DEC 验证分数均方距离最小者。没有完整可行解时仅要求 AUROC，并在后续触发决策保留。如果 FRR 也不高于 DEC，则冻结融合策略。当前 13 个设置采用融合。

**FRR 约束 Baseline。** 若主要保护条件通过但 FRR 失败，保持原 d 排序，在同样 91 个 Seen 验证阈值中最大化 BA，要求 G/F≥DEC，FRR≤DEC−5 pp。当前触发 C1/QD，阈值为 `0.9466999769210815`。5 pp 是验证校准预算，不是未知测试分布上的概率保证。

**DEC 决策保留。** 若主要保护条件失败，固定 `A_D=1[s_D>=tau_D]`，定义 `m_K=(2*A_D-1)+0.25+atan(d)/(2*pi)`。后半项严格递增且落在 `(0,0.5)`，因此决策不变，接受组和拒绝组内部按检测器排序。回退须先在 Seen 验证集达到 Baseline AUROC，否则校准报错。当前触发 C2_alt/QD。

## 4. 输出与阈值

未覆盖查询使用 `m_D=(s_D-tau_D)/sigma_D`，tau_D 是原 DEC Seen-BA 阈值，sigma_D 是正的训练标准差，保留原 DEC 排序和决策。融合与 FRR 约束策略也用 `(score-threshold)/positive_train_scale` 映射到零。最终按覆盖状态选择 m_K 或 m_D，`S>=0` 接受；保留原骨干第一个合法窗口，拒绝则置空。

**不再对最终混合分数重新最大化 Seen-BA。** 重新选择阈值会破坏决策保持保证。这是显式阈值协议变体，不能称为原 final-score Seen-BA 协议下全部达标；原协议版本的四项主要指标为 14/15。

CDF 秩与最终边距不是发生概率。没有新增可学习权重，不意味着无校准：融合超参数、阈值、经验分布及固定预训练解析器仍是方法组成部分。

## 5. 复现与边界

`calibrate_seen_guard.py` 只读取 train/Seen-val、文本解析缓存及 Seen 验证原窗口 IoU，不读取 test。新增 `val_quality.npz` 是与 val qid 对齐的原生窗口集合 IoU，只用于校准约束。

数值环境固定 NumPy 1.24.4；解析环境单独使用 NumPy 2。历史探索部分训练标准差继承了 NumPy 2 的中间结果；发布包统一重建正尺度，最大调整约 8.48e-9，原阈值与策略保持。正比例尺度变化不改变阈值零的决策；当前全部点估计及 2,000 次 bootstrap 区间保持一致。详见 `calibration/numerical_normalization.json`。

全部 15 个设置的当前点估计通过六项检查：Seen AUROC≥Baseline，Unseen AUROC与原 DEC 相同，G-mIoU/Rej-F1≥DEC，Seen FRR不升，Unseen FRR相同。[完整结果](results/FULL_RESULTS.md)提供逐设置与宏平均区间。

测试集已在七轮方法探索中反复查看。参数只用 Seen 验证数据确定，不等于整个算法设计从未受测试结果影响。本发布是探索性复现，需要独立留出确认；固定校准 bootstrap 不覆盖方法搜索不确定性。

Seen 回升而 Unseen 不变时 Gap 必然增大，未保留原 DEC 中由 Seen 下降带来的 Gap 缩小。A1/A2_alt 仍有 Unseen<0.60 的设置。本分支复现缓存后处理与定位提交评测，不包含视频重训或重提特征；局部证据仍共享历史 HQ 候选，窗口来自各骨干自身提交。
