# Task A 增强：冻结定位器的四板训练

目标不是重新训练 FlashVTG，而是在 Task A 的成功条件下继续增强：统一加载历史 E0 `best.ckpt`，冻结全部定位参数，只训练约 2.18M 参数的只读判别头。

## 四板

| 板块 | 方法 | 主要假设 |
|---|---|---|
| A1 | 多粒度 Event Query | 文本态与三层视频态的存在证据互补，逐层监督比只读最终层稳定 |
| A2 | 联合 cardinality | 直接预测 `N=0/1/2/3+`，由同一分布导出 existence/plurality，避免两个头逻辑冲突 |
| A3 | 相似度 hard negative | batch 内选择最相似的错配文本，只对 detached head 施加负例损失，避免 Task D 损伤定位 |
| A4 | 组合只读 verifier | A1+A2，并融合冻结的 saliency/T2V 统计和 hard negatives |

## 安全与评测约束

- 每个 epoch 逐张量检查所有冻结参数完全不变。
- 每个 epoch 将 `pred_relevant_windows_pre_exist` 与历史 E0 的 465 条 Val 输出逐值比较；任何差异立即终止。
- checkpoint 只按 Val AUROC 选择；同时报告固定 0.4、固定 0.5 和 Val BA 阈值下的 G-mIoU。
- 当前阶段禁止加载或评测官方 Test，避免 A-D 已看 Test 后继续造成隐性 Test 调参。
- 调度上限为每张物理 GPU 同时两个任务，配置为 GPU0 跑 A1/A2，GPU1 跑 A3/A4。

启动或恢复：

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -B code/scheduler.py
```

实时结果见 `RESULTS.md`，逐 epoch 证据见 `runs/<run_id>/trace.jsonl`。
