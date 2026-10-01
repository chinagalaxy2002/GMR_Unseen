# A/A1/B 实验目录与结果索引

本阶段已结束，结论 **INCONCLUSIVE**，停止当前实现。没有启动 R、完整模型、共享 map 下一阶段、多 seed 或原 sit 续训。训练并发为每张 GPU 最多两个任务、两张最多四个。

等权 pseudo AUROC：H .5975、P .6077、C .5755、J .6085、T .6193；J 对 P 的 paired 区间跨零。固定实际文本后 J PairAcc .4538，区间跨 .5；固定候选 map 重排的 raw R1@.5 从原 29.36% 降至 J 17.66%。双流时间来源未核实，sit 的 primitive 匹配负例仅一个视频。来源检查还发生了真实 U 发布文件读取边界偏差；U 行没有进入拟合、前向、选点或指标，偏差不能隐去。

## 阅读入口

- [最终报告](report/REPORT.md)：完整结果、覆盖、不确定性和限制。
- [决策](report/DECISION.md)与[机器可读决策](report/DECISION.json)。
- [执行状态](STATUS.json)、[交接](HANDOFF.md)、[复现说明](REPRODUCE.md)。
- [读取边界偏差](audit/PROTOCOL_INCIDENT.json)：保留原失败和修订，不能声称完全未接触 U。

## 文件布局

| 路径 | 内容 |
|---|---|
| `code/` | 隔离的动作 probe、输入审计、H/P/C/J/T、并发调度、评估、paired bootstrap 和交付检查；发布脚本不参与实验 |
| `EXECUTION_FREEZE.json` | 初始范围、监督、预算、选择规则和原资产 hash，保留原件 |
| `EVENT_CODE_FREEZE.json` | 模块参数量、源码 hash、跨度规则修订与并发上限 |
| `PRIMITIVE_CONTROL_FREEZE.json` | S_train 固定支持/匹配规则、seen 阈值、选中 checkpoint |
| `*_CODE_FREEZE.json` | 推理、统计与报告实现的阶段性源码记录；不是额外模型变体 |
| `audit/` | BPE/span 逐行审计、文本缓存来源、双流 shape/time、原标签蕴含、actual-text 控制、覆盖和协议偏差 |
| `runs/minimal_validation/` | 12 个动作 probe、15 个事件 head 的权重与账本、预测、map、训练/失败日志和运行记录 |
| `report/` | 报告、决策、逐族/等权 paired 统计、共同视频 bootstrap traces、定位修复/破坏、完整性检查 |
| `research/` | 已有文献核验和工程审计；本轮没有重复开展文献研究 |
| `publication/` | GitHub 上传文件清单、hash、发布状态与回执；独立 Git 工作区位于忽略的 `.local/` |
| `cache/` | 本地重建缓存、临时目录和依赖；不上传 |
| `research/.local/` | 本地论文、第三方源码和历史上传工具；不上传 |

## 关键结果文件

- [逐族/等权 paired 统计](report/PAIRED_STATISTICS.json)：1000 次 seed3407，共同原视频 bootstrap，族等权。覆盖不足时报告有效 bootstrap 次数，不能把组合对数当独立样本量。
- [全部逐行预测](runs/minimal_validation/PREDICTIONS.jsonl)：7345 条 seen/pseudo 记录；各族各 split 文件保留相同信息，便于单组复核。
- [原候选定位修复/破坏](report/LOCALIZATION_REPAIRS_DAMAGE.json)：全部原正例分母，GT 只用于评价。
- [训练账本](runs/minimal_validation/TRAINING_LEDGER.json)：12 个动作 probe 各20轮上限、15 个小 head 各8轮；原完整模型新增训练轮数为0。
- [原资产终检](report/INTEGRITY.json)：18358 条受保护路径 hash 未变；预测/聚合/候选读取独立核验。

权重命名为 `{family}_action_{control}.pt` 和 `{family}_{H|P|C|J|T}.pt`。每个 `{family}_{module}_{split}_maps.npz` 通过 `offset` 切分逐行局部 map；`{family}_{split}_evaluation.npz` 保存同顺序的存在、定位与实际文本控制数组。对应 JSONL 的行顺序是数组唯一索引，不跨文件按候选位置猜测匹配。

## 上传边界

上传本目录内的方案、代码、审计和实验结果，包括小模块权重、NPZ 和失败日志。保留原相对路径，不搬动已有实验产物，以免破坏冻结记录、源码读取路径和报告链接。

不上传 `cache/`、任何 `.local/`、Python bytecode、凭据或原始 backbone/原 GMR checkpoint。原数据、特征、其他实验、原停止队列和其他工作区未提交改动不纳入此次提交。实验输出中的原机器绝对路径为来源标识，外部资产不随目录复制。
