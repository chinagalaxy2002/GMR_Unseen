# Baseline AUROC 退化机制实验交接

更新时间：2026-10-13 00:13:55 CST（Asia/Shanghai）。这是交接时刻的快照，最新状态以正式队列 `STATUS.json` 和各 run 的 `STATUS.json` 为准。

## 1. 接手后先做什么

**正式队列已在后台训练，不要重复启动、恢复 QIVR 或覆盖输出目录。** 先查看下面的状态入口，确认控制器、四个训练进程及监控文件继续更新。当前无需用户再次批准继续队列。

仓库根目录：`/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。

本轮代码根目录（下文 R）：`experiments/agy_test/auroc_generalization_20261012/qivr_gmr`。名称沿用旧目录，但本轮训练不含 QIVR。

正式队列（下文 Q）：`R/monitoring/experiments/baseline_full_diagnostics_20261013`。

```bash
cd /home/guoxiangyu/paper/Openword/generalized-moment-retrieval
/home/guoxiangyu/miniconda3/envs/gmr/bin/python \
  experiments/agy_test/auroc_generalization_20261012/qivr_gmr/decoder_suite.py status \
  --output experiments/agy_test/auroc_generalization_20261012/qivr_gmr/monitoring/experiments/baseline_full_diagnostics_20261013
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader
```

`Q/FULL_MONITORING.md`／`FULL_MONITOR_STATUS.json`：三骨干通用汇总，采用最新**完整** Seen 验证结果。
`Q/MONITORING.md`／`RESPONSES.md`：原有匹配、梯度和训练响应摘要；Flash 的 DETR 专属项目为 N/A，应结合通用汇总和 Flash 原始记录查看。
`Q/logs/<tag>.log`：训练日志；`Q/controller.log`：调度异常。

## 2. 用户目标和已经确定的决策

研究目标是在不明显损伤 Seen AUROC 的条件下缓解 Unseen AUROC 下降。但当前阶段先诊断原生 baseline 的退化机制，不能把监控本身当作改进算法或性能收益。

用户明确要求：

1. 观察真正的 decoder query／槽位，而非仅观察 QIVR 的语义证据激活槽。
2. 在训练过程中分别记录 positive localization、positive existence、negative existence 及对应激活数量。
3. 追踪槽位 GT 匹配次数、同样本归属变化、定位与存在梯度冲突、去 SA 后正确覆盖还是负样本伪响应增加。
4. 接入 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR，覆盖三个数据集全部 33 个 baseline 设置。
5. 独立队列运行 baseline，停止 QIVR 队列并保留已有结果；每张卡同时最多两个训练进程，优先跨数据集／跨骨干。

不能把此前“Soccer 语义证据激活槽数为 0”解释为 DETR decoder queries 未激活，也不能把旧 QIVR 的现象当作原生 baseline 的结论。QIVR 的联合训练没有完成最终冻结 Unseen 评估，不能据此断言联合训练已经证明失败。

## 3. 当前后台状态

控制器 PID：**2249194**。队列状态 running；55 项中 running 4、queued 51、complete 0、failed 0。

| GPU | 当前任务 | 训练 PID | 快照进度 |
|---|---|---:|---|
| 0 | Soccer / A1_soccer / Moment / with_sa | 2249276 | epoch 3，batch 1300，global step 4306 |
| 0 | clean_v3 / A1_v3 / QD / with_sa | 2249280 | epoch 4，batch 500，global step 2342 |
| 1 | Soccer / A1_soccer / QD / with_sa | 2249286 | epoch 4，batch 200，global step 2456 |
| 1 | Charades-CG v2 / C3_CG / Flash / native | 2249283 | epoch 2，batch 450，global step 2036 |

GPU0/1 均为 RTX3090。快照时显存约 2.4／2.1 GB、利用率 78%／77%。磁盘剩余约 80 GB，需持续留意完整候选、raw probe、逐 epoch 日志和 checkpoint 的累计大小；当前没有磁盘不足自动暂停机制。

`Q/LAUNCH_VERIFIED.json` 已核验四项均进入训练，实际写出 train/probe/validation、共享梯度、优化及 raw NPZ。PID 会随队列推进变化，不应把本表当作永久进程清单。

已取消且应保留的队列：

- `R/monitoring/experiments/joint_qivr_training_20261012`：cancelled，旧 QIVR 输出和取消审计保留。
- `R/monitoring/experiments/baseline_decoder_training_20261012`：cancelled；为升级完整监控停止，旧输出及原实现快照保留，不与正式队列合并。

## 4. 实验范围和冻结协议

| 数据集 | 划分 | baseline 数 |
|---|---|---:|
| clean_v3 | A1_v3、A2_v3、A3_v3、C1_v3、C2_v3 | 15 |
| charades_cg_v2 | C3_CG | 3 |
| Soccer | A1_soccer、A2_soccer、A3_soccer、C1_soccer、C2_soccer | 15 |

共 **33 个原生 baseline**。Moment/QD 的全部 11 划分各另有 no_sa 配对，共 **22 个干预设置**，总计 **55 项**。Flash 没有 DETR decoder self-attention 干预，不虚构 Flash no_sa。

每项 fresh initialization、seed 3407、100 epochs。所有模型参数参与训练；CLIP／SlowFast／文本为预提取特征，其特征提取器不在训练图中。因此本轮不是“冻结原模型，仅训练新增头”。各 run 的 `parameter_updates.jsonl` 记录实际模块更新。

仅使用 S+/S− 训练与 Seen validation 选择；选择 epochs 1..100 中 Seen AUROC 最大者，并列取最早。阈值按 Seen validation 的 5..95 百分位共 91 个候选最大化 BA，并列取最早。写出 `FROZEN_CALIBRATION.json` 后才创建 test 数据集。

**协议差异必须保留：**历史 baseline 按 Seen localization 指标选择 checkpoint，本队列统一按 Seen AUROC 选择。因此这里是原生架构／损失的诊断性复现，不能宣称完全相同的历史 checkpoint 选择复现。与历史冻结预测的配对变化包含训练随机性和选择协议差异，不是 QIVR／新算法收益。

Moment/QD 采用原有 LR 的 AdamW，100 epochs 内常数 LR；历史 opt 的 LR drop 为 Moment 400、QD 200，均未到本轮长度。Flash 使用原生 AdamW（foreach=False）＋StepLR（gamma=.5，原 opt lr_drop）。未实现历史 early stopping，固定跑满 100 epochs。

## 5. 实现入口与数据依赖

| 文件（相对 R） | 用途 |
|---|---|
| `decoder_suite.py` | 55 项队列，两个 GPU 各两个训练槽，检测外部 GPU 进程，跨数据集／骨干优先 |
| `run_decoder_experiment.py` | Moment/QD 原生训练、with/no-SA、Seen 校准及最终冻结评估 |
| `run_flash_monitor_experiment.py` | Flash 原生训练、时序候选监控及最终冻结评估 |
| `src/decoder_slot_monitor.py` | DETR 逐层 query、原生 attention、跨度／重叠／匹配 raw 与摘要 |
| `src/auroc_mechanism_monitor.py` | 逐样本分数／错排／LOO／梯度、原生损失拆分、Flash 时序记录、最终 gap 分解 |
| `src/mechanism_monitor.py` | 原生实际 matcher 捕获、训练归属变化和共享参数梯度 |
| `src/response_monitor.py` | 正负响应与定位汇总、模块参数实际更新 |
| `full_monitor_report.py` | 三骨干通用队列报告 |
| `decoder_report.py` | 已完成固定 probe 的 DETR 逐层报告 |
| `monitor_qivr.py` | 沿用注册表、bootstrap、benchmark 工具；名称不代表本轮训练 QIVR |

数据／历史 baseline 注册表：`experiments/agy_test/training_free_auroc_20261012/common.py` 的 SPECS／paths／video_dirs。

- clean_v3：`v3_release_baselines_20261009`。
- CG v2：标注／评估 `charades_cg_v2_evaluation_20261011`；原训练冻结 checkpoint `charades_cg_baselines_20261010`。
- Soccer：`soccer_unseen_baselines_20261011`。

不要修改 release、原 checkpoint、features 或原 baseline predictions。每次新运行必须使用新输出目录。

DETR Python：`/home/guoxiangyu/miniconda3/envs/gmr/bin/python`（Torch 2.6.0+cu124）。
Flash Python：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python`（Torch 2.0.1+cu118，历史 baseline 环境）。
`flashvtg` 环境的 Torch 2.13.0+cu130 与当前驱动不兼容，**不要切回该环境启动正式训练**。

