# DDV 独立审计产物

推荐从 [DDV_AUDIT_REPORT.md](DDV_AUDIT_REPORT.md) 阅读。源实验为 [DDV](../decomposed_directional_verifier/README.md)，发布概览见 [实验整理](../../../docs/reports/ddv_experiment_20261006.md)。

| 文件 | 内容 |
|---|---|
| `audit_metrics.json` | 五个检查点重放、15 份缓存核对、公平比较、正确 G-mIoU |
| `bootstrap.json` | 2,000 次共享视频 Bootstrap、逐划分及类别区间 |
| `source_checks.json` | 输入列来源、源反事实配对比例、90 行特征抽查、无梯度参数 |
| `input_manifest.json` | 原本地输入 SHA-256；其中大量输入文件不在 GitHub 发布包 |
| `audit_ddv.py` | 原模型重放、Seen-only detector-only 控制训练及指标复算 |
| `audit_sources.py` | 特征来源与活动参数核查 |

原审计已完成，本次发布没有重新训练或运行模型测试。模型重放误差约 1.19e-7；原输入文件 91 份复查未变。Bootstrapping 条件于固定单种子模型，不覆盖训练随机性。

本地还有 `{split}/detector_only_control.pt`、`{split}/audit_predictions.npz`、`bootstrap_draws.npz` 和日志，按项目既有发布口径不随 Git 仓库上传。源码中的复验命令需要先恢复这些实验输入；依赖见 [DDV README](../decomposed_directional_verifier/README.md)。

源码的绝对 Python 环境路径仅描述原运行环境，移植时使用自己的 Python。两个脚本只写各自的审计目录；重跑会覆盖其中的控制和指标文件。
