# 第二阶段关闭报告

结束时间：2026-10-01T00:32:26.838520+08:00。用户主动结束；全部活动训练、调度和等待流程已停止。

Sit保存77轮训练账本，best epoch编号11、latest编号76；最后完成seen评测76轮，pseudo评测尚未执行。Open_close完成100轮及训练侧评测/诊断，best编号49。所有编号为0-based。Checkpoint均可读取；无新干预或正式确认。

| 已完成baseline族 | pseudo AUROC | raw R1@.5 | 官方gated R1@.5 | FRR | RR | canonical文本PairAcc及95%区间 |
|---|---:|---:|---:|---:|---:|---|
| throw | 0.5731 | 0.2672 | 0.2694 | 0.0884 | 0.1321 | 0.2568 [0.0294, 0.5233] |
| open_close | 0.5346 | 0.2632 | 0.2664 | 0.1457 | 0.1683 | 0.5470 [0.5067, 0.5883] |

以上为各族baseline，不是候选增益；不计算缺少sit的三族均值，也不宣称显著共同改善。各原视频端点区间不是跨族联合区间。完整关闭理由、覆盖限制、梯度判断和gate后处理修正见[DECISION.md](../DECISION.md)。

Throw补充的敏感性、latest D3、gate后处理及完整块梯度统计已保存。Open_close原D3/D1/D2及敏感性、latest D3、gate后处理审计已保存；完整块梯度补充未运行。Sit全部机制诊断未运行。三族汇总代码和报告模板仅为已备好代码，未产出的结果不算已完成。

原第一阶段六组和正式数据/特征未重跑或覆盖。结束前状态保存在plan/user_stop_snapshot/，当前queue_state.json、followup_state.json及sit status.json均标记stopped_by_user。
