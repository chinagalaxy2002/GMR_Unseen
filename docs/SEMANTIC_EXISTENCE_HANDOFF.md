# Semantic Existence v1 主实验交接

> **历史交接（首轮与 seed 3407 严格 GMR）。** E0–E7 的最新完成状态、定位对照、semantic-seen reference 与清空上下文后的恢复入口，请先读 [`CURRENT_WORK_HANDOFF.md`](CURRENT_WORK_HANDOFF.md)。下文保留早期运行细节，不代表当前待办。

更新时间：2026-09-27（Asia/Shanghai）。这是清空会话上下文后的恢复入口。项目根目录为 `/home/guoxiangyu/paper/Openword`，下文的相对路径均以 `generalized-moment-retrieval/` 为起点。数据构建口径另见 [`data/release/semantic_existence_v1/HANDOFF.md`](../../data/release/semantic_existence_v1/HANDOFF.md)，原实验方案见同目录的 `plan.md`。

## 1. 本轮目标、完成状态

研究问题：模型只在 seen semantics 上学习时刻定位与 existence/rejection，能否在 downstream-training-unseen semantics 中区分 **U+（存在）** 与 **U−（缺席）**。首轮已完成方案中的 E2–E5：Moment-DETR-GMR、FlashVTG-GMR 的单种子训练、同 checkpoint 的 raw/拒绝后定位、四象限和 535 对 matched-U 诊断；另补充 QD-DETR-GMR。**首轮三组及第二轮新种子 3407、强制 100 epoch 的训练与完整测试均已完成。第二轮的 checkpoint、脚本、逐项指标和解读见 [`semantic_existence_100ep_results.md`](semantic_existence_100ep_results.md)。**尚未运行 E0/E1 定位-only 对照、semantic-seen oracle。

实验协议固定为：

| 阶段 | 文件 | 数量与用途 |
| --- | --- | --- |
| 训练 | `/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1/train.jsonl` | S+ 6,851、S− 1,466；U+/U− 均为 0 |
| 选 checkpoint 与阈值 | `features/charades_semantic_existence/val_seen.jsonl` | S+ 694、S− 168；由正式 `val.jsonl` 筛出，**不使用其中 U+/U−** |
| 最终测试 | `/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1/test.jsonl` | S+ 2,090、S− 592、U+ 881、U− 947，共 4,510 |
| 同视频配对 | 发布目录下 `matched_u_pairs.jsonl` | 535 对 U+/U−，用于 PairAcc |

模型的任务特定参数从头训练，没有载入在完整 Charades-STA 上微调过的定位 checkpoint。预先提取的 CLIP/SlowFast 视频特征与 CLIP 文本特征可以使用，因为这里的 unseen 定义是 **downstream-training-unseen**。本轮使用已有 `/home/guoxiangyu/paper/新建文件夹/charades/vid_clip`（512 维）和 `vid_slowfast`（2304 维），约每秒一帧特征；`clip_length=1`、`max_v_l=200`。正句文本特征来自同目录 `txt_clip`，负句由 CLIP ViT-B/32 生成，合并在 `features/charades_semantic_existence/clip_text`。检查结果：14,345 条样本的文本特征齐全，5,449 个视频的两种视频特征齐全。

## 2. 模型、checkpoint 与运行记录

表中的 epoch 同时列出人类计数和 checkpoint 内的零起始 `epoch`。三份最佳 checkpoint 的选模只依赖 seen 验证集。

| 模型 | 种子；训练终点；最佳 epoch | 选模指标 | 最佳 checkpoint | 训练/验证记录 |
| --- | --- | --- | --- | --- |
| Moment-DETR-GMR | 2023；第 12 个 epoch 早停；最佳第 4 个（`epoch=3`） | seen 验证 mAP 25.66% | `results/semantic_existence/moment_detr_gmr/best.ckpt` | 同目录 `train.log`、`val.log` |
| FlashVTG-GMR | 2024；运行 30 个 epoch；最佳第 21 个（`epoch=20`） | seen 验证 R@1@0.5 与 R@1@0.7 的平均值 43.085；该 checkpoint 的 mAP 为 37.66% | `results/semantic_existence/flash_vtg_gmr/charadesSTA-video_tef-seen_only_seed2024_resume_fixed-2026-09-27-14-10-34/model_best.ckpt` | `results/semantic_existence/flash_training_resume_fixed.log`、该 run 目录的 `train.log.txt`、`eval.log.txt`、`opt.json` |
| QD-DETR-GMR | 2023；运行 30 个 epoch；最佳第 27 个（`epoch=26`） | seen 验证 mAP 24.76% | `results/semantic_existence/qd_detr_gmr/best.ckpt` | 同目录 `train.log`、`val.log`；控制台记录 `results/semantic_existence/qd_detr_train.log` |

