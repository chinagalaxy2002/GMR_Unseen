不是“原始 Charades-STA 全量训练 → 我们的新 test 测试”作为主实验。那样会破坏我们最核心的 **unseen** 定义，因为你专门 hold out 的 `open/close` 和 16 个组合本来就在原始训练数据里；如果重新拿原始训练集训练，U+ / U− 就不再是真正的 downstream-training-unseen。

围绕核心问题，最干净的实验协议应该是：

> **只在 seen semantics 上学习 localization + existence，然后直接测试 unseen semantics 下，模型能否区分 U+ 和 U−。**

也就是：

\[
\text{Train: }S^+ + S^-
\quad\longrightarrow\quad
\text{Test: }S^+,S^-,U^+,U^-.
\]

我核过你指定的 GMR 官方实现，它本身支持自定义 `train_path/eval_path`，并且当 `use_exist_head=true` 时会保留 `relevant_windows=[]` 的 null samples，用这些样本训练 existence branch；Moment-DETR-GMR 和 FlashVTG-GMR 都可以直接沿这套方式适配你的 JSONL。关键不是换它的方法，而是换成我们这个 **seen-only train → semantic-novelty test** 的实验协议。

## 1. 主实验到底应该怎么训练

你现在正式 `train.jsonl` 的设计其实非常适合这个问题：

| Train | 数量 |
|---|---:|
| S+ | 6851 |
| S− | 1466 |
| U+ | **0** |
| U− | **0** |

这一点不要改。

模型训练阶段只看到：

\[
S^+:\text{seen + present}
\]

和

\[
S^-:\text{seen + absent}.
\]

也就是说模型在训练时能学会两个能力：

\[
\text{localization}
\]

以及

\[
\text{existence/rejection}.
\]

但它**完全没有看过 held-out semantics 对应的 U+/U−**。

测试阶段突然给它：

\[
U^+:\text{unseen + present}
\]

和

\[
U^-:\text{unseen + absent}.
\]

这时我们才有资格问：

> **模型学到的是“视频中是否存在”这个真正的视觉—语义判断，还是仅仅把训练阶段熟悉的 semantic distribution 当成 existence shortcut？**

所以这是第一原则：

> **正式 baseline 训练用你的 `train.jsonl`，而不是恢复到原始 Charades-STA training set。**

---

# 2. 但是 val 现在有一个非常重要的问题

你现在：

| Val | 数量 |
|---|---:|
| S+ | 694 |
| S− | 168 |
| U+ | 300 |
| U− | 356 |

如果你训练时拿整个 `val.jsonl` 做：

- early stopping；
- checkpoint selection；
- existence threshold selection；
- hyperparameter tuning；

那么严格意义上就发生了 **semantic development leakage**。

尤其你的 val/test 很可能共享同一组 held-out action/combination ontology，例如 `open/close`。模型权重虽然没有训练这些样本，但研究者已经利用 U+/U− performance 调过模型。

所以正式 protocol 建议把当前 val **逻辑上拆成两个视图**，不需要重新生成数据：

```text
val_seen:
    S+ + S-

val_unseen_probe:
    U+ + U-
```

**Primary setting：**

\[
\text{train}=S^++S^-
\]

\[
\text{model selection}=val(S^++S^-)
\]

\[
\text{threshold calibration}=val(S^++S^-)
\]

然后：

\[
test=S^+,S^-,U^+,U^-.
\]

`val_unseen_probe` 可以用于最终诊断，但在最终 hyperparameter 固定之前不要看它。

这个细节很重要，否则审稿人完全可以问：

> “你说 test semantics unseen，但你已经根据同一类 unseen semantics 的 validation performance 调过阈值和超参数了。”

---

# 3. 我建议四组 baseline，而不是只训练一个 GMR

这样才能真正回答核心问题，而不是只报一个模型的数字。

| Baseline | 训练数据 | 是否有 rejection head | 用途 |
|---|---|---:|---|
| **B0 Plain Moment-DETR / FlashVTG** | S+ only | 否 | 测纯 localization 的 semantic generalization |
| **B1 Moment-DETR-GMR** | S+ + S− | 是 | **主要 baseline** |
| **B2 FlashVTG-GMR** | S+ + S− | 是 | **主要 baseline，验证现象不是单一 backbone 导致** |
| **B3 Semantic-oracle** | seen + 部分 held-out semantics | 是 | 上界/诊断：证明失败来自 novelty，而非模型根本不会做任务 |

