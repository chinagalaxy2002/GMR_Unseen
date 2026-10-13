# Mechanism experiment live monitor

Seen-only training, single seed; initialization and duration are frozen in SUITE.json. Incomplete runs are not scientific results. Training flips include stochasticity; fixed probes run in eval mode. Negative gradient cosines are descriptive measurements, not significance tests.

| Job | State / epoch / batch | PID | Last training GT matches by slot | Train flip % | Fixed-probe flip % | Pure loc/exist cosine (valid samples) |
|---|---|---:|---|---:|---:|---|
| soccer_A1_soccer_moment_with_sa | complete / - / - | 2249276 | [1131, 44, 57, 670, 1326, 1316, 1227, 698, 620, 912] | 23.21 | 7.00 | 0.00022912191812629563 (2937) |
| soccer_A1_soccer_qd_with_sa | complete / - / - | 2249286 | [940, 880, 870, 953, 424, 559, 865, 971, 827, 712] | 16.77 | 17.00 | -2.7854258146249922e-05 (1503) |
| soccer_A1_soccer_flash_native | training / 13 / 850 | 2316383 | - | N/A | N/A | N/A (0) |
| clean_v3_A1_v3_moment_with_sa | complete / - / - | 2295773 | [1839, 5, 2645, 3, 3, 4292, 10, 2, 0, 2] | 1.51 | 1.56 | -0.00016759929398013092 (1228) |
| clean_v3_A1_v3_qd_with_sa | complete / - / - | 2249280 | [3, 35, 2, 2001, 0, 0, 1, 2, 4281, 2476] | 2.67 | 0.00 | 0.0003894214481403345 (1228) |
| clean_v3_A1_v3_flash_native | complete / - / - | 2267138 | - | N/A | N/A | N/A (0) |
| charades_cg_v2_C3_CG_moment_with_sa | complete / - / - | 2271907 | [2, 1, 1, 4, 2246, 4, 2, 3917, 163, 2] | 0.99 | 0.00 | -0.0001696713222428009 (1586) |
| charades_cg_v2_C3_CG_qd_with_sa | training / 88 / 450 | 2297046 | [63, 91, 41, 44, 238, 1799, 3290, 85, 615, 76] | 17.30 | 18.75 | 5.330067626956264e-05 (1389) |
| charades_cg_v2_C3_CG_flash_native | complete / - / - | 2249283 | - | N/A | N/A | N/A (0) |
| soccer_A2_soccer_moment_with_sa | complete / - / - | 2282265 | [1095, 49, 911, 774, 801, 1118, 1077, 590, 790, 1082] | 19.80 | 10.58 | 2.0936529535071927e-05 (3006) |
| soccer_A2_soccer_qd_with_sa | complete / - / - | 2269149 | [964, 861, 870, 960, 559, 652, 885, 947, 822, 767] | 12.33 | 65.38 | 0.0002202240880250034 (1530) |
| soccer_A2_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_flash_native | training / 61 / 1250 | 2291891 | - | N/A | N/A | N/A (0) |
| soccer_A3_soccer_moment_with_sa | training / 44 / 1500 | 2304521 | [1022, 1013, 1069, 773, 1054, 234, 826, 1010, 633, 782] | 33.46 | 23.08 | -5.740719090838141e-05 (1330) |
| soccer_A3_soccer_qd_with_sa | complete / - / - | 2282058 | [1058, 910, 882, 995, 459, 608, 921, 988, 856, 739] | 17.66 | 14.42 | -0.00012277826890129976 (1546) |
| soccer_A3_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C1_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C1_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C1_v3_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C2_soccer_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C2_soccer_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C2_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C2_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C2_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C2_v3_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A1_soccer_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A1_soccer_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A1_v3_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A1_v3_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| charades_cg_v2_C3_CG_moment_no_sa | complete / - / - | 2284662 | [22, 26, 1, 0, 3946, 7, 0, 2333, 0, 7] | 0.60 | 0.00 | 8.43630950412753e-05 (1586) |
| charades_cg_v2_C3_CG_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A2_soccer_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A2_soccer_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A3_soccer_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_A3_soccer_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C1_v3_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C1_v3_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C2_soccer_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| soccer_C2_soccer_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C2_v3_moment_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_C2_v3_qd_no_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
