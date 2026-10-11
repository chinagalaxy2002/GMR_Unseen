# Charades-CG → Charades-CG-GMR 数据制作方案

版本：revision-4；2026-10-11 补入 Seen 测试集。本文按用户要求替代旧审核方案：异常数据直接剔除，负例按 Moment of Untruth 的域内负例算法生成，不再增加 agent 语义审核、仲裁或人工复核。当前已按本方案完成 v2 数据生成与独立机械验收；v1 保留为 Train + Novel-Composition 的历史版本。最新用户要求恢复 Test-Trivial 作为 Seen 测试，替代此前排除 Test-Trivial 的范围调整；Novel-Word 仍不纳入。

## 1. 数据从哪里来，最终变成什么

**Charades-CG 官方正例 → 删除异常行 → 整理 Train / Val / Test → CLIP 筛选并重新配对视频 → 加入等量负例。**

输入位置：`data/release/charades_cg_gmr_v1/source/`，官方提交 `2372337e9166b8e26b83ce936a8474c6ae127290`。

| 原始文件 | 整理方式 | 最终用途 |
|---|---|---|
| `train.json` | 沿用 seed=3407 的视频级训练/验证分配 | Train、Val：S+ 与新增 S− |
| `test_trivial.json` | 保留官方常规测试身份 | Test：S+ 与新增 S− |
| `novel_composition.json` | 保留官方 Unseen 身份和 `novels` 标记 | Test：U+ 与新增 U− |
| `novel_word.json` | 单独保留 | 本次不纳入训练、负例生成和主测试 |

S/U 描述查询的组合身份；正/负描述查询与目标视频是否匹配。Test-Trivial 的 S 是官方常规测试参考口径。CG 已有的 945 个组合条目直接继承，不重新定义组合，不重新审核全部原始正例。

测试视频统一属于 Test，查询分别保留 Test-Trivial / Novel-Composition 身份。两类查询可以来自同一视频。

## 2. 删除异常行

删除空查询、缺少必要字段、非法时长或窗口，以及不满足 **0 ≤ start < end ≤ duration** 的正例；不裁剪或修复原始窗口。格式正确的原始查询直接保留，不再进行语法与角色审核。

按已核对的四份源文件，明确的窗口越界行共 2,228 条；本次三份纳入来源剔除 2,119 条，另 109 条属于未纳入的 Novel-Word。仅按上述窗口条件及非空查询整理后，数量如下：

| 来源 | 原始正例 | 剔除窗口越界 | 保留正例 |
|---|---:|---:|---:|
| 官方 Train | 8,281 | 1,255 | 7,026 |
| Test-Trivial | 3,096 | 412 | 2,684 |
| Novel-Composition | 3,442 | 452 | 2,990 |
| Novel-Word（另存） | 695 | 109 | 586 |

沿用当前视频分配，7,026 条训练来源正例分为 **Train 6,342 条、Val 684 条**。只保存一个简单的剔除清单，记录源 ID 和原因。清洗和验证抽取是对官方数据的修改，在说明中注明；S/U 仍按官方来源继承。

## 3. 按 Moment of Untruth 生成负例

