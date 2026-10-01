# 交接：事件绑定证据与存在定位共同泛化

更新：2026-10-01。状态：方案完成，执行未开始。

本轮已按用户八篇重点清单做全文/可得源码核验，并检查一个原train样本特征metadata。研究核验已完成；新增模型前向、probe拟合和训练仍未执行。详见[综述与清单更正](research/LITERATURE_REVIEW.md)、[工程源码审计](research/PROJECT_SOURCE_AUDIT.md)。原方案已单独上传GitHub快照，修订版本同步状态见本地上传记录。

## 用户方向

不以 local sigmoid 的绝对尺度改进为主线。先验证动作运动与实体外观是否形成可迁移事件绑定，再验证相对于 primitive 的证据盈余，最后检验同一 evidence map 对 localization/existence 的共同作用。

本轮用户明确要求建立新目录方案并补充 correspondence_generalization/plan；已将空 new 目录改名为 event_binding_generalization，并交付 README、EXPERIMENT_PLAN、METHOD_SPEC、HANDOFF。没有授权范围内遗漏的训练任务；本次未启动诊断/拟合/前向/训练。

## 阅读顺序

1. [README](README.md)及[完整方案](EXPERIMENT_PLAN.md)。
2. [候选框架](METHOD_SPEC.md)。
3. [原项目总方向](../correspondence_generalization/plan/EXPERIMENT_PLAN.md)及[第二阶段决策](../correspondence_generalization/2026年9月30日_存在与定位共同泛化的机制诊断/DECISION.md)。

## 若后续进入实施

用户进一步明确：训练、评测、部署的所有新增代码只能放在原 `new` 改名后的本目录；不修改其他位置任何代码。配置、日志、缓存、临时构建与模型产物同样留在本目录。原实现只读引用，适配须在本目录复制/封装并记录来源。原 `correspondence_generalization/plan/` 只更新用户要求的 Markdown 文档。

先执行方案阶段 A：特征/文本对齐、primitive 和绑定负例覆盖审计。明确范围后再拟合阶段 B 的 H/P/C/J/T 小模块；J 有效才考虑 R。原模型冻结也不代表新读出器零训练。

加入A1动作可读性门槛：motion-only S+ GT segment→verb，对照静态/appearance/文本。原三族仅留动作，不能当完整组合泛化证据；先审计训练侧pair覆盖，不自动增加正式C组。输入raw双流在统一投影前保留，cached token对齐需重建BPE映射。

每项执行前创建独立 freeze、来源 hash、预算和状态，保存失败；当前无此类运行产物。不恢复旧 stopped 队列，不补 sit，不读取真实 U，不修改原数据、特征、checkpoint、旧结果或第一阶段成绩。

## 最容易误读的点

- 已有结果没有证明绑定缺失；只能据此优先检验新假设。
- IAE-VTG 已做动作/实体与运动/外观绑定。本方案潜在贡献是严格未见语义事件存在及共同作用，不是分支设计本身。
- IAE还做了NA-VMR拒绝及Novel-C/Novel-W；不能仅以拒绝/组合/两个输出当差异。单对退化是公开公式推导而非实际作者代码bug结论，新J必须保留visual values。
- co-occurrence、clip 级 joint、实体身份绑定不等价。
- S− 的完整事件 absent 不意味着其 primitive absent；扰动也不自动成为负标签。
- 盈余是需要 null 和尺度约束的假设，不能直接减三个无关 sigmoid；J 有效而 R 无效时放弃盈余。
- 共享 map 不自动保证共同收益；原候选重排不能补几何缺失，query scalar 不能改变候选排序。
- 只有 GT 条件读出或定位单项变好不能宣布总目标完成。
- HRVTG已公开官方论文和代码；在线LoRA与主轨不兼容，但不能误称reward直接读test人工GT。EVIDENT/ActPrompt要求更细输入；EviDETR是MR/HD，不是existence。
- 隔离覆盖loader/import副作用；原dataset的missing-feature日志默认写data_path旁，新wrapper必须接管。

当前三项优先工作：覆盖审计；H/P/C/J/T 对照定义；J 成立后再冻结 R 和共享输出最小干预。人员时间、设备预算未知，不承诺运行耗时。

修订后的顺序为：输入/负例与语义轴审计→动作可读性→非退化J及H/P/C/T+单流/静态对照→J成立后R→共享map共同验证。不同时堆ISA/TORC/CPR/MoE/VC/AR/VD。