其中最重要的是 B1/B2。

### B0 为什么要留？

因为我们需要回答：

> U+ 定位失败，到底是 localizer 根本看不懂 unseen semantics，还是 existence head 错误地把它拒绝了？

Plain Moment-DETR/FlashVTG 没有 rejection branch。

如果：

```text
Plain model:
U+ localization = 还可以
```

但：

```text
GMR model:
U+ 被大量 reject
```

那么证据非常强：

> 问题不是 localization，而是 **novelty-induced over-refusal**。

否则如果 plain localizer 在 U+ 本来就彻底失败，那么不能把问题全部归咎于 rejection。

---

# 4. 同一个 GMR checkpoint 必须做两种 inference

这可能是整篇论文最重要的 diagnostic experiment。

GMR Adapter 会输出：

```text
pred_exist_score
```

并利用 existence score 去 suppress/gate temporal predictions。

所以对于 B1/B2，同一个 checkpoint 做：

### Raw localization

完全不使用 existence gate：

\[
\text{query}\rightarrow temporal\ windows.
\]

测试：

> 如果不允许模型拒绝，它对 U+ 到底能定位多好？

### Gated localization

启用 GMR 原有 existence gate：

\[
s_{\text{window}}'
=
s_{\text{window}}\cdot g(s_{\text{exist}}).
\]

测试：

> 加入 existence 判断之后，U+ 性能掉了多少？

如果出现：

\[
Loc_{\mathrm{raw}}(U+)=\text{不错}
\]

但：

\[
Loc_{\mathrm{gated}}(U+)\ll Loc_{\mathrm{raw}}(U+),
\]

同时 U− rejection 很高，那么你真正想找的 phenomenon 基本就被抓到了：

> **Existence estimator confuses semantic novelty with absence.**

这个比简单说“U+ R@0.5 比 S+ 低”强得多。

---

# 5. 整篇论文最核心的 evaluation 不是总 G-mIoU

GMR 原来的：

- AUROC；
- Rej-F1；
- Acc；
- mAP；
- mR；
- mIoU；
- G-mIoU；

全部保留。

但是你的主表一定要增加按四象限拆解。

真正核心的是下面几个量。

对于 U+：

\[
FRR_{U+}
=
P(\hat E=0\mid U+)
\]

也就是：

> **unseen-positive false refusal rate**

越低越好。

对于 U−：

\[
RR_{U-}
=
P(\hat E=0\mid U-)
\]

也就是：

> unseen-negative rejection rate。

越高越好。

然后定义一个非常直观的 over-refusal gap：

\[
\Delta_{\text{OR}}
=
FRR_{U+}-FRR_{S+}.
\]

如果：

```text
FRR(S+) = 8%
FRR(U+) = 35%
```

那么：

\[
\Delta_{\text{OR}}=27\%.
\]

这直接说明：

> semantics 一旦 unseen，模型在目标真实存在的情况下也明显更愿意拒绝。

这才是你论文要证明的 failure mode。

---

# 6. U+ / U− AUROC 应该单独算

不要只算整个 test AUROC。

至少要有：

\[
AUROC_{\text{seen}}
:
S+\;vs\;S-
\]

和

\[
AUROC_{\text{unseen}}
:
U+\;vs\;U-.
\]

那么可以直接比较：

\[
\Delta_{\text{AUROC}}
=
AUROC_{\text{seen}}
-
AUROC_{\text{unseen}}.
\]

这是 existence generalization gap。

模型如果：

```text
Seen AUROC    0.91
Unseen AUROC  0.63
```

论文的问题就非常清楚。

---

# 7. 535 对 matched U+/U− 应该成为你的“核心测试集”

你现在的数据里最有价值的可能不是完整 `test.jsonl`，而是：

```text
test_matched_u.jsonl
```

535 对，同视频、同 source positive 的 U+/U−。

