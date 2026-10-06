# 项目总交接：Semantic Novelty × Event Existence

更新：2026-09-29。**清空对话上下文后先读本文件即可恢复项目全貌。**项目根目录为 `/home/guoxiangyu/paper/Openword/generalized-moment-retrieval`。文中的代码路径从仓库根目录起算，Markdown 链接可直接打开。本文描述当前已完成状态，旧交接和方案中的「待运行」「尚未提交」等文字只是历史快照。

## 一分钟了解项目

- **研究问题：**广义视频时刻检索模型只在下游训练见过的语义上学习后，能否区分「视频中真的没有该事件」与「事件存在，但查询动作或动作–物体组合在下游训练中未见」？这里的未见只针对任务训练，不声称 CLIP、SlowFast 等预训练从未接触这些概念。
- **数据与方法：**以 Charades-STA 的真实正例及时间窗为基础，构建 S+（已见且存在）、S−（已见且缺席）、U+（未见且存在）、U−（未见且缺席）四象限；训练只用 S+/S−，checkpoint 和存在阈值只用 seen validation，最后在四象限 test 评估。三个 backbone 是 Moment-DETR-GMR、QD-DETR-GMR、FlashVTG-GMR。本仓库当前交付的是 benchmark、模型适配和诊断实验，尚无新模型。
- **完成状态：**阶段 1 的 A0/v1、E0–E7 和补充 QD-DETR 对照均完成。阶段 2 的 A1、A2_alt、A3、C1、C2_alt 五个冻结划分均发布并校验；三个模型在每组的训练及测试全部完成，共 **15 次训练和 15 份测试评测**。当前没有等待续跑的阶段 2 任务。
- **核心发现：**阶段 2 的 15 次运行中，seen AUROC 均高于 unseen AUROC，差值为 **0.128–0.309**。错误形态不统一：A2_alt 几乎全部接受未见查询，C2_alt 的 Moment 则几乎全部拒绝。结论限于同一个 Charades 视频域、每配置单种子。

## 两阶段设计与实验结果

| 阶段/组 | 保留语义 | Test U+ / U− | 同视频 U+/U− 配对 | 状态 |
| --- | --- | ---: | ---: | --- |
| A0 / v1 | 完整动作 `open/close`，另有 16 个动作–物体组合 | 881 / 947 | 535；只覆盖动作级 | 固定参照，E0–E7 完成 |
| A1 | 动作 `put/take` | 465 / 1,119 | 312 | 三模型完成 |
| A2_alt | 动作 `drink/pour` | 168 / 312 | 79 | 三模型完成 |
| A3 | 动作 `run/walk` | 192 / 594 | 129 | 三模型完成 |
| C1 | 组合 `sit|bed/chair/couch` | 162 / 270 | 144 | 三模型完成 |
| C2_alt | 组合 `open/close|box/cabinet` | 115 / 254 | 33 | 三模型完成 |

阶段 1 的严格 GMR、定位-only、raw/硬拒绝定位、semantic-seen reference 和 text-only 对照均已有结果；seed 3407 的严格 GMR seen/unseen AUROC 分别是 Moment **0.8665/0.5701**、QD **0.8713/0.5854**、Flash **0.8574/0.5588**。A0 组合级缺少同视频配对，因此阶段 2 特别要求组合级配对覆盖。A2、C2 的初选候选因配对不足，在任何新模型结果出现前按冻结规则换成 A2_alt、C2_alt。

阶段 2 沿用 seed 3407、强制 100 epoch、关闭早停，五组分别从头训练。按组等权的 seen−unseen AUROC 差：动作轴 Moment/QD/Flash 为 **0.2365/0.2649/0.2289**；组合轴为 **0.2031/0.1856/0.1744**。同一测试 qid 在一个划分为 U、另一个划分为 S 的比较已完成：动作轴 1,041 个互异 qid、2,082 个有向比较；组合轴 801 个有向比较。它固定了测试视频和句子，但不同划分的训练 S+ 分布及模型校准也变了，**不是纯语义暴露的因果估计**。逐组 15 行 AUROC、配对、拒绝和定位结果在[阶段 2 完整报告](reports/semantic_existence_multisplit_results.md)，精确数值在[机器可读指标](semantic_existence_v2_metrics/)。

