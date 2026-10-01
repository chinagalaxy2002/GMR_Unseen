# 研究恢复入口

更新：2026-10-01。先读[总方向](EXPERIMENT_PLAN.md)、[事件绑定框架补充](EVENT_BINDING_FRAMEWORK.md)，再读[新方案](../../event_binding_generalization/EXPERIMENT_PLAN.md)和[新目录交接](../../event_binding_generalization/HANDOFF.md)。旧诊断细节参考[第二阶段详细交接](../2026年9月30日_存在与定位共同泛化的机制诊断/plan/HANDOFF.md)与[决策](../2026年9月30日_存在与定位共同泛化的机制诊断/DECISION.md)。

第二阶段训练已停止；三族评测收尾、固定读出、候选排序/几何、支持桥接与冻结时序表示诊断均已完成。原NEXT_TASK已完成，不能作为待执行任务重跑。旧恢复prompt只用于查看历史阶段，不作为新路线执行入口。

用户要求基于新判断建立方案，已将空experiments/new改名为experiments/event_binding_generalization，写好研究设计与候选框架。新路线优先验证动作/实体joint相对holistic及primitive控制的增量，再检验盈余与同一map的共同输出。绑定缺失尚未证实，IAE-VTG已做相关绑定机制，不能把双分支本身当首次贡献。

当前新方案状态为planned；没有新增训练、前向、拟合或评测。后续先做输入/语义分解/原负例覆盖审计，再明确小模块实施范围。用户明确要求全部新增训练、评测、部署代码及配置、日志、缓存和产物只写在新目录；其他目录任何代码均不得修改。原plan仅维护本次要求的Markdown方案和入口。

用户后续要求上传并按八篇论文及源码修订：研究核验已完成，包含全文、官方可得代码和一个train输入metadata样本，仍无模型前向/拟合。更新顺序为输入/覆盖→动作可读性→非退化J与H/P/C/T及单流/静态→J成立后R→map共同验证。IAE拒绝/组合重叠、HRVTG开源及额外资源边界见[综述](../../event_binding_generalization/research/LITERATURE_REVIEW.md)。原方案已有独立GitHub快照；修订上传由新目录的本地记录追踪，不修改本机主分支/索引或其他未提交工作。

总目标仍为GMR未见AUROC与raw定位共同改善、gated最终收益与seen/拒绝护栏；独立VTG用于界定迁移范围。目前不进入复杂训练或正式确认，后续训练不因历史授权自动执行。任务细节与状态只在阶段目录维护。
