# 候选框架：事件绑定与 primitive 条件证据

状态：conceptual proposal，未实现、未验证。此文件把框架具体化，尚不充当可直接运行的训练配置。

用户要求代码完全隔离：任何新增训练、评测或部署实现仅位于本新目录（原 `new`，已改名 `event_binding_generalization`），配置、运行日志、缓存与构建产物也保存在本目录；其他目录代码不得修改。原实现只读引用，必要适配在本目录复制/封装并记录来源，不通过修改导入目标或原配置完成适配。

2026-10-01根据[论文/源码核验](research/LITERATURE_REVIEW.md)修订。输入能力诊断先于方法训练，单对视觉依赖和primitive条件控制成为首版必要条件。

## 1. 输入和证据链

冻结外观流 a_t（原 CLIP）与运动流 m_t（原 SlowFast），从原 query 提取动作 token/span v 和实体 token/span n；复杂 query 还需保留施事/受事及关系。原 holistic query 路径作为控制，不因解析失败丢弃样本。

实际原输入按 `[CLIP512 | SlowFast2304 | TEF2]` 拼接，再统一投影到256维。新wrapper在投影前切分原raw streams并作独立映射，不能任意拆融合hidden。TEF不进入primitive语义支持分支，位置偏置单列控制。min_len截断不是时间戳对齐；词到cached BPE token的mapping与SOT/EOT/32-token截断需单独审计。

框架为：

\[
A_t=f_A(m_t,v),\quad E_t=f_E(a_t,n),\quad
J_t=f_J(m_t,a_t,v,n,\text{local temporal context}).
\]

A/E 是角色条件响应，不因命名就成为纯 primitive 概率；CLIP/SlowFast 也不是干净的实体/动作检测器。J 必须访问视觉条件交互；仅用 noun–verb 文本兼容度不足以称为绑定。第一版以局部时间对应为验证粒度，不承诺身份级绑定。

### 单对非退化与 pair 保真

令动作视觉表示 z^A_t、实体视觉表示 z^E_t 保留原视觉 values/residual，例如分别映射 `[m_t, v, local_context(m)]` 与 `[a_t,n,local_context(a)]`；交互读出显式访问这两组视觉表示及其局部关系。pair weights 只能用于聚合该视觉条件交互，不能只加权原 query noun/verb values 后声称获得绑定。

公开 IAE 公式中，单noun×verb对的pair softmax恒为1，后续marginal汇聚只剩文本token；该退化是本轮推导，未经作者源码确认。因此实施前检查固定query不同视频的J可变化、单对J不是时间常数、有效visual gradient路径存在（诊断不更新原模型），并单对/多对分层。响应变化是架构必要性检查，不代表已有正确事件判别。

多对使用 `Σ_(n,v) π_t(n,v) φ(z^A_(t,v),z^E_(t,n),visual_context)` 直接聚合pair-conditioned interaction；独立noun/verb marginals作为控制，避免丢失pair correlation。原pooled输入缺空间身份，因此错误施事/受事样本只能审计能力上限；不添加虚构track或identity监督。

### 前置动作能力检查

先在S+ GT上做motion-only segment→verb可读性probe，与appearance-only、时间均值/静态及masked-query text-only比较。与完整事件存在监督分开；probe没有目标U标签拟合，不引入LVLM/GRPO/新人工标签。冻结特征缺失或无法读出的动作信息不能靠更复杂J保证补回。

## 2. primitive-only 对照与证据盈余

先建立不能显式访问动作—实体联合视觉交互的加性控制：

\[
P_t=u(A_t)+w(E_t).
\]

另设同时间 AND 控制 C_t，用于区分简单共激活与更强 joint。P/C 和 J 在相同原事件监督、同一聚合协议下比较；不把不同任务训练得到的任意 sigmoid 数值直接相减。

证据盈余的研究定义是“primitive-only 模型不能解释的事件支持”，而不是预先固定的 J−A−E。可检验的候选为：

\[
\Delta_t=J_t-b_S(A_t,E_t),
\]

其中 b_S 仅在原 S train 上拟合、以 J 的数值单位预测 primitive 可解释响应；评估前冻结。若采用残差拟合，使用按原视频分组的 out-of-fold 预测训练残差分支，避免同样本拟合残差虚小；fold 数、函数族和容量先冻结。b_S 的外推误差必须报告，不能将 OOD 残差自动解释为绑定。

该公式仅为受控诊断候选：独立训练分数的尺度自由度、共享输入引起的依赖及 null 模型设定都影响残差。先检验 J 对 P/C 的增量，再检验 J+Δ 对 J 的增量。若没有可复现的尺度/拟合约束，暂不实施该 R 臂，结论为盈余尚未具体化。

J、P、b_S 和Δ在同一时间索引/同一候选窗的有效支持集上比较。禁止把 `max J`、`max A`、`max E`（可能来自三段不同事件）直接作盈余。该定义是 operational conditional increment，不等于经验证的概率、PMI、log-likelihood ratio或因果交互；null可能把真实binding一并解释掉，若R无增量应放弃而非扫拟合族。

