# 工作交接：Semantic Existence v1

更新于 2026-09-28（Asia/Shanghai）。清空对话上下文后，先读本文件，再按需打开下方详细报告。项目根目录：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。当前分支 `main`；编写本文件前 HEAD 为 `b3cf091628357402b70b3c5b273b868377d98015`，工作区原本干净。本轮新增本交接文件，并修改 README 和旧交接的入口提示，**这些文档改动尚未提交**。**E0–E7 及补充的 QD-DETR 实验均已完成，没有待续训练任务；本仓库尚未提出新模型。**用户已明确要求加入 QD-DETR，并且暂不做新的多种子实验。

## 1. 研究问题与不可破坏的协议

研究问题：只在已见语义上学习时刻定位和目标存在判断后，GMR 模型能否在下游训练未见的语义中区分 **U+（事件存在）** 与 **U−（事件缺席）**。这里的 *unseen* 指 **downstream-training-unseen**，不要求 CLIP、SlowFast 等通用预训练模型从未接触相关概念。

| 数据 | S+ | S− | U+ | U− | 用途 |
| --- | ---: | ---: | ---: | ---: | --- |
| Train | 6,851 | 1,466 | 0 | 0 | 严格 GMR 只用 S+/S−；定位-only 只用 S+ |
| Validation | 694 | 168 | 300 | 356 | **仅 S+/S−** 用于 GMR 选模及阈值；定位-only 仅用 S+ 选模 |
| Test | 2,090 | 592 | 881 | 947 | 最终四象限评价；共 4,510 条 |

正式数据在 [`data/release/semantic_existence_v1/`](../data/release/semantic_existence_v1/)，原方案在 [`plan.md`](../data/release/semantic_existence_v1/plan.md)。`matched_u_pairs.jsonl` 有 535 对同视频、同来源正例的 U+/U−。**不要用 val U+/U− 调参、选 checkpoint 或阈值；不要用完整原始 Charades-STA 任务微调 checkpoint 初始化严格主实验。**E6 故意加回 held-out 语义，只能称 semantic-seen/leakage reference。

数据发布版的 U+ test 数为 **881**；复核报告的 884 包含打包前隔离的 3 条 `dress|front` 解析错误。负例复核只有数据集所有者对该批次的全局 attestation，没有逐条双人复核日志。数据集本身的限制见[构建说明](semantic_existence_dataset.md)。

## 2. 已完成的实验

三种 backbone 是 Moment-DETR、QD-DETR、FlashVTG。严格 GMR 和定位-only 主比较采用 seed **3407**、最多 100 epoch、不早停，checkpoint 只按 seen validation 选择。早期还保留过另一组较短训练的历史结果，见[旧交接](SEMANTIC_EXISTENCE_HANDOFF.md)；不要把种子与训练长度同时变化的两组结果解释为纯训练长度效应。

| 实验 | 内容 | 状态与报告 |
| --- | --- | --- |
| E0/E1 + QD | 三个无 existence head 的 S+ 定位-only 对照 | 完成；[定位对照报告](semantic_existence_localization_controls.md) |
| E2/E3 + QD | 三个严格 S+/S− GMR baseline | 完成；[100-epoch 报告](semantic_existence_100ep_results.md) |
| E4/E5 + QD | 同一 GMR checkpoint 的 raw 与 seen 阈值硬拒绝定位 | 完成；见定位对照报告及 `diagnostics.json` |
| E6 | 三个 semantic-seen reference：把 2,679 条 held-out 训练正例加回，共 10,996 条 | 完成；[E6 报告](semantic_existence_semantic_seen_reference_results.md) |
| E7 | 字符 n-gram text-only、matched-U 不确定性分析 | 完成；结果在发布包和本地 `results/` |
| 补充分组 | 未见动作 `open/close` 与 16 个未见动作–物体组合 | 已打包；[子集说明](../data/release/semantic_existence_v1/test_subgroups/README.md) |

所有训练 `exit_code` 和评分 `finalize_exit_code` 均为 `0`；三个 GMR/E6 test submission 各覆盖 4,510 个互异 qid。定位-only test 各覆盖 2,971 个正例 qid。已核过 E6 训练、验证、测试无视频或 qid 重叠；发布数据校验通过。

## 3. 当前应记住的结果

以下百分比均为 seed 3407 的 test 诊断。FRR 是正例错误拒绝率，RR 是负例拒绝率；PairAcc 是 matched-U 正例 existence 分数高于负例的比例，平局计 0.5。

