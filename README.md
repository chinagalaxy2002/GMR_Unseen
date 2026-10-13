# GMR Baseline Generalization Diagnostics

This branch documents the behavior of **Moment-DETR-GMR, QD-DETR-GMR, and FlashVTG-GMR** on seen and unseen queries. It contains diagnostic code, training text logs, epoch summaries, evaluation tables, selection and early-stopping traces, configuration, and status snapshots.

<!-- CURRENT_SNAPSHOT_START -->
Latest uploaded log snapshot: **2026-10-13 20:44:42, Asia/Shanghai**. Queue: **25 complete, 3 running, 2 paused, 7 queued, 1 failed, and 20 cancelled**. These counts include the original diagnostic jobs and three additional publication-protocol reproductions.

[Training status](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/CURRENT_TRAINING_STATUS.md) · [Machine-readable status](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/CURRENT_TRAINING_STATUS.json) · [Upload manifest](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/CURRENT_LOG_UPLOAD_MANIFEST.json)
<!-- CURRENT_SNAPSHOT_END -->

## Diagnostic coverage

The full mechanism diagnostics below belong to the original baseline diagnostic runs. The three additional publication-protocol reproductions retain native training and validation logs, checkpoint-selection traces, early-stopping records, and final evaluation outputs separately.

| # | Diagnostic area | Recorded measurements | Applicable models |
|---|---|---|---|
| 1 | **Training progress and experimental protocol** | Epoch, batch, global step, learning rate, elapsed time, seed, configuration and code hashes, selected checkpoint metric, best epoch, consecutive epochs without improvement, early stopping, process state, and errors. | All three backbones |
| 2 | **Existence classification and score distributions** | Positive/negative raw logits, sigmoid probabilities, native benchmark scores, score saturation, rounding-induced ties, misordered positive-negative pairs, and extreme reversed pairs. | All three backbones |
| 3 | **Temporal localization and candidate responses** | Top-1 localization IoU, best-candidate/oracle coverage, activated candidate counts, correct responses on positive examples, spurious responses on negative examples, and joint localization/existence outcomes. | All three backbones |
| 4 | **Decoder-slot specialization and assignment stability** | Actual Hungarian ground-truth matches per query, assignment changes, training assignment-flip rates, fixed-probe flip rates, and slot utilization. Training matches come from the native criterion. | Moment and QD |
| 5 | **Internal representations and attention** | Layer-wise query cosine similarity, distance, rank, candidate overlap, native self-attention and cross-attention; temporal representations, multiscale pyramid features, candidate boundaries, cross-attention, and native foreground/regression targets for Flash. | Model-specific instrumentation |
| 6 | **Loss contributions and gradient interactions** | Localization, foreground-classification, and existence losses; S+/S− loss contributions; task-gradient norms, cosine similarities, and conflicts; gradient norms before clipping, clipping coefficients, and learning rates. | All three backbones |
| 7 | **Pooling and existence-head contributions** | Which slots or temporal units contribute to pooling, contribution shares from correct/matched slots, changes in logits and probabilities after removing one unit, and existence-head ReLU activation rates. | All three backbones, with different pooling units |
| 8 | **Parameter updates and stratified behavior** | Actual parameter changes per module and epoch; positive-negative ranking within the same video; statistics grouped by video length, ground-truth count, and truncation. | All three backbones |
| 9 | **Seen/unseen generalization and gap decomposition** | Seen and Unseen AUROC, actual rejection F1, end-to-end G-mIoU@1, signed Seen−Unseen gaps, overall rejection F1/rate/G-mIoU, S+/U+ false-rejection rates, subset counts, video-cluster bootstrap intervals, and the 2×2 positive-negative AUROC matrix. | Completed frozen evaluations |

The 2×2 AUROC matrix evaluates **S+ versus S−, U+ versus S−, S+ versus U−, and U+ versus U−**. Its symmetric gap decomposition separates changes associated with positive and negative score distributions.

### Recording stages and frequency

| Stage | Frequency and records |
|---|---|
| Training | Response summaries for each batch; native DETR matching and loss decomposition at each step. Expensive representation, attention, gradient, and leave-one-unit-out diagnostics use the first batch and every 50 steps. Flash loss attribution follows the configured sampling schedule. |
| Fixed Seen probe | Evaluation-mode diagnostics every epoch, including assignment stability, representations, pooling contributions, and score behavior. |
| Full Seen validation | Every epoch: existence scores, localization/candidate behavior, pooling diagnostics, stratified results, and checkpoint-selection statistics. |
| Frozen test evaluation | After the checkpoint and Seen-validation threshold are fixed: Seen/Unseen metrics, joint outcomes, AUROC decomposition, and 2,000 video-cluster bootstrap draws. |
| Parameter updates | Module-level update measurements every epoch. |

