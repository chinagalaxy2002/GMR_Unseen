# A/A1/B 最小验证：当前执行范围

本文件记录 A/A1/B 阶段的执行范围。阶段已完成，观测值见[实验报告](report/REPORT.md)，当前状态见[状态页](report/DECISION.md)；恢复入口见 [RECOVERY_PROMPT.md](RECOVERY_PROMPT.md)。

## 核心问题

在 primitive 本身已经相关的情况下，joint visual interaction 是否提供跨未见语义仍然有效的额外证据？

本阶段不是直接构建最终模型，也不拟合 primitive-residual R。顺序为：最少量输入合法性检查 → SlowFast 动作可读性 → token/span 与双流时间对应完整审计 → H/P/C/J/T 小模块 → 冻结候选上的局部定位读出 → 决策。

## 允许与禁止

| 允许 | 本阶段不执行 |
| --- | --- |
| 原 S_train 上的诊断 probe 和 H/P/C/J/T 小模块拟合 | 原骨干、原 GMR、decoder、边界头或完整模型训练 |
| 原 train/seen/training-side pseudo 的只读输入、覆盖和标签审计 | 发布包真实 U/test、额外正式划分/骨干/多 seed |
| 原 S+ GT 用于训练与动作 probe；GT 用于最终指标计算 | GT 推理选窗、S+ 窗外全负、伪造跨视频 absence |
| 冻结原候选上的 map 重排和 raw 定位检查 | 新候选生成、边界回归、联合 shared-map 方法训练 |
| 简单单流/静态、actual-text 和合法时间扰动控制 | R/null/残差拟合、ISA/TORC/CPR/MoE、全套 inversion 辅助训练 |
| 全部新增实现/缓存/日志/结果写在新目录 | 改其他目录代码、启动旧队列、补 sit 或部署 |

初始范围固定原 A1/QD、seed3407、throw/open_close/sit 已有训练侧视图。发布划分 A1 与阶段 A1 动作 probe 应明确区分。三族主要是动作留出，不足以单独支持组件已见的组合泛化；本次不新增组合训练视图。

## 前置诊断与最小矩阵

动作 probe 使用原 S+ GT 内的 SlowFast，拟合仅用 S_train；appearance-only、时间均值/静态及 masked-query 文本控制用于排查物体/语言捷径。不能把答案 verb 本身输入 text-only probe，不能在未见 verb 标签上拟合闭集分类器。失败仅限制本次可读性，不证明所有表示读出都无信息。

随后核验缓存 token 的 BPE/特殊 token/截断、角色与原句对齐。实际两流为 `[CLIP512 | SlowFast2304]`，TEF 单列，不进入 primitive 语义路径；保留投影前 raw streams，核对真实时间来源。单个已有样本的维度检查和 min_len 相等不能替代完整审计。

| 模块 | 作用 |
| --- | --- |
| H | 完整 query 与双流的 holistic 局部 map |
| P | 动作/实体响应的加性 primitive map |
| C | 同时间响应的简单 AND map |
| J | 直接依赖 visual values 的局部 joint interaction map |
| T | 纯文本存在控制；无真实时序视觉 map，定位记 NA |

P/C 可复用事先定义的 primitive 表示，但必须记录哪些参数共同训练/独立拟合，不能让其变成明显弱于 J 的容量或监督控制。首版只冻结一个主聚合和有限训练上限，checkpoint 只用 seen 选择，不在 pseudo 结果上改定义。原模型前向允许，原参数保持冻结；新增 probe/head 拟合确实是训练，应如实计数。

## primitive 条件证据

总体 AUROC 不能独立回答科学问题。原事件标签与元数据足够时，报告经原证据确认的 primitive 相关而事件缺席子集。S− 不自动提供这种标签。

缺少直接标注时，可以使用只在 S_train 定义的 primitive 支持匹配/分层作为操作性控制；覆盖、规则、匹配误差和 primitive 可读性单列。该结果仍不能冒充人工确认的对象身份绑定。规则不能按 J 的 pseudo 得分选择；无有效对照时结论为未决。

相同实际文本特征/mask 的跨视频控制排查语言先验；只有字符串相同不算控制成立。使用共同原视频 bootstrap，query/pair 权重和端点处理显式记录，组合对数不是独立样本量。

## B 中的真实定位验证

局部 map 在冻结原候选内做固定汇聚并重排，GT 不进入选窗。对 H/P/C/J 使用同一读取机制，融合只在 seen 冻结。评估完整 pseudo 正例集合的 raw R1@.5，给 J 对原排序及对 H/P/C 的差值、修复/破坏和无正确候选覆盖。

峰入 GT、GT 内平均 AUC、oracle 覆盖和 S+ 候选 PairAcc 都是辅助，不能替代真实定位增益。query 共同 scalar 不能改 raw 排序；重排不能修候选缺失。此无边界更新的读取实验是 B 的诊断，不是下一阶段完整 shared-map 联合训练。

## 决策与阶段出口

| 结论 | 判定 | 后续 |
| --- | --- | --- |
| STOP | 有效输入、控制和覆盖下，J 未带来超过 H/P/C/T 的额外可迁移视觉证据 | 停止该版本，不扫系数/加损失挽救 |
| INCONCLUSIVE | primitive 条件覆盖、时间/文本对齐或统计精度不足 | 记录未决及限制，停止；不以不显著等同否定 |
| PASS_FOR_NEXT_STAGE_PROPOSAL | J pseudo AUROC 优于 H/P/C/T，paired 差值支持增量；primitive 条件/actual-text 支持视觉贡献；无 GT map 对 raw 定位也有收益，seen/拒绝护栏满足 | 只提出共享 map 下一阶段，不自动运行 |

报告总体与逐族、1000 次 seed3407 共同原视频 paired bootstrap、等权族汇总及原护栏。开发阶段仍为探索性；点估计不等式本身不等于机制成立。仅单任务改善或 GT 条件有效不能判 PASS；不得用 seen 退化缩小 gap。

成功也不触发 R/C/D：用户本次明确只开始 A/A1/B。下一阶段的盈余、shared-map 联合训练和正式 U 确认都不在本指令范围。

## 运行记录与交付

执行前保存 EXECUTION_FREEZE.json：来源/模型 hash、合法数据视图、模块结构/参数量、聚合、监督、优化器与轮数上限、选择规则、覆盖规则、指标和预算。随后维护 STATUS.json，记录各项 pending/running/completed/failed/blocked/skipped 及原因，继续时读取状态而不重复已完成任务。

建议产物：`audit/`、`code/`、`configs/`、`runs/minimal_validation/`、`report/REPORT.md`、`report/DECISION.md`。这些是未来布局，目前没有对应运行产物。全过程保护原代码/资产 hash，处理原 loader 缺特征日志、pycache 和临时目录副作用。所有代码与产物在本新目录，原 plan 只同步 Markdown 状态。
