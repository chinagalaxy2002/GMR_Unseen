# A/A1/B 文件与结果索引

阶段状态：**INCONCLUSIVE**。本目录记录 seed 3407、throw/open_close/sit 三族的 A/A1/B 运行。

## 入口

- [实验现象记录](report/REPORT.md)
- [阶段状态](report/DECISION.md) · [执行状态 JSON](STATUS.json)
- [复核与复现说明](REPRODUCE.md)
- [协议事件记录](audit/PROTOCOL_INCIDENT.json)

## 目录内容

| 路径 | 文件内容 |
|---|---|
| `code/` | 动作 probe、输入审计、H/P/C/J/T、小模块评估、统计和 GitHub 发布脚本 |
| `EXECUTION_FREEZE.json`、`EVENT_CODE_FREEZE.json` | 实验设置、来源 hash、模块参数和预算记录 |
| `audit/` | token/span、缓存、视频特征长度、primitive 与文本控制覆盖记录 |
| `runs/minimal_validation/` | probe/head 权重、逐行预测、局部 map、日志和训练账本 |
| `report/` | 指标表、paired 区间、bootstrap traces、定位计数及状态页 |
| `research/` | 文献与工程审计文档 |
| `publication/` | 本次快照中的文件清单、环境记录和发布计划 |

`cache/` 包含约 53.6 GB 本地缓存与临时依赖，没有包含在 GitHub 快照中。`research/.local/` 和 `publication/.local/` 是本地文件，不在上传快照中。

## 核心文件

- [逐族 paired 统计](report/PAIRED_STATISTICS.json)：1000 次共同原视频 bootstrap。
- [完整逐行预测](runs/minimal_validation/PREDICTIONS.jsonl)：7,345 行，含 seen 和 pseudo。
- [候选定位计数](report/LOCALIZATION_REPAIRS_DAMAGE.json)。
- [训练账本](runs/minimal_validation/TRAINING_LEDGER.json)：12 个动作 probe、15 个小模块。
- [完整性记录](report/INTEGRITY.json)：18358 条原资产 hash 记录。
- GitHub commit 与文件核验记录由发布完成消息提供；快照清单见 `publication/UPLOAD_MANIFEST.json`。

小模块 map 文件用 offsets 对应逐行预测。详细数组定义见 [复现说明](REPRODUCE.md)。
