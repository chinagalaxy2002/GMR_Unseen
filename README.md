# DEC-Power-CDF：纯净方法与 baseline 复现

本独立分支仅包含 DEC 幂律乘积门控、与它配对的 baseline 评测代码、冻结输入及完整结果。没有其他实验方法或训练工程。

- [算法介绍与评估边界](METHOD.md)
- [完整两张表：15 组逐划分结果及五划分宏平均](results/FULL_RESULTS.md)
- [逐项数值和阈值 CSV](results/metrics.csv)
- [改善、掉点及 95% CI CSV](results/comparisons.csv)
- [输入来源与 SHA256](data/SOURCE_MANIFEST.json)
- [复现验证记录](VALIDATION.md)

## 五划分等权宏平均

| Backbone | Baseline Seen → DEC | Baseline Unseen → DEC | Rej-F1 (%) | G-mIoU@1 (%) |
|---|---:|---:|---:|---:|
| Moment-DETR | 0.7518 → 0.7180 | 0.5287 → 0.6122 | 58.03 → 59.40 | 37.99 → 39.74 |
| QD-DETR | 0.7476 → 0.7262 | 0.5144 → 0.6086 | 56.27 → 58.93 | 38.06 → 40.23 |
| FlashVTG | 0.7730 → 0.7211 | 0.5714 → 0.6200 | 58.70 → 59.41 | 43.34 → 44.04 |

五划分为 A1、A2_alt、A3、C1、C2_alt。上述数字不是合并样本的 AUROC。Seen 下降与正例误拒率上升是实际代价；部分划分的定位/拒绝指标下降，详见完整表。

## 复现

Python 3.8+，CPU 即可，不需要 GPU，不运行训练或后台调度。数据约 9 MB，已包含于该分支，无需外部路径或 token。

```bash
python -m pip install -r requirements.txt
# 同时复现 baseline、DEC、全部结果表及 2000 次配对视频 bootstrap
python evaluate.py --output reproduced_results --bootstrap 2000
# 单独复现历史 baseline
python reproduce_baseline.py --output baseline_results
# 只复算点估计，跳过 bootstrap
python evaluate.py --output reproduced_results --bootstrap 0
```

`reproduced_results/comparisons.csv` 给出 DEC 相对 baseline 的 ΔSeen、ΔUnseen、ΔRej-F1、ΔG-mIoU：负数直接标明掉点。`metrics.csv` 提供所有阈值和未四舍五入的逐划分指标。每次复算都会从原始定位窗口重新计算集合 IoU，并核对冻结缓存，防止定位指标只依赖预填汇总。

此处“baseline 复现”指同协议下从真实历史缓存分数和定位提交重新评测，包括其未见概念表现偏低以及 DEC 带来的各项下降；不包含从原始视频重训 backbone。三个骨干的名称是 Moment-DETR、QD-DETR、FlashVTG；表中简写为 moment、qd、flash。

## 文件

| 路径 | 内容 |
|---|---|
| `dec.py` | 路由、训练 CDF、幂律乘积、历史验证阈值 |
| `evaluate.py` | baseline/DEC 完整评测、原始窗口 IoU、配对视频 bootstrap、结果表 |
| `reproduce_baseline.py` | baseline 独立入口 |
| `data/<split>/{train,val,test}.npz` | 14 维历史标量特征、查询、qid、视频、标签、分区；val 只保留 Seen |
| `data/<split>/windows.jsonl` | 真值和各 backbone 第一个合法预测窗口 |
| `data/SOURCE_MANIFEST.json` | 原仓库输入路径、解析后的实际路径及内容哈希 |
| `data/ASSET_MANIFEST.json` | 本分支冻结输入内容哈希 |
| `results/` | 完整 Markdown 表、CSV、JSON 和 bootstrap 配置/区间 |

该方法免训练，因而没有 DEC 权重文件。使用的是保留并列的训练 CDF 修正版；历史测试集重排名的 QD 0.6332 不能当成本版本结果。缓存的局部证据共享 HQ 候选，方法仍属于探索性验证，具体限制见算法说明。
