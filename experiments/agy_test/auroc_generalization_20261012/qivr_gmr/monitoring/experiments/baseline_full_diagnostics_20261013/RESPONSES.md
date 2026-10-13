# Positive localization / positive existence / negative existence during training

Training measurements only; active = valid span and foreground probability >0.5. Fixed eval probes are saved separately. Existence score is per query, not per slot.

| Job | Epoch / step | S+ matched IoU | S+ localization L1 | S+ existence score | S− existence score | S+ / S− foreground slots | S+ / S− evidence slots |
|---|---|---:|---:|---:|---:|---|---|
| soccer_A1_soccer_moment_with_sa | 100 / 150300 | 0.4972 | 0.0130 | 0.6036 | 0.2707 | 3.3425 / 1.4502 | N/A / N/A |
| soccer_A1_soccer_qd_with_sa | 100 / 75200 | 0.4005 | 0.0153 | 0.5126 | 0.3218 | 2.8783 / 0.2082 | N/A / N/A |
| soccer_A1_soccer_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A1_v3_moment_with_sa | 67 / 41100 | 0.7946 | 0.0289 | 0.9644 | 0.3797 | 1.5443 / 0.9487 | N/A / N/A |
| clean_v3_A1_v3_qd_with_sa | 100 / 61400 | 0.8292 | 0.0232 | 0.9959 | 0.0782 | 1.2824 / 0.1304 | N/A / N/A |
| clean_v3_A1_v3_flash_native | 100 / 122800 | N/A | N/A | 1.0000 | 0.0000 | 2.5000 / 2.0000 | N/A / N/A |
| charades_cg_v2_C3_CG_moment_with_sa | 100 / 79300 | 0.8327 | 0.0230 | 0.9778 | 0.0237 | 1.2758 / 0.0417 | N/A / N/A |
| charades_cg_v2_C3_CG_qd_with_sa | 37 / 29250 | 0.6033 | 0.0628 | 0.5154 | 0.5156 | 1.9724 / 1.9825 | N/A / N/A |
| charades_cg_v2_C3_CG_flash_native | 100 / 158600 | N/A | N/A | 1.0000 | 0.0000 | 2.0000 / 2.0000 | N/A / N/A |
| soccer_A2_soccer_moment_with_sa | 100 / 153000 | 0.3979 | 0.0168 | 0.5623 | 0.2734 | 3.5706 / 1.3593 | N/A / N/A |
| soccer_A2_soccer_qd_with_sa | 100 / 76500 | 0.4136 | 0.0146 | 0.5045 | 0.3086 | 2.8414 / 0.1794 | N/A / N/A |
| soccer_A2_soccer_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A2_v3_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A2_v3_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A2_v3_flash_native | 36 / 47622 | N/A | N/A | 0.9966 | 0.4322 | 1.7143 / 1.0000 | N/A / N/A |
| soccer_A3_soccer_moment_with_sa | 6 / 8500 | 0.3767 | 0.0188 | 0.5122 | 0.3235 | 3.4966 / 0.8972 | N/A / N/A |
| soccer_A3_soccer_qd_with_sa | 100 / 77300 | 0.4043 | 0.0157 | 0.5392 | 0.3080 | 3.3742 / 0.2680 | N/A / N/A |
| soccer_A3_soccer_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A3_v3_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A3_v3_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A3_v3_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C1_soccer_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C1_soccer_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C1_soccer_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C1_v3_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C1_v3_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C1_v3_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C2_soccer_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C2_soccer_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C2_soccer_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C2_v3_moment_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C2_v3_qd_with_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C2_v3_flash_native | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A1_soccer_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A1_soccer_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A1_v3_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A1_v3_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| charades_cg_v2_C3_CG_moment_no_sa | 100 / 79300 | 0.8374 | 0.0225 | 0.9849 | 0.0128 | 1.2423 / 0.0392 | N/A / N/A |
| charades_cg_v2_C3_CG_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A2_soccer_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A2_soccer_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A2_v3_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A2_v3_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A3_soccer_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_A3_soccer_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A3_v3_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_A3_v3_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C1_soccer_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C1_soccer_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C1_v3_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C1_v3_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C2_soccer_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| soccer_C2_soccer_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C2_v3_moment_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
| clean_v3_C2_v3_qd_no_sa | - / - | N/A | N/A | N/A | N/A | N/A / N/A | N/A / N/A |
