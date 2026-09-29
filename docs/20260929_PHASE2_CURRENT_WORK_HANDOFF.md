# 阶段 2 当前工作交接（2026-09-29）

## 先看这里

阶段 2 的五个冻结语义划分、15 次模型训练和 15 份测试评测均已完成。正式标注、选择记录、构建与评测脚本、结果报告和机器可读指标已推送到 GitHub 远端 `gmr-unseen/main`。仓库中的 [README](../README.md) 是总入口；[阶段 2 预定方案](20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md)记录事前规则；[完整结果报告](semantic_existence_multisplit_results.md)和[指标目录](semantic_existence_v2_metrics/)记录正式结果。历史 A0/v1 与 E0–E7 的细节仍见[阶段 1 交接](20260928_1_CURRENT_WORK_HANDOFF.md)。

恢复工作时先读本文件、结果报告和 README，再查看具体指标 JSON。当前没有待完成的阶段 2 训练或测试；不需要重启训练队列。工作区里另有未跟踪的 `Unseenarc_model/`，它与本次阶段 2 发布无关，未被修改或提交。

## 问题与固定协议

研究对象是 Charades-STA 派生的广义视频时刻检索：查询事件可能真实存在或不存在，查询动作或动作–物体组合也可能在**下游任务训练**中未见。四象限为 S+、S−、U+、U−。`unseen` 不表示 CLIP 或 SlowFast 的预训练从未见过相应概念。每组只用本组 S+/S− 训练，只用本组 seen validation 选 checkpoint 和校准存在阈值，test 不参与调参。正例沿用原始时间窗，负例为空窗。

A0 是保持不变的 v1 参照：动作级保留 `open/close`，组合级另有 16 个保留组合；v1 的 matched-U 配对只覆盖动作级。阶段 2 独立构建三组动作保留和两组组合保留。五组使用同一个 Charades 视频域及原始视频切分，因此“独立”指不同预先冻结的语义保留与独立训练，不是统计独立的视频域。

| 组 | 轴与保留语义 | Train | Val | Test | Test U+ / U− | 同视频同来源 U 对 | U+ 配对覆盖 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | 动作 `put`, `take` | 8,608 | 1,759 | 5,170 | 465 / 1,119 | 312 | 67.1% |
| A2_alt | 动作 `drink`, `pour` | 10,323 | 1,686 | 4,945 | 168 / 312 | 79 | 47.0% |
| A3 | 动作 `run`, `walk` | 10,352 | 1,774 | 5,293 | 192 / 594 | 129 | 67.2% |
| C1 | 组合 `sit|bed/chair/couch` | 10,516 | 1,607 | 4,705 | 162 / 270 | 144 | 88.9% |
| C2_alt | 组合 `open/close|box/cabinet` | 10,612 | 1,607 | 4,705 | 115 / 254 | 33 | 28.7% |

## 数据构建、冻结和审查来源

原训练与测试正例、Charades 标注、Action Genome、VerbNet 和视频归档位于 `/home/guoxiangyu/paper/Openword/data/`、`/home/guoxiangyu/paper/Openword/external/verbnet/` 与 `/home/guoxiangyu/paper/Openword/downloads/`。正式发布包的仓库副本在 [`data/release/semantic_existence_v2/`](../data/release/semantic_existence_v2/)；本机原始构建和中间文件在 `/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v2/`。仓库发布标注和审计资料，不包含原视频、CLIP/SlowFast 特征、checkpoint、逐查询预测或 `work/` 构建中间文件。

候选统计覆盖 123 个动作和 1,221 个组合。选择规则、初选失败记录、候选表、五组 spec 和冻结哈希都在 [`selection/`](../data/release/semantic_existence_v2/selection/)。初选 A2 的候选配对只有 11 对、初选 C2 只有 1 对；两者在模型结果产生前依规则替换为 A2_alt 和 C2_alt。动作组共享同一批 1,500 条训练 S−，组合组共享另一批 1,500 条；各组 S+ 因保留语义不同而变化。

数据负责人对哈希绑定的当前批次作出**整批人工核对确认**：4,491 条新负例和 156 条语义解析抽样均通过；2,485 条与 v1 完全一致的负例沿用 v1 原有批次确认来源。这是全局 attestation，没有逐 qid 决定表或双人审核记录。不能在论文中写成逐条双人视频复核。已知 `dress|front` 解析错误在打包前隔离。正式门槛包括至少 80 个测试 U+、40 个 U−、50 个 U+ 视频、20 个同视频配对和 15% 的 U+ 配对覆盖；最大单保留语义占比及解析 QC 另受冻结规则约束。

