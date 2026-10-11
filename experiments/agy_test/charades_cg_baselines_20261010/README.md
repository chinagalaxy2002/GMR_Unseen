# Charades-CG-GMR C3_CG baselines

Replicates the native training/inference protocol in `../v3_balanced_baselines_20261010` for Moment-DETR-GMR, QD-DETR-GMR and FlashVTG-GMR. Each model starts fresh: seed 3407, maximum 100 epochs, early-stopping patience 26, original per-backbone batches and feature ordering. Native code is copied from that experiment. Checkpoints and BA thresholds use Seen validation only.

Source: `data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v1`. Immutable annotation snapshots are under `groups/C3_CG/release/C3_CG/`. Train has 6,342 S+ and 6,342 S−; Seen validation has 684 S+ and 684 S−; test has 2,990 U+ and 2,990 U−. The published package excludes Test-Trivial; no Seen test metrics or Seen→Unseen test gaps can be computed. They are N/A, including S+ test FRR. Calibration-set scores are not used as Seen test results.

Exact-query SHA256 matching permits token-feature reuse; 572 missing unique texts are encoded with the same local CLIP token-state extraction used for previous experiments. All three backbones use the same verified text/video feature inputs. Feature and source manifests record identities and checksums.

`QUEUE_STATUS.json` and per-model `runs/*/console.log` track progress. `FINAL_EVALUATION_STATUS.json` is written only after the pipeline terminates. Evaluation outputs under `evaluation/` include the original requested tables, all available AUROC/Rej-F1/G-mIoU@1 metrics, CSV/JSON and bootstrap CIs. Each backbone keeps its own frozen native predictions, checkpoint manifest, Seen calibration metadata and 2,000 video-cluster bootstrap draws. Standalone relative gains/change/reduction are undefined; no macro over the old five splits is computed.

Launch: `/home/guoxiangyu/miniconda3/envs/univtg/bin/python -u experiments/agy_test/charades_cg_baselines_20261010/run_baselines.py` from repository root. A filesystem lock prevents duplicate queues. Pipeline failures remain explicit in status files; interrupted training is never silently overwritten.

Durable tmux session: `c3_cg_baselines_20261010`.