### Backbone-specific interpretation

**Moment and QD** have decoder queries and Hungarian assignments. Their diagnostics describe query specialization, matching, overlap, and query-level pooling contributions.

**Flash** uses temporal representations and multiscale temporal candidates. It has no DETR decoder slots or Hungarian assignments. Flash leave-one-unit-out measurements remove a pooled video temporal unit while keeping the native query representation fixed; the removed unit is not a multiscale candidate.

Flash uses its native **SlowFast → CLIP** feature order and six-decimal logit scores. Moment/QD use **CLIP → SlowFast** and four-decimal probability scores. Raw logits, sigmoid probabilities, BCE, and native benchmark scores are recorded separately.

Negative examples have no localization ground truth; their ground-truth coverage and matched IoU are **N/A**. Training assignment changes include dropout and sampling effects and are compared with fixed evaluation probes. Gradient conflicts, local removal interventions, and gap decompositions are descriptive diagnostic measurements rather than standalone causal estimates. The preset probability/foreground threshold of 0.5 and IoU threshold of 0.5 are used for descriptive statistics.

## Experiment scope and scheduling

| Dataset | Splits | Original baseline settings | Original DETR no-SA settings |
|---|---|---:|---:|
| Clean v3 | A1, A2, A3, C1, C2 | 15 | 10 |
| Charades-CG v2 | C3_CG | 3 | 2 |
| Soccer | A1, A2, A3, C1, C2 | 15 | 10 |
| Total | 11 splits | **33** | **22** |

The original suite has **55 settings**. Its two completed CG no-SA runs are retained; the remaining **20 no-SA runs are cancelled**. Three publication-protocol reproductions were added, giving **58 registered jobs** in total. QIVR is not part of this queue.

Original diagnostic runs use fresh initialization, seed **3407**, **100 epochs**, and train all model parameters with pre-extracted CLIP, SlowFast, and text features. Scheduling allows at most **two active training tasks per GPU**, prioritizes **CG and Clean v3**, and runs **Soccer last**. Paused Soccer processes retain their training state.

## Checkpoint selection and early stopping

Training uses **S+/S− only**. Checkpoints, thresholds, and hyperparameters are selected using **Seen validation only**. Test evaluation follows checkpoint and threshold freezing.

| Protocol | Checkpoint selection | Training termination |
|---|---|---|
| Original full diagnostics | Highest Seen-validation AUROC; earliest epoch on a tie | Fixed 100 epochs |
| Publication reproduction: Moment | Highest Seen-validation MR-full-mAP | Stop after **26** consecutive non-improving epochs (`es_cnt >= 26`), capped at 100 epochs |
| Publication reproduction: QD | Highest Seen-validation MR-full-mAP; native mIoU fallback for a non-numeric mAP | Stop after **27** consecutive non-improving epochs (`es_cnt > 26`), capped at 100 epochs |
| Publication reproduction: Flash | Highest Seen-validation mean of R1@0.5 and R1@0.7 | Stop after **27** consecutive non-improving epochs (`es_cnt > 26`), capped at 100 epochs |

Publication reproductions use `max_es_cnt=26`. Only a **strict improvement** resets the counter; ties count as non-improvements. Threshold calibration maximizes balanced accuracy on Seen validation. The original AUROC-selected runs and localization-selected reproductions retain separate labels and outputs.

