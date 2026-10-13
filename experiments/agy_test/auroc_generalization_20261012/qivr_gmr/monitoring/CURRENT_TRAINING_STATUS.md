# 当前训练状态

采集时间：2026-10-13T23:09:56.677760+08:00。

队列：{'complete': 27, 'cancelled': 30, 'failed': 1}。

| 任务 | 状态 | 当前/结束轮次 | 最佳轮次 | 早停 |
|---|---|---:|---:|---|
| clean_v3_C1_v3_flash_native | complete | None/100 | 17 | — |
| clean_v3_C2_v3_flash_native | cancelled | 78/100 | 38 | — |
| publication_charades_cg_v2_C3_CG_moment_with_sa | complete | 40/40 | 14 | True |
| publication_clean_v3_A1_v3_qd_with_sa | complete | 100/100 | 98 | False |
| publication_clean_v3_A2_v3_flash_native | failed | 51/100 | 24 | True |

本次仅同步训练文本日志、逐 epoch 汇总、最终指标、选模/早停轨迹、校准配置和状态。没有新增上传原始数据归档、NPZ、逐样本预测或 bootstrap 数组。

此前提交和历史归档保留；本页面及 CURRENT_TRAINING_STATUS.json 是本次状态入口。
