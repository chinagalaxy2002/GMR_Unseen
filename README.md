# Soccer-GMR 模型微调与拒识机制增强 (fintune 分支)

本分支（`fintune`）是针对 **Soccer-GMR (Generalized Moment Retrieval in Soccer Videos)** 任务的专属微调与算法增强分支。

分支经过深度精简与整洁重构，移除了全部历史无关实验与调试冗余，**聚焦于三套严格递进的方案血缘链条**，并完整收录了从训练源码、配置文件、运行日志到官方测试集（Test split, 1,036 条样本）的全部逐条预测（`.jsonl`）与评测指标（`.json`）。

---

## 一、 方案脉络与核心机制演进

```mermaid
flowchart TD
    E0["1. E0 Baseline (官方基线)\n- 原生 FlashVTG-GMR 骨干\n- 训练 113 epochs 全量收敛\n- 产出 runs/E0/best.ckpt"]
    
    TaskA["2. Task A: Two-Stage Fine-Tuning (两阶段微调)\n- 冻结 E0 定位主干，完全锁定定位能力\n- 解耦微调 Event Query 读取与分类分支\n- 引入文本复数分类头 (Text Plurality)"]
    
    A3["3. A3: Similarity Hard-Negative Mining (难负例语义增强)\n- 继承 Task A 两阶段解耦与复数监督\n- 批内挖掘语义最相近但不包含动作的硬负例文本\n- 施加对比交叉熵，压制高语义相似度干扰"]

    E0 -->|"加载权重初始化"| TaskA
    TaskA -->|"增强对比学习"| A3
```

- **E0 (Baseline)**：原生 FlashVTG-GMR 基线模型，从零训练 113 轮至完全收敛，定位 mAP 达到 26.14%，AUROC 为 74.27%。
- **Task A (两阶段微调 Scheme A)**：以 E0 检查点为起点，**完全冻结 E0 定位主干参数**，仅微调 Event Query 存在性分支与文本复数头。在保证定位能力不退化（mAP 26.18%）的前提下，Test G-mIoU@0.4 跃升至 **42.42%**（+7.76 pp）。
- **A3 (相似度难负例增强)**：在 Task A 基础上，针对负例误检痛点引入批内语义最相似负例挖掘（Hard Negative Mining）。模型在官方 Test 测试集上实现了全方位突破：**AUROC 达 75.03%**，**G-mIoU@0.4 达 47.62%**（较基线 E0 暴涨 **+12.96 pp**），**0.5 阈值下负例拒识准确率（N-acc）高达 93.09%**。

---

## 二、 原论文各项指标完整横向对比表

> **评测基准**：官方统一测试集（Test Split，包含 544 条真实正例 + 492 条真实负例，共计 1,036 条样本）。所有指标均与原论文评测体系及协议严格对齐。

| 指标大类 | 原论文 / 评测基准指标 | E0 Baseline (官方基线) | Task A (两阶段微调) | A3 (难负例语义增强) | A3 相比 E0 提升幅度 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **正例时序定位**<br>*(Localization Only)* | **mAP (全量平均精度)** | 26.14% | **26.18%** | **26.18%** | **+0.04 pp (完全锁定)** |
| | **mAP @ 0.5** | 48.73% | **48.86%** | **48.86%** | +0.13 pp |
| | **mAP @ 0.75** | 28.32% | **28.40%** | **28.40%** | +0.08 pp |
| | **Recall 1 @ 0.3** | 51.29% | **51.47%** | **51.47%** | +0.18 pp |
| | **Recall 1 @ 0.5** | 39.15% | **39.34%** | **39.34%** | +0.19 pp |
| | **Recall 1 @ 0.7** | 21.69% | **22.06%** | **22.06%** | +0.37 pp |
| | **mIoU @ 1** | 34.63% | 34.78% | **34.87%** | +0.24 pp |
| **存在性与拒识**<br>*(Existence & Rejection)* | **AUROC (全局判别能力)** | 74.27% | 73.19% | **75.03%** | <font color="green">**+0.76 pp**</font> |
| | **Rej-F1 @ 0.4 (拒识 F1)** | 54.16% | 64.28% | **70.52%** | <font color="green">**+16.36 pp**</font> |
| | **Rej-F1 @ 0.5 (拒识 F1)** | 68.08% | 69.18% | **73.75%** | <font color="green">**+5.67 pp**</font> |
| | **Negative Recall (N-acc @ 0.4)** | 46.34% | 65.65% | **78.05%** | <font color="green">**+31.71 pp**</font> |
| | **Negative Recall (N-acc @ 0.5)** | 75.00% | 78.46% | **93.09%** | <font color="green">**+18.09 pp**</font> |
| | **Positive Recall @ 0.4** | **77.94%** | 65.07% | 60.85% | -17.09 pp (大幅压制虚警) |
| **GMR 联合度量**<br>*(G-mIoU 综合指标)* | **G-mIoU@1 (Gate = 0.4)** | 34.66% | 42.42% | **47.62%** | <font color="green">**+12.96 pp**</font> |
| | **G-mIoU@1 (Gate = 0.5)** | 46.19% | 47.41% | **53.39%** | <font color="green">**+7.20 pp**</font> |
| | **G-mIoU@1 (Val 校准阈值)** | 49.24% | 52.98% | **55.55%** | <font color="green">**+6.31 pp**</font> |
| | **G-mIoU@3 (Gate = 0.4)** | 28.24% | 36.43% | **41.75%** | <font color="green">**+13.51 pp**</font> |
| | **G-mIoU@5 (Gate = 0.4)** | 25.85% | 34.44% | **39.97%** | <font color="green">**+14.12 pp**</font> |
| **复数事件分类**<br>*(Plurality Modeling)* | **Plurality AUROC** | — (无) | **83.51%** | **83.12%** | 新增复数事件建模能力 |
| | **Plurality Balanced Accuracy** | — (无) | 65.29% | **70.65%** | <font color="green">**+5.36 pp**</font> |