Checkpoint 的 SHA-256，用于清空上下文后确认文件未被覆盖：

```text
Moment  e93cbbec883e73a3a144c8dbfd2972fe935db9733ad32736a5f32542a5d754e7
Flash   202691e7301bd1d735ebe24661c9fa94069a1e16299a04f4f490966cb4bd13e2
QD      1fc745f343925c563bcb49483f611fa901f6f41ba335cca1685df251a346da8d
```

FlashVTG 在首个 epoch 后遇到 PyTorch AdamW `foreach` 兼容错误。`training/flash_vtg_gmr/inference.py` 的优化器已设 `foreach=False`，加载旧优化器状态后也强制关闭该项；随后从首个 epoch 的完整 checkpoint（模型、优化器、调度器）以同一个种子续跑。中间以 `resume` 命名的旧目录不是另一组独立实验；**采用上表 `resume_fixed` 目录的最终 checkpoint 和结果**。

## 3. 最终结果

下表均为正式 test。诊断阈值先在 seen 验证集上最大化 balanced accuracy，再固定到 test。FRR 是正例被拒绝的比例，RR 是负例被拒绝的比例；PairAcc 比较同视频配对中的两个 `pred_exist_score`。`raw → 拒绝后` R@1@IoU 0.5 使用同一个 checkpoint：前者忽略 existence 拒绝，后者在分数低于上述阈值时将输出视为空集。这是**诊断用硬拒绝**；模型原始预测文件中的 GMR gate 是软分数调整，不能把两者混称。

| 模型 | 验证阈值 | Seen AUROC | Unseen AUROC | S+ FRR | S− RR | U+ FRR | U− RR | U+ raw → 拒绝后 R@1 | Matched-U PairAcc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Moment-DETR-GMR | 0.8802 | 0.8413 | 0.5712 | 27.42% | 79.73% | 23.04% | 23.86% | 34.62% → 27.58% | 64.49% |
| FlashVTG-GMR | 0.9250 | 0.8878 | 0.6146 | 15.60% | 76.18% | 50.40% | 64.84% | 37.34% → 18.62% | 49.72% |
| QD-DETR-GMR | 0.8272 | 0.8608 | 0.5921 | 17.61% | 75.51% | 51.87% | 64.10% | 30.99% → 15.21% | 49.07% |

官方 GMR 完整 test 评测使用评测器本身的默认分类阈值，数值与上一表的 seen 校准阈值不可直接混用：

| 模型 | 官方 overall AUROC | G-mIoU@1 | mAP |
| --- | ---: | ---: | ---: |
| Moment-DETR-GMR | 67.81% | 23.55% | 25.48% |
| FlashVTG-GMR | 80.58% | 32.28% | 33.87% |
| QD-DETR-GMR | 77.44% | 28.53% | 22.35% |

结论须准确表述：三模型的 seen→unseen AUROC 均明显下降。FlashVTG 与 QD-DETR 同时有较高 U− 拒绝率和很高 U+ 错误拒绝率，体现 **novelty-induced over-refusal**；二者 matched-U PairAcc 约 50%，在配对条件下几乎无法排序。Moment-DETR 的 U+ FRR 低于 S+，主要错误反而是 **U− 误接受**（仅 23.86% 被拒绝），不能把它写成同样的过度拒绝。数据已有文本线索风险：发布包的字符 n-gram 诊断 overall AUC 0.7885、unseen AUC 0.5678、matched-U PairAcc 0.5421，因此论文不能只凭 overall AUROC 断言视觉存在判断成功。

## 4. 产物索引与脚本

| 用途 | 入口或产物 |
| --- | --- |
| 原方案/数据说明 | 发布包 `plan.md`、`HANDOFF.md`、`statistics.json`、`text_only_diagnostic.json` |
| 构造 `val_seen`、正句链接、负句 CLIP 特征 | `scripts/prepare_charades_semantic_existence.py`；所需 CLIP ViT-B/32 权重为 `/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt` |
| 四象限、阈值、AUROC、raw/拒绝后 R@1、PairAcc | `scripts/analyze_semantic_existence.py` |
| Moment-DETR 训练/推理 | `training/moment_detr_gmr/train.py`、`evaluate.py`；Charades 配置 `configs/moment_detr_gmr/dataset/charades_semantic_existence.yml`；环境 `/home/guoxiangyu/miniconda3/envs/gmr/bin/python` |
| FlashVTG 训练/推理 | `training/flash_vtg_gmr/train.py`、`inference.py`；完整运行参数保存在最终 run 的 `opt.json`；环境 `/home/guoxiangyu/miniconda3/envs/univtg/bin/python` |
| QD-DETR 训练/推理 | `scripts/train_semantic_existence_qd_detr.sh`、`scripts/infer_semantic_existence_qd_detr.sh`，实现位于 `training/qd_detr_gmr/`、`models/qd_detr_gmr/`，配置位于 `configs/qd_detr_gmr/`；环境 `gmr` |
| 官方评测 | `eval/eval_main.py`；各模型 `official_test_metrics.json` |