这里可以定义一个特别干净的 pairwise metric：

\[
PairAcc
=
P
\left(
s_{\text{exist}}(U+)
>
s_{\text{exist}}(U-)
\right).
\]

直观解释：

> 对同一个视频、两个都属于 unseen 的相似 query，模型能不能把真正存在的那个打出更高 existence score？

随机：

\[
50\%.
\]

如果 GMR 只有 55%，说明：

> 它虽然可能在普通 rejection benchmark 上很好，但**一旦把 familiarity 控掉，真正判断 existence 的能力非常有限**。

如果改进模型做到 70%/75%，这个指标就非常有说服力。

而且你现在字符 n-gram 在这个 matched subset 的 pair ranking 是 `0.5421`。这个数字接近 0.5，但不要直接宣称“已经没有语言偏差”；建议后面给它做 paired bootstrap 或 permutation CI，因为 535 对下 0.5421 是否显著高于随机需要正式统计。

---

# 8. 你当前的 text-only diagnostic 决定了论文应该重点看 matched set

目前：

```text
overall text-only AUC = 0.7885
seen AUC              = 0.8889
unseen AUC            = 0.5678
matched U pair acc    = 0.5421
```

这里有一个必须正视的问题：

**整体 test，特别是 S+/S−，存在明显 language artifact。**

所以如果模型在整个 test 上获得非常高的 rejection：

> 不能直接证明它真的看视频了。

它可能部分利用：

> 原始人工正句 vs minimal-edit negative

的文本风格。

因此第一版论文中，核心 claim 最好建立在两层证据上：

```text
Full test
    → benchmark performance

Matched U+/U-
    → scientific diagnosis
```

也就是说：

> **完整 test 用来评价整体 open-world GMR；535 对 matched-U 用来验证“unseen ≠ absent”这个核心假设。**

这样会稳很多。

---

# 9. “原始 Charades-STA 训练”并不是没用，但只能作为辅助实验

你刚才问是不是：

> 原始数据训练 → 特定数据测试？

答案是：

**可以做，但不能作为 primary baseline。**

因为它会有 semantic leakage。

可以把它定义成一个：

### Closed-world / leaked-semantic reference

重新把：

```text
removed_train_holdouts.jsonl
```

里的 held-out positive 放回 training。

这样模型见过 `open/close` 和那 16 类 held-out composition。

再测试相同 test。

这个实验回答的是：

> 如果 semantic novelty 消失，这个模型的 existence 判断能恢复多少？

假设：

```text
Strict seen-only GMR:
U+ FRR = 36%

Semantic-oracle GMR:
same samples FRR = 12%
```

那么说明：

> 这个 24-point gap 确实来自 semantic novelty，而不是这些视频/query 本身特别难。

这会是一个很好的 **oracle diagnostic**。

但论文里必须明确叫：

> semantic-seen oracle / leakage reference

而不是正式 zero-shot baseline。

---

# 10. 还有一个不能做的事情：用标准 Charades checkpoint 初始化主 baseline

如果 Moment-DETR/FlashVTG checkpoint 已经在**完整原始 Charades-STA training set** fine-tune 过，那么：

> held-out semantics 已经被模型看过了。

这也破坏实验。

所以主 baseline 应该：

```text
generic pretrained feature extractor
    ↓
CLIP / SlowFast 等可以保留

task-specific localizer/GMR
    ↓
只在 semantic_existence_v1/train.jsonl 训练
```

也就是说：

**foundation pretraining 可以有。**

因为你定义的是：

> downstream-training-unseen，

不是：

> foundation-model-never-seen。

但不能使用已经在完整 Charades-STA 上 fine-tuned 的 localizer checkpoint 作为主实验初始化。

---

# 11. GMR 官方脚本不能原样直接套 Soccer 参数

这一点也提前提醒接终端的 agent。

我核过当前 repo：

Moment-DETR-GMR 和 FlashVTG-GMR 的训练接口确实支持自定义：

```text
train_path
eval_path
t_feat_dir
v_feat_dirs
```

所以数据格式没问题。

但官方 shell script 默认是 Soccer-GMR，例如 FlashVTG-GMR 默认：

