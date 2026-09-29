# Semantic Existence v1：E6 semantic-seen reference 结果

2026-09-28，单种子 3407。Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR 的 100 epoch 训练、完整 test 推理、四象限诊断和官方评测均已完成，三个训练 `exit_code` 与总评分 `finalize_exit_code` 均为 `0`。机器可读比较见 [`strict_vs_reference.json`](../../results/semantic_existence/semantic_seen_reference_seed3407_100ep/strict_vs_reference.json)。

## 实验口径

严格主实验仅用 6,851 条 S+ 与 1,466 条 S− 训练，共 8,317 条。E6 把原训练视频中的 2,679 条 held-out 正例加回，成为 9,530 条正例与 1,466 条负例，共 10,996 条。两组均用 862 条 seen validation 选择 checkpoint 和校准 existence 阈值，测试完全相同的 4,510 条查询。E6 的最佳 checkpoint 分别来自 Moment 第 6、QD 第 13、Flash 第 24 个 epoch（人类计数）。原训练、验证、测试之间没有视频或 qid 重叠；E6 checkpoint 均启用了 existence head。

E6 **有意让 held-out 语义进入下游训练**，属于 semantic-seen/leakage reference，不能当作严格 unseen baseline。它同时增加了正例数量、改变了正负比例，因此下表的差值不能单独归因于语义新颖性。

## 核心结果

下表百分比均为正式 test。FRR 越低越好，RR、AUROC、PairAcc 越高越好。阈值只在 seen validation 上校准。箭头左侧为严格 seen-only GMR，右侧为 E6 reference。

| Backbone | U+ FRR ↓ | U− RR ↑ | Unseen AUROC ↑ | 535 对 PairAcc ↑ | U+ raw R@1@0.5 ↑ | U+ 硬拒绝后 R@1@0.5 ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR | 29.17 → **3.63** | 38.33 → **3.27** | 57.01 → **45.67** | 55.70 → **57.48** | 32.92 → **35.30** | 24.40 → **34.62** |
| QD-DETR | 63.79 → **3.41** | 80.68 → **4.33** | 58.54 → **53.35** | 48.41 → **70.37** | 30.65 → **33.83** | 11.80 → **33.48** |
| FlashVTG | 46.42 → **2.50** | 51.53 → **2.64** | 55.88 → **46.10** | 50.75 → **52.15** | 37.34 → **56.87** | 20.32 → **56.07** |

三个模型的 U+ 错误拒绝均大幅下降，但 U− 拒绝几乎消失；因此 E6 没有同时解决“接受存在事件”和“拒绝缺席事件”。其 unseen AUROC 反而全部低于严格模型。QD-DETR 的 matched-U 排序改善 **21.96 个百分点**，但仅 **4.33%** 的 U− 被 seen 阈值拒绝。这说明配对排序能力与固定阈值下的拒绝能力必须分别报告；QD 的排序改善不能解释成端到端存在判断已经可靠。

差值的 95% 视频聚类 bootstrap 区间（单位：百分点，10,000 次重采样）如下：

| Backbone | Δ U+ FRR | Δ U− RR | Δ PairAcc |
| --- | ---: | ---: | ---: |
| Moment-DETR | −25.54 [−29.16, −22.05] | −35.06 [−38.08, −32.05] | +1.78 [−3.50, +7.13] |
| QD-DETR | −60.39 [−64.58, −56.08] | −76.35 [−80.32, −72.12] | +21.96 [+15.62, +28.23] |
| FlashVTG | −43.93 [−48.18, −39.63] | −48.89 [−52.87, −44.81] | +1.40 [−2.80, +5.68] |

这些区间针对固定训练结果和测试视频抽样；它们不代表跨种子的稳定性。官方完整 test 的 overall AUROC 分别为 Moment 53.96%、QD 59.49%、Flash 54.61%，详见各模型的 `official_test_metrics.json`。官方阈值口径与上表的 seen-validation 硬拒绝诊断不同，不应混用。

## 解释与下一步

E6 表明“见过 held-out 正例”可以明显提高 U+ 接受率，也能提高某些模型的原始定位；但在只加入 held-out 正例、没有对应 U− 训练负例的设置下，三个模型倾向于把 U+ 与 U− 都判为存在。这个参考实验是**单边正例注入**，不是干净的语义新颖性因果消融，也不是合格的开放语义拒绝模型。论文应将它作为诊断，而非性能上界。

结合[定位-only 对照](semantic_existence_localization_controls.md)，当前最稳妥的结论是：严格 GMR 中，QD-DETR 与 FlashVTG 的 U+ 定位损失有明显的拒绝分量；加入 held-out 正例虽能恢复 U+ 接受，却破坏 U− 拒绝。后续方法应在保持 U− 拒绝的同时降低 U+ 错误拒绝，并在 matched-U 上同时报告排序和阈值指标。

## 复现核查

- 三组 test submission 各有 4,510 个互异 qid；`diagnostics.json` 四象限数量均为 S+ 2,090、S− 592、U+ 881、U− 947。训练集有 10,996 个互异 qid，验证/测试视频与其不重叠。
- 最佳 checkpoint SHA-256：Moment `67adcb81a6ff0ae608786de17f2f2f15961177281230d17447fb7ff8f0ea375e`；QD `6d9cb9efd0b0372a489ea979c17002cbfcf6f6350a5f4c9aec187bb11cb9ab6d`；Flash `330d4fad1d99628299baf07fc8724bdfa34c29442dde656e17a9eed666d78ea0`。
- 训练入口为 [`schedule_semantic_seen_references.sh`](../../scripts/schedule_semantic_seen_references.sh)，推理、诊断及官方评分入口为 [`finalize_semantic_seen_references.sh`](../../scripts/finalize_semantic_seen_references.sh)，比较脚本为 [`compare_semantic_seen_reference.py`](../../scripts/compare_semantic_seen_reference.py)。
