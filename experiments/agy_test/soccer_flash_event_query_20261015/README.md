# Soccer-GMR Standard：Temporal Event Query 跨骨干验证

接手实验请先读 [HANDOFF.md](HANDOFF.md)，其中包含当前进程快照、队列、验证证据和异常恢复方法。

本实验将用户方案A（E2，专用全局Event Query）应用到FlashVTG-GMR、Moment-DETR-GMR、QD-DETR-GMR。每个骨干只做E0/E2成对训练，共6项正式任务。所有新增源码、缓存、日志、checkpoint与文档均在本目录；原工程、其他实验和下载特征只读。不增加语义划分，不合并Train/Val/Test，不加入Full规模、方案B或其他消融。

## 正在运行与自动队列

两个Flash任务已经启动，GPU0为E0、GPU1为E2。`code/dual_gpu_queue.py` 接管这两个已有PID，不重启它们。等待两项Flash训练及测试均完成，再同时启动Moment的E0/E2；两项Moment均完成后启动QD的E0/E2。每张GPU同时只运行一个本实验任务。DETR启动前在对应GPU用真实Val fixture执行CUDA检查，检查通过后才训练。

用户明确要求终止其他实验，已终止相关训练、数据加载与调度器。终止清单见 `provenance/TERMINATED_OTHER_TRAINING_*.json`；已有文件保留，本队列不会重启它们。旧的 `code/controller.py` 是冻结的早期单卡调度文件，当前不运行；不要与新队列同时启动。

- 当前队列：[QUEUE_STATUS.json](QUEUE_STATUS.json)
- 固定队列计划：[QUEUE_PLAN.json](QUEUE_PLAN.json)
- 实时进度与成对结果：[RESULTS.md](RESULTS.md)、[RESULTS.json](RESULTS.json)
- 当前后台启动信息：[LAUNCH.json](LAUNCH.json)
- 诊断字段说明：[DIAGNOSTICS.md](DIAGNOSTICS.md)

查看汇总：

```bash
/home/guoxiangyu/miniconda3/envs/gmr/bin/python -B code/queue_status.py
```

后台队列日志为 `logs/dual_gpu_queue.log`；训练日志为 `logs/E0.log`、`logs/E2.log`、`logs/moment_E0.log` 等。Flash目录为 `runs/E0`、`runs/E2`，其他目录为 `runs/moment_E0`、`runs/moment_E2`、`runs/qd_E0`、`runs/qd_E2`。

## 数据与初始化

使用官方Soccer-GMR Standard的完整Train=4,138、Val=465、Test=1,036条。训练集正例2,136、负例2,002，含713条多事件正例。qid与视频在三部分间均不重叠。完整性、特征维数、有限值和SHA见 [DATA_AUDIT.json](DATA_AUDIT.json) 与 [FEATURE_MANIFEST.json](provenance/FEATURE_MANIFEST.json)。所有读取样本数必须与标注相等，禁止缺失特征导致静默删样本。

六项检索模型均从随机初始化训练，CLIP文本、CLIP视频、SlowFast使用已经下载的固定特征。每个骨干的E0/E2以同一seed初始化相同原生参数，随后仅E2替换存在性head；训练开始前重置随机数并使用同一shuffle generator种子。Flash seed2024，Moment/QD遵循原生seed2023。同一骨干成对比较，不把不同骨干的绝对成绩当作E2增益。

| 骨干 | E0存在性路径 | E2读取层 | E0参数 | E2参数 |
|---|---|---|---:|---:|
| FlashVTG | 原文本AdaPooling与视频mean pooling拼接→MLP | 文本一次+3层视频时序encoder | 10,600,985 | 12,644,121 |
| Moment-DETR | 10×256 Decoder Slot逐维max→MLP | 文本一次+2层联合encoder的视频部分 | 4,889,354 | 6,470,922 |
| QD-DETR | 10×256 Decoder Slot逐维max→MLP | 文本一次+T2V之后2层视频encoder | 7,651,622 | 9,233,190 |

E2是专用全局存在性Query，不是候选级Slot-aware方案B；没有Plurality、Slot匹配辅助损失或反事实配对监督。各骨干的定位结构和原生候选排序保持原有设计。共享编码器受到存在性梯度更新，因此训练后的定位结果仍可能变化。

## E2具体位置与实现

Flash实现见 [code/event_model.py](code/event_model.py)；Moment/QD接口见 [code/detr_event_model.py](code/detr_event_model.py)。共享EventHead包括：

1. 学习参数Query，形状1×1×256，正态初始化乘0.02。
2. 读取 `input_txt_proj` 之后的有效文本token。Flash不读取40个dummy token。
3. 按编码器顺序逐层读取有效视频token，每层独立CrossBlock。Flash不读取T2V或pyramid；QD不额外读取T2V层输出。Moment联合encoder的文本部分不作为这一阶段的视频memory。
4. MLP `256→256→1` 输出全局存在logit。DETR返回B维，Flash接口保留B×1再由原模型处理。

CrossBlock为256维、8-head attention，FFN为256→512→256、ReLU、dropout0.1，attention与FFN分别使用残差和LayerNorm。padding被mask，memory不detach。原生存在性调用点执行新head，原来的BCE和推理输出读取同一个logit。每次forward的上下文在finally清空。

QD的时序encoder输入含global token，Event Query只读取后面的有效视频token；不把global token当第一个视频位置。原模型在训练时还会用错配文本执行第二次saliency前向；存在性head执行后将context标记为consumed，后一次前向不会进入Event Query证据。该原生额外计算本身保留，但saliency权重按原训练入口设为0。

