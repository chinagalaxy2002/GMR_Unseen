# Semantic Existence v3 Balanced 构建记录

构建日期：2026-10-10。随机种子：3407。

源数据为 `data/release/semantic_existence_v3_release/`，新增数据独立保存于 `data/release/semantic_existence_v3_balanced/`。五组 Train、Validation、Test 各自补齐到正负 1:1；全部原始样本、qid、标注、四象限归属与视频划分保留。主划分 JSONL 以源文件的原始字节作为前缀，新增记录追加在文件末尾。

## 数据规模

下表每个单元格为「正例数 / 最终负例数」。Validation 对应文件名 `val.jsonl`。

| 组 | Train | Validation | Test | Train 新增负例 | Validation 新增负例 | Test 新增负例 |
|---|---:|---:|---:|---:|---:|---:|
| A1_v3 | 8,801 / 8,801 | 1,119 / 1,119 | 3,453 / 3,453 | 7,783 | 724 | 2,295 |
| A2_v3 | 9,791 / 9,791 | 1,119 / 1,119 | 3,453 / 3,453 | 8,773 | 724 | 2,295 |
| A3_v3 | 9,747 / 9,747 | 1,119 / 1,119 | 3,453 / 3,453 | 8,729 | 724 | 2,295 |
| C1_v3 | 10,042 / 10,042 | 1,119 / 1,119 | 3,453 / 3,453 | 9,203 | 724 | 2,295 |
| C2_v3 | 10,100 / 10,100 | 1,119 / 1,119 | 3,453 / 3,453 | 9,261 | 724 | 2,295 |

五组划分合计新增 58,844 条独立 qid 的伪负例，其中 S− 57,682 条、U− 1,162 条。五组样本合计 142,682 行；这些是按组累计的规模，不能解读为互不重叠的原始视频或 Query 数量。

完整 S+/S−/U+/U− 数量见新 release 的 `statistics.csv`、`statistics.json`、`splits/*/semantic_inventory.json` 与 `README.md`。

## CLIP 筛选