五个仓库发布包均通过 [`validate_release.py`](../scripts/validate_release.py)：训练、验证、测试视频交集为 0，匹配配对和 held-out 约束通过，每组 10 个发布文件的 SHA-256 核验通过。`statistics.json` 是隔离解析错误后的最终计数；`review_report.json` 中的部分计数记录了隔离前状态。原 A0 包未改写。

## 训练和本地结果位置

队列 [`queue_semantic_multisplit_training.sh`](../scripts/queue_semantic_multisplit_training.sh) 已在 2026-09-29 14:55:53（北京时间）写入 `complete_all`。五组依次训练，每组三模型并行：Moment-DETR-GMR 与 QD-DETR-GMR 在 GPU 0，FlashVTG-GMR 在 GPU 1。全部使用 seed 3407、强制 100 epoch、关闭早停；15 个模型的 `exit_code` 都是 `0`。每组三模型完成后，使用 [`finalize_semantic_multisplit_group.sh`](../scripts/finalize_semantic_multisplit_group.sh) 运行 best checkpoint 测试推理、四象限诊断和官方 GMR 评分。五个 `evaluation_status.txt` 都为 `complete`，三模型的每份预测都与该组 test qid 集合完全一致，无缺失或重复。

本机路径：

```text
结果与日志：results/semantic_existence/multi_split_v2/<split>/<moment|qd|flash>/
队列状态：results/semantic_existence/multi_split_v2/queue_status.txt
文本特征：features/semantic_existence_v2/<split>/clip_text/
seen 验证视图：features/semantic_existence_v2/<split>/val_seen.jsonl
视频特征：/home/guoxiangyu/paper/新建文件夹/charades/{vid_clip,vid_slowfast}/
正式数据：data/release/semantic_existence_v2/<split>/
发布指标：docs/semantic_existence_v2_metrics/<split>/<model>/
```

本地 `results/` 和 `features/` 被 Git 忽略；GitHub 已发布各模型的 `diagnostics.json`、`official_test_metrics.json`、bootstrap 区间和跨划分摘要。官方 GMR 指标与四象限诊断使用不同 gate 和阈值定义，不可互换。现有结果目录已有 checkpoint；若只是读结果，不要再次执行训练入口。

## 测试结果：恢复判断所需数字

下表的 AUROC 和 PairAcc 为 0–1，FRR、RR 和 R@1 为百分比。`raw→hard` 是同一 checkpoint 的 U+ R@1@IoU 0.5 在 seen-validation 阈值硬拒绝前后；这是诊断操作。

| 组 | 模型 | Seen / unseen AUROC | PairAcc | U+ FRR / U− RR | U+ raw→hard R@1 |
| --- | --- | --- | ---: | --- | --- |
| A1 | Moment | 0.804 / 0.497 | 0.559 | 23.23 / 25.47 | 23.01→17.85 |
| A1 | QD | 0.783 / 0.506 | 0.572 | 16.13 / 18.23 | 24.52→20.65 |
| A1 | Flash | 0.816 / 0.506 | 0.556 | 19.14 / 20.82 | 29.46→23.66 |
| A2_alt | Moment | 0.769 / 0.551 | 0.620 | 0.00 / 0.64 | 26.79→26.79 |
| A2_alt | QD | 0.744 / 0.473 | 0.456 | 0.60 / 0.32 | 31.55→31.55 |
| A2_alt | Flash | 0.773 / 0.524 | 0.506 | 0.00 / 0.96 | 42.86→42.86 |
| A3 | Moment | 0.749 / 0.564 | 0.469 | 29.17 / 33.00 | 39.58→28.12 |
| A3 | QD | 0.733 / 0.487 | 0.453 | 30.21 / 31.31 | 44.27→33.33 |
| A3 | Flash | 0.742 / 0.614 | 0.516 | 23.44 / 43.77 | 46.88→34.38 |
| C1 | Moment | 0.761 / 0.562 | 0.629 | 3.70 / 7.78 | 48.77→47.53 |
| C1 | QD | 0.780 / 0.562 | 0.635 | 3.09 / 5.56 | 42.59→41.98 |
| C1 | Flash | 0.753 / 0.548 | 0.556 | 3.70 / 3.70 | 51.23→48.77 |
| C2_alt | Moment | 0.676 / 0.469 | 0.727 | 98.26 / 96.85 | 35.65→0.00 |
| C2_alt | QD | 0.698 / 0.545 | 0.530 | 47.83 / 53.94 | 38.26→24.35 |
| C2_alt | Flash | 0.691 / 0.547 | 0.545 | 61.74 / 64.57 | 42.61→15.65 |

