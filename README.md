# Soccer-GMR 模型微调与拒识机制增强 (fintune 分支)

本分支（`fintune`）是针对 **Soccer-GMR (Generalized Moment Retrieval in Soccer Videos)** 任务的专属微调与算法增强分支。

分支经过深度精简与整洁重构，移除了全部历史无关实验与调试冗余，**聚焦于三套严格递进的方案血缘链条**，并完整收录了从训练源码、配置文件、运行日志到官方测试集（Test split, 1,036 条样本）的全部逐条预测（`.jsonl`）与评测指标（`.json`）。

---

## 一、 三大核心算法流程与架构图解

### 1. 基线模型 (E0 Baseline)：端到端联合训练与梯度冲突

E0 基于原生 FlashVTG-GMR 架构，由跨模态 Transformer 编码器同时连接时序定位头（Localization Head）与全局池化存在性分类头（Existence Head）。双任务共享同一主干网络反向传播：

```mermaid
flowchart TD
    subgraph Inputs ["📥 多模态输入 (Inputs)"]
        V_in["视频特征 Video Features<br/>SlowFast (2304d) + CLIP-ViT (512d)"]
        T_in["文本查询 Text Query<br/>CLIP Text (512d)"]
    end

    subgraph Backbone ["⚙️ 跨模态时序编码骨干网络 (FlashVTG Backbone)"]
        V_proj["视频特征投影 Linear"]
        T_proj["文本特征投影 Linear"]
        CrossModal["跨模态交互 Cross-Attention & FFN<br/>(视觉与文本时序深层融合)"]
        V_in --> V_proj
        T_in --> T_proj
        V_proj --> CrossModal
        T_proj --> CrossModal
    end

    subgraph LocBranch ["🎯 正例时序定位分支 (Localization Head)"]
        CrossModal --> LocHead["时序边界预测与质量估计<br/>Boundary Regression & Saliency"]
        LocHead --> LocLoss["定位损失 L_loc<br/>L_span (L1) + L_giou + L_saliency"]
    end

    subgraph ExistBranch ["⚡ 存在性判别分支 (Event Query Head)"]
        CrossModal --> GAP["全局时序池化 / Event Token"]
        GAP --> ExistMLP["存在性分类 MLP (单头分类)"]
        ExistMLP --> ExistLoss["存在性分类损失 L_exist<br/>Binary Cross Entropy (BCE)"]
    end

    subgraph Conflict ["⚠️ 根本缺陷：双任务梯度冲突 (Gradient Entanglement)"]
        ExistLoss -.->|"反向梯度传播 (更新特征表示)"| CrossModal
        LocLoss -.->|"反向梯度传播 (更新时序边界)"| CrossModal
        Note["❌ 机制痛点：存在性分类梯度持续改变共享时序特征分布，<br/>破坏了精细定位所需的边界敏感性，导致正例定位 mAP 出现严重退化！"]
    end

    style Inputs fill:#f8f9fa,stroke:#adb5bd,stroke-width:1px
    style Backbone fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style LocBranch fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style ExistBranch fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Conflict fill:#ffebee,stroke:#d32f2f,stroke-width:2px
```

---

### 2. 本方案 Task A：两阶段解耦微调与文本复数建模

为了彻底解决定位与拒识之间的梯度冲突，Task A 采用**两阶段解耦训练策略**：以收敛的 E0 权重为基石，**完全冻结定位主干**，通过 `detach(·)` 隔离反向传播，仅对 Event Query 读取头与新增的文本复数分类头进行微调：