## 数据从哪里来、如何构建

正式可共享标注在仓库的 [`data/release/semantic_existence_v1/`](../data/release/semantic_existence_v1/) 与 [`data/release/semantic_existence_v2/`](../data/release/semantic_existence_v2/)；本机原始数据和构建工作区在 `/home/guoxiangyu/paper/Openword/data/`。每个 v2 组的 `train.jsonl`、`val.jsonl`、`test.jsonl`、`matched_u_pairs.jsonl`、`semantic_inventory.json`、`statistics.json`、`review_report.json`、`split_spec_provenance.json`、`manifest.json` 等已发布。仓库不含原视频、CLIP/SlowFast 特征、checkpoint、逐查询预测和构建中间文件。

构建顺序：从原 Charades-STA 正例保留查询和人工时间窗 → 统计 123 个动作与 1,221 个组合 → 按冻结规则选取语义及质量门槛 → 由同视频正例修改动作或物体生成负例候选，并用其他正例、Charades、Action Genome 排除已知冲突 → 对精确候选批次作人工核对 → 各动作组共享一批 1,500 条训练 S−，各组合组共享另一批 1,500 条 → 校验配对、语义隔离、视频不重叠及 SHA-256 → 打包发布。冻结选择规则、候选表、spec、初选失败记录和复核来源在 [`selection/`](../data/release/semantic_existence_v2/selection/)；具体实现见[阶段 2 事前方案](20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md)和[数据构建说明](reports/semantic_existence_dataset.md)。

**复核来源的准确表述：**数据负责人对哈希绑定的整批 4,491 条新负例及 156 条解析 QC 样本确认通过；2,485 条与 v1 完全一致的负例沿用原批次来源。没有逐 qid 决定表或双人视频审核记录，不能写成逐条双人复核。已知 `dress|front` 解析错误在发布前隔离。五组发布包均通过 `scripts/validate_release.py`，视频切分没有交集，配对与 held-out 约束、每组 10 个发布文件哈希均通过。

## 结果如何解释

主要观察量是 seen/unseen 存在 AUROC、同视频同来源 U+/U− 的 PairAcc、U+ 错误拒绝率与 U− 拒绝率、以及同一 checkpoint 的 U+ 定位 raw→seen 阈值硬拒绝 R@1@IoU 0.5。**诊断用硬拒绝**和官方 GMR 评测器使用的 gate/阈值不同，不能混作同一指标。完整报告还给出 text-only 对照、查询分布和按测试视频聚类的 2,000 次 bootstrap 95% 区间；区间不反映训练种子的变化。

可写成「在多个预先冻结的 Charades-STA 未见动作与未见组合划分中，三种模型的存在区分能力均有 seen→unseen 退化」。不能写成「所有开放视频环境普遍失败」。五组共享同一视频域；每配置一个训练种子；C1、C2_alt 的 U+ 对象分别只涉及三个、两个物体；C1/C2_alt 的 text-only 配对准确率分别为 0.625/0.818，查询措辞可能贡献配对信号。阶段 1 的 E6 有意把 held-out 训练正例加回，只是 semantic-seen 参考，不是严格 unseen baseline。

## 文件导航：哪些仍有用

