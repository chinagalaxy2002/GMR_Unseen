# 清空上下文后的执行指令：只做 A/A1/B 最小验证

状态：本文件是可复制的执行指令；当前仅保存指令，未启动诊断、拟合或训练。以下范围优先于旧方案中关于 R/C/D 或后续模块的描述。

清空上下文后，将下面整段复制给新会话。

```text
请开始事件绑定方向的 A/A1/B 最小验证，并持续完成到最终报告与停止/未决/通过建议；不开始完整模型训练，也不自动进入下一阶段。

唯一新代码与产物目录：
/home/guoxiangyu/paper/Openword/generalized-moment-retrieval/experiments/event_binding_generalization
它就是原 experiments/new 改名后的目录。所有新增代码、配置、训练/评测脚本、缓存、日志、临时文件和模型产物都放在这里。其他目录任何代码、原数据/标签、特征、checkpoint、旧结果和停止队列一律只读。原 correspondence_generalization/plan 仅可同步 Markdown 交接，不得修改其中的代码或启动旧队列。

先阅读新目录的 README.md、MINIMAL_VALIDATION_SCOPE.md、HANDOFF.md、EXPERIMENT_PLAN.md、METHOD_SPEC.md、research/LITERATURE_REVIEW.md 和 research/PROJECT_SOURCE_AUDIT.md；按需参考 correspondence_generalization 的第二阶段 DECISION.md。已有文献核验和历史诊断不重复执行；检查当前状态，已有本阶段有效产物则从未完成处继续，不重置任务。

本阶段唯一科学问题：
在 primitive 本身已经相关的情况下，joint visual interaction 是否提供跨未见语义仍然有效的额外证据？

按以下顺序执行：
1. 先做最少量特征/标签来源检查，保证读取合法；然后检查动作是否真的可从冻结 SlowFast 中读出。只在原 S_train 拟合小 motion-only segment→verb probe，并与 appearance-only、静态/时间均值等必要控制比较。原 S+ GT 只用于训练和动作诊断，不进入实际 existence/localization 推理。闭集分类词表只来自 S_train，不能用 held-out verb 标签拟合测试类别；覆盖不足记未决。
2. 再完整检查 query token/span 分解、BPE/SOT/EOT/截断、正负缓存来源和双流时间对应。实际输入顺序为 CLIP512 | SlowFast2304 | TEF2；在原统一投影前保留两流，不任意拆融合 hidden。min_len 截断不等于时间对齐，无法核实时间来源则标明假设并限制结论。
3. 前置条件可测后，只拟合 H/P/C/J/T 五种小模块：H=完整 query 的 holistic 局部读出；P=加性 primitive；C=同时间 AND；J=显式视觉交互；T=纯文本控制。原骨干和原 GMR checkpoint 全部冻结。J 在单 noun–verb 对时也须直接依赖 visual values；不照搬可能退化为文本常数的 pair softmax 路径。相近容量、相同原事件监督、相同有效时间 mask 和主聚合；一次冻结宽度、优化器、轮数上限、checkpoint 选择和主读出，不扫超参或后看 pseudo 挑公式。

范围：原 A1/QD、seed3407，沿用 throw/open_close/sit 的原训练侧留族视图。每族仅其 S_train 拟合，seen validation 选择/校准，training-side pseudo 用于冻结方案的探索性验证。这里发布划分 A1 与阶段 A1 动作诊断不是同一概念。sit 不补训练，不读发布包真实 U/test；不另建组合留出训练、不扩展正式 C1/C2、多 seed 或同预算成对核验。

必须回答 primitive 条件问题，而非只看总体 AUROC：
- 先审计原标签/元数据能否确认 primitive 相关但完整事件 absent 的样本。S− 只确认完整事件缺席，不能推出动作或实体缺席，也不能自动确认两者存在。
- 若只能用 S_train 定义的 primitive 分数匹配/分层，固定规则后应用到 pseudo，并明确这是 operational score control，不是人工确认的真实 primitive/binding 标签；不据 J 的结果挑样本。
- 全局 pseudo AUROC 之外，报告该条件子集/匹配分析、相同实际文本跨视频控制、覆盖、J 对 H/P/C/T 的 paired 差值与不确定性。缺少有效控制或覆盖不足应记未决。

局部 map 的真实定位检查属于 B 的必要输出：
只对冻结原模型的既有候选，用各模块 map 在候选窗内的固定汇聚作 candidate-specific 重排，评估所有原 pseudo 正例的 raw R1@0.5；H/P/C 同样应用该读出。先在 seen 数据固定读取/融合规则，再用于 pseudo。GT 仅评估命中，不参与选窗。保留原全正例分母、候选缺失和修复/破坏统计，不把峰入 GT、GT 条件 AUC 或 oracle 当实际定位增益。此检查不训练 decoder、边界回归或新的 shared-map 完整模型。

统计沿用 seed3407、1000 次共同原视频 paired bootstrap、族等权；报告总体和逐族、paired J−H/P/C/T 与定位差值。pseudo 是开发证据，不是正式 U 确认；单 seed 不宣称跨训练种子稳定。保留原 seen/拒绝护栏，不通过降低 S 表现或更有利阈值宣称成功。

当前不做：R/primitive-residual/null 拟合、共享 map 的联合完整训练、边界生成/回归、ISA/TORC/CPR/MoE/VC/AR/VD 新训练、额外教师、新骨干/特征提取、像素级 prompts、测试时更新、正式 U 确认、独立 VTG 新训练或部署。

在运行前写独立 EXECUTION_FREEZE.json 和小模块预算；维护 STATUS.json 与运行记录，保存失败和修订。代码隔离要覆盖导入副作用：原 loader 会在 data_path 旁写缺特征日志；新 wrapper 接管日志或使用新目录内 hash 相同的视图副本，pycache/临时路径也留在新目录。冻结配置、合法只读检查和范围内的小模块实现可自主完成，不因已有授权反复询问；缺少不可推断的必要资源时准确记录阻塞，不伪造结果。

最终报告只给三种结论：
STOP：控制与覆盖足够，而 J 没有额外可迁移证据；停止该版本，不堆损失挽救。
INCONCLUSIVE：输入/对齐/primitive 条件覆盖或统计精度不足；停止本阶段，明确未决，不能当机制已否定或已成立。
PASS_FOR_NEXT_STAGE_PROPOSAL：J 的 pseudo AUROC 高于 H/P/C/T，paired 差值支持该增量，primitive 条件与实际文本控制支持视觉贡献，同时无 GT 的局部 map 对 raw R1@0.5 有真实增益且护栏满足。此结果只允许提出下一阶段方案，不自动执行下一阶段。

若总体 AUROC 更高但 primitive 条件控制无支持，或只改善定位/只在 GT 条件有效，不能判 PASS。不同族证据不一致如实报告，不挑族加权或泛化成组合/身份绑定已成立。

交付代码、冻结配置、覆盖审计、逐行预测、paired 统计、最终 REPORT.md 和 DECISION.md，并同步新目录 HANDOFF/README；原 plan 只更新 Markdown 入口与状态。完成本阶段后结束，不自动继续 R/C/D 或完整模型训练。
```
