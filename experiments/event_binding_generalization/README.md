# 事件绑定证据与存在定位共同泛化

创建：2026-10-01。状态：**方案已建立，尚未执行新诊断、读出器拟合或方法训练。**

本目录由原 `experiments/new/` 空目录改名为 `experiments/event_binding_generalization/`。研究承接 correspondence_generalization 的两项已完成工作，但使用独立方案和未来产物，不恢复旧队列。

研究路线：动作运动证据 + 实体外观证据 → 事件绑定证据 → 相对于 primitive 的证据盈余；检验同一张时序 evidence map 能否同时改善未见语义的 localization 和 existence。

首要问题是：在仅用已见语义训练的条件下，显式 joint evidence 是否比 holistic score 和独立 primitive 的组合更能区分未见事件正负例？绑定缺失和盈余有效性均为待验证假设。

- [完整研究方案](EXPERIMENT_PLAN.md)：已有证据、研究问题、最小实验矩阵、统计及停止规则。
- [候选框架](METHOD_SPEC.md)：证据形成、primitive-only 对照、共享 map 的两条输出路径及监督边界。
- [交接与状态](HANDOFF.md)：下一步顺序、尚待冻结的实施选择、执行边界。
- [原项目总方向](../correspondence_generalization/plan/EXPERIMENT_PLAN.md)与[框架补充](../correspondence_generalization/plan/EVENT_BINDING_FRAMEWORK.md)。

本次授权与交付为目录和方案文档。没有启动训练、前向、评测或正式 U 确认，没有改动模型、数据、特征、旧结果及停止队列。

**代码隔离约束（用户明确要求）：** 本目录就是原 `new` 改名后的新工作目录。后续新增训练、评测、部署代码及脚本、配置、日志、缓存和模型产物全部保存在本目录内；其他目录的任何代码均不得修改。可以只读引用原数据、特征、checkpoint 和代码；需要适配原实现时在本目录内复制/封装并记录来源，不回写来源文件。原项目 `plan/` 仅维护用户要求的 Markdown 方案和入口。