| 严格 GMR | Seen AUROC | Unseen AUROC | U+ FRR | U− RR | Matched PairAcc |
| --- | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR | 86.65% | 57.01% | 29.17% | 38.33% | 55.70% |
| QD-DETR | 87.13% | 58.54% | 63.79% | 80.68% | 48.41% |
| FlashVTG | 85.74% | 55.88% | 46.42% | 51.53% | 50.75% |

三模型的 seen→unseen 存在判断均明显下降，但错误类型不同：Moment 主要误接受 U−，QD 与 Flash 对 U+ 有明显额外拒绝。因此**不能把所有模型概括为同一种过度拒绝机制**。

| U+ R@1@IoU 0.5 | 定位-only | 严格 GMR raw | 严格 GMR 硬拒绝后 |
| --- | ---: | ---: | ---: |
| Moment-DETR | 35.07% | 32.92% | 24.40% |
| QD-DETR | 34.85% | 30.65% | 11.80% |
| FlashVTG | 44.27% | 37.34% | 20.32% |

`raw` 取同一 GMR checkpoint 的 `pred_relevant_windows_pre_exist`；“硬拒绝后”按 seen validation 校准阈值输出空集。这是**诊断用硬 gate**，与官方 GMR 软分数 gate/默认阈值不同。QD 和 Flash 的 raw→硬拒绝下降分别为 18.84 和 17.03 个百分点。定位-only 与 GMR raw 的差别还混合了训练数据/目标变化，不能单独归因于 existence head。

| E6 semantic-seen reference | U+ FRR | U− RR | Unseen AUROC | Matched PairAcc |
| --- | ---: | ---: | ---: | ---: |
| Moment-DETR | 3.63% | 3.27% | 45.67% | 57.48% |
| QD-DETR | 3.41% | 4.33% | 53.35% | 70.37% |
| FlashVTG | 2.50% | 2.64% | 46.10% | 52.15% |

E6 几乎都接受 U+，但也几乎都接受 U−；**不是性能上界或成功的开放语义拒绝器**。QD 的配对排序从 48.41% 升到 70.37%，但 seen 阈值下仅拒绝 4.33% 的 U−。E6 同时增加正例数量并改变正负比例，因此不能把其差值视为语义新颖性的纯因果效应。

E7 的 text-only AUROC 为 overall **0.7885**、unseen **0.5678**；matched-U PairAcc **0.5421**，按 325 个视频聚类的 95% bootstrap 区间 **0.4925–0.5928**。完整 test 有文本捷径风险；matched-U 更适合核心科学诊断，但这个区间也不能证明完全没有文本线索。所有模型仍只有每配置一个种子的结果；视频聚类区间不反映训练种子不确定性。

## 4. 分组分析的边界

发布包的 [`test_subgroups/`](../data/release/semantic_existence_v1/test_subgroups/) 已含 JSONL 视图、`counts.csv`、`metrics.csv`、`matched_pair_metrics.csv`。`unseen_action` 有 U+ **675**、U− **882**；`unseen_composition` 有 U+ **206**、U− **65**。535 对 matched-U **全部属于 unseen_action**，按正例动作分为 `open` 352 对、`close` 183 对；组合类没有 PairAcc。16 个组合中有的没有 U− 或样本极少，空的 `dress|front` 是 QC 后的预期结果；不要对小组 AUROC 作稳定结论。

## 5. 文件、环境与复现入口

| 用途 | 位置 |
| --- | --- |
| 原方案与发布数据 | [`plan.md`](../data/release/semantic_existence_v1/plan.md)、[`train/val/test.jsonl`](../data/release/semantic_existence_v1/) |
| 严格 seed 3407 GMR | 本地 `results/semantic_existence/seed3407_100ep/{moment,qd,flash}/`；训练入口 [`run_semantic_existence_100ep_tmux.sh`](../scripts/run_semantic_existence_100ep_tmux.sh) |
| 定位-only | 本地 `results/semantic_existence/localization_only_seed3407_100ep/{moment,qd,flash}/`；[`run_semantic_localization_controls.sh`](../scripts/run_semantic_localization_controls.sh) 与 [`finalize_semantic_localization_controls.sh`](../scripts/finalize_semantic_localization_controls.sh) |
| E6 reference | 本地 `results/semantic_existence/semantic_seen_reference_seed3407_100ep/{moment,qd,flash}/`；[`schedule_semantic_seen_references.sh`](../scripts/schedule_semantic_seen_references.sh) 的 `start` 与 [`finalize_semantic_seen_references.sh`](../scripts/finalize_semantic_seen_references.sh) |
| 指标实现 | [`analyze_semantic_existence.py`](../scripts/analyze_semantic_existence.py)、[`analyze_localization_decomposition.py`](../scripts/analyze_localization_decomposition.py)、[`compare_semantic_seen_reference.py`](../scripts/compare_semantic_seen_reference.py)、[`eval/eval_main.py`](../eval/eval_main.py) |
| 机器可读总表 | 本地 `results/semantic_existence/localization_only_seed3407_100ep/localization_decomposition.json`、`semantic_seen_reference_seed3407_100ep/strict_vs_reference.json` |

