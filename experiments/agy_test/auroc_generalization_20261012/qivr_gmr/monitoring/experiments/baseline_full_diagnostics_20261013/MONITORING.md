# Mechanism experiment live monitor

Seen-only training, single seed; initialization and duration are frozen in SUITE.json. Incomplete runs are not scientific results. Training flips include stochasticity; fixed probes run in eval mode. Negative gradient cosines are descriptive measurements, not significance tests.

| Job | State / epoch / batch | PID | Last training GT matches by slot | Train flip % | Fixed-probe flip % | Pure loc/exist cosine (valid samples) |
|---|---|---:|---|---:|---:|---|
| soccer_A1_soccer_moment_with_sa | complete / - / - | 2249276 | [1131, 44, 57, 670, 1326, 1316, 1227, 698, 620, 912] | 23.21 | 7.00 | 0.00022912191812629563 (2937) |
| soccer_A1_soccer_qd_with_sa | complete / - / - | 2249286 | [940, 880, 870, 953, 424, 559, 865, 971, 827, 712] | 16.77 | 17.00 | -2.7854258146249922e-05 (1503) |
| soccer_A1_soccer_flash_native | training / 59 / 800 | 2316383 | - | N/A | N/A | N/A (0) |
| clean_v3_A1_v3_moment_with_sa | complete / - / - | 2295773 | [1839, 5, 2645, 3, 3, 4292, 10, 2, 0, 2] | 1.51 | 1.56 | -0.00016759929398013092 (1228) |
| clean_v3_A1_v3_qd_with_sa | complete / - / - | 2249280 | [3, 35, 2, 2001, 0, 0, 1, 2, 4281, 2476] | 2.67 | 0.00 | 0.0003894214481403345 (1228) |
| clean_v3_A1_v3_flash_native | complete / - / - | 2267138 | - | N/A | N/A | N/A (0) |
| charades_cg_v2_C3_CG_moment_with_sa | complete / - / - | 2271907 | [2, 1, 1, 4, 2246, 4, 2, 3917, 163, 2] | 0.99 | 0.00 | -0.0001696713222428009 (1586) |
| charades_cg_v2_C3_CG_qd_with_sa | complete / - / - | 2297046 | [78, 114, 68, 43, 621, 1569, 3117, 65, 601, 66] | 18.81 | 21.88 | 1.5723535661745678e-05 (1586) |
| charades_cg_v2_C3_CG_flash_native | complete / - / - | 2249283 | - | N/A | N/A | N/A (0) |
| soccer_A2_soccer_moment_with_sa | complete / - / - | 2282265 | [1095, 49, 911, 774, 801, 1118, 1077, 590, 790, 1082] | 19.80 | 10.58 | 2.0936529535071927e-05 (3006) |
| soccer_A2_soccer_qd_with_sa | complete / - / - | 2269149 | [964, 861, 870, 960, 559, 652, 885, 947, 822, 767] | 12.33 | 65.38 | 0.0002202240880250034 (1530) |
| soccer_A2_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A2_v3_moment_with_sa | training / 3 / 100 | 2339296 | [93, 155, 114, 70, 2678, 4927, 110, 1487, 83, 74] | 71.67 | 62.50 | 0.001098343027506635 (30) |
| clean_v3_A2_v3_qd_with_sa | training / 23 / 450 | 2333334 | [9, 33, 7, 2286, 1, 0, 13, 19, 4498, 2925] | 5.41 | 3.12 | 0.0004207427885383689 (308) |
| clean_v3_A2_v3_flash_native | complete / - / - | 2291891 | - | N/A | N/A | N/A (0) |
| soccer_A3_soccer_moment_with_sa | complete / - / - | 2304521 | [1209, 1326, 1276, 674, 1238, 58, 917, 695, 936, 87] | 23.49 | 11.54 | 1.284673810977171e-05 (3022) |
| soccer_A3_soccer_qd_with_sa | complete / - / - | 2282058 | [1058, 910, 882, 995, 459, 608, 921, 988, 856, 739] | 17.66 | 14.42 | -0.00012277826890129976 (1546) |
| soccer_A3_soccer_flash_native | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_moment_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_qd_with_sa | queued / - / - | - | - | N/A | N/A | N/A (0) |
| clean_v3_A3_v3_flash_native | training / 1 / 750 | 2339297 | - | N/A | N/A | N/A (0) |
| soccer_C1_soccer_moment_with_sa | training / 22 / 300 | 2332680 | [662, 526, 738, 569, 509, 733, 858, 655, 742, 574] | 64.13 | 80.61 | -0.0006703409915752167 (586) |
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
| charades_cg_v2_C3_CG_qd_no_sa | training / 91 / 150 | 2323156 | [1, 1399, 105, 2, 0, 111, 110, 1, 3422, 1191] | 5.64 | 3.12 | 0.00021099979996601427 (1432) |
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
