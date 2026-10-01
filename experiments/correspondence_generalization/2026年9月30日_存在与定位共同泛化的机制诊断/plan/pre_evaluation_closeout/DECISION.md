# 第二阶段关闭决策

时间：2026-10-01T00:31:27.617968+08:00。状态：**按用户最新指令结束（ended_by_user）**。

## 决定

用户明确要求“停止训练吧。这个实验可以结束了。sit最优epoch在11.” 已停止sit训练、主调度器与补充等待流程，结束本轮。此前继续执行授权不再适用。不进入条件干预，不启动PCGrad、loss重权、绝对支持模块或正式U确认；不恢复旧队列、第一阶段六组或多seed。

## 最终执行状态

| 族 | 训练 | seen-only best epoch编号 | pseudo评测与诊断 |
|---|---|---:|---|
| throw | 复用已完成模型，未重训 | baseline 99；adapter 13 | 已完成原诊断及本次辅助审计 |
| open_close | 已完成100轮 | 49 | pseudo评测、D3/D1控制/D2及辅助审计已完成 |
| sit | 用户终止；账本77轮，最后完成seen评测76轮 | **11** | 尚未执行pseudo评测及机制诊断 |

表中checkpoint epoch编号为0-based。sit best编号11对应第12轮，seen MR-full-mAP=25.25；latest编号76可读取。两个新增族的best/latest checkpoint、训练日志和全部已完成产物保留，原模型不迁移不覆盖。sit没有result.json，不把主动结束记为训练完成或异常失败。

## 已完成证据与解释边界

- Throw baseline伪未见AUROC=.5731、raw R1@.5=.2672、官方gated=.2694；open_close为.5346/.2632/.2664。这是各留族baseline表现，不是方法增益。
- Throw同句canonical文本控制PairAcc=.2568，95%原视频端点区间[.0294,.5233]，仅37对；open_close=.5470，区间[.5067,.5883]，7367相关对、158同句组。open_close支持该覆盖内的有限视觉条件排序增量，throw仍不确定；不能从两个族推出三族共同证据，不能将配对组合视作独立重复试验。
- 两个已完成baseline的hard失败中raw定位错误占比约95.8%和95.7%。诊断硬拒绝不是官方soft gate否决。
- 源码与后处理对齐审计显示：gated保存时间窗经过clip_ts/round_multiple，raw保存窗未经过这一步。不能把其命中差异直接写成gate改top1；冻结raw主指标未调整。
- 已完成局部梯度证据未满足“跨best/latest、至少两个语义族、至少两个共享块”的稳定冲突线索。Throw baseline best/latest权重相同；open_close best仅interaction满足局部规则、latest无块满足。sit缺失，因此机制判断保持受限，不宣称损失冲突成立或被完整否定。
- 辅助遮蔽/乱序分析只报告固定模型分数与预测变化，未按扰动后的原标签报告反事实准确率；无参数更新。

## 未完成及取消项

Sit剩余训练、pseudo评测与D3/D1/D2、三族共同视频bootstrap汇总、候选干预及正式确认随用户结束取消。没有候选联合主要终点比较，不能宣称共同改善门槛通过，也不能把“未检验”写作“已证明失败”。冻结数值界限保持不变。

关闭依据首先是用户明确结束，不为这一决定构造额外机制理由。若未来用户另行发起研究，应单独定义范围；当前旧恢复prompt与历史授权不再作为执行入口。

## 保存位置

关闭报告：[FINAL_STATUS.md](report/FINAL_STATUS.md)。停止信号和核验：[STOP_RECORD.json](plan/STOP_RECORD.json)、[STOP_CHECKPOINT_CHECK.json](plan/STOP_CHECKPOINT_CHECK.json)、[HANDOFF_STATUS.json](plan/HANDOFF_STATUS.json)。停止前队列与交接保存在plan/user_stop_snapshot/；完成诊断继续保存在diagnostics/，日志在logs/，模型在runs/。
