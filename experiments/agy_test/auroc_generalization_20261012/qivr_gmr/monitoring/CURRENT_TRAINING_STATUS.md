# 当前训练状态

采集时间：2026-10-13T17:26:46.360996+08:00。

队列：{'complete': 21, 'paused': 2, 'queued': 11, 'running': 4, 'cancelled': 20}。

| 任务 | 状态 | 当前/结束轮次 | 最佳轮次 | 早停 |
|---|---|---:|---:|---|
| soccer_A1_soccer_flash_native | paused | 59/100 | — | — |
| clean_v3_A3_v3_qd_with_sa | running | 48/100 | — | — |
| clean_v3_A3_v3_flash_native | running | 91/100 | — | — |
| soccer_C1_soccer_moment_with_sa | paused | 22/100 | — | — |
| clean_v3_C2_v3_moment_with_sa | running | 12/100 | — | — |
| publication_charades_cg_v2_C3_CG_moment_with_sa | complete | 40/40 | 14 | True |
| publication_clean_v3_A1_v3_qd_with_sa | complete | 100/100 | 98 | False |
| publication_clean_v3_A2_v3_flash_native | running | 49/100 | — | — |

本次仅同步训练文本日志、逐 epoch 汇总、最终指标、选模/早停轨迹、校准配置和状态。没有新增上传原始数据归档、NPZ、逐样本预测或 bootstrap 数组。

此前提交和历史归档保留；本页面及 CURRENT_TRAINING_STATUS.json 是本次状态入口。
