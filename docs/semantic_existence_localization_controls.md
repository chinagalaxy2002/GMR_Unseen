# Semantic Existence v1：定位-only 对照与拒绝损失拆解

2026-09-28，seed 3407。对应原方案 E0/E1，并增加 QD-DETR backbone。三组训练与测试均已完成，`exit_code=0`；自动评分 `finalize_exit_code=0`。E6 semantic-seen reference 的结果另见 [`semantic_existence_semantic_seen_reference_results.md`](semantic_existence_semantic_seen_reference_results.md)，本报告只分析定位对照。

## 协议与产物

定位-only 模型仅使用 6,851 条 train S+，只在 694 条 val S+ 上选 checkpoint，不使用 existence head。测试只看原 test 的 2,090 条 S+ 和 881 条 U+。三个模型均用 seed 3407、100 epoch 上限且不早停；视频与文本特征、Charades 时序配置沿用相应 GMR baseline。最佳 checkpoint 分别为 Moment 第 4、QD 第 97、Flash 第 29 个 epoch（人类计数）。这些模型不是从完整 Charades-STA 微调 checkpoint 初始化。

对照中的 **GMR raw** 是已完成的同种子 GMR checkpoint 输出的 `pred_relevant_windows_pre_exist`；**GMR hard-gated** 是当 `pred_exist_score` 低于 seen validation 校准阈值时将查询视为空集。这里的硬拒绝是诊断指标，不等于官方 GMR 的软分数 gate。所有 R@1 均在同一批 test 查询上计算，IoU 阈值为 0.5。

完整机器可读结果为 [`localization_decomposition.json`](../results/semantic_existence/localization_only_seed3407_100ep/localization_decomposition.json)。单模型原始评分分别见 `results/semantic_existence/localization_only_seed3407_100ep/{moment,qd,flash}/localization_comparison.json`；脚本为 [`analyze_localization_decomposition.py`](../scripts/analyze_localization_decomposition.py)。

## U+ 结果

| Backbone | Plain U+ R@1 | GMR raw U+ R@1 | GMR hard-gated U+ R@1 | Plain − raw | Raw − hard gate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR | 35.07% | 32.92% | 24.40% | 2.16 pp [−1.01, 5.36] | 8.51 pp [6.42, 10.71] |
| QD-DETR | 34.85% | 30.65% | 11.80% | 4.20 pp [−0.22, 8.64] | 18.84 pp [15.63, 22.07] |
| FlashVTG | 44.27% | 37.34% | 20.32% | 6.92 pp [3.01, 10.90] | 17.03 pp [14.12, 20.04] |

方括号为按视频聚类重采样 10,000 次所得的 95% percentile 区间，只描述这个固定测试集上的抽样不确定性，不涵盖训练种子变动。`Plain − raw` 不能单独归因于 existence head，因为两次训练也分别使用 S+ 与 S+/S−；`Raw − hard gate` 则是在**同一个 GMR checkpoint** 内关闭/开启硬拒绝所得的精确差值。

QD-DETR 和 FlashVTG 的 U+ 原始定位仍能命中约 31% 和 37%，但硬拒绝分别拿掉 18.84 和 17.03 个百分点。这直接支持存在判断造成额外 U+ 定位损失。Moment-DETR 的硬拒绝损失较小，同时它在主实验中大量误接受 U−，因此不能把三种 backbone 的失败机制写成完全相同。

## 535 对 matched-U 中的正例

| Backbone | Plain U+ R@1 | GMR raw U+ R@1 | GMR hard-gated U+ R@1 | U+ false refusal |
| --- | ---: | ---: | ---: | ---: |
| Moment-DETR | 34.77% | 33.46% | 24.86% | 26.17% |
| QD-DETR | 35.33% | 32.15% | 7.48% | 77.94% |
| FlashVTG | 43.55% | 37.76% | 14.58% | 56.07% |

Matched-U 的 U+ 是 535 个同视频 U+/U− 配对中的真实存在查询。QD-DETR、FlashVTG 的错误拒绝在这个核心子集上更重。配对分数排序和不确定性另见 [`matched_pair_uncertainty.json`](../results/semantic_existence/seed3407_100ep/matched_pair_uncertainty.json)。

复算发布版字符 n-gram text-only 模型后，其 535 对 PairAcc 为 54.21%，按 325 个视频聚类的 95% bootstrap 区间为 **49.25%–59.28%**，双侧符号检验 p=0.0570；区间包含 50%。这不能证明配对子集完全没有文本线索，但比完整 test 的文本-only AUROC 78.85% 更适合研究视觉存在判断。可复算输出见 [`text_only_pair_uncertainty.json`](../results/semantic_existence/seed3407_100ep/text_only_pair_uncertainty.json)。

## 核查

- 三个定位-only checkpoint 均无 `exist_head` 参数；最佳 checkpoint SHA-256 分别为 Moment `f856fcefa451a9d974163a8b7e65fd04d0cfddab6d7c9b0392315f791fbea98b`、QD `0629c8216b3d105304fc81c4fbf06385d00a756170d8578bf68f2fb69a600f7f`、Flash `80a6303aae16dda75207bc1d581ad5be50fbc9b051246890a5b1b63b0871f721`。
- 拆解脚本复算的三组 GMR U+ raw/hard-gated R@1 与既有 `diagnostics.json` 逐值一致。
- 首次误含 U+ 的验证视图已在首次验证前停止，未产生可用 checkpoint；正式三组训练均仅使用 694 条 val S+。