E2存在性损失不经过Decoder Slot；检查验证其梯度进入Event Query、文本/视频投影和共享编码器。定位损失仍正常更新Decoder与定位头。

## 训练与选模协议

| 设置 | Flash | Moment | QD |
|---|---:|---:|---:|
| train batch | 8 | 8 | 16 |
| eval batch | 1 | 4 | 8 |
| AdamW lr | 3e-5 | 5e-5 | 1e-4 |
| wd / clip norm | 1e-4 / 0.1 | 1e-4 / 0.1 | 1e-4 / 0.1 |
| 最多epoch | 400 | 400 | 200 |
| 连续不改善早停 | >80（81次） | ≥50 | >50（51次） |
| StepLR周期 / gamma | 400 / 0.5 | 400 / 0.1 | 200 / 0.1 |
| train loader workers | 0 | 4 | 4 |
| 原生窗口软门控阈值 | 0.5 | 0.3 | 0.3 |
| 额外NMS | normal 0.7 | 无 | 无 |

详细配置在 [configs/protocol.json](configs/protocol.json)、[configs/moment_protocol.json](configs/moment_protocol.json)、[configs/qd_protocol.json](configs/qd_protocol.json)。Moment/QD原生L1/GIoU/分类损失系数为10/1/4，保留辅助decoder监督，存在性BCE系数1。两者CLI均强制 `mr_only=True`、`lw_saliency=0`，本实验遵循实际入口而非Moment base YAML中未生效的saliency=1。

**全部按原生验证集 `MR-full-mAP` 严格提升选模和早停，平分保留较早epoch，正式初始best=0。** Flash使用NMS前mAP；Moment/QD原生入口没有额外NMS。选模不使用AUROC、G-mIoU、NMS后Flash成绩或Test。Flash最佳概率保留三位、DETR四位，沿用原生2秒边界后处理；QD还保留按视频duration裁剪边界。

冻结最佳checkpoint SHA、epoch和评价配置后，才在完整官方Test上推理，报告AUROC、完整logit AUROC、G-mIoU@1/@3/@5、mAP、mR、mR+、Rej-F1、N-acc等。G-mIoU拒识阈值固定0.4，另报告0.4/0.5/0.6/0.8的分类指标，不根据Test选择阈值。

每轮保存best/latest、优化器、StepLR、Python/NumPy/Torch/CUDA RNG、独立sampler generator及早停计数。支持epoch边界恢复；队列重启时按PID与starttime接管已有任务。任务异常时阻止后续阶段启动并记录failed，不把失败当完成。

## 与原工程的差异及审计

- 只在独立副本修正Flash/QD T2V层的batch/head mask展开：`.repeat(nhead,1,1)` 改为 `.repeat_interleave(nhead,dim=0)`。E0/E2使用同一修正，原工程没有修改。这是受控修正baseline，不冒称逐步复现发布训练。
- Flash原入口异常地把loss作为StepLR的epoch参数，本runner改为每epoch正常step，E0/E2相同；DETR本来就是每epochstep。
- Moment/QD独立副本中两个standalone evaluator的utils导入改为相对导入，避免多骨干并存时导错包；评价公式不变。
- 使用独立shuffle generator与可恢复checkpoint，未逐位复现原生随机数流。正式DETR训练用原生4个workers；Val诊断与评价用0个workers，batch不变。
- 正式环境 `/home/guoxiangyu/miniconda3/envs/gmr/bin/python`，PyTorch2.6.0+cu124、nncore0.4.7；不修改环境。与论文环境存在版本差异。

Flash正在运行的54个冻结文件逐一核对未变，manifest是 `provenance/FROZEN_SOURCE.json`。新增DETR与队列的独立manifest是 `provenance/DETR_FROZEN_SOURCE.json`。`provenance/OUTSIDE_BEFORE.json` 记录101个外部源码hash，启动和汇总时验证未改。运行中不要修改冻结文件或配置；需要变更方法时另建版本。

## 代码验证与结果边界

真实Val的无/单/多事件fixture已通过两种骨干的CPU检查：相同原生权重定位输出一致、混合与全负batch损失有限、梯度路径正确、batch/head维度正确、诊断hook不改变输出、自定义推理与原生入口预测一致。见 `tests/DETR_CHECKS_moment_cpu.json`、`tests/DETR_CHECKS_qd_cpu.json`。

四项一轮端到端流程测试在 `tests/detr_smoke_runs/`，验证保存、原生mAP选模、诊断、冻结、评价。`tests/DETR_RESUME_CHECKS_*.json` 验证最终epoch后恢复不会产生额外更新。所有smoke的train/val/test均复用三条Val fixture；数字不是正式科学实验结果。CUDA检查将在每个DETR任务获得GPU后执行，当前不占用Flash GPU开展额外训练。

本地已发布Flash checkpoint的只读复算位于 `reference/`。AUROC=74.00、Rej-F1@0.4=61.72与公开主表一致；G-mIoU@1=39.60（主表39.58）、mAP=25.65（主表24.62）。差异原因尚未隔离，不归功于E2，也不用于修改E2。详情见 [reference/COMPARISON.md](reference/COMPARISON.md)。

每个骨干当前只计划一个seed，需以同骨干完整Test的E2−E0判断本轮效果；不能据此宣称稳定提升或SOTA。