三组最佳验证预测、测试预测、诊断与官方结果分别在以下位置：

| 模型 | 最佳 seen 验证预测 | test 预测 | 诊断、官方结果 |
| --- | --- | --- | --- |
| Moment | `results/semantic_existence/moment_detr_gmr/best_charades_semantic_existence_val_preds.jsonl` | 同目录 `test/moment_detr_gmr_test_submission.jsonl` | 同目录 `diagnostics.json`、`official_test_metrics.json` |
| Flash | 最终 `resume_fixed` run 目录下 `best_charadesSTA_val_preds.jsonl` | 同 run 目录 `test/hl_test_submission.jsonl` | 同 run 目录 `diagnostics.json`、`official_test_metrics.json` |
| QD | `results/semantic_existence/qd_detr_gmr/best_charades_semantic_existence_val_preds.jsonl` | 同目录 `test/qd_detr_gmr_test_submission.jsonl` | 同目录 `diagnostics.json`、`official_test_metrics.json` |

原仓库的 `scripts/train_flash_vtg_gmr.sh` 和 `scripts/infer_flash_vtg_gmr.sh` 使用 Soccer-GMR 默认参数，**不是本次 Charades 运行命令**；恢复时以最终 run 的 `opt.json` 与上述数据路径为准。QD 训练脚本带 `--overwrite`，会删除其指定结果目录；复现时应给新 `RESULTS_DIR`，保留现有 checkpoint。

## 5. 已完成核查与下一步

- 从 checkpoint 读取并核对了训练/验证路径、seed、`use_exist_head=true`、`clip_length=1`、`max_v_l=200`；QD 最佳验证预测的诊断 JSON 已逐字节复算一致。
- 三模型最佳验证预测的 qid 集合均与 `val_seen.jsonl` 的 862 条完全一致；正式测试预测均与 `test.jsonl` 的 4,510 条完全一致，无漏样本或重复 qid。
- QD 负例进入 `loss_exist`，模型为带 query-dependent transformer 的 QD-DETR；Flash 的负例也保留于训练。三份模型已按各自的 seen 验证目标选最佳 checkpoint。
- 项目仓库目前有未提交的代码、脚本、配置与 `results/`、`features/` 等未跟踪文件。**清理或切换工作树前先保存这些文件**；不要把当前结果当作已提交到 Git。
- 第一批结果每模型只有一个种子，不要据单次运行宣称模型排序具有统计稳定性。第二批新种子 3407 的 100-epoch 训练用于检查是否因训练不足造成观察到的失败；完成后的测试也应单独报告，不能用测试结果回调超参数。随后可按 `plan.md` 补 E0/E1（不带 existence head 的 localization-only 对照），再决定是否做 semantic-seen oracle、语言风格平衡和统计区间。

## 6. 已完成：新种子 3407、强制 100 epoch

用户在首轮完成后要求检查未收敛的可能性：**三个模型均换为种子 3407，从头训练恰好 100 个 epoch，禁用早停**。训练集、seen-only 验证集、冻结特征、模型结构和主要超参数保持与首轮一致。Moment-DETR 和 QD-DETR 的训练 CLI 已增加 `--seed`；两者的 `--max_es_cnt -1` 现在明确表示禁用早停，Flash 原本支持 `-1`。训练入口是 [`scripts/run_semantic_existence_100ep_tmux.sh`](../scripts/run_semantic_existence_100ep_tmux.sh)，启动命令：

```bash
cd /home/guoxiangyu/paper/Openword/generalized-moment-retrieval
bash scripts/run_semantic_existence_100ep_tmux.sh launch
```

脚本在 2026-09-27 15:47 CST 已启动；再次运行 `launch` 会跳过仍存在的同名会话，不会为它们另启训练。会话与资源分配如下：