依据 [Moment of Untruth 的第 3.3 节，WACV 2025 第 5339 页](https://openaccess.thecvf.com/content/WACV2025/papers/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.pdf)，对每个候选 Query 计算其与目标视频全部已知正例 Query 的 CLIP 文本余弦相似度，取最大值作为伪相似度。随后，对该 Query 的候选视频按伪相似度升序排序，保留最低一半。参考[官方仓库](https://github.com/keflanagan/MomentofUntruth)，核对的仓库版本为 `ac2adcdd56230a3169adf965fc7926d3ee2784ce`；仓库未提供离线负例抽样脚本，因此本项目根据论文公式实现。

- 文本编码器为本机 OpenAI CLIP ViT-B/32 预训练权重。使用 EOT 向量经 `text_projection` 投影后的句子特征，转 float32 并 L2 归一化。
- 对源 master 的 15,034 条正例按完整 Query 文本去重，编码 9,017 条不同文本。缓存、权重和编码器代码的 SHA256 记于 `clip_metadata.json`。
- 本机 CLIP 包的 `tokenize()` 默认会截断至 32 个 token。本次直接使用同包的 CLIP BPE tokenizer，保留完整文本，添加 SOT/EOT 并补零至 77；超过上下文长度时报错，不静默截断。
- 来源 Query 仅取当前组、当前划分中已有的正例。相同文本取 qid 字典序最小的一条作为来源，避免重复文本按原始标注频次获得额外抽样权重。
- 候选目标视频为当前组、当前划分已包含的视频，排除来源视频。若有 N 个候选视频，取升序排名 `1..floor(N/2)`；完全相同的浮点分数按目标视频 ID 字典序打破平局。
- 目标视频的参考 Query 使用源 `master/positive_clean.jsonl` 中该视频的全部正例，包括训练视频中因 held-out 规则而未放入训练的正例。这些信息只用于数据构建时排除潜在假负例，相关 held-out Query 不会作为训练样本加入。
- 先确定最低 50% 的排名范围，再执行标注冲突检查与去重，避免在排除后重新排序而纳入原先排名较高的配对。

所有新增配对的 `rank_fraction <= 0.5`。实际伪相似度范围约为 0.462671–0.866608，其中 58,839 条的余弦值大于或等于 0.5。这与按每条 Query 的视频排名筛选相符：0.5 不是余弦阈值。

## 语义约束和补齐策略

held-out 判定复制自完成全量语义审计后使用的 `scripts/apply_full_semantic_audit_v3.py` 中的纯函数，避免导入该文件时触发其顶层数据修改操作。动作组按完整事件列表的动作族判断；组合组保留对象别名和语义角色约束：C1 的 sit 需要 support_surface/location，C2 的 open/close 需要 theme。purpose、intended、negated 事件不被视为已断言的 held-out 事件。

新增记录完整复用来源正例的 `events` 和 `semantic_graph`，重新确定目标视频、时长和独立 qid，设置 `exist_label=0`、`relevant_windows=[]`。训练来源只包含 S+，因此新增训练负例只属于 S−。qid 的 `train`/`test` 字符串前缀不是当前划分依据；实际划分遵循 v3 保存的 `split` 与视频分配。

目标视频的全部已知正例用于保守排除：规范化后的 Query 完全相同；已有相同或别名动作，且对象相同、包含、通用或未指定；比较的锚点角色不同、无法据此确认事件不同；或列出的相反动作作用于相同锚点。相反动作排除属于额外的保守过滤，不能据此推断两个动作在同一视频内不可能共存。具体动作别名和规则保存在构建脚本中。

验证和测试中，按当前划分 S+/U+ 的比例，以最大余数法分配新增 S−/U− 名额。抽样采用独立派生的组/划分随机种子，轮流访问随机排列的来源 Query，并从其最低半区视频随机列表中选择可用目标。同一 Query 可重复用于不同目标视频；同一组、同一划分内的新增 Video–Query 配对不得重复，也不能与任何已有配对重复。

要求是每个完整划分正负 1:1，Seen 和 Unseen 子集没有额外要求各自 1:1。例如源 C1 验证集已有 U−=97、U+=56，测试集已有 U−=264、U+=142；保留原始样本且只补充负例无法让这些子集单独达到 1:1。

## 文件与使用

- `splits/<group>/{train,val,test}.jsonl`：训练和评测的完整增强数据。
- `splits/<group>/val_seen.jsonl`：重新生成的 Seen 验证子集，用于 checkpoint、阈值与超参数选择。
- `provenance/<group>/<split>_added.jsonl`：对应划分的全部新增记录，含来源和 CLIP 排名。
- `master/negative_added.jsonl`：所有组的新增伪负例；qid 包含组和划分信息的稳定哈希。
- `master/positive_clean.jsonl`、`master/negative_clean.jsonl`：原始已审计的正例和负例池，原样保留。新增伪负例不会被混入已审计 `negative_clean` 池；应使用完整 `splits/` 进行实验。
- `matched_u_pairs.jsonl`、`test_matched_u.jsonl`：保留原始匹配配对；跨视频新增样本不能声称是同源视频的匹配反事实对。
- `source_manifest.json`、`checksums.sha256`：源文件校验和与新 release 校验和。
- `clip_metadata.json`、`construction_protocol.json`：权重、向量缓存、编码细节、抽样规则、源码哈希和完整构建参数。
- `validation_report.json`：结构、语义和全部新增配对 CLIP 排名重算的校验结果。

原有各轴共享的已审计训练负例池保留。由于五组训练正例数和 held-out 定义不同，补齐后的完整训练负例池按组生成，不能再将增强后的所有训练负例声称为轴内完全相同的共享池。

本次生成数据和筛选所需的句子向量，不执行模型训练。新 qid 的训练文本特征尚未单独生成；因 Query 文本直接复用正例，可在训练特征目录按 `source_qid` 复用或链接对应文本特征，或调用项目特征准备流程。

## 构建与校验命令

以下命令从仓库根目录执行。构建器拒绝覆盖已存在的输出目录；再次构建时指定新的 `--output`。

```bash
/home/guoxiangyu/miniconda3/envs/univtg/bin/python \
  scripts/build_semantic_existence_v3_balanced.py \
  --clip-code '/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video' \
  --clip-weights '/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt' \
  --device cuda:0 --seed 3407

/home/guoxiangyu/miniconda3/envs/univtg/bin/python \
  scripts/validate_semantic_existence_v3_balanced.py --device cuda:0
```

校验器检查全部原始数据的字节保留和源文件 SHA256、15 个划分的正负数量、视频和 qid 隔离、完整事件 held-out 定义、训练仅 S+/S−、来源正例和目标时长、空窗口、Video–Query 去重、标注冲突排除、配额、master/provenance/统计一致性和 `val_seen`。它从冻结的 CLIP 向量重新计算每条新增配对的分数、完整候选视频排名和最低半区截断值。校验不会重新编码文本或观看视频。

实际校验结果为 **PASS**：15 个划分全部通过，58,844 条新增配对全部通过分数和排名重算，原始源数据校验和未变化。完整结果与校验时间见新 release 的 `validation_report.json`。

## 解释边界

**全部新增负例均为伪负例。低 CLIP 文本相似度及标注冲突排除不能证明事件一定没有发生，视频标注也可能不完整；本次没有进行逐视频核验。** 原始负例的既有审计状态不因新增伪负例而改变。

数据平衡不能直接说明拒绝判断或未见语义泛化改善。后续实验需冻结 Seen-validation 上选择的 checkpoint、阈值与超参数，逐组、逐 backbone 报告 Seen/Unseen AUROC、实际 Rej-F1、端到端 G-mIoU@1、Seen−Unseen 差值及视频簇 bootstrap 区间。与同组同 backbone 的 v3 baseline 比较时报告 Unseen Net Gain、Seen Change、Gap Reduction 和配对区间；解释 Rej-F1/G-mIoU 差异时需列出类比例变化。只有五组均完成后才报告正式五组宏平均。
