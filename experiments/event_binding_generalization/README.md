# Event Binding Generalization

本目录保存事件绑定方向 A/A1/B 最小验证的代码、执行记录和结果。

阶段状态：**INCONCLUSIVE**。实验执行已结束。按族观测到 pseudo 等权族 AUROC：H .5975、P .6077、C .5755、J .6085、T .6193；raw R1@0.5：原模型 .2936、J .1766。双流时间戳及对应特征缓存的提取记录未找到。一次来源检查读取了含 U 行的 val 文件；U 行未进入拟合、推理或指标计算，详情见协议事件记录。

- [实验现象记录](report/REPORT.md)：动作 probe、输入覆盖、primitive 控制、AUROC、定位和配对区间。
- [文件索引](ARTIFACT_INDEX.md) · [复核与复现](REPRODUCE.md) · [运行状态](STATUS.json)。
- GitHub 快照文件清单见 `publication/UPLOAD_MANIFEST.json`。

结果使用 seed 3407 的原训练侧 pseudo 与 seen 视图。阶段内完成 12 个动作 probe 和 15 个小模块拟合；原骨干与原完整模型新增训练为 0 轮。输入缓存、模型权重、代码 hash 和覆盖记录按相对文件路径保存。

本目录中的 [完整研究方案](EXPERIMENT_PLAN.md)、[候选方法规格](METHOD_SPEC.md)和[交接历史](HANDOFF.md)包含方案内容。当前实验观测与状态以本页所链接的报告和状态记录为准。