| 模型 | tmux 会话 | GPU | 日志目录 |
| --- | --- | --- | --- |
| Moment-DETR-GMR | `semantic_moment_seed3407_100ep` | 0 | `results/semantic_existence/seed3407_100ep/moment/` |
| QD-DETR-GMR | `semantic_qd_seed3407_100ep` | 0 | `results/semantic_existence/seed3407_100ep/qd/` |
| FlashVTG-GMR | `semantic_flash_seed3407_100ep` | 1 | `results/semantic_existence/seed3407_100ep/flash/` |

三组训练均已完成，`exit_code=0`；Moment/QD/Flash 各有 100 个 epoch 的训练记录。GPU 0 同时运行两个较小模型，GPU 1 运行 Flash。日志根目录及每个模型的 `run_metadata.txt` 保留种子、轮数和开始时间。训练所选最佳 epoch 分别为 Moment 11、QD 66、Flash 60。`tmux` 启动时有本机 `libtinfo` 版本提示，但未影响训练。

恢复上下文后，可只读检查历史日志；不要重新运行 `launch`：

```bash
cd /home/guoxiangyu/paper/Openword/generalized-moment-retrieval
tmux ls | rg 'semantic_(moment|qd|flash)_seed3407_100ep'
for m in moment qd flash; do
  echo "$m"
  tail -n 5 "results/semantic_existence/seed3407_100ep/$m/console.log"
  cat "results/semantic_existence/seed3407_100ep/$m/exit_code" 2>/dev/null || true
done
```

新种子测试已在训练、按 seen 验证集选模之后完成，没有用 test 调参。Moment/QD 的 checkpoint 在各自日志目录内 `best.ckpt`；Flash 的最佳 checkpoint 位于 `results/semantic_existence/seed3407_100ep/flash/charadesSTA-video_tef-seen_only_seed3407_100ep-<时间戳>/model_best.ckpt`。完整路径、哈希和验证结果见第二轮结果报告。

新 seed 最佳 checkpoint 已完成完整 test，沿用首轮推理与诊断脚本，结果保存到 `seed3407_100ep` 下各自独立的 `test/` 目录。三模型 seen existence AUROC 为 0.857–0.871，而 unseen 为 0.559–0.585；535 对 matched-U 的 PairAcc 为 48.4%–55.7%。Flash/QD 在 U+ 上较常误拒绝，Moment 在 U− 上较常误接受。详细四象限、raw/硬拒绝和官方 GMR 指标见 [`semantic_existence_100ep_results.md`](semantic_existence_100ep_results.md)。

第二轮使用过的测试推理命令（只读最佳 checkpoint，不启动新训练）：

```bash
cd /home/guoxiangyu/paper/Openword/generalized-moment-retrieval
R="$PWD/results/semantic_existence/seed3407_100ep"
D=/home/guoxiangyu/paper/Openword/data/release/semantic_existence_v1
F="$PWD/features/charades_semantic_existence"
V='/home/guoxiangyu/paper/新建文件夹/charades'
GMR=/home/guoxiangyu/miniconda3/envs/gmr/bin/python
UNIVTG=/home/guoxiangyu/miniconda3/envs/univtg/bin/python

CUDA_VISIBLE_DEVICES=0 "$GMR" training/moment_detr_gmr/evaluate.py \
  --dataset charades_semantic_existence --model_path "$R/moment/best.ckpt" \
  --split test --eval_path "$D/test.jsonl" --t_feat_dir "$F/clip_text" \
  --v_feat_dirs "$V/vid_clip" "$V/vid_slowfast" --results_dir "$R/moment/test"

MODEL_PATH="$R/qd/best.ckpt" RESULTS_DIR="$R/qd/test" \
  bash scripts/infer_semantic_existence_qd_detr.sh

FLASH_RUN="$(find "$R/flash" -mindepth 1 -maxdepth 1 -type d \
  -name 'charadesSTA-video_tef-seen_only_seed3407_100ep-*' | sort | tail -1)"
CUDA_VISIBLE_DEVICES=1 "$UNIVTG" -m training.flash_vtg_gmr.inference \
  configs/flash_vtg_gmr/model.py --resume "$FLASH_RUN/model_best.ckpt" \
  --eval_split_name test --eval_path "$D/test.jsonl" \
  --eval_results_dir "$FLASH_RUN/test" --device 0 --nms_thd -1
```

随后分别以对应的 `best_*_val_preds.jsonl` 和 test submission 运行 `scripts/analyze_semantic_existence.py`；用 `eval/eval_main.py --submission_path ... --gt_path "$D/test.jsonl" --save_path ...` 产生官方结果。推理结束先检查每个 submission 恰好覆盖正式 test 的 4,510 个 qid，再作跨种子结论。