采用论文 §3.3 的 **In-Domain negatives**：保留已有句子，为它重新分配视频；用 CLIP 的文本相似度筛掉相似程度较高的视频。论文 §4 说明域内负例数量与正例相同。[论文原文](https://arxiv.org/html/2502.08544v2#S3.SS3)

以下先给出算法，再明确本项目的固定实现参数。我们只使用该论文的域内负例部分，不生成域外新句子。

### 第一步：分别准备三个候选池

分别在 Train、Val、Test 内执行，不跨池借用句子或视频。

- Train 池：6,342 条训练正例及其视频。
- Val 池：684 条验证正例及其视频。
- Test 池：2,684 条 Test-Trivial 与 2,990 条 Novel-Composition 正例的并集及其视频。

对每个视频 V，收集当前池中属于它的所有正例描述，记为 Q(V)。Test 中同一视频的 S+、U+ 描述合并到 Q(V)，不能只取其中一类。删除异常行后不再有合法描述的视频不进入候选池。

### 第二步：用 CLIP 编码句子

将当前池每条不同的查询文本输入同一 CLIP 文本编码器，获得句向量，并做 L2 归一化。相同文本只编码一次，所有源实例仍保留。

设归一化向量为 e(q)，两句的余弦相似度为：

`sim(q, r) = e(q) · e(r)`

这里比较的是**查询文本与已有描述文本**，不计算视频画面与文本的 CLIP 相似度。

### 第三步：给每个候选视频计算一个分数

对正例 `(A, q)`，排除原视频 A；如果另一个视频已有完全相同的查询 q，也排除该视频，遵守论文 `q 不属于 Q(V)` 的条件。

对剩余每个视频 V，将 q 与 Q(V) 中的每句话比较，取最高相似度：

`score(q, V) = max[sim(q, r), r ∈ Q(V)]`

因此，只要该视频有一句已知描述与 q 很相似，视频的分数就会较高。不能把多句相似度取平均。

### 第四步：只保留分数最低的一半视频

针对 q，把候选视频按 score 从低到高排序，保留最低 50% 作为可选集合。

例如有 100 个候选视频，只保留排名 1—50 的视频。这里的 50% 是**排名比例**，不是要求相似度低于 0.5。

### 第五步：为这句话抽取一个新视频

从最低一半中随机选择视频 B，组成 `(B, q)`。原来的 `(A, q)` 仍作为正例保留。

一个正例实例生成一个负例实例；q 完全不变。S/U 标签跟随 q：Seen 查询换视频后成为 S−，Unseen 查询换视频后成为 U−，不由 B 的其他查询类型决定。

### 第六步：写入负例标签

负例记录：

```text
vid                 = 新视频 B
query               = 原句 q
exist_label         = 0
relevant_windows    = []
duration            = 新视频 B 的时长
partition           = S− 或 U−，继承 q 的官方身份
source_qid/vid      = 原正例 ID 与视频 A
official_subset     = 原查询的官方子集
novels              = 原查询已有的组合标记
construction_method = mout_in_domain_clip_reassignment
```

这类负例是按论文算法构造的负例，不标成 agent 审核或视频确认的负例。生成后仅检查文件格式、数量和划分归属，不再加入语义冲突筛选、审核队列或额外重排规则。

### 固定实现参数

论文规定了 CLIP 文本相似度、逐视频最大值和最低 50% 选择；以下是本项目为复现固定的实现选择，不宣称是论文指定参数：

- 文本编码器沿用本项目已有的 OpenAI CLIP ViT-B/32，记录权重与编码配置。
- Train/Val/Test 全部使用上述筛选规则；论文在 §3.3 对测试集明确描述了该筛选，我们在三个池中统一执行。
- 随机种子 3407；固定源实例处理顺序；同分视频按视频 ID 排序。
- 候选数 N≥2 时保留前 `floor(N/2)` 个；不足两个则记录无法生成。
- 从可选视频中均匀随机抽取。相同 q 在多个源实例出现时，优先无放回分配不同目标视频以免产生重复视频—查询负例；可选集合耗尽则记缺额，不添加其他生成机制。
- 每个原实例只采一个负例，源正例与对应负例建立 pair_id。编码可按不同文本去重，不能把原始实例数量一起去掉。

## 4. 最终如何组织

采用一个独立的 C3_CG 扩展包，不与原 v3 A1—C2 的训练行混合：

```text
data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2/
  README.md
  source_manifest.json
  removed_rows.jsonl
  video_splits.json
  negative_generation.json
  statistics.json
  splits/C3_CG/
    train.jsonl        # S+、S−
    val_seen.jsonl     # S+、S−，用于选模和阈值
    test.jsonl         # S+、S−、U+、U−
    pairs.jsonl        # 正例与同句负例的关联
```

v2 已生成全部正负配对，实际数量如下：

| 集合 | S+ | S− | U+ | U− | 总计 |
|---|---:|---:|---:|---:|---:|
| Train | 6,342 | 6,342 | 0 | 0 | 12,684 |
| Val | 684 | 684 | 0 | 0 | 1,368 |
| Test | 2,684 | 2,684 | 2,990 | 2,990 | 11,348 |

本次配对缺额为 0，共 12,700 对。Train/Val 与 v1 逐字节相同，原 2,990 条 U+ 保持不变；测试负例因改用联合测试候选池而重新生成。v1 不覆盖，v2 的逐项验收与校验和记录在发布目录和 `data/release/charades_cg_gmr_v1/work/`。

训练和阈值校准只用 Seen。测试分别汇总 Seen/Unseen 的 AUROC、Rej-F1、G-mIoU@1 及差值，按 AGENTS.md 保存整体拒绝指标、类别数量、视频聚类置信区间与结果文件。Test-Trivial 与 Novel-Composition 共享的视频在 bootstrap 中共同重采样。
