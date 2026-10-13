# Mechanism experiment live monitor

Seen-only training, single seed; initialization and duration are frozen in SUITE.json. Incomplete runs are not scientific results. Training flips include stochasticity; fixed probes run in eval mode. Negative gradient cosines are descriptive measurements, not significance tests.

| Job | State / epoch / batch | PID | Last training GT matches by slot | Train flip % | Fixed-probe flip % | Pure loc/exist cosine (valid samples) |
|---|---|---:|---|---:|---:|---|
| soccer_A1_soccer_moment_with_sa | complete / - / - | 2249276 | [1131, 44, 57, 670, 1326, 1316, 1227, 698, 620, 912] | 23.21 | 7.00 | 0.00022912191812629563 (2937) |
| soccer_A1_soccer_qd_with_sa | complete / - / - | 2249286 | [940, 880, 870, 953, 424, 559, 865, 971, 827, 712] | 16.77 | 17.00 | -2.7854258146249922e-05 (1503) |
| soccer_A1_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A1_v3_moment_with_sa | training / 67 / 600 | 2295773 | [1799, 2, 2652, 6, 8, 4315, 9, 4, 4, 2] | 1.89 | 1.56 | -0.00023043497490194778 (823) |
| clean_v3_A1_v3_qd_with_sa | complete / - / - | 2249280 | [3, 35, 2, 2001, 0, 0, 1, 2, 4281, 2476] | 2.67 | 0.00 | 0.0003894214481403345 (1228) |
| clean_v3_A1_v3_flash_native | complete / - / - | 2267138 | - | N/A | N/A | N/A (0) |
| charades_cg_v2_C3_CG_moment_with_sa | complete / - / - | 2271907 | [2, 1, 1, 4, 2246, 4, 2, 3917, 163, 2] | 0.99 | 0.00 | -0.0001696713222428009 (1586) |
| charades_cg_v2_C3_CG_qd_with_sa | training / 37 / 700 | 2297046 | [38, 99, 2309, 112, 139, 300, 2807, 106, 310, 122] | 23.67 | 34.38 | 0.00020101941001741537 (586) |
| charades_cg_v2_C3_CG_flash_native | complete / - / - | 2249283 | - | N/A | N/A | N/A (0) |
| soccer_A2_soccer_moment_with_sa | complete / - / - | 2282265 | [1095, 49, 911, 774, 801, 1118, 1077, 590, 790, 1082] | 19.80 | 10.58 | 2.0936529535071927e-05 (3006) |
| soccer_A2_soccer_qd_with_sa | complete / - / - | 2269149 | [964, 861, 870, 960, 559, 652, 885, 947, 822, 767] | 12.33 | 65.38 | 0.0002202240880250034 (1530) |
| soccer_A2_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_flash_native | training / 36 / 300 | 2291891 | - | N/A | N/A | N/A (0) |
| soccer_A3_soccer_moment_with_sa | training / 6 / 750 | 2304521 | [249, 934, 481, 268, 925, 867, 1303, 911, 1223, 1255] | 66.93 | 53.85 | 0.0005597139460788029 (168) |
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
