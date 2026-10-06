# 数据集、原始视频与已提取特征

Google Drive：[GMR_Unseen_Dataset_Features_20261006](https://drive.google.com/drive/folders/17wf_qE7wdGpplPxaHuYA-JGdnb_1CHHs)。包在用户指定父目录 `1ERbWP2hl4DYl6n3j3JrvzcbGuDfW80Rm` 下。16 个归档，共约 17.89 GB（16.66 GiB）。

## 包含内容

- Charades-STA 派生的 semantic_existence_v1/v2 全部发布标注与五划分 train/val/test、matched pairs、来源及计数。
- 这两个发布版实际使用的视频并集：6,142 个原始 Charades 480p MP4，五个独立 tar 分卷，保持原始视频字节。
- 每个视频对应的 CLIP、SlowFast 特征均齐全，各 6,142 份；服务器符号链接已保存为实际数据。
- 原文本特征、投影对齐查询/多模态特征、三骨干/HQ 导出、当前及历史验证器特征缓存、Seen val/test 候选。
- README、恢复脚本、逐文件和逐归档 SHA-256/MD5、视频索引、NPZ 字段说明、上传核验回执。

这是本项目使用的视频子集，不是完整 Charades 全量下载。验证器权重位于本 GitHub 分支；数据包还提供 15 个 baseline 最佳检查点、Flash 配置及 baseline 从头训练所需的 v2 文本 token 特征和 Seen validation 视图。数据来源条款仍适用。访问 Drive 需要相应文件夹权限。

## 下载与恢复

配置好自己的 rclone `gdrive:` 后：

```bash
mkdir -p gmr_assets
rclone copy gdrive:GMR_Unseen_Dataset_Features_20261006 ./gmr_assets \
  --drive-root-folder-id 1ERbWP2hl4DYl6n3j3JrvzcbGuDfW80Rm \
  --transfers 3 --checkers 6 --checksum --progress
cd gmr_assets
sha256sum -c SHA256SUMS
python restore_bundle.py --repo-root /path/to/GMR_Unseen --verify-files
```

仓库应使用分支 `experiments/independent-candidate-verifier-20261006`。恢复脚本核对归档，按仓库相对路径解包并建立特征别名；遇到内容不同的已有文件会停止，因此建议干净 checkout。完整教程在 Drive 包内 README.md；每类 NPZ 的键/维度见 FEATURE_SCHEMA.md/json。

数据训练和选模仍只用 Seen；不能因下载包中含 test/U 标签而将它们用于拟合、校准或选模。

## Baseline 训练复现

`09_baseline_training_text_and_views.tar.gz` 与 `11_baseline_checkpoints_and_configs.tar.gz` 已纳入恢复脚本和哈希清单。恢复后运行 `python reproduction/check_assets.py --raw-videos`，逐查询检查 train、Seen val、test 的文本特征及对应视频特征。三个 baseline 的 100 epoch 从头训练入口为 `reproduction/run_baselines.py --stage train-and-infer`；具体环境与命令见根 README。

## 上传核验结果

2026-10-06 上传完成。16 个归档及配套元数据已在远端逐项核对大小与 MD5；`rclone check` 返回 35 个匹配文件、0 个差异。根目录 34 个文件的核验信息、Drive 文件 ID 与字节数见 [上传回执](UPLOAD_RECEIPT_20261006.json)，同名原回执也保存在 Drive 文件夹中。Baseline train / Seen validation / test 的逐查询文本和视频特征路径已检查，无缺失；本次未重新执行模型训练。