可补充同一 J scorer 的时序错位对照，破坏两流局部对齐但保留各流边际，用于检查响应是否依赖对齐。错位是分布外扰动，实体持续可见或周期动作可能使其失效；不是天然的负例、事件 absent 标签或可直接部署的基线。具体 null 的选择不可在 pseudo 结果上扫描。

共同两流乱序/逆序与单流错位是不同控制：前者检查clip间order，后者检查跨流对应；预提取SlowFast逆序不逆转clip内方向。方向敏感、重复动作和实体持久性须按原S规则分层。RCORE TORC不直接作为所有动作上的新absence损失，CPR合成物体注入不提供真实事件发生证明。

**不强制 Δ 单独承担所有决策。** 真事件也可能已被 primitives 充分解释而 Δ 很小；不存在事件也可能因 primitive 对照低估而 Δ 很大。保留 J 和 primitive 支持，验证必要性与盈余，避免奖励“两个 primitives 都弱、残差却高”的伪证据。

## 3. 一张 evidence map 的两条输出路径

先采用 J_t 作为共享 map B_t；只有 R 验证通过，才以预先冻结的小融合函数 B_t=F(J_t,P_t,Δ_t) 替换。定位与存在不使用两套独立语义 map。

\[
\text{query, video}\to B_{1:T}\to
\begin{cases}
\text{localization: interval support / temporal representation},\\
\text{existence: fixed global aggregation }G(B_{1:T}).
\end{cases}
\]

- 定位第一步：按每个原候选窗的有效时间位置汇聚 B_t，与原候选分数形成固定融合进行重排；必须是 candidate-specific，query 共享 scalar 不改变 raw 排序。窗几何缺失不能靠重排修复。
- 定位第二步（独立变体）：若排序作用成立但几何仍限制，再将 B_t 接入时序表示/边界回归；记录生成与排序两个作用，保留原定位控制。
- 存在：正负 query 使用同一有效时间 mask 和同一 G；不读 GT，不按正负使用不同搜索范围。mean、max、固定比例 top-k 各有稀释/极值/时长风险，第一版只冻结一个主聚合，其余如需展示列为辅助，不后选有利者。
- 输出接口：保留原存在输出字段、seen-only 阈值和官方 gate 流程；候选分数/存在概率需按原接口约定映射。AUROC 验证排序，FRR/RR 单独验证阈值迁移，不能以“相对证据”绕过后者。

首版至少保留local holistic map（H，控制EviDETR-style evidence flow）及其pooled relevance读出（控制CausalVTG-style global QR），不加MoE或更改匹配。共享map通过only-loc/only-exist/bypass/primitive-substitution消融检验；若map可训练，detach仅检验梯度耦合，不能用遮挡共同掉分宣称因果中介。EviDETR的MR2HD实际服务highlight detection，原配置saliency loss=0，不能冒充等价evidence supervision。

## 4. 训练监督边界

原 S+ GT 内提供事件局部支持，原 S− 整段提供完整 query 事件缺席。存在可用 bag/MIL，定位保留原分类/span/gIoU 监督；具体损失和权重执行前冻结。

原 S− 不提供逐动作或逐实体 absence，原 S+ 窗外不全标负，GT 不进入实际推理。不使用目标 U、额外教师、伪造跨视频负例或测试时更新。不直接修改 Hungarian matching；IAE-VTG 的 ISA 可作后续明确对照，不能与首版多个机制同时加入。

分解监督若仅来自完整事件标签，primitive 分支可能携带完整事件或文本先验；通过角色遮蔽/单流/文本控制评估，仍不能据此宣称因果 disentanglement。

不直接移植EVIDENT的dense-token/DINOv2 objectness蒸馏、ActPrompt encoder内prompts或HRVTG在线LoRA；若未来增加这些资源/更新协议，另立资源轨并公平对照。可选annotation-derived verb auxiliary一次只加一个，比较J与J+aux，先定义训练侧标签覆盖。

## 5. 实施前必须冻结的选择

1. token/span 对齐、角色解析与失败回退，以及 held-out 语义隔离审计。
2. 原双流对齐和局部上下文范围，A/E/J/H 的函数与参数量。
3. H/P/C/J/T 的监督、优化器、轮数上限、checkpoint 选择和唯一主聚合 G。
4. R 的 primitive-only null、同尺度约束及拟合/外推审计；若未明确，先只执行 J 验证。
5. map→候选/边界与 map→存在的融合定义、原 gate 接口和训练侧阈值选择。
6. 三族覆盖、共同视频统计、paired 指标及停止门槛；正式 U 和独立 VTG 的后续独立范围。
7. motion可读性/静态捷径控制、单对非退化、visual直接路径、多对pair保真及同支撑null。
8. import/loader的副作用隔离：原dataset会把missing_features日志写到原data_path旁，须新wrapper接管或传入本目录的字节相同视图副本；pycache/临时文件/结果也在新目录。不能运行旧脚本让其隐式回写受保护目录。

这些是可运行方案所需技术定义，不是新增用户确认流程。当前请求仅为方案建设，尚未开始实施或训练。