| 位置 | 作用与阅读时机 |
| --- | --- |
| 本文件 | **唯一的上下文恢复入口**；先读这里，再按问题追溯证据。 |
| [阶段 1 当前工作交接](20260928_1_CURRENT_WORK_HANDOFF.md) | A0/v1、E0–E7 完成状态及本机路径；其中旧时间点的 Git/待办状态不要当作当前状态。 |
| [阶段 2 实验方案](20260928_2_PHASE2_MULTI_SPLIT_EXPERIMENT_PLAN.md) | 事前规则、筛选门槛、替代组决策和方法依据，写论文方法时使用；其中候选阶段待办为历史记录。 |
| [阶段 2 当前工作交接](20260929_PHASE2_CURRENT_WORK_HANDOFF.md) | 五组训练、测试、产物路径和 15 行结果表；查具体运行时使用。 |
| [早期主实验交接](SEMANTIC_EXISTENCE_HANDOFF.md) | 首轮短训练、checkpoint 哈希及故障排查的历史记录；不是当前状态入口。 |
| [`reports/`](reports/) | **仍有用的详细证据：**v1 数据管线、100-epoch 严格 GMR、定位-only/E4–E5、E6、动作轴同样本对照、阶段 2 五组完整结果。主结论以阶段 2 完整报告和 JSON 为准。 |
| [`semantic_existence_v2_metrics/`](semantic_existence_v2_metrics/) | 15 组诊断/官方指标、bootstrap、同样本比较、text-only 与查询分布；数值复核的权威来源。 |
| [`archive/`](archive/) | A1 单组临时报告与按时间追加的旧进度记录；已被完整报告取代，仅供追溯，不作为当前结论引用。 |
| `index.html`、`script.js`、`styles.css` | 上游 GMR 项目的静态网页资源，不是本研究的数据或结果文档。 |

`reports/` 中各文件的用途：[数据构建](reports/semantic_existence_dataset.md)用于追溯 v1 来源和依赖；[v1 严格 GMR](reports/semantic_existence_100ep_results.md)、[定位对照](reports/semantic_existence_localization_controls.md)、[E6 参考](reports/semantic_existence_semantic_seen_reference_results.md)保留阶段 1 的不同实验细节；[动作轴结果](reports/semantic_existence_action_multisplit_results.md)详述 A1–A3 同样本对照；[阶段 2 完整结果](reports/semantic_existence_multisplit_results.md)是五组正式结果的文字主报告。`archive/` 中的 [A1 临时结果](archive/semantic_existence_A1_results.md)与[阶段 1 进度快照](archive/semantic_existence_experiment_status.md)保留原貌供审计，其中过时的状态语句不适用于当前工作。

## 恢复时从哪里继续

本机训练结果与日志在 `results/semantic_existence/`，阶段 2 在 `results/semantic_existence/multi_split_v2/<split>/<moment|qd|flash>/`；文本特征在 `features/semantic_existence_v2/<split>/`，视频特征在 `/home/guoxiangyu/paper/新建文件夹/charades/{vid_clip,vid_slowfast}/`。这些路径通常被 Git 忽略；在新机器上仍可用发布标注和指标理解研究结果，但复现训练必须另备视频、特征和环境。排队脚本 `scripts/queue_semantic_multisplit_training.sh` 已记录 `complete_all`；没有需要重启的队列。

只读核对发布包：

```bash
python scripts/validate_release.py
for split in A1 A2_alt A3 C1 C2_alt; do
  python scripts/validate_release.py --release "data/release/semantic_existence_v2/$split"
done
cat results/semantic_existence/multi_split_v2/queue_status.txt
```

下一步若写论文，应按动作轴、组合轴分别报告逐组结果、配对覆盖、同样本比较、text-only 对照与局限；如果要扩展结论，先另行设计多种子或新视频域实验，不改写现有冻结发布包。当前没有尚未完成的既定训练或测试。GitHub 发布目标为 [`chinagalaxy2002/GMR_Unseen`](https://github.com/chinagalaxy2002/GMR_Unseen) 的 `main`；`origin` 是上游 GMR 仓库，提交前须核对远端。

## 2026-10-06：DDV 实验与独立审计补充

最新入口为 [DDV 实验整理](reports/ddv_experiment_20261006.md)与[独立审计](../experiments/agy_test/ddv_audit_20261006/DDV_AUDIT_REPORT.md)。DDV 在五划分单种子上达到 Unseen 0.6134、Gap 0.1550；相对三骨干融合控制存在 Unseen 增益及 Seen 取舍。A1 Gap 扩大，阈值迁移与方向推理尚待解决。正式数字使用[修正汇总](../experiments/agy_test/decomposed_directional_verifier/benchmark_audited.json)，旧 DDV 原报告中有 G-mIoU、PairAcc 与表述问题。恢复上下文时先读此最新入口，再追溯旧阶段报告。

本次代码、报告及指标发布到同一 GitHub main；检查点、特征和逐查询预测继续保留本地。当前下一步为容量/模态/gate 对照、Seen-only 运行点校准及新语义多种子验证。