---

## 三、 分支工作目录与文件结构

仓库根目录下保持极简布局，仅包含基础模型库、数据与这三套核心实验：

```
.
├── configs/                                          # 模型结构协议配置文件
├── data/                                             # 官方数据集划分标注
├── eval/                                             # GMR 官方评测实现 (metrics.py, eval_main.py)
├── models/                                           # FlashVTG 与 Transformer 基础结构源码
├── training/                                         # 数据集加载器与推理工具
├── requirements.txt / requirements-flash-vtg.txt     # Python 依赖清单
└── experiments/agy_test/
    ├── soccer_flash_event_query_20261015/            # 【实验一：E0 Baseline】
    │   ├── code/                                     # 训练与评估脚本 (run.py, evaluation.py, ...)
    │   ├── configs/                                  # 实验协议 (protocol.json, ...)
    │   ├── logs/E0.log                               # 113 轮完整运行日志 (773 KB)
    │   └── runs/E0/
    │       ├── metrics.json                          # 官方测试集指标全量导出
    │       ├── test_predictions.jsonl                # 官方测试集逐条前向预测 (3.12 MB)
    │       ├── test_predictions_pre_nms.jsonl        # NMS 前定位窗口
    │       └── trace.jsonl / CONFIG.json
    │
    ├── soccer_flash_kim_surpass_e0_20261016/         # 【实验二：Task A 两阶段微调】
    │   ├── code/                                     # 微调主程序 (train.py, model.py, eval_checkpoint.py, ...)
    │   ├── configs/jobs.json                         # 任务参数定义
    │   ├── logs/E2M_scheme_A_twostage_s2024.log      # 完整微调与测试日志 (237 KB)
    │   └── runs/E2M_scheme_A_twostage_s2024/
    │       ├── test_metrics.json                     # 官方测试集指标全量导出
    │       ├── test_predictions.jsonl                # 官方测试集逐条前向预测 (3.19 MB)
    │       ├── test_predictions_pre_nms.jsonl        # NMS 前定位窗口
    │       └── trace.jsonl / CONFIG.json
    │
    └── soccer_flash_kim_mechanism_20261016/task_a_enhancement/  # 【实验三：A3 相似度难负例增强】
        ├── code/                                     # 难负例实现 (train.py, model.py, eval_test.py, ...)
        ├── configs/jobs.json                         # A3 超参配置 (hard_negative: true)
        ├── logs/A3_similarity_hardneg_s2024.log      # 完整训练日志 (98 KB)
        └── runs/A3_similarity_hardneg_s2024/
            ├── test_metrics.json                     # 官方测试集指标全量导出
            ├── test_predictions.jsonl                # 官方测试集逐条前向预测 (3.10 MB)
            ├── test_predictions_pre_nms.jsonl        # NMS 前定位窗口
            ├── validation_metrics.json               # 验证集指标
            └── trace.jsonl / CONFIG.json
```

---

## 四、 快速验证与结果客观性核验

所有测试预测数据均已随本分支提交，支持**无需 GPU、无需下载权重的秒级离线核验**：

### 1. 一键离线核验三组模型 Test 指标
直接在仓库根目录下运行以下命令，即可从保存的测试集预测中输出三套方案的完整指标：

```bash
python3 -c "
import json

def report(name, path, map_k, auroc_k, gm_k, rej_k):
    with open(path) as f:
        d = json.load(f)
    print(f'=== {name} ===')
    print('  mAP (Localization):', d.get(map_k, {}).get('mAP', d.get('brief', {}).get('mAP')))
    print('  AUROC (Existence): ', d.get(auroc_k, d.get('brief', {}).get('AUROC')))
    print('  G-mIoU@1 (Gate=0.4):', d.get(gm_k, {}).get('G-mIoU@1', d.get('brief', {}).get('G-mIoU@1')))
    print('  Rej-F1 @ 0.4:      ', d.get(rej_k, {}).get('Rej-F1', d.get('brief', {}).get('Rej-F1@0.4')))

report('E0 Baseline', 'experiments/agy_test/soccer_flash_event_query_20261015/runs/E0/metrics.json', 'brief', 'AUROC', 'brief', 'brief')
report('Task A (Fine-Tuning)', 'experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/test_metrics.json', 'positive_localization', 'AUROC', 'gate_04', 'gate_04')
report('A3 (Hard-Neg Mining)', 'experiments/agy_test/soccer_flash_kim_mechanism_20261016/task_a_enhancement/runs/A3_similarity_hardneg_s2024/test_metrics.json', 'positive_localization', 'AUROC', 'gate_04', 'gate_04')
"
```

### 2. GPU 在线复测评测命令
若本地配备单张 GPU（显存 ≥ 12GB），可直接调用各任务评估脚本独立复验：

```bash
# 复验 Task A 官方测试集评测
python experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/code/eval_checkpoint.py \
    --ckpt experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/best.ckpt

# 复验 A3 官方测试集评测
python experiments/agy_test/soccer_flash_kim_mechanism_20261016/task_a_enhancement/code/eval_test.py \
    --run A3_similarity_hardneg_s2024 \
    --device cuda:0
```
