# DAO 清洁版根因诊断

完成于 2026-10-06。入口：[ROOT_CAUSE_REPORT.md](ROOT_CAUSE_REPORT.md)。只写本目录，没有训练新模型或覆盖旧产物。

- `diagnose.py`：15 份特征复查、五 checkpoint 冻结分解、训练/验证泛化落差、A1 统一编码和投影对照。
- `paired_controls.py`：保持同视频配对结构的置换、独立视频聚类 bootstrap、prior 主导程度。
- `reference_centering.py`：固定无标签训练视频参考的校准诊断。
- `feature_audit.json`、`frozen_diagnosis.json`、`fit_diagnosis.json`：对应全量结果。
- `A1_clip_diagnosis.json`、`paired_controls.json`、`A1_reference_centering_diagnosis.json`：投影、视觉对应和校准证据。
- `*_scores.npz`：对齐 qid 的逐查询诊断分数；非正式新方法预测。
- `artifact_manifest.json`：审计结束时的输入及产物 SHA256 快照。

当前结论：旧标签通道与 cxw 错误已修复；清洁 DAO 尚未改善 Unseen AUROC。正确投影 CLIP 有部分视觉对应信号，现有 prior 和联合训练没有保住这部分信号。先做输入对齐与无自由 prior 的最小重训对照。
