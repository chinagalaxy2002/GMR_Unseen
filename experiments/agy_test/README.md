# AGY 实验代码与审计索引

当前入口：**[Aligned Calibration Verifier (AC-Verifier)](aligned_calibration_verifier/README.md)**。

## 当前可支持的结论

五划分、单种子探索结果中，AC 相对 HQ 缓存完整 logit 基线将 Mean Unseen AUROC 从 0.5027 提高到 0.5188，Seen−Unseen Gap 从 0.2484 降到 0.2373，Seen AUROC 同时从 0.7511 提高到 0.7561。独立视频聚类 bootstrap 支持该宏平均改善；收益主要集中于 C1，未见动作普遍改善尚未确认。当前 AC 只验证 QD-DETR-GMR，新增编码器为 CLIP ViT-B/32，无已验证的多 backbone 迁移结果。

结论及归因更正以 [AC_AUDIT_REPORT.md](ac_audit_20261006/AC_AUDIT_REPORT.md) 为准，原 [EXPERIMENT_REPORT.md](aligned_calibration_verifier/EXPERIMENT_REPORT.md) 保留作历史记录。

## 目录与状态

| 目录 | 内容 / 状态 |
| --- | --- |
| `aligned_calibration_verifier/` | 当前 P0/P1 代码、五划分指标与复现说明 |
| `ac_audit_20261006/` | 当前方法独立审计、冻结干预、正确视频置换与 bootstrap |
| `dao_root_cause_20261005/` | 清洁 DAO 的表示对齐、语言先验与跨视频信号诊断 |
| `dao_audit_20261005/` | 原 DAO 标签泄漏审计；原 0.6883 Unseen AUROC 无效 |
| `decomposed_action_object_verifier/` | 历史 DAO 代码与原/清洁指标；原版不能作成功方法使用 |
| `audit_20261005/` | 早期适配器审计与完整 logit/源模型重放；提供 AC 的 `prepared_auc` 依赖 |
| `dual_pool_adapter/` | 历史双池适配与新鲜源推理对照 |
| `e2e_training/`, `code/`, `report/` | 历史探索源码与指标；结论须结合后续审计阅读 |

`RESEARCH_REPORT_AGY_TEST.md` 为历史研究报告，未经本次发布重新评测。旧报告中的强增益、全视觉归因或“彻底排除捷径”等表述不作为当前结论。

## 发布范围与复现限制

只发布源码、Markdown 与小型指标 JSON。忽略 `.npz/.pt/.ckpt/.pth`、缓存、日志、逐查询预测和原视频。训练产物仍在原本地目录；GitHub 不是包含全部运行输入的完整制品包。`PUBLICATION_MANIFEST.json` 记录发布前来源文件的 SHA256；各审计 `artifact_manifest.json` 是原本地产物快照，包含未发布的大文件，不能直接作为 GitHub 版本完整性清单。

AC 复现见 [专用 README](aligned_calibration_verifier/README.md)。历史脚本部分依赖 `experiments/gmr_unseen_existence_20261005/cross_confirmation/` 的额外缓存/数据视图；其 `code/common.py` 作为直接源码依赖同时发布，不代表该独立实验全部产物已发布。未在本次上传过程中重新训练或运行模型测试。
