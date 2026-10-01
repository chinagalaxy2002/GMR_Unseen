# 当前工程源码与输入核验

日期：2026-10-01。只读检查，没有导入训练入口、模型前向或拟合。路径以仓库根目录为基准；本报告区分实际输入事实、实现行为与设计推论。

## 1. 严格协议与当前模型

项目根 README 的 Research question and protocol 规定：下游只训练 S+/S−，seen validation 选择 checkpoint 与存在阈值，目标 U 的 validation/test 不用于选择。CLIP/SlowFast 预训练可能见过相关语义，不能宣称基础预训练完全 zero exposure。训练侧从原 S 重新留出的 pseudo 视图用于本轮机制开发，不能混用发布包真实 U。

`models/qd_detr_gmr/model.py:89–93,120` 在拼接视频特征上做统一投影；`:157–158` 把 decoder 最后一层 query states 送入存在头。`models/qd_detr_gmr/gmr_adapter.py:19–29` 对 decoder query states 做 max/mean，再经 MLP 输出一个存在 logit。它不是直接对时间 evidence map 做聚合。

设计推论：新分支需要在统一投影前保留原 CLIP/SlowFast 分量。不能从融合后的 256 维 hidden 直接划坐标，宣称一半实体、一半运动。只读加载旧模型并在新目录编写 wrapper/复制适配，保持 baseline 输出可复算，不改原 model.py。

## 2. 双流维度与时间处理

当前冻结配置 `experiments/correspondence_generalization/code/configs/qd_throw_seed3407_resolved.json` 实际为 `v_feat_dirs=[vid_clip,vid_slowfast]`，即 CLIP 在前、SlowFast 在后；字符串 `v_feat_types=slowfast_clip` 不是拼接顺序依据。`v_feat_dim=2818`、`t_feat_dim=512`、`max_v_l=200`、`max_q_l=32`、`clip_length=1`。

只读检查 throw 原 train 第一行对应已有文件，得到 CLIP `(29,512)`、SlowFast `(30,2304)`，两者均只有 `features` key。`code/vendor/qd_dataset.py:241–264` 各流独立 L2 归一化，分别截断 max_v_l，再截到 min_len，最后按列表顺序拼接。TEF 在 `:143–151` 追加，因此实际输入通道为 `[CLIP:512 | SlowFast:2304 | TEF:2]`。

这一个样本确认了维度和不同长度现象，不是全数据完整审计，也不证明时间错位。数组没有 timestamps；截到 min_len 只使长度相同，不证明 clip center、stride 或 receptive field 相同。后续阶段 A 需核对提取来源；来源不足时显式标注对齐假设，不随意插值后称原协议保持。

机器可读记录见 [SOURCE_INPUT_AUDIT.json](SOURCE_INPUT_AUDIT.json)。没有读取正式 U 的样本或特征内容。

## 3. 文本缓存与角色对齐

同一 train 样本的 text NPZ 只有 `last_hidden_state`，形状 `(10,512)`，未保存 token IDs/offset。`code/vendor/qd_dataset.py:220–238` 截取前 max_q_l token 并归一化；不能把第 i 个自然语言词直接映射为第 i 个 cached token。

`scripts/prepare_charades_semantic_existence.py:33–43` 复用正例旧特征；`:55–60` 用 CLIP tokenizer 对新负查询做 77-token 编码、按非零长度保存 hidden states。角色解析必须核对使用同一 tokenizer 的词到 BPE 映射、SOT/EOT、截断、缓存来源；BPE 词映射可以在新目录做只读 tokenization，不必重跑 encoder。若需要重新提取新文本表征，必须独立记录资源/协议变化，不覆盖原缓存。

role token 仍是上下文化的完整句子表征，可能携带其他 primitive 信息。因此“只取 verb/noun”不保证 disentanglement；text-only、单流和固定实际文本控制都不可省略。

## 4. 时间表示与 saliency

`models/qd_detr_gmr/transformer.py:138–144` 先运行 text-to-video encoder，再进行 temporal encoder；`:144–157` 去除 global token，向 decoder 提供 memory_local 并返回。可以在新目录 wrapper 明确读取 raw streams、early 或 memory，但三者是否有相同可读性需要区分。

原配置 `mr_only=true`、`lw_saliency=0`；native saliency 输出在 `model.py:160–165` 计算，但本实验没有有效 saliency loss。原生 saliency 无效不能证明已训练 evidence head 失效。EviDETR 的 MR→HD 需要其监督/模块，不因现有代码能输出 saliency 就已具备等价机制。

`model.py:168–185` 的 batch-rotated text 路径产生 saliency negatives；其输出不是经原数据核实的 event absence。首版不能启用该路径来给所有 primitive 分支制造 absent 标签。

## 5. gate 与实际定位路径

`code/vendor/qd_evaluate.py:73–86` 分开 foreground 和存在分数，gate 对 query 所有候选施加同一 multiplier；`gmr_adapter.py:46–61` 给出 soft/hard 定义。非零共同 multiplier 保持候选排序，因此新 map 若只接全 query scalar 不会改善 raw R1。

`qd_evaluate.py:88–108` 保存 raw/gated 候选和四位小数存在分数；`:122–131` 再做时间 clip/round 后处理。新输出须保留 native precision、slot ID 与原窗口映射，不能直接拼接不同排序数组。旧指标仍按原保存口径，新 precision 诊断单列。

candidate-specific map 汇聚能够重排已有窗；无正确候选的样本仍无法被修复。边界回归或生成变更需单立干预，不把 GT oracle 覆盖当实际可实现结果。

## 6. 导入也可能产生外部写入

`code/vendor/qd_dataset.py:87,123–126` 在发现缺特征时把 missing_features 日志写到原 data_path 旁。即使训练脚本自身放在新目录，直接调用原 dataset 也可能回写旧目录。新 wrapper 必须接管异常日志目录，原 train/seen/pseudo 视图可复制到新目录再传给 loader，并核验字节/hash，不给原标签文件写旁路产物。

环境缓存、临时目录、pycache、结果路径、tensorboard/tracker 和相对工作目录均设置在新目录。导入原模块可禁用外部 pycache 或设置新目录缓存位置；不通过修改原源码达成隔离。

## 7. 下一步最低实现约束

1. 在任何拟合前核验 tokenizer 映射、流顺序、TEF 排除和时间对应来源。
2. 用 raw-stream visual residual 保证单 noun–verb 对的 J 也有视觉变化；先做静态代码/输入输出契约检查，避免文本常数路径。
3. 在 S+ GT 上先检验动作可读性，再比较 H/P/C/J；GT probe 不作为无 GT 推理成绩。
4. 所有新增训练/评测/部署代码和任何副作用都写在本新目录，原代码和原资产只读。

外部 Python 源码 hash 的核对范围为 models、training、scripts 和旧实验 code，共 132 文件；基线和最终一致性结果保存在本新目录本地核验记录，并在交付总检查报告概述。该检查证明本轮这些文件未变，不证明整个磁盘不存在其他进程的变动。