本机训练环境：Moment/QD 用 `/home/guoxiangyu/miniconda3/envs/gmr/bin/python`，Flash 用 `/home/guoxiangyu/miniconda3/envs/univtg/bin/python`。视频特征在 `/home/guoxiangyu/paper/新建文件夹/charades/{vid_clip,vid_slowfast}`，文本特征在 `features/charades_semantic_existence/clip_text`；视频特征约 1 秒分辨率，CLIP 512 维、SlowFast 2304 维，`clip_length=1`、`max_v_l=200`。`features/`、`results/` 和构建中间数据被 `.gitignore` 排除；在同一机器清空对话仍可用，**仅克隆 Git 仓库时不会有 checkpoint、逐查询预测或原视频/特征**。E6 的 2,679 条 held-out 训练正例在本机 `data/processed/semantic_existence/removed_train_holdouts.jsonl`，也不属于发布包。

恢复后先运行只读核查：

```bash
python scripts/validate_release.py
for root in results/semantic_existence/localization_only_seed3407_100ep results/semantic_existence/semantic_seen_reference_seed3407_100ep; do
  for model in moment qd flash; do printf '%s/%s: ' "$root" "$model"; cat "$root/$model/exit_code"; done
  printf '%s/finalize: ' "$root"; cat "$root/finalize_exit_code"
done
git status --short
```

预期发布包校验有 535 对 matched-U、split 视频交集 0、10 个 SHA-256 核验通过；上述训练和评分退出码均为 `0`。在重跑任何训练前检查已有结果目录，以免覆盖 checkpoint。详细命令及环境说明以 [README](../README.md) 为准。

## 6. 接下来从哪里继续

方案 E0–E7 的训练与测试已完成；本节原始交接时还没有新模型实验，第二阶段现状见下节。下一步若要写论文，先用[严格结果](semantic_existence_100ep_results.md)、[定位拆解](semantic_existence_localization_controls.md)、[E6 结果](semantic_existence_semantic_seen_reference_results.md)和[分组文件](../data/release/semantic_existence_v1/test_subgroups/)确定可支持的 claim。核心表应并列报告 U+ FRR、U− RR、unseen AUROC、matched-U PairAcc 及 raw→hard-gated U+ 定位，保留 seen-only 校准协议和单种子限制。任何新方法的目标是**降低 U+ 错误拒绝，同时保持 U− 拒绝**；仅提高 U+ 接受率可能重现 E6 的失败。

## 7. 第二阶段进度（2026-09-28 后续）

用户已要求实施多语义划分重复实验，并加入同一样本 U→S 跨划分对照、共享已见负例训练池和组合级最低配对门槛。完整方案及当前数字见[第二阶段实施记录](20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md)。最终组为 A1、A2_alt、A3、C1、C2_alt；初选 A2 和 C2 因候选配对不足而留作失败记录。五组均已通过正式发布校验，全部标注和选择资料均已纳入仓库。

数据负责人已对哈希绑定的 4,491 条新负例及 156 条解析抽样作整批人工确认；该口径不是逐条审核日志。另有 2,485 条与 v1 已发布负例完全一致，沿用原有批次确认来源。五组的 15 个模型均完成 seed 3407、100 epoch 训练和测试评测；预测精确覆盖 test qid。四象限指标、official GMR 评分、text-only 对照、查询分布和按视频 cluster bootstrap 区间均已生成；动作级与组合级同样本 U→S 对照也已完成。完整结果见 README 与[多划分结果报告](semantic_existence_multisplit_results.md)，机器可读输出见 [`semantic_existence_v2_metrics/`](semantic_existence_v2_metrics/)；本节之前的 E0–E7 记录仍指 v1。
