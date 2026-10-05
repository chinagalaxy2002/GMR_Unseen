# Aligned Calibration Verifier (AC-Verifier)

当前实现基于冻结 **QD-DETR-GMR** 输出与 **CLIP ViT-B/32** 投影。仅使用 Seen 数据训练，Seen validation 选择 checkpoint 与阈值。当前单种子 `3407`，五划分 `A1/A2_alt/A3/C1/C2_alt`。

## 结果与解释

| 模型 | Mean Seen AUROC | Mean Unseen AUROC | Gap | Mean PairAcc |
| --- | ---: | ---: | ---: | ---: |
| HQ 完整 logit | 0.7511 | 0.5027 | 0.2484 | 0.5181 |
| 独立 P0 Detector Adapter | 0.7535 | 0.5078 | 0.2456 | 0.5261 |
| P1 AC-Verifier | 0.7561 | 0.5188 | 0.2373 | 0.5331 |

[独立审计](../ac_audit_20261006/AC_AUDIT_REPORT.md)复现了宏平均结果，支持 +1.61 pp Unseen AUROC、1.11 pp Gap 缩小。C1 是主要收益来源，动作三组改善区间仍跨零。当前结果不能证明新语义、多种子、多 backbone 或完整 GMR 门控定位均改善。原报告中的 `Baseline Fresh` 指 HQ 缓存完整 logit，本轮没有重新执行整个 backbone。

当前 P1 只使用整句候选/全局相似度。短语向量用于诊断，SlowFast 不参与 P1。参考定义为 `normalize(mean(normalize(mean_frames(v))))`，由唯一训练视频构建，再减去 `cos(query, reference)`；这是固定校准定义，未经证明为无偏边际期望。

## 输入资源

运行前准备下列本地资源，GitHub 不包含它们：

1. `data/release/semantic_existence_v2/{split}/{train,val,test}.jsonl` 与 `matched_u_pairs.jsonl`（仓库发布数据）。
2. HQ 检测器缓存：`experiments/agy_test/cache/hq/{split}/{train,val,test}.npz`。按 qid 与发布数据对齐；数组字段为 `qids/vids/hs/fg/spans/orig_logits/partitions/durations/labels`。
3. CLIP 视频帧特征：`{video_id}.npz`，字段 `features` 为 T×512，与文本投影同一 CLIP 坐标系。
4. UniVTG-NA `run_on_video/clip` 的 `model.py`、`simple_tokenizer.py` 及 BPE 词表，以及原实验兼容的 TorchScript `ViT-B-32.pt`。该实现的 `encode_text` 返回含 `last_hidden_state` 的字典，不能直接替换成返回最终 embedding 的任意 CLIP 实现。

HQ schema：`hs` N×K×256，`fg` N×K，`spans` N×K×2 为归一化 **center,width**，`orig_logits/labels/partitions/durations/qids/vids` 按同一 N 顺序。候选来自最大 foreground slot，转 start/end 后按归一化时间裁剪帧。`h_pool` 是 slot max/mean 拼接的 512 维向量。请保持完整 logit 精度与视频隔离。

环境需 PyTorch、NumPy、SciPy、scikit-learn，CLIP tokenizer 需 `regex`、`ftfy` 等其源码依赖。历史运行使用本机 `univtg` 环境；本次未生成锁定环境，也未在全新环境复跑。

## 路径配置与运行

发布版为外部 CLIP 资源增加环境变量覆盖，未改变默认路径或数学计算。请设置真实路径：

```bash
export AC_VIDEO_CLIP_DIR=/path/to/charades/vid_clip
export AC_CLIP_CODE=/path/to/UniVTG-NA/run_on_video
export AC_CLIP_WEIGHTS=/path/to/ViT-B-32.pt
python experiments/agy_test/aligned_calibration_verifier/extract_aligned_features.py
python experiments/agy_test/aligned_calibration_verifier/train_and_eval.py
```

运行位置为仓库根目录。提取将生成 15 份 `aligned_features/{split}/{train,val,test}.npz`；训练将写入 `runs/{split}/verifier_checkpoint.pt`、`metrics.json` 和 `benchmark_summary.json`。运行会覆盖同名产物，请在自己的工作副本复现。

训练默认 30 次 full-batch AdamW 更新，lr 0.001；P0/P1 独立初始化，非完全匹配的 detector 初始化。脚本当前只保存 P1 checkpoint，不保存 P0 checkpoint 和逐查询预测。后续配对种子实验应补齐这些产物。

独立审计还需上述 HQ/视频缓存、生成的 aligned features 和 P1 checkpoints：

```bash
PYTHONDONTWRITEBYTECODE=1 python experiments/agy_test/ac_audit_20261006/audit_ac.py
```

审计会重放 P0，并写入自己的目录；`AC_VIDEO_CLIP_DIR` 同时供审计读取。源码中的原置换控制打乱已校准相似度，不能当作严格固定 query 的视频置换；后者由审计实现。原 `Text-Only` 名称实际指关闭新增相似度、保留 detector 视觉输入，审计报告给出了更正。

## 多 backbone 迁移

本仓库已有 Moment-DETR、QD-DETR、FlashVTG 基线，但 **本 AC 版本仅实现/评测 QD-DETR 缓存路径与 256 维 slot 接口**。方法可通过新的缓存导出器、slot 输入维度适配、foreground 定义和边界坐标统一迁移；目前没有即插即用的 backbone 参数或已验证的迁移结果。更换 CLIP backbone 也需要重新生成配套投影/帧特征和参考，不应沿用旧缓存。

## 产物索引

- [model.py](model.py)、[extract_aligned_features.py](extract_aligned_features.py)、[train_and_eval.py](train_and_eval.py)：当前实现。
- [benchmark_summary.json](benchmark_summary.json)、`runs/{split}/metrics.json`：原运行汇总。
- [EXPERIMENT_REPORT.md](EXPERIMENT_REPORT.md)：原实验报告，需结合审计更正阅读。
- [AC_AUDIT_REPORT.md](../ac_audit_20261006/AC_AUDIT_REPORT.md)、[bootstrap.json](../ac_audit_20261006/bootstrap.json)：独立复验与统计范围。

GitHub 只发布代码、报告与小型指标；检查点、逐查询预测、原始特征和大缓存保持本地。产物 manifest 是原本地快照；发布时增加的路径覆盖和文档不属于原 manifest 哈希。