特征顺序：DETR 为 CLIP→SlowFast；Flash 为 SlowFast→CLIP。Flash 原生 benchmark 使用六位小数 logit，DETR 使用四位小数 sigmoid 概率。原始 logit／概率／benchmark score 分开保存，Flash BCE 从原始 logit 计算。

## 6. 监控口径和采样

详细说明见同目录 `FULL_BASELINE_MONITORING.md`。这里列出接手分析最容易混淆的部分。

**训练全程廉价统计：**实际 DETR GT 匹配／归属变化，正负响应汇总，原生 weighted losses、全局裁剪前梯度范数／系数／LR。DETR 的 S+/S− localization／foreground／existence 贡献复用实际 final/aux 匹配并精确可加；不重新 Hungarian。Flash 原生 localization／classification 只监督 S+，S− 主要提供 existence 监督，这一点应纳入机制比较。

**昂贵诊断采样：**首 batch 和每 50 global steps，记录共享表征梯度、逐层／逐单元结构、LOO、池化所属等。DETR 逐层 raw 每 epoch 首训练 batch 保存；Flash raw 同理。不能称为“每一步都保存全部梯度／全部 attention”。

**固定 Seen probe：**每类最多 64 个 hash 选定训练样本、epoch0 起每 epoch eval 模式观察。DETR 排除 GT 数超出 max_windows 的样本，保证同 GT 可追踪。Flash 复用原生预加载数据；其 gt／span labels 统计需结合 BundleLoss 实际 target，不能仅凭 max_windows 推断实际全部监督。