15 次运行的 seen AUROC 均高于 unseen AUROC，差值范围 0.128–0.309。按组等权平均时，动作轴三模型的 AUROC 差分别为 0.2365、0.2649、0.2289；组合轴两组分别为 0.2031、0.1856、0.1744。A2_alt 的 U+ 错拒接近零，同时 U− 拒绝也低于 1%，说明它几乎全部接受未见查询。C2_alt 的 Moment 模型几乎同时拒绝全部 U+ 和 U−，硬拒绝把 U+ 定位从 35.65% 降到 0。各模型更精确的小数、官方评分及按测试视频聚类的 2,000 次 bootstrap 95% 区间在[指标目录](semantic_existence_v2_metrics/)；区间不反映训练种子变动。

相同 `qid`、视频、句子、真值和正例时间窗的 U→S 对照已分轴完成。动作轴有 1,041 个互异测试 qid、2,082 个有向比较；组合轴有 801 个有向比较。C2_alt→C1 的同一样本里，三模型对真实存在查询的 seen−unseen 分数平均增加 0.128–0.283，对不存在查询也增加 0.161–0.258；C1→C2_alt 的分数变化接近零。对照固定了测试内容，但训练 S+ 分布和模型校准也随划分变化，不能单独解释为纯粹的语义暴露因果效应。动作轴详见[动作组报告](semantic_existence_action_multisplit_results.md)，组合轴详见[完整报告](semantic_existence_multisplit_results.md)。

text-only 对照已对五组重跑。C1 和 C2_alt 的 text-only matched PairAcc 分别为 0.625 和 0.818，说明配对排名仍可能受到查询措辞的影响；具体全量/seen/unseen AUROC 在 [`text_only/`](semantic_existence_v2_metrics/text_only/)。C1 U+ 仅涉及三个物体，C2_alt 仅两个；A2_alt 的 U+ 中 `glass` 与 `cup` 占 72%。按四象限的查询长度、动作及物体分布在 [`test_query_distributions.json`](semantic_existence_v2_metrics/test_query_distributions.json)。

## 当前结论边界与下一步

可支持的阶段 2 结论是：在同一个 Charades-STA 视频域的多个预先冻结、分别训练的动作和组合保留划分上，三种 GMR 模型的未见语义存在区分能力稳定低于已见语义；具体错误方向、配对准确率和定位 gate 损失随划分明显变化。不能写成“所有开放视频环境普遍失败”，也不能把组合组 text-only 配对结果忽略。每个配置只有一个训练种子，组合轴仅有两组且对象集中，审核来源为整批 attestation。

阶段 2 已无待跑的计划内训练或测试。若继续论文工作，应从[完整结果报告](semantic_existence_multisplit_results.md)和逐组指标 JSON 选取逐组表、等权轴均值、配对数及视频聚类区间，保持动作轴与组合轴分开；再决定是否需要额外种子、视频域或更细粒度负例审核来增强结论。任何新实验都应作为新协议和新版本记录，不改写这些冻结发布包。

## 恢复时的只读检查

在仓库根目录执行：

```bash
git log -1 --oneline
cat results/semantic_existence/multi_split_v2/queue_status.txt
for split in A1 A2_alt A3 C1 C2_alt; do
  python scripts/validate_release.py --release "data/release/semantic_existence_v2/$split"
  cat "results/semantic_existence/multi_split_v2/$split/group_status.txt"
  cat "results/semantic_existence/multi_split_v2/$split/evaluation_status.txt"
done
```

本地模型文件不存在于新机器时，以已发布的 [README](../README.md)、[正式数据](../data/release/semantic_existence_v2/) 和[机器可读指标](semantic_existence_v2_metrics/)恢复可共享的证据；复现训练需自行准备原视频与特征。
