# Full baseline monitoring

Training on Seen only. Table uses the latest completed full Seen validation pass; incomplete training is not a final result. Decoder slots apply to Moment/QD; temporal candidates apply to Flash. Training diagnostics are sampled every 50 steps plus the first batch; fixed Seen probes and validation run every epoch.

| Job | State / epoch | GPU | Seen AUROC | S+ probability median | S− probability median |
|---|---|---:|---:|---:|---:|
| soccer_A1_soccer_moment_with_sa | complete / 100 | 0 | 0.7702 | 0.4452 | 0.2011 |
| soccer_A1_soccer_qd_with_sa | complete / 100 | 1 | 0.6958 | 0.3607 | 0.3154 |
| soccer_A1_soccer_flash_native | training / 13 | 1 | 0.7298 | 0.4492 | 0.3245 |
| clean_v3_A1_v3_moment_with_sa | complete / 100 | 1 | 0.7441 | 1.0000 | 0.9805 |
| clean_v3_A1_v3_qd_with_sa | complete / 100 | 0 | 0.7312 | 1.0000 | 0.9794 |
| clean_v3_A1_v3_flash_native | complete / 100 | 0 | 0.7802 | 1.0000 | 0.9957 |
| charades_cg_v2_C3_CG_moment_with_sa | complete / 100 | 0 | 0.7755 | 0.9949 | 0.0001 |
| charades_cg_v2_C3_CG_qd_with_sa | training / 88 | 1 | 0.4986 | 0.4350 | 0.4357 |
| charades_cg_v2_C3_CG_flash_native | complete / 100 | 1 | 0.8226 | 1.0000 | 0.0000 |
| soccer_A2_soccer_moment_with_sa | complete / 100 | 0 | 0.7622 | 0.4579 | 0.2696 |
| soccer_A2_soccer_qd_with_sa | complete / 100 | 1 | 0.7072 | 0.3804 | 0.2949 |
| soccer_A2_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_A2_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_qd_with_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_flash_native | training / 61 | 0 | 0.7827 | 1.0000 | 0.9656 |
| soccer_A3_soccer_moment_with_sa | training / 44 | 0 | 0.7632 | 0.4187 | 0.2566 |
| soccer_A3_soccer_qd_with_sa | complete / 100 | 1 | 0.7067 | 0.3574 | 0.2698 |
| soccer_A3_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_A3_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_A3_v3_qd_with_sa | queued / None | None | — | — | — |
| clean_v3_A3_v3_flash_native | queued / None | None | — | — | — |
| soccer_C1_soccer_moment_with_sa | queued / None | None | — | — | — |
| soccer_C1_soccer_qd_with_sa | queued / None | None | — | — | — |
| soccer_C1_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_C1_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_C1_v3_qd_with_sa | queued / None | None | — | — | — |
| clean_v3_C1_v3_flash_native | queued / None | None | — | — | — |
| soccer_C2_soccer_moment_with_sa | queued / None | None | — | — | — |
| soccer_C2_soccer_qd_with_sa | queued / None | None | — | — | — |
| soccer_C2_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_C2_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_C2_v3_qd_with_sa | queued / None | None | — | — | — |
| clean_v3_C2_v3_flash_native | queued / None | None | — | — | — |
| soccer_A1_soccer_moment_no_sa | queued / None | None | — | — | — |
| soccer_A1_soccer_qd_no_sa | queued / None | None | — | — | — |
| clean_v3_A1_v3_moment_no_sa | queued / None | None | — | — | — |
| clean_v3_A1_v3_qd_no_sa | queued / None | None | — | — | — |
| charades_cg_v2_C3_CG_moment_no_sa | complete / 100 | 1 | 0.7543 | 0.9826 | 0.0001 |
| charades_cg_v2_C3_CG_qd_no_sa | queued / None | None | — | — | — |
| soccer_A2_soccer_moment_no_sa | queued / None | None | — | — | — |
| soccer_A2_soccer_qd_no_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_moment_no_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_qd_no_sa | queued / None | None | — | — | — |
| soccer_A3_soccer_moment_no_sa | queued / None | None | — | — | — |
| soccer_A3_soccer_qd_no_sa | queued / None | None | — | — | — |
| clean_v3_A3_v3_moment_no_sa | queued / None | None | — | — | — |
| clean_v3_A3_v3_qd_no_sa | queued / None | None | — | — | — |
| soccer_C1_soccer_moment_no_sa | queued / None | None | — | — | — |
| soccer_C1_soccer_qd_no_sa | queued / None | None | — | — | — |
| clean_v3_C1_v3_moment_no_sa | queued / None | None | — | — | — |
| clean_v3_C1_v3_qd_no_sa | queued / None | None | — | — | — |
| soccer_C2_soccer_moment_no_sa | queued / None | None | — | — | — |
| soccer_C2_soccer_qd_no_sa | queued / None | None | — | — | — |
| clean_v3_C2_v3_moment_no_sa | queued / None | None | — | — | — |
| clean_v3_C2_v3_qd_no_sa | queued / None | None | — | — | — |