**全量 Seen validation：**每 epoch 保存逐样本原始／舍入分数、候选与存在耦合、错排／ties、同视频排序、长度／截断分层、LOO 和 score summary。逐层 raw 以固定 probe 为主，不把全验证每层 hs 都堆入磁盘。

**最终 test：**冻结后保存 S+/S−/U+/U− 完整预测和候选、机制记录及 bootstrap；不根据 Unseen 结果调参、早停或选择 checkpoint。

主要指标解释：

- native foreground 激活、正确覆盖槽、max-pool 所属槽、LOO 有影响槽是不同量。
- `response_monitor` foreground active 使用 valid span 且 >0.5；部分新记录明确命名 `ge_0_5` 使用 ≥0.5，分析时按字段定义，勿混用。
- negative 没有 GT，定位精度／正确匹配采用 NA；S− 的激活反映潜在伪响应，不是定位失败率。
- train 归属 flip 包含 dropout／GT 随机采样；固定 eval probe flip 更适合观察训练轨迹。
- 原生 attention 是已经返回的 head 平均权重；训练 dropout 后行和未必为 1，摘要会归一化。no_sa 的 self-attention 是缺失／disabled，不伪造全零。
- DETR LOO 移除一个 decoder query 再计算原生存在头；Flash LOO 移除一个有效视频时序单元，保持 query 表征固定。Flash mean pooling 没有 max-owner，owner 字段为 None 是正常情况。
- Flash pyramid 候选与池化视频单元不是同一索引空间；Flash 不报告 Hungarian 槽位分配／decoder self-attention。
- `localization_success` 是 foreground 最高候选 IoU≥0.5 的诊断；`oracle_localization_success` 是任一候选覆盖。native end-to-end G-mIoU 另按原生后处理和无效跨度过滤计算。
- 梯度冲突、LOO、同视频比较、分层统计及 gap 分解是诊断证据，不单独证明因果。

