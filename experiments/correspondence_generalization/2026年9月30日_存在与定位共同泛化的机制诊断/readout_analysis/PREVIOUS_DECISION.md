# 三族诊断收尾决策

更新：2026-10-01T00:45:36.130365+08:00。状态：**仅评测的收尾已完成；不进入复杂干预训练。**

## 授权与执行范围

用户先停止第二阶段训练，随后批准“sit保存模型评测→三族诊断汇总→更新DECISION；新增训练为零”。本次只执行这一收尾范围。旧训练/补充队列保持stopped_by_user，没有恢复训练、重新选择checkpoint或启动候选。原关闭决策保存在plan/pre_evaluation_closeout/DECISION.md。

Throw和open_close训练完成100轮；sit保留77轮训练账本，原seen-only best编号11（第12轮），latest编号76（第77轮）。本次对sit补充best/latest评测与诊断，不将其标记为100轮训练完成。跨族均值描述已保存模型，不能解释为三个族统一完成100轮后的证据。

## 主要结果

| 族 | 伪未见AUROC | raw R1@.5 | 官方gated R1@.5 | canonical文本PairAcc（共同视频95%区间） |
|---|---:|---:|---:|---|
| throw | .5731 | 26.72% | 26.94% | .2568 [.0232, .5335] |
| open_close | .5346 | 26.32% | 26.64% | .5470 [.5046, .5864] |
| sit | .6540 | 35.04% | 35.36% | .5682 [.4586, .6692] |
| 等权族均值 | .5873 | 29.36% | 29.65% | .4573 [.3706, .5578] |

1000次bootstrap、seed3407，以共同原视频权重处理跨族重用；同句配对使用两个视频端点权重的乘积。AUROC与raw绝对97.5%区间、gated及FRR/RR等95%区间、覆盖和视频交集见[完整报告](report/DIAGNOSTIC_REPORT.md)。这些是baseline绝对表现，不是候选对baseline的paired增益。没有候选，因此共同主要终点显著改善与seen/拒绝不劣门槛没有进行方法比较，不能宣称通过或失败。

## 证据判断

**视觉条件排序：跨族支持仍不充分。** Open_close的同句控制支持该覆盖内有限视觉增量，throw和sit的区间跨.5；等权族均值也跨.5。Throw仅10个同句组、37对，open_close158组/7367对，sit45组/359对；组合对数不是独立样本数。不能因为open_close覆盖大或结果较好就用按对数加权替代冻结的等权族汇总。也不能由未获得跨族支持推出输入不可辨识或模型不使用视频。

**稳定共享层损失冲突：未达到预登记线索。** 每checkpoint按D3规则筛查16个S+ batch，eval模式、autograd.grad、参数更新0。Throw baseline只有decoder满足单点负cosine规则，且best/latest权重相同；open_close best只有interaction满足，latest无块满足；sit best/latest均无块满足。Throw adapter的单块负值在两个checkpoint间换块。原交集范数与补充完整块范数的符号规则一致，没有“至少两个共享块、跨不同checkpoint、跨至少两个族”的稳定线索。Saliency权重0，缺失有效saliency梯度不代表一致。此结论限于当前16batch局部几何，不是对全部训练历史或因果冲突的完整否定。

**定位错误是主要hard失败组成，但不是存在退化的已证实原因。** 三族raw错误/hard失败比例分别95.77%、95.67%、95.75%。Raw正确却被诊断硬拒的比例为15/124、63/497、18/219；throw/open_close值得描述，但不能把它们称为官方soft gate完全否决。三个baseline的伪未见RR仅.1321/.1683/.2308，拒绝泛化仍弱。失败占比本身不说明修复定位就会改善AUROC。

**相对/绝对排序的差异只作描述。** 同视频PairAcc分别.8154/.5904/.6943，跨视频为.5728/.5346/.6539。比较构成和覆盖不同，throw同视频只有65对；不凭这些差异认定视频偏置或直接启动绝对支持模块。

**Gate与后处理已分清。** 官方soft gate对每条query乘同一分数标量；gated保存窗单独经过时间裁剪/取整。给raw应用同样后处理后，三族baseline和throw adapter的全部排序坐标一致。Raw/gated命中变化由此解释，不能称为gate重排或否决。冻结raw主要指标仍使用原保存raw窗，对齐结果仅为辅助。

**Sit早期best优于保存latest的描述不能变成泛化因果结论。** Best→latest伪未见AUROC .6540→.6209，raw .3504→.3264，gated .3536→.3216。Best仍按原seen-only规则固定，未据此在pseudo上选epoch；没有完整轨迹、100轮完成或种子稳定性结论。

## 决定与后续边界

本次停止复杂方法路线，不启动PCGrad、loss重权或绝对支持模块，也不进入正式U确认。原因是跨族视觉条件排序支持不足，稳定梯度冲突线索未出现，相对/绝对差异尚不足以确定具体可修复机制；不能用新增训练替代诊断门槛。

如果以后另开研究，优先限定为固定模型的时序对应与存在读出关系分析，例如分析已有S+定位正确/错误样本的存在分数与时序支持关系；该方向目前只是待定义任务，不是已验证机制或新增算法，不在本次授权内自动执行。完整控制预算或具体方法需由新范围明确，不恢复旧75组、教师/window、多seed或第一阶段六组。

## 验证与保存

本次12项评测/诊断/汇总任务全部returncode=0，新增训练轮数与参数更新均为0；56个受保护原文件hash全部未变（原checkpoint、训练状态、账本、视图、旧诊断及停止队列）。详见[完整报告](report/DIAGNOSTIC_REPORT.md)、[完整性检查](report/CLOSEOUT_INTEGRITY.json)、closeout_state.json与plan/CLOSEOUT_FREEZE.json。旧停止记录保留，新产物位于diagnostics/sit/baseline/，sit预测在evaluation_bundle/；不伪造原训练result.json。
