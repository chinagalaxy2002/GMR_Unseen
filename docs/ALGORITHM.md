# 算法：DEC-Power-CDF + Seen Guard

![Algorithm overview](../figures/algorithm_overview.svg)

图的上层是只读取训练集和 Seen 验证集的校准；下层是冻结后的推理。推理不读取查询的 Seen/Unseen 分区、存在性标签、语义图或留出类别名单。

## 输入与记号

- `d`：当前骨干历史存在性分数；`E`：原 DEC 固定路由的证据。
- `F_d, F_E`：训练参考中点经验 CDF；`x=F_d(d)`，`y=F_E(E)`。
- `s_D=x^0.65 y^0.85`：原 DEC 分数。
- `I`：训练正例查询经固定解析器得到的动作—物体组合表。
- `G`：G-mIoU；`F`：Rej-F1；`FRR`：正例误拒率。

## 校准伪代码

```text
for each split and backbone:
    build I from parsed positive TRAIN queries
    fit F_d and F_E on TRAIN samples
    evaluate Baseline and DEC on SEEN VALIDATION
    choose tau_D by original 91-percentile Seen-BA rule

    for alpha in {0, 0.025, ..., 1}:
        f_alpha = (1-alpha) * x^0.65 + alpha * s_D
        choose tau_alpha by 91-percentile Seen-BA rule
        main_guard = AUC_alpha >= AUC_baseline
                     and G_alpha >= max(G_baseline, G_DEC)
                     and F_alpha >= max(F_baseline, F_DEC)

    prefer candidates passing main_guard
    otherwise prefer candidates passing AUC protection alone
    choose the candidate closest to s_D by validation mean squared score distance

    if main_guard passes and FRR_alpha <= FRR_DEC:
        freeze FUSION and tau_alpha
    else if main_guard fails:
        freeze DEC decisions; rank raw d inside accepted/rejected groups
        require its Seen-validation AUC >= Baseline
    else:
        use raw d
        choose the maximum-BA threshold among the same 91 candidates subject to
            G >= G_DEC, F >= F_DEC, FRR <= FRR_DEC - 5 percentage points
        freeze this constrained BASELINE threshold

    freeze positive train-score scales and all choices
```

候选或回退不满足条件时校准报错；这套发布算法不承诺对任意新数据都能找到可行解。当前触发模式分别为 13 个融合、C1/QD 的 FRR 约束、C2_alt/QD 的决策保留。

## 推理伪代码

```text
pair = fixed_text_parser(Q)
s_D = F_d(d)^0.65 * F_E(E)^0.85

if pair is missing or pair not in I:
    S = (s_D - tau_D) / sigma_D
else:
    apply the offline-frozen covered-query policy:
        FUSION: S = (f_alpha - tau_alpha) / sigma_alpha
        FRR-constrained BASELINE: S = (d - tau_R) / sigma_d
        fixed DEC decisions:
            A_D = 1[s_D >= tau_D]
            S = (2*A_D - 1) + 0.25 + atan(d)/(2*pi)

accept iff S >= 0
if accepted: return the original native localization window
else: return an empty prediction
```

决策保留分支中 `0.25+atan(d)/(2*pi)` 严格递增且属于 `(0,0.5)`，因此不会跨越 0；原 DEC 接受/拒绝逐样本不变。未覆盖分支是正比例仿射变换，也保留原 DEC 排序和阈值决策。

## 图文件

- [SVG](../figures/algorithm_overview.svg)：文本可编辑的矢量图。
- [PDF](../figures/algorithm_overview.pdf)：论文插图。
- [PNG](../figures/algorithm_overview.png)：预览。
- [绘图源码](../figures/draw_algorithm.py)：重新生成三种格式。
- [自包含图注与设计说明](../figures/CAPTION.md)。

当前组合路由恰好对应这个基准的 Seen/Unseen 分区，因为解析器沿用了数据构建规则。这是方法的实际适用边界；不能把图中的“训练覆盖”当成独立验证过的通用 OOD 检测器。