## 7. 结果文件与分析顺序

每项 run：`CONFIG.json`／`OPT.json`／`STATUS.json`／`validation.jsonl`／`best.ckpt`／`last.ckpt`。

监控文件：

- `monitor/epochs.jsonl`、`assignments_epoch_*.npz`：DETR 实际训练匹配与归属变化。
- `monitor/fixed_probe.jsonl`、`fixed_probe_epoch_*.npz`：DETR 固定 GT 归属。
- `monitor/decoder_slots/`：逐层 query、native self/cross attention、跨度和重叠 raw NPZ／JSONL。
- `monitor/flash_temporal/`：视频／pyramid／attention／原生 foreground 和 regression targets，采样响应。
- `monitor/auroc_mechanisms/train_queries.jsonl`、`probe_queries.jsonl`、`validation_queries.jsonl`、`test_queries.jsonl`。
- 同目录 `*_epoch_*_ranking.npz`：逐 query raw logit、raw probability、native score、错排比例。
- 同目录 `*_epoch_*_scores.json`：分布、ties、AUROC、极端反序对、同视频和分层分析。
- 同目录 `shared_gradients.jsonl`、`optimization.jsonl`、`objective_split.jsonl`（DETR）、`existence_loss_contributions.jsonl`。
- `monitor/parameter_updates.jsonl`：模块实际参数更新，包括 Flash pyramid／coord／class／conf／pooling。

最终：`FROZEN_CALIBRATION.json`、`validation_predictions.npz`、`predictions.npz`、`candidate_cache.pt`、`metrics.json`／`metrics.csv`／`METRICS.md`、`bootstrap.npz`、`candidate_diagnostics.npz`。

最终 2×2 ranking：S+ vs S−（SS）、U+ vs S−（US）、S+ vs U−（SU）、U+ vs U−（UU）。

- 正样本偏移贡献 = 0.5 × [(SS−US)＋(SU−UU)]。
- 负样本偏移贡献 = 0.5 × [(SS−SU)＋(US−UU)]。
- 两者相加 = Seen−Unseen AUROC Gap。

`monitor/auroc_mechanisms/final_gap_decomposition.json`／对应 bootstrap NPZ 给出原生 frozen score 的 2000 次共享视频 cluster CI。跨分区比较为描述性分解，不能说某一贡献就是已经证实的因果效应。

建议分析顺序：先检查模型确实更新和 checkpoint 轨迹；再看正负 logit 分布／错排与 ties；再拆 top1 定位、oracle coverage、存在判别联合结果；最后关联槽位匹配／重复、attention／pooling、梯度冲突和 SA 配对。优先跨数据集、跨骨干确认现象，避免只看 Soccer 或单一 epoch。

## 8. 已完成验证及工程检查历史

`R/monitoring/FULL_MONITOR_TEST_RESULTS.json`：Moment/QD × with/no-SA 四种组合，监控前后输出／训练梯度／Torch RNG 逐位一致；S+/S− 原生损失贡献之和与原损失一致。测试包含多 GT 正例与空 GT 负例。

`R/monitoring/FLASH_FULL_MONITOR_TEST_RESULTS.json`：Flash 同类逐位一致、捕获真实 native targets；加载历史 checkpoint，16 条 Seen 验证 logit 最大差异 2e-6、native set-IoU 差异 0。

有效工程 smoke 包括：

- `full_monitor_smoke_moment_v5`：clean_v3 / Moment。
- `full_monitor_smoke_qd_cg_v6`：CG v2 / QD，包含最终 gap bootstrap。
- `full_monitor_smoke_moment_final_v7`：Soccer / Moment，包含最终 raw score／BCE 口径和 gap bootstrap。
- `full_monitor_smoke_flash_clean_v5`、`full_monitor_smoke_flash_cg_v6`：Flash 在两个 Charades 设置的端到端 smoke；Soccer 由历史 parity 测试和先前端到端检查覆盖。