The publication reference is [publication/gmr-baseline-summary-20261011](https://github.com/chinagalaxy2002/GMR_Unseen/tree/publication/gmr-baseline-summary-20261011), frozen at commit `2677cfecddd0101b187d0ab413f2b51fe09ea201`.

### Targeted reproduction status at the uploaded snapshot

| Setting | Final training epoch | Best epoch | Early stop | Evaluation state |
|---|---:|---:|---|---|
| CG C3 Moment | 40 | 14 | Yes | Complete |
| Clean A1 QD | 100 | 98 | No | Complete |
| Clean A2 Flash | 51 | 24 | Yes | Test inference failed because `frozen_checkpoints/opt.json` was missing; final test metrics were not generated |

Only these three settings were added for retraining. Other completed settings were retained. Historical prediction-parity and pipeline-replay checks use published artifacts and are identified separately from new training results.

[Protocol audit](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/publication_protocol_reproduction_20261013_v2/PROTOCOL_AUDIT.md) · [Native entry-point checks](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/publication_protocol_reproduction_20261013_v2/NATIVE_ENTRYPOINT_CHECKS.json) · [Published prediction parity](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/publication_protocol_reproduction_20261013_v2/PUBLISHED_PREDICTION_PARITY.json) · [Historical pipeline replay](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/publication_protocol_reproduction_20261013_v2/PIPELINE_REPLAY_CHECKS.json) · [Reproduction status](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/REPRODUCTION_STATUS.json)

## Generalization reporting

Each completed split and backbone is reported separately with:

- **Seen and Unseen AUROC, actual Rej-F1, and end-to-end G-mIoU@1**.
- **Performance Gap = Seen − Unseen**, in percentage points; negative gaps remain improvements.
- Overall Rej-F1, overall rejection rate, S+ and U+ false-rejection rates, and overall G-mIoU@1.
- Positive/negative counts for each subset and **95% video-cluster bootstrap confidence intervals**, using 2,000 draws.
- For available same-split, same-backbone paired comparisons: **Unseen Net Gain, Seen Change, and Gap Reduction** for all three metrics, with paired bootstrap intervals. Standalone baselines have no baseline-relative change.

Rej-F1 and G-mIoU depend on subset class proportions. Cross-protocol historical differences are labeled as protocol differences. Five-split macro averages are reported only after all five splits are complete; unfinished runs and partial summaries retain explicit status labels.

## Repository records and upload policy

Current synchronization includes **training text logs, epoch summaries, final metric tables, selection/early-stopping traces, calibration/configuration, and progress snapshots**. It adds **zero checkpoints, raw arrays, per-sample prediction files, bootstrap arrays, or raw-data archives**. Features, videos, caches, credentials, and duplicate source trees are excluded.

Existing historical Release archives remain available through the [archive index](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/RECORDS_README.md). They describe earlier snapshots; they are not newly generated archives. Local raw diagnostic records and frozen predictions retain their original paths. The [current upload manifest](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/CURRENT_LOG_UPLOAD_MANIFEST.json) specifies the files copied in the latest log synchronization. `DIAGNOSTIC_SNAPSHOT.json` describes the earlier 00:34 snapshot.

All published status files are **time-stamped snapshots**, not a live dashboard. Server paths and process IDs refer to the training machine.

## Documentation, entry points, and validation

| Resource | Purpose |
|---|---|
| [Diagnostic scope](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/DIAGNOSTIC_LOG_SCOPE.md) | Nine diagnostic areas and recording stages |
| [Full monitoring specification](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FULL_BASELINE_MONITORING.md) | Detailed fields, sampling, and interpretation |
| [Handoff](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/HANDOFF_20261013_BASELINE_FULL_DIAGNOSTICS.md) | Implementation, operational context, evidence, and recovery notes |
| [Original suite](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/SUITE.json) | Frozen original 55-setting configuration |
| [Queue snapshot](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/STATUS.json) | Uploaded job states |
| [Seen monitoring summary](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013/FULL_MONITORING.md) | Latest complete Seen-validation summaries in the uploaded records |
| [Priority scheduler](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/priority_decoder_controller.py) | CG/Clean priority, Soccer pausing, and two tasks per GPU |
| [DETR diagnostic runner](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/run_decoder_experiment.py) | Moment/QD baseline diagnostics |
| [Flash diagnostic runner](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/run_flash_monitor_experiment.py) | Native Flash temporal diagnostics |
| [Publication reproduction runner](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/run_publication_reproduction.py) | Native-protocol training and frozen evaluation |
| [AUROC mechanism monitor](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/src/auroc_mechanism_monitor.py) | Scores, pooling interventions, gradients, and loss decomposition |
| [Decoder-slot monitor](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/src/decoder_slot_monitor.py) | Query representations, matching, and attention |
| [DETR validation evidence](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FULL_MONITOR_TEST_RESULTS.json) | Four DETR combinations: matching outputs, gradients, RNG state, and exact native loss decomposition |
| [Flash validation evidence](experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/FLASH_FULL_MONITOR_TEST_RESULTS.json) | Instrumentation checks; 16 historical Seen examples with maximum logit difference ≤2e-6 and zero set-IoU difference |

The branch includes model/dataset source and registry support for the diagnostic runners. Execution requires locally prepared annotations and features plus the documented environments. The server uses `gmr` with Torch **2.6.0+cu124** for DETR and `univtg` with Torch **2.0.1+cu118** for Flash. Existing background training continues on the server; the repository records its uploaded snapshots.
