# C3_CG v2: frozen baseline Seen/Unseen re-evaluation

Completed: 3/3. Same original checkpoint and Seen-validation threshold; no training or test tuning.

| Backbone | Seen AUROC | Unseen AUROC | Gap (pp) | Seen Rej-F1 (%) | Unseen Rej-F1 (%) | Gap (pp) | Seen G-mIoU@1 (%) | Unseen G-mIoU@1 (%) | Gap (pp) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| moment | 0.6338 | 0.5587 | +7.51 | 63.87 | 60.10 | +3.77 | 45.95 | 41.49 | +4.46 |
| qd | 0.5050 | 0.4984 | +0.66 | 57.42 | 57.58 | -0.16 | 39.44 | 38.11 | +1.33 |
| flash | 0.7997 | 0.7204 | +7.93 | 70.63 | 64.24 | +6.39 | 53.43 | 44.96 | +8.47 |

Gap = Seen − Unseen; negative gaps retained. 2,000 joint target-video-cluster bootstrap draws, seed 3407. Full absolute/subset/gap CIs are in bootstrap.json and per-backbone draws. Standalone relative method gains are undefined; no five-split macro. F1/G-mIoU depend on class proportions. Negative labels are constructed, not video-confirmed.
