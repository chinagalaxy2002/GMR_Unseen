# GMR-Unseen 微调分支 (fintune) 实验总览与复现指南

本分支（`fintune`）精简并专注于 **Soccer-GMR** 任务上的三组核心实验及其演进血缘关系，剔除了所有与本主线无关的临时产物、中间消融（Scheme B/C/D、A1/A2/A4 等）与重复源码。

---

## 1. 实验脉络与方案演进

```
 [1. E0 Baseline]
   └── 原生 FlashVTG-GMR 基础模型 (训练 113 epochs, 收敛定位 mAP 26.14%, AUROC 74.27%)
            │
            ▼ (作为初始化检查点: runs/E0/best.ckpt)
 [2. Task A: Two-Stage Fine-Tuning]
   └── 冻结 E0 定位主干，微调 Event Query 分支，引入 Text Plurality 机制与置信度门控
   └── 成果：保持定位 mAP (26.18%) 的同时，Test G-mIoU@0.4 提升至 42.42% (+7.76 pp)，Plurality AUROC 达 83.51%
            │
            ▼ (作为结构与超参基准)
 [3. A3: Similarity Hard-Negative Mining]
   └── 在 Task A 架构上引入语义相似度难负例挖掘，增强模型区分语义相近但事实不存在动作的能力
   └── 成果：Val AUROC 进一步提升至 74.76% (+2.16 pp)，Val G-mIoU@0.4 提升至 47.14% (+5.73 pp)
```

---

## 2. 核心指标对比一览

### 官方测试集 (Test Split, 1,036 条样本)

| 实验方案 | 标识符 / 运行目录 | 定位 mAP | AUROC | G-mIoU@0.4 | G-mIoU@0.5 | 校准最优 G-mIoU | Plurality AUROC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0 Baseline** | `runs/E0` | 26.14% | 74.27% | 34.66% | 46.19% | 49.24% | — (未引入) |
| **Task A (两阶段微调)** | `runs/E2M_scheme_A_twostage_s2024` | **26.18%** | **73.19%** | **42.42%** | **47.41%** | **52.98%** | **83.51%** |

### 验证集 (Validation Split, 465 条样本)

| 实验方案 | 标识符 / 运行目录 | 定位 mAP | AUROC | G-mIoU@0.4 | G-mIoU@0.5 | 校准最优 G-mIoU | Plurality BA | Plurality AUROC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **E0 Baseline** | `runs/E0` | 26.82% | 72.35% | 34.40% | 46.20% | 49.30% | — | — |
| **Task A 原版** | `runs/E2M_scheme_A_twostage_s2024` | 26.82% | 72.60% | 41.41% | 46.29% | 52.86% | 62.78% | 79.00% |
| **A3 难负例增强** | `runs/A3_similarity_hardneg_s2024` | 26.82% | **74.76%** | **47.14%** | **51.13%** | 52.51% | **72.78%** | **81.70%** |

*(注：A3 保持定位输出指纹完全一致，定位 mAP 严格保持 26.82%)*

---

## 3. 目录与文件布局

```
experiments/agy_test/
├── soccer_flash_event_query_20261015/          # 【实验一：E0 基线】
│   ├── README.md / RESULTS.md / RESULTS.json  # 实验报告与总指标
│   ├── code/                                  # 训练与评测源码 (run.py, evaluation.py, ...)
│   ├── configs/                               # 协议配置文件 (protocol.json, ...)
│   ├── logs/E0.log                            # 完整训练与评测日志 (773 KB)
│   └── runs/E0/                               # 核心输出
│       ├── metrics.json / validation_metrics.json
│       ├── test_predictions.jsonl             # 官方 Test 逐条预测 (3.12 MB)
│       ├── validation_predictions.jsonl       # Val 逐条预测
│       └── trace.jsonl / CONFIG.json
│
├── soccer_flash_kim_surpass_e0_20261016/       # 【实验二：Task A 两阶段微调】
│   ├── RESULTS.md / RESULTS.json              # 实验结果报告与统计
│   ├── TASKS_SUMMARY.md                       # Task A 详细原理与配置说明
│   ├── code/                                  # 两阶段微调代码 (train.py, model.py, eval_checkpoint.py, ...)
│   ├── configs/                               # 调度与超参配置 (jobs.json, protocol.json)
│   ├── logs/E2M_scheme_A_twostage_s2024.log   # 完整微调与测试日志 (237 KB)
│   └── runs/E2M_scheme_A_twostage_s2024/      # 核心输出
│       ├── test_metrics.json / validation_metrics.json
│       ├── test_predictions.jsonl             # 官方 Test 逐条预测 (3.19 MB)
│       ├── validation_predictions.jsonl       # Val 逐条预测
│       └── trace.jsonl / CONFIG.json
│
└── soccer_flash_kim_mechanism_20261016/task_a_enhancement/  # 【实验三：A3 相似度难负例增强】
    ├── README.md / RESULTS.md / FINAL_REPORT.md             # 机制验证与消融分析报告
    ├── FINAL_REPORT.json / RESULTS.json
    ├── code/                                                # A3 难负例挖掘实现 (train.py, model.py, ...)
    ├── configs/jobs.json                                    # A3 任务参数配置
    ├── logs/A3_similarity_hardneg_s2024.log                 # 完整训练与评测日志 (98 KB)
    └── runs/A3_similarity_hardneg_s2024/                    # 核心输出
        ├── validation_metrics.json
        ├── validation_predictions.jsonl                     # Val 逐条预测
        └── trace.jsonl / CONFIG.json
```

---

## 4. 快速验证与结果客观性核验

所有评估预测（`.jsonl`）和详细指标（`.json`）均已完整跟踪在各实验目录下。任何人均可直接利用 Python 脚本进行无需 GPU 的纯离线客观核验：

### 核验命令 1：验证 E0 基线 Test 指标
```bash
python3 -c "
import json
with open('experiments/agy_test/soccer_flash_event_query_20261015/runs/E0/metrics.json') as f:
    d = json.load(f)
print('E0 Test mAP:', d['brief']['mAP'])
print('E0 Test AUROC:', d['brief']['AUROC'])
print('E0 Test G-mIoU@0.4:', d['brief']['G-mIoU@1'])
"
```

### 核验命令 2：验证 Task A Test 指标与提升幅度
```bash
python3 -c "
import json
with open('experiments/agy_test/soccer_flash_kim_surpass_e0_20261016/runs/E2M_scheme_A_twostage_s2024/test_metrics.json') as f:
    d = json.load(f)
print('Task A Test mAP:', d['positive_localization']['mAP'])
print('Task A Test AUROC:', d['AUROC'])
print('Task A Test G-mIoU@0.4:', d['gate_04']['G-mIoU@1'])
print('Task A Plurality AUROC:', d.get('plurality', {}).get('AUROC'))
"
```

### 核验命令 3：验证 A3 难负例在 Val 上的表现
```bash
python3 -c "
import json
with open('experiments/agy_test/soccer_flash_kim_mechanism_20261016/task_a_enhancement/runs/A3_similarity_hardneg_s2024/validation_metrics.json') as f:
    d = json.load(f)
print('A3 Val AUROC:', d['AUROC'])
print('A3 Val G-mIoU@0.4:', d['gate_04']['G-mIoU@1'])
print('A3 Val G-mIoU@0.5:', d['fixed_05']['G-mIoU@1'])
print('A3 Plurality BA:', d.get('plurality', {}).get('balanced_accuracy'))
print('A3 Plurality AUROC:', d.get('plurality', {}).get('AUROC'))
"
```
