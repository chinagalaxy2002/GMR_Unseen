# Clean v3 release baselines

![原 GMR README 的 GMR Adapter 总体方法图](../../../assets/adapter10.png)

*原 [GMR](https://github.com/dymm9977/generalized-moment-retrieval) 方法图：存在判断决定返回定位结果或空集。*

GMR 同时判断事件是否存在并定位其时间窗。我们关注：**面对训练未见的动作或组合，模型能否找准真实事件，并拒绝未发生的事件？** 本实验在五组语义划分上仅用 Seen 训练和选模，评测三个 GMR 骨干；三模型的五划分宏平均 AUROC 从 Seen 到 Unseen 下降 **18.96–20.76 pp**，表明存在判断明显退化，支持进一步联合研究拒绝与定位的语义泛化。

Dataset: `data/release/semantic_existence_v3_release`, isolated from historical initial-v3 runs. Five groups × Moment-DETR-GMR / QD-DETR-GMR / FlashVTG-GMR, seed 3407, fresh training, maximum 100 epochs, early stop after 27 validations without improvement. Only S+/S− training and full Seen validation checkpoint/threshold selection. The initial six jobs run on two GPUs (three jobs per GPU), and remaining jobs are queued.

Finalization is complete only when `FINAL_EVALUATION_STATUS.json` has `complete: true`. Until then, evaluation files are partial/provisional. The running queue and automatic finalizer use tmux sessions `v3_release_baselines_20261009` and `v3_release_baseline_finalize_20261009`.

Artifacts:

- `RELEASE_VALIDATION.json`, `DATA_AUDIT.json`: clean release validation, snapshot hashes and exact-query feature coverage.
- `SOURCE_MANIFEST.json`, `native_source/`, `PROTOCOL.json`: source snapshot and fixed protocol.
- `QUEUE_STATUS.json`, `queue.log`: live progress/errors.
- `groups/<group>/runs/<backbone>/console.log`: training progress.
- `groups/<group>/frozen_checkpoints/<backbone>/`: Seen-selected weights, predictions and checksums.
- `groups/<group>/evaluation/<backbone>/`: frozen Seen threshold, test scores/windows, bootstrap draws and metrics.
- `evaluation/STANDARD_EVALUATION.md`: both requested tables, per group and complete five-group equal-weight macros.
- `evaluation/metrics.csv`, `metrics.json`, `bootstrap.json`: machine-readable outputs.
- `FINAL_EVALUATION_STATUS.json`: final completion and score readout.

AUROC uses Moment/QD native four-decimal sigmoid and Flash native six-decimal logit (the native three-decimal Flash probabilities have saturation ties). Threshold maximizes BA over 91 Seen-validation percentiles 5–95, earliest tie, with acceptance score >= threshold. G-mIoU@1 uses each backbone's first valid native window, without skipping windows extending beyond annotation duration. Rejected negatives receive 1, rejected positives 0. All test rows retained. Baseline relative Unseen Net Gain, Seen Change and Gap Reduction are undefined and shown as —; the table CI is absolute Unseen AUROC. All eight metric absolute intervals are saved. Video-cluster bootstrap: 2,000 draws, seed 3407, frozen checkpoint and threshold; complete five-split macro uses paired draws over the common video universe. CI does not measure variation across training seeds.

Verification: `check_evaluator_parity.py` replays 4,999 historical rows for each backbone and matches all eight corrected historical metrics within 1e-7. This verifies arithmetic only; historical metrics are not new release results.

Restart only after ensuring no existing queue is running. Do not overwrite interrupted training: the runner deliberately refuses a checkpoint-bearing unfinished run. Successful exited runs are reused.

```bash
/home/guoxiangyu/miniconda3/envs/univtg/bin/python -u experiments/agy_test/v3_release_baselines_20261009/run_baselines.py
/home/guoxiangyu/miniconda3/envs/univtg/bin/python -u experiments/agy_test/v3_release_baselines_20261009/finalize_baselines.py
```

Future experiments must also report Seen/Unseen Rej-F1 and G-mIoU@1 and their pp gaps. Current supplementary summary: `evaluation/GENERALIZATION_DROP_COMPARISON.md`, `degradation_metrics.csv/json`, and `degradation_bootstrap.json`. The watcher automatically includes each newly evaluated setting and final high-precision scores.