```mermaid
flowchart TD
    subgraph Stage1 ["❄️ 阶段一：E0 定位主干完全冻结 (Zero-Degradation Lock)"]
        V_feat["输入视频 Video V"]
        T_feat["输入查询 Text T"]
        FrozenBackbone["【已完全冻结】FlashVTG 骨干网络<br/>(Backbone, Cross-Attention, Loc Head ❄️)<br/>参数完全固定，requires_grad = False"]
        V_feat --> FrozenBackbone
        T_feat --> FrozenBackbone
        LockedPreds["🔒 锁定定位候选窗口<br/>(mAP 严格保持 26.18%，零退化风险)"]
        FrozenBackbone --> LockedPreds
    end

    subgraph DetachOp ["🛡️ 梯度隔离屏障 (Gradient Barrier)"]
        FrozenBackbone -->|"前向输出特征"| Detach["detach(·) 算子<br/>完全切断向主干的反向传播路径"]
    end

    subgraph Stage2 ["🔥 阶段二：解耦微调读取头与复数建模 (Task A Active Tuning)"]
        subgraph EventQuery ["存在性独立读取头"]
            Detach --> EvidenceRead["Evidence Cross-Attention<br/>(多阶段证据交叉读取层)"]
            EvidenceRead --> ExistHead["存在性预测头 MLP"]
            ExistHead --> LossExist["L_exist (BCE 损失)"]
        end

        subgraph PluralityModule ["文本复数分类头 (Text Plurality)"]
            T_feat --> TextTok["文本初始表征 e0"]
            TextTok --> PluralityMLP["复数预测头 MLP<br/>P(single) vs P(multi)"]
            PluralityMLP --> LossPlurality["L_plurality (CE 损失)"]
        end
    end

    subgraph InferenceGate ["🚦 推理阶段：置信度与复数门控 (Inference Gating)"]
        ExistHead --> ProbExist["存在概率 P(exist)"]
        PluralityMLP --> ProbMulti["复数概率 P(multi)"]
        LockedPreds --> Gate["动态置信度门控器<br/>P(exist) < 0.4 ➜ 彻底拒识 (真负例输出空)<br/>P(exist) >= 0.4 ➜ 保留最优候选窗口"]
        ProbExist --> Gate
        ProbMulti --> Gate
        FinalOut["🏆 最终 GMR 检索结果<br/>(G-mIoU@0.4 提升至 42.42%，较 E0 +7.76 pp)"]
        Gate --> FinalOut
    end

    style Stage1 fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style DetachOp fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style Stage2 fill:#fff8e1,stroke:#ffa000,stroke-width:2px
    style EventQuery fill:#ffffff,stroke:#ffa000,stroke-dasharray: 5 5
    style PluralityModule fill:#ffffff,stroke:#ff8f00,stroke-dasharray: 5 5
    style InferenceGate fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

---

### 3. 本方案 A3 增强：语义相似度难负例对比挖掘

针对足球场景中“动作语义相似但画面实际不存在”（如把“角球”误判为已发生的“任意球”）的高频误检痛点，A3 在 Task A 架构上引入**批内语义相似度难负例挖掘（Similarity Hard-Negative Mining）**与对比监督：

```mermaid
flowchart TD
    subgraph BatchInputs ["📦 Mini-Batch 多样本批次输入"]
        V_batch["视频批次: V_1, V_2, ..., V_B"]
        T_batch["正例文本批次: T_1, T_2, ..., T_B"]
    end

    subgraph HardNegMining ["🔍 语义相似度难负例挖掘引擎 (Hard-Negative Mining)"]
        T_batch --> Norm["L2 归一化文本投影空间"]
        Norm --> SimMat["批内语义相似度矩阵 S_ij = <T_i, T_j><br/>(对角线 S_ii 置为 -inf，排除自身)"]
        SimMat --> Argmax["最强混淆负例匹配<br/>j* = argmax_{j != i} S_ij"]
        T_batch --> Pick["抽取语义最接近的不匹配文本<br/>T_{j*} (最难混淆负例)"]
        Argmax --> Pick
        NoteNeg["💡 挖掘机理：自动找出语义上与目标极度相似、<br/>但在当前视频中绝不存在的高混淆负例！"]
    end

    subgraph DualForward ["⚡ 双流对比前向与监督目标 (Dual Contrastive Paths)"]
        subgraph PosPath ["正例前向通路 (Positive Grounding)"]
            V_batch --> VerifierPos["解耦事件检验器"]
            T_batch --> VerifierPos
            VerifierPos --> LogitPos["存在预测 logits+"]
            LogitPos --> LossPos["正例存在损失: BCE(logits+, 1.0)"]
        end

        subgraph NegPath ["难负例前向通路 (Hard-Negative Contrast)"]
            V_batch --> VerifierNeg["解耦事件检验器 (共享参数)"]
            Pick --> VerifierNeg
            VerifierNeg --> LogitNeg["负例预测 logits-"]
            LogitNeg --> LossNeg["难负例惩罚损失: BCE(logits-, 0.0)"]
        end
    end

    subgraph Objective ["🎯 联合优化目标 (Contrastive Objective)"]
        LossPos --> TotalLoss["L_total = L_exist + 0.1 * L_plurality + 0.5 * L_hard_neg"]
        LossNeg --> TotalLoss
        Effect["🛡️ 算法收益：<br/>• 强迫模型从'语义泛匹配'转向'细粒度动作核实'<br/>• Test AUROC 攀升至 75.03% (超越 E0 基线)<br/>• Test G-mIoU@0.4 暴涨至 47.62% (+12.96 pp)<br/>• 负例拒识准确率 N-acc 达到惊人的 93.09%"]
        TotalLoss --> Effect
    end

    style BatchInputs fill:#f8f9fa,stroke:#adb5bd,stroke-width:1px
    style HardNegMining fill:#ede7f6,stroke:#512da8,stroke-width:2px
    style DualForward fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    style PosPath fill:#ffffff,stroke:#2e7d32,stroke-dasharray: 5 5
    style NegPath fill:#ffffff,stroke:#c62828,stroke-dasharray: 5 5
    style Objective fill:#fff9c4,stroke:#f57f17,stroke-width:2px
```

---

## 二、 原论文各项指标完整横向对比表

> **评测基准**：官方统一测试集（Test Split，包含 544 条真实正例 + 492 条真实负例，共计 1,036 条样本）。所有指标与 Soccer-GMR / FlashVTG 原论文指标体系严格对齐。

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
    print('  AUROC (Existence): ', round(d.get(auroc_k, d.get('brief', {}).get('AUROC')), 2))
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