早期 `full_monitor_smoke_*` 失败目录及 `FLASH_PARITY_DEBUG.json` 保留工程排错记录，不能作为正式结果或当前仍未解决的问题。已修复问题包括：Flash 环境 CUDA 不兼容、视频扩展名处理、head LOO 对原生 GMRAdapter 输入维度、预加载数据集子集长度、Feature 拼接顺序以及 Flash logit／probability 的 BCE 口径。

可重跑的测试（会写独立测试结果文件，运行前避免影响正式卡资源）：

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python \
  experiments/agy_test/auroc_generalization_20261012/qivr_gmr/verify_full_monitor.py
/home/guoxiangyu/miniconda3/envs/univtg/bin/python \
  experiments/agy_test/auroc_generalization_20261012/qivr_gmr/verify_flash_monitor.py
```

现在无新修改无需重复测试或额外占卡。

## 9. 后续运行、故障处理与剩余工作

1. 让当前队列继续；所有设置尚未完成。不要提前输出正式性能结论或五划分 macro。
2. 定期检查 controller、run 状态／错误日志、GPU 数量及磁盘。正式进程参数可在队列 STATUS 的 argv 查到，实际 PID 应与 `/proc/<pid>/cmdline` 对照。
3. 单项失败时，先保留失败现场并诊断。runner 要求 fresh 输出，没有自动 resume CLI；不能直接覆盖失败 run 或把 last.ckpt 当作已经支持断点恢复。修复后应使用新目录明确记录 rerun 与原 job 的关系，并显式处理汇总入口，不能伪造原任务 complete。
4. 若必须改动模型／runner／监控源码，先考虑排队任务尚会读取这些文件。`SOURCE_SNAPSHOT` 是审计副本，**运行命令仍指向 R 的源码，并非直接执行快照**。不要让后续任务无记录地使用新版本；应受控处理队列、版本和输出。
5. 不应停止整个进程组来处理单项任务。控制器和训练进程同属 detached 会话；操作前确认 PGID，避免误伤本队列及其他研究任务。
6. 不发送邮件／消息，不部署，不改原数据／结果。新算法改动应在诊断后另起明确实验。

`Q/SOURCE_SNAPSHOT` 保存本轮调度、runner、监控和 models/training 源码；`Q/SOURCE_SNAPSHOT_SHA256.json` 记录 92 个文件哈希；`SUITE.json`／各 CONFIG 保存配置、release 和源文件哈希。

尚待完成：55 项完整训练与冻结评估、完整 SA 配对报告、跨骨干／数据集机制分析，以及满足下节口径的最终交付。当前并未完成这些工作。

## 10. 最终科学报告要求

各 split／backbone 单独报告 Seen／Unseen AUROC、实际 Rej-F1、end-to-end G-mIoU@1，signed Performance Gap = Seen−Unseen（pp），保留负 gap。另给 overall Rej-F1／rejection rate／G-mIoU、S+／U+ FRR、各子集正负样本计数及 video-cluster bootstrap 95% CI。

与同 split／backbone reference 比较，报告三指标的 Unseen Net Gain、Seen Change、Gap Reduction 和 paired CI；standalone baseline 的相对改进未定义。历史比较必须注明选择协议差异。no-SA 与 with-SA 独立使用预先声明的 Seen-only 选择规则，配对结果在 `Q/pairs/` 完成后生成。

Rej-F1／G-mIoU 依赖子集类比例，应说明解释限制。正式五划分 macro 只有五个划分全部完成才成立；CG v2 只有一个划分，不伪装五划分。保存 Markdown、CSV/JSON、冻结预测、校准和 bootstrap 原始产物；所有未完成结果标为 partial。
