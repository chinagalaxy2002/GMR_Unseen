# Task A enhancement: Train/Val status

All methods load the same E0 checkpoint, freeze the localizer, and require an exact E0 localizer fingerprint.

| Run | State | GPU | Epoch | Val AUROC | G-mIoU@1(0.4) | G-mIoU@1(0.5) | Native mAP | Fingerprint |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A1_multigranularity_s2024 | complete | 0 | 6 | 75.41923436041083 | 31.81 | 40.6 | 26.82 | OK |
| A2_joint_cardinality_s2024 | complete | 0 | 6 | 75.53314659197011 | 34.93 | 45.2 | 26.82 | OK |
| A3_similarity_hardneg_s2024 | complete | 1 | 6 | 74.76003734827263 | 47.14 | 51.13 | 26.82 | OK |
| A4_combined_readonly_s2024 | complete | 1 | 6 | 75.33333333333331 | 47.47 | 46.48 | 26.82 | OK |
