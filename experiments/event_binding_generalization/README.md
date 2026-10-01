目录导航：[实验与结果索引](ARTIFACT_INDEX.md) · [复核与复现](REPRODUCE.md)。

更新 2026-10-01T13:56:45.080110+08:00：**A/A1/B 已完成，结论 INCONCLUSIVE；本阶段停止，未启动 R/共享 map 完整训练。**

本轮结果见 [REPORT.md](report/REPORT.md)、[DECISION.md](report/DECISION.md)、[STATUS.json](STATUS.json)。新增代码与全部产物仅位于本目录；旧队列和原代码/数据均只读。下方方案/历史状态保留为执行前记录，当前状态以上述报告为准。

---

# 事件绑定证据与存在定位共同泛化

创建：2026-10-01。状态：**方案已建立，尚未执行新诊断、读出器拟合或方法训练。**

2026-10-01 文献/源码修订：已核验用户指定八篇论文，静态阅读可确认的官方代码及本项目源代码，并只读检查一个原 train 特征样本；没有模型前向/拟合。方案现在依次验证动作可读性、单对视觉非退化的 joint、primitive 条件增量和共享 evidence map。

本目录由原 `experiments/new/` 空目录改名为 `experiments/event_binding_generalization/`。研究承接 correspondence_generalization 的两项已完成工作，但使用独立方案和未来产物，不恢复旧队列。

**最新范围限定：** 清空上下文后仅开始 A/A1/B 最小验证：先检查 SlowFast 动作可读性，再完整核验 token/span 和双流时间对应，然后只拟合 H/P/C/J/T。B 包含冻结原候选上的无 GT 定位读取检查；不做 R、下一阶段 shared-map 联合训练或完整模型训练。恢复入口见下方。

研究路线：动作运动证据 + 实体外观证据 → 事件绑定证据 → 相对于 primitive 的证据盈余；检验同一张时序 evidence map 能否同时改善未见语义的 localization 和 existence。

首要问题是：在仅用已见语义训练的条件下，显式 joint evidence 是否比 holistic score 和独立 primitive 的组合更能区分未见事件正负例？绑定缺失和盈余有效性均为待验证假设。

- [完整研究方案](EXPERIMENT_PLAN.md)：已有证据、研究问题、最小实验矩阵、统计及停止规则。
- [清空上下文后直接复制的指令](RECOVERY_PROMPT.md)与[当前 A/A1/B 范围](MINIMAL_VALIDATION_SCOPE.md)：优先于完整方案中的后续构想。
- [候选框架](METHOD_SPEC.md)：证据形成、primitive-only 对照、共享 map 的两条输出路径及监督边界。
- [交接与状态](HANDOFF.md)：下一步顺序、尚待冻结的实施选择、执行边界。
- [八篇论文关注重点核验与修订依据](research/LITERATURE_REVIEW.md)：包含 HRVTG 开源状态更正、IAE 已有拒绝/组合泛化及各方法资源边界。
- [当前工程源码与输入核验](research/PROJECT_SOURCE_AUDIT.md)：流顺序、时间对齐、token 映射及隔离副作用。
- [原项目总方向](../correspondence_generalization/plan/EXPERIMENT_PLAN.md)与[框架补充](../correspondence_generalization/plan/EVENT_BINDING_FRAMEWORK.md)。

本次授权与交付为目录和方案文档。没有启动训练、前向、评测或正式 U 确认，没有改动模型、数据、特征、旧结果及停止队列。

**代码隔离约束（用户明确要求）：** 本目录就是原 `new` 改名后的新工作目录。后续新增训练、评测、部署代码及脚本、配置、日志、缓存和模型产物全部保存在本目录内；其他目录的任何代码均不得修改。可以只读引用原数据、特征、checkpoint 和代码；需要适配原实现时在本目录内复制/封装并记录来源，不回写来源文件。原项目 `plan/` 仅维护用户要求的 Markdown 方案和入口。