```text
clip_length = 2
max_v_l = 75
v_feat_dim = 2816
CLIP + SlowFast
```

这些是 Soccer-GMR 配置，不应该机械复制到 Charades。

Agent 应该新建：

```text
charades_semantic_existence
```

配置。

原则是：

> **保留 GMR Adapter / loss / existence mechanism；Charades 的 video feature extraction、temporal sampling、clip length、max sequence length 尽量沿用相应 Charades baseline 的标准设置。**

否则最后可能把 dataset effect 和 feature/config mismatch 混在一起。

---

# 12. 我建议最终实验矩阵就定成这样

| Exp | Model | Train | Val for selection | Test | 目的 |
|---|---|---|---|---|---|
| E0 | Moment-DETR | S+ | S+ | S+, U+ | 纯 localization generalization |
| E1 | FlashVTG | S+ | S+ | S+, U+ | 第二个 localization backbone |
| **E2** | **Moment-DETR-GMR** | **S+ + S−** | **val S+ + S− only** | **四象限** | **核心实验** |
| **E3** | **FlashVTG-GMR** | **S+ + S−** | **val S+ + S− only** | **四象限** | **核心实验 / backbone robustness** |
| E4 | E2 checkpoint | 同 E2 | 同 E2 | U+，关闭 vs 开启 existence gate | 判断 over-refusal 来自哪里 |
| E5 | E3 checkpoint | 同 E3 | 同 E3 | U+，关闭 vs 开启 existence gate | 同上 |
| E6 | GMR semantic-seen oracle | 加回 held-out semantics | seen validation | 同一 test | novelty upper bound |
| E7 | text-only | train text | seen val | full + matched-U | 检查语言 shortcut |

其中真正应该先跑的是：

> **E2、E3、E4、E5。**

B0/E0/E1 做控制。

Oracle 和 text-only 做解释。

---

# 13. 每个 baseline 最终至少输出这样一张核心表

以后论文主表甚至可以长这样：

| Model | S+ Loc ↑ | S− Reject ↑ | U+ Loc ↑ | U+ FRR ↓ | U− Reject ↑ | U-AUROC ↑ | Matched Pair ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Moment-DETR | | | | | | | |
| Moment-DETR-GMR | | | | | | | |
| FlashVTG | | | | | | | |
| FlashVTG-GMR | | | | | | | |

然后再加一个 diagnostic：

| Model | Raw U+ Loc | Gated U+ Loc | Δ Gate | S+ FRR | U+ FRR | Δ Over-refusal |
|---|---:|---:|---:|---:|---:|---:|
| Moment-DETR-GMR | | | | | | |
| FlashVTG-GMR | | | | | | |

如果这个表出现：

> **raw U+ localization 尚可，但 gated U+ 明显降低；同时 U− rejection 很好。**

那就是你现在整个研究最想证明的结果。

---

## 14. 所以现在最优先做什么

不要先做新模型。

先用当前数据完整验证下面这个链：

\[
\boxed{
\text{train only on }S^+,S^-
}
\]

\[
\Downarrow
\]

\[
\boxed{
\text{standard GMR learns seen existence}
}
\]

\[
\Downarrow
\]

\[
\boxed{
\text{test on }U^+,U^-
}
\]

\[
\Downarrow
\]

如果发现：

\[
RR_{U-}\uparrow
\]

但同时：

\[
FRR_{U+}\uparrow
\]

尤其 matched-U 中：

\[
s(U+)\not\gg s(U-),
\]

那么才有证据支持：

> **现有 GMR 的 existence estimator 没有真正 disentangle semantic novelty from target absence。**

这时下一步新模型才有明确目标：

> **不是把 refusal 做得更强，而是在保持 U− rejection 的同时，显著降低 U+ false refusal。**

另外有一个发布文档的小问题最好现在修掉：`review_report.json` 写的是 U+ = **884**，而最终 `test.jsonl` 是 U+ = **881**；你前面解释这是 3 条 `dress|front` 解析错误被发布前隔离，所以逻辑上能对上，但正式统计最好统一注明 **884 reviewed → 3 QC-excluded → 881 released**，否则以后容易被当成数据版本不一致。
