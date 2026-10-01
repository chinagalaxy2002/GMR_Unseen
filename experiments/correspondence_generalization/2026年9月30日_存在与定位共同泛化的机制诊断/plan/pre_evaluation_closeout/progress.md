# 第二阶段结束记录

更新时间：2026-10-01T00:29:05.524257+08:00。**用户明确要求停止训练并结束本实验，取代此前继续执行授权。**

- 调度器、sit训练worker、补充等待流程均已终止；无GPU计算进程，阶段tmux已退出。未重启训练。
- open_close已完成100轮、seen-only选择及pseudo评测、D3/D1同句控制/D2 best/latest和辅助敏感性、latest D3、gate后处理审计；best epoch编号49。
- sit训练账本77轮，latest checkpoint编号76；最后完成seen评测76轮。best checkpoint编号11（0-based，即第12轮），seen MR-full-mAP=25.25。停在训练/评测流程中，未生成result.json或pseudo预测；不标记为100轮完成或技术失败。
- 两族best/latest checkpoint均通过CPU可读性检查，原checkpoint与日志保留。
- throw已有模型和完成诊断保留；补充敏感性、latest D3、后处理审计、完整块梯度统计已完成，无参数更新。
- 三族汇总未完成，条件干预与正式确认未启动；随本次结束取消，不自行续跑或补训练。

终止信号见STOP_RECORD.json；停止前快照见user_stop_snapshot/；完整状态见HANDOFF_STATUS.json；关闭决策见[DECISION.md](../DECISION.md)。数值指标与机制仍以已完成证据为限，用户结束不等于证明损失冲突成立或否定。
