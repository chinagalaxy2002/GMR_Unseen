# 框架补充：事件绑定证据与存在定位共同泛化

更新：2026-10-01。状态：新方案已建立，尚未执行；不覆盖两项已完成工作的结论。

本轮新增论文/源码核验已经完成，模型诊断、读出拟合和训练仍未执行。[八篇清单及综述](../../event_binding_generalization/research/LITERATURE_REVIEW.md)与[工程输入审计](../../event_binding_generalization/research/PROJECT_SOURCE_AUDIT.md)是以下修订的证据入口。

## 方向调整

根据用户判断，将“local sigmoid → 统一 absolute scale → existence”降为非主线，优先验证：

\[
\boxed{\text{动作运动证据}+\text{实体外观证据}
\rightarrow\text{事件绑定证据}
\rightarrow\text{相对于 primitive 的证据盈余}}
\]

随后由同一时序 evidence map 分别服务 localization 和 existence。最终存在分数及 seen-only 阈值仍需可迁移，但不预设标尺校准是主要研究贡献。

## 与已有证据的关系

第一阶段没有 GMR 共同收益；第二阶段候选 foreground/几何支持及简单时序读出未建立稳定无 GT 视觉支持。局部 GT 条件信息仍有有限可读性。这些发现支持另检验证据形成机制，**不证明动作—实体绑定缺失，更不证明新路线已有效**。

## 框架与最低对照

冻结原 CLIP/SlowFast 特征，以角色条件读出构造 A_t、E_t，再形成视觉条件 joint J_t。先比较 holistic H、加性 primitive P、简单同时间 AND C、joint J 和纯文本 T。J 支持后再检验 primitive 条件盈余 R，不预设 R 必须优于 J。

修订后在绑定前加入原S+ GT上的motion-only动作可读性probe，对照appearance/static/时间均值与masked-query文本控制。动作可读性和事件绑定是不同门槛；原三族仅留动作，不足以单独声称组件已见的组合泛化。先审计训练侧pair覆盖，不自动扩展正式组。

新J须在单noun–verb对时仍依赖raw visual values/residual，多对保留pair-conditioned visual interaction。公开IAE公式在单对softmax+marginal-only路径可能退化为文本常数，这是本轮公式推导，不是已核实作者代码错误。首版在原统一投影前保留CLIP/SlowFast，不能把融合hidden任意切成动作/实体。

盈余概念为 J_t−b_S(A_t,E_t)，b_S 仅在原 S train 上拟合并与 J 同单位；它不是三个独立 sigmoid 的任意相减。残差外推、primitive 混杂和纯文本解释必须审计。保留真实事件的 primitive 支持，不强制残差单独充当存在证据。

所有差值在同时间索引/候选窗支撑上计算，禁止分别max的不同primitive峰值相减；盈余是待验证的操作性增量，非已证明的概率/PMI/因果证据。clip间共同逆序/乱序与单流错位分别检查order和alignment，不给扰动自动赋absence。

同一 map 的定位路径保留时间结构并影响候选排序/边界；存在路径使用所有正负样本一致的无 GT 聚合。query 共享 scalar 不能改善 raw 排序，原候选重排不能修复候选缺失。

H局部map/pooled scalar控制evidence flow与global relevance；only-loc/only-exist、bypass和primitive替换检验共享作用。detach只检验训练耦合，遮挡是OOD敏感性而非因果中介证明；首版不叠MoE、ISA、TORC、CPR或整套生成辅助目标。

## 执行和科学边界

- 用户明确要求全部新增训练/评测/部署代码及配置、日志、缓存、构建和模型产物只放在原 `new` 改名后的新目录；其他目录代码一律只读。原 `plan/` 仅补充 Markdown 方案和入口；需要适配原实现时在新目录复制/封装，不回写原代码。
- 原loader缺特征日志会写到原data_path旁；新wrapper必须接管日志、导入缓存和临时文件等副作用，不能只靠脚本位置实现隔离。原文本缓存无token IDs，BPE/角色对齐和双流时间来源须核验。
- 先审计 token/span 对齐、双流时间对应和原负例覆盖，再限定小模块验证；当前只完成方案文档。
- 原 S− 只确认完整事件 absent；不新增跨视频负标签，不将 S+ 窗外全标负，不给动作/实体分支伪造 absence 标签。
- 时间错位/stream 重配只作扰动控制，不能自动当已标注绑定负例。
- pooled clip 证据先对应时间级 joint；对象身份/施事受事绑定在无空间证据时未验证。
- 初始 A1/QD、seed3407、throw/open_close/sit 原训练侧留族，sit 不补训练；真实 U 不用于开发。旧队列保持停止。
- 共同 AUROC+raw、gated 与 seen/拒绝护栏沿用；独立正例 VTG 界定迁移范围。
- J 不优于 H/P/C 时停止该绑定版本；R 不优于 J 时放弃盈余；只改善单任务或仅有 GT 条件信号不算共同成功。

## 文献定位和详细入口

IAE-VTG（Zhao 等，2026）已做动作/实体绑定、NA-VMR拒绝及Novel-C/Novel-W；RaTSG（Dong 等，2024）已联合存在反馈与定位。本方案差异须通过严格协议和primitive-conditioned视觉增量建立，不能仅凭共同输出或未见组合命名宣称创新。

RCORE已确认object-driven verb shortcut及TORC/CPR机制；Invert4TVG inversion指任务逆置；ActPrompt和EVIDENT需要encoder内部/空间dense证据，不能直接移植原pooled特征。CausalVTG提供global relevance对照；EviDETR为MR/HD证据流而非存在验证；HRVTG官方PDF/代码已公开，原清单闭源说法需更正，其在线LoRA仍不属于固定推理主轨。详细全文、版本、源码证据和限制见[核验综述](../../event_binding_generalization/research/LITERATURE_REVIEW.md)。

新目录为 [event_binding_generalization](../../event_binding_generalization/README.md)，原 `experiments/new/` 为空，已改名。单一详细方案维护于该目录，原 plan 只补充方向与入口：

- [完整实验设计](../../event_binding_generalization/EXPERIMENT_PLAN.md)
- [候选框架及实施前技术冻结项](../../event_binding_generalization/METHOD_SPEC.md)
- [状态和后续交接](../../event_binding_generalization/HANDOFF.md)
