# Full baseline monitoring

Training on Seen only. Table uses the latest completed full Seen validation pass; incomplete training is not a final result. Decoder slots apply to Moment/QD; temporal candidates apply to Flash. Training diagnostics are sampled every 50 steps plus the first batch; fixed Seen probes and validation run every epoch.

| Job | State / epoch | GPU | Seen AUROC | S+ probability median | S− probability median |
|---|---|---:|---:|---:|---:|
| soccer_A1_soccer_moment_with_sa | training / 14 | 0 | 0.7188 | 0.3265 | 0.2845 |
| soccer_A1_soccer_qd_with_sa | training / 17 | 1 | 0.6900 | 0.2713 | 0.2158 |
| soccer_A1_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_A1_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_A1_v3_qd_with_sa | training / 20 | 0 | 0.7951 | 0.9986 | 0.7414 |
| clean_v3_A1_v3_flash_native | queued / None | None | — | — | — |
| charades_cg_v2_C3_CG_moment_with_sa | queued / None | None | — | — | — |
| charades_cg_v2_C3_CG_qd_with_sa | queued / None | None | — | — | — |
| charades_cg_v2_C3_CG_flash_native | training / 8 | 1 | 0.7486 | 0.7323 | 0.3711 |
| soccer_A2_soccer_moment_with_sa | queued / None | None | — | — | — |
| soccer_A2_soccer_qd_with_sa | queued / None | None | — | — | — |
| soccer_A2_soccer_flash_native | queued / None | None | — | — | — |
| clean_v3_A2_v3_moment_with_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_qd_with_sa | queued / None | None | — | — | — |
| clean_v3_A2_v3_flash_native | queued / None | None | — | — | — |
| soccer_A3_soccer_moment_with_sa | queued / None | None | — | — | — |
| soccer_A3_soccer_qd_with_sa | queued / None | None | — | — | — |
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
| charades_cg_v2_C3_CG_moment_no_sa | queued / None | None | — | — | — |
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
