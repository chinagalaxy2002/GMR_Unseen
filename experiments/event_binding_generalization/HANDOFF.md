# 当前交接状态

A/A1/B 已结束，记录状态为 **INCONCLUSIVE**。此页只记当前执行与观测文件位置。

本阶段执行了 12 个 SlowFast 动作 probe、15 个 H/P/C/J/T 小模块。实验记录共有 7,345 条 seen/pseudo 行。原模型新增训练为 0 轮。

观测值：pseudo 等权族 AUROC 为 H .5975、P .6077、C .5755、J .6085、T .6193；raw R1@0.5 为原模型 .2936、J .1766。双流特征的时间戳与提取记录没有找到，sit primitive 匹配负例覆盖为 1 个视频。

来源检查读取过含 U 行的 val 文件；该文件只用于来源成员核对。U 行没有进入拟合、前向、选点或指标，详见[协议事件记录](audit/PROTOCOL_INCIDENT.json)。

主要交付：

- [现象报告](report/REPORT.md)
- [阶段状态](report/DECISION.md)
- [代码与结果索引](ARTIFACT_INDEX.md)
- [复核与复现说明](REPRODUCE.md)
- [执行状态](STATUS.json)
- 发布快照文件清单见 `publication/UPLOAD_MANIFEST.json`

较早的方案、文献笔记与完整方法设想仍保留在本目录。它们描述的是研究方案和历史记录，不属于本阶段新增结果。
