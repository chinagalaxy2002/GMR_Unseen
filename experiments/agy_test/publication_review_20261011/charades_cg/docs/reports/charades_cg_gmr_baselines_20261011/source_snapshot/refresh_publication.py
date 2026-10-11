#!/usr/bin/env python3
"""Refresh only the C3_CG publication overlay from completed v2 inference.

The prior overlay is archived before replacement. Balanced v3 is read-only.
No training, calibration selection, or test-time tuning occurs here.
"""
import csv
import hashlib
import importlib.util
import inspect
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REVIEW = REPO / "experiments/agy_test/publication_review_20261011"
RELEASE_REL = "data/release/semantic_existence_v3_release/extensions/charades_cg_gmr_v2"
REPORT_REL = "docs/reports/charades_cg_gmr_baselines_20261011"
ASSET_REL = "assets/charades_cg_gmr"
BACKBONES = ("moment", "qd", "flash")
NAMES = {"moment": "Moment-DETR-GMR", "qd": "QD-DETR-GMR", "flash": "FlashVTG-GMR"}
SHORT = {"moment": "Moment-DETR", "qd": "QD-DETR", "flash": "FlashVTG"}
METRICS = (("auc", "AUROC"), ("rej_f1", "Rej-F1"), ("gmiou1", "G-mIoU@1"))
COLORS = ("#0072B2", "#D55E00", "#009E73")
sys.dont_write_bytecode = True


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def file_state(folder):
    return {str(p.relative_to(folder)): {"bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(folder.rglob("*")) if p.is_file()}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def table(headers, data):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(map(str, row)) + " |" for row in data])


def fmt(value, metric="pct"):
    return f"{value:.4f}" if metric == "AUROC" else f"{value:.2f}%"


def ci(row, prefix, metric="pct", signed=False):
    lo, hi = row[prefix + "_ci_low"], row[prefix + "_ci_high"]
    if signed:
        return f"[{lo:+.2f}, {hi:+.2f}]"
    digits = 4 if metric == "AUROC" else 2
    return f"[{lo:.{digits}f}, {hi:.{digits}f}]"


def figure(fig, output, name):
    output.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(output / (name + "." + extension), dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_performance(full, output):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    for ax, (key, title) in zip(axes, METRICS):
        rr = [next(r for r in full if r["backbone"] == bb and r["metric"] == title) for bb in BACKBONES]
        for offset, prefix, color, hatch in ((-.18, "seen", "#0072B2", ""), (.18, "unseen", "#E69F00", "//")):
            values = np.array([r[prefix] for r in rr])
            lo, hi = [np.array([r[prefix + suffix] for r in rr]) for suffix in ("_ci_low", "_ci_high")]
            x = np.arange(3) + offset
            ax.bar(x, values, .33, color=color, edgecolor="white", hatch=hatch, label=prefix.capitalize())
            ax.errorbar(x, values, yerr=[np.maximum(0, values - lo), np.maximum(0, hi - values)],
                        fmt="none", ecolor="#333333", capsize=3, lw=1)
            for xx, value, top in zip(x, values, hi):
                ax.text(xx, top + (.017 if key == "auc" else 1.7), f"{value:.3f}" if key == "auc" else f"{value:.1f}", ha="center", fontsize=8.5)
        ax.set(xticks=np.arange(3), xticklabels=[SHORT[b] for b in BACKBONES],
               ylim=(0, 1 if key == "auc" else 100), title=title, ylabel="Score (0–1)" if key == "auc" else "Score (%)")
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
    axes[0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("Charades-CG-GMR v2: C3_CG Seen / Unseen test", fontsize=14)
    fig.text(.5, -.01, "95% video-cluster bootstrap CI; 2,000 joint draws; seed 3407.\n"
             "S+ = S− = 2,684; U+ = U− = 2,990; checkpoints and Seen-validation thresholds frozen.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .94))
    figure(fig, output, "seen_unseen_performance")


def plot_gaps(full, output):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
    for ax, (_, title) in zip(axes, METRICS):
        for i, bb in enumerate(BACKBONES):
            r = next(r for r in full if r["backbone"] == bb and r["metric"] == title)
            ax.errorbar(r["gap_pp"], i,
                        xerr=[[max(0, r["gap_pp"] - r["gap_pp_ci_low"])], [max(0, r["gap_pp_ci_high"] - r["gap_pp"])]],
                        marker=("o", "s", "^")[i], color=COLORS[i], capsize=4, lw=1.4)
            ax.annotate(f'{r["gap_pp"]:+.2f}', (r["gap_pp"], i), xytext=(0, -16), textcoords="offset points", ha="center", fontsize=9)
        ax.axvline(0, color="#555555", lw=1, linestyle="--")
        ax.set(title=title, xlabel="Seen − Unseen (pp)", yticks=range(3), ylim=(2.5, -.6))
        ax.grid(axis="x", alpha=.18)
        ax.margins(x=.22)
    axes[0].set_yticklabels([SHORT[b] for b in BACKBONES])
    fig.suptitle("Charades-CG-GMR v2: signed generalization gaps", fontsize=14)
    fig.text(.5, -.02, "95% CI from joint video-cluster draws, including videos shared by Seen and Unseen.\n"
             "Negative gaps denote higher Unseen point estimates; class proportions affect Rej-F1 and G-mIoU.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, .93))
    figure(fig, output, "generalization_gaps")


def plot_counts(counts, output):
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    splits = ("train", "val_seen", "test")
    left = np.zeros(3)
    for part, color, hatch in zip(("S+", "S-", "U+", "U-"), ("#0072B2", "#56B4E9", "#D55E00", "#E69F00"), ("", "//", "", "//")):
        values = np.array([counts["C3_CG"][s].get(part, 0) for s in splits])
        ax.barh(np.arange(3), values, left=left, color=color, edgecolor="white", hatch=hatch, label=part)
        for y, x, n in zip(range(3), left, values):
            if n:
                ax.text(x + n / 2, y, str(n), ha="center", va="center", fontsize=9, color="white" if part in ("S+", "U+") else "black")
        left += values
    ax.set(yticks=range(3), yticklabels=splits, xlabel="Video–query pairs", title="Charades-CG-GMR v2: all four test quadrants")
    ax.invert_yaxis()
    ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.16))
    fig.text(.5, -.035, "Train / calibration: S+/S− only. Test: official Test-Trivial (Seen) + Novel-Composition (Unseen).\n"
             "Both test subsets have a 1:1 positive / constructed-negative ratio.", ha="center", fontsize=9)
    fig.tight_layout()
    figure(fig, output, "dataset_composition")


def plot_pipeline(output):
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.set(xlim=(0, 11), ylim=(0, 3.5))
    ax.axis("off")
    steps = [("官方 Charades-CG", "Train + Test-Trivial\n+ Novel-Composition"),
             ("机械清理与划分", "剔除 2,119 条异常窗口\n训练 / 验证保持不变"),
             ("联合 Test 换视频", "同视频全部 S/U 正描述\nCLIP 最低 50% 内采样"),
             ("同句正负配对", "Seen / Unseen 各自 1:1\n负例是构造标签")]
    for i, (title, body) in enumerate(steps):
        x = .15 + 2.75 * i
        ax.add_patch(FancyBboxPatch((x, 1.1), 2.35, 1.6, boxstyle="round,pad=.08", facecolor="#EEF5FA", edgecolor="#0072B2", lw=1.2))
        ax.text(x + 1.175, 2.3, title, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + 1.175, 1.65, body, ha="center", va="center", fontsize=9)
        if i < 3:
            ax.annotate("", xy=(x + 2.67, 1.9), xytext=(x + 2.43, 1.9), arrowprops={"arrowstyle": "->", "lw": 1.4})
    ax.text(5.5, 3.2, "Charades-CG-GMR v2：补回 Seen 测试与联合重配负例", ha="center", fontsize=14)
    ax.text(5.5, .5, "复用原 checkpoint 与 Seen-validation 阈值 → v2 重新推理 → 联合视频聚类 bootstrap", ha="center", fontsize=10.5)
    ax.text(5.5, .1, "Novel-Word 不进入主评估；低文本相似度不能确认实际视频缺席。", ha="center", fontsize=10, color="#8B3B13")
    figure(fig, output, "construction_pipeline")


def write_portable_plotter(package):
    header = '''#!/usr/bin/env python3
"""Redraw v2 figures from this overlay's frozen JSON, without model weights."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for path in Path("/usr/share/fonts/opentype/noto").glob("NotoSansCJK-*.ttc"):
    font_manager.fontManager.addfont(str(path))
families = sorted({f.name for f in font_manager.fontManager.ttflist if "CJK" in f.name})
plt.rcParams.update({"font.family": ["DejaVu Sans"] + families[:1], "font.size": 10,
                     "svg.fonttype": "none", "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})
'''
    constants = "\n".join(f"{name} = {globals()[name]!r}" for name in ("BACKBONES", "SHORT", "METRICS", "COLORS"))
    functions = "\n\n".join(inspect.getsource(f) for f in (figure, plot_performance, plot_gaps, plot_counts, plot_pipeline))
    run = f'''
if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    report = root / {REPORT_REL!r}
    output = Path(__file__).resolve().parent
    full = json.loads((report / "ALL_METRICS_WITH_CI.json").read_text())
    counts = json.loads((report / "LOCAL_VERIFICATION.json").read_text())["dataset_counts"]
    plot_performance(full, output)
    plot_gaps(full, output)
    plot_counts(counts, output)
    plot_pipeline(output)
    print("Redrawn 4 v2 figures as SVG/PDF/PNG")
'''
    (package / ASSET_REL / "render_figures.py").write_text(header + constants + "\n\n" + functions + run)


def write_report(builder, package, records, full, counts, status):
    report = package / REPORT_REL
    lookup = {r["backbone"]: r for r in records}
    stats = read(REPO / RELEASE_REL / "statistics.json")
    source_counts = stats["clean_positive_rows_by_source"]
    data_audit = read(HERE / "DATA_AUDIT.json")
    assert data_audit["encoded_new_texts"] == 161
    assert data_audit["unique_texts"] - data_audit["encoded_new_texts"] == 7734
    test_rows = builder.rows(REPO / RELEASE_REL / "splits/C3_CG/test.jsonl")
    positive_overlap = len({r["vid"] for r in test_rows if r["partition"] == "S+"} &
                           {r["vid"] for r in test_rows if r["partition"] == "U+"})
    target_overlap = len({r["vid"] for r in test_rows if r["partition"].startswith("S")} &
                         {r["vid"] for r in test_rows if r["partition"].startswith("U")})
    assert positive_overlap == 1087 and target_overlap == 2084
    quad_rows = [[split, *[counts["C3_CG"][split].get(p, 0) for p in ("S+", "S-", "U+", "U-")],
                  sum(counts["C3_CG"][split].values()), stats["video_counts"]["val" if split == "val_seen" else split]]
                 for split in ("train", "val_seen", "test")]
    examples = []
    for part in ("S+", "S-", "U+", "U-"):
        pool = [r for r in test_rows if r["partition"] == part]
        sample = min(pool, key=lambda r: (abs(len(r["query"]) - 65), str(r["qid"])))
        examples.append(sample)
    dump(report / "QUERY_EXAMPLES.json", examples)
    ci_rows = [[NAMES[r["backbone"]], r["metric"], fmt(r["seen"], r["metric"]), ci(r, "seen", r["metric"]),
                fmt(r["unseen"], r["metric"]), ci(r, "unseen", r["metric"]), f'{r["gap_pp"]:+.2f}', ci(r, "gap_pp", signed=True)] for r in full]
    full_table = table(["Backbone", "指标", "Seen", "Seen 95% CI", "Unseen", "Unseen 95% CI", "Gap（pp）", "Gap 95% CI（pp）"], ci_rows)
    overall = []
    abs_ci = read(HERE / "evaluation/bootstrap.json")
    for bb in BACKBONES:
        for key, title in (("rej_f1", "Overall Rej-F1"), ("rr", "Overall RR"), ("s_frr", "S+ FRR"), ("u_frr", "U+ FRR"), ("gmiou1", "Overall G-mIoU@1")):
            limits = abs_ci[bb]["absolute"][key]
            overall.append({"split": "C3_CG", "backbone": bb, "metric": title, "unit": "%",
                            "value": lookup[bb][key], "ci_low": limits[0], "ci_high": limits[1]})
    dump(report / "OVERALL_METRICS_WITH_CI.json", overall)
    builder.write_csv(report / "OVERALL_METRICS_WITH_CI.csv", overall)
    overall_table = table(["Backbone", "指标", "点估计", "95% CI"],
                          [[NAMES[r["backbone"]], r["metric"], fmt(r["value"]), f'[{r["ci_low"]:.2f}, {r["ci_high"]:.2f}]'] for r in overall])
    (report / "OVERALL_METRICS_WITH_CI.md").write_text("# 整体拒绝、正例误拒和端到端定位\n\n" + overall_table + "\n")
    protocol = builder.PROTOCOL_TEXT.replace("## 4. Baseline 怎样训练和评估？", "## 4. Baseline 怎样训练和重新评估？")
    protocol = protocol.replace("| 训练 | 每个设置从头训练，无 warm start；", "| 原训练 | 本次复用原设置的冻结 checkpoint，未重新训练；原设置从头训练，无 warm start；")
    protocol = protocol.replace("| Bootstrap | 2,000 次视频聚类重采样，seed 3407；同视频的查询整体抽样；", "| Bootstrap | 2,000 次视频聚类重采样，seed 3407；联合 Test 的全部视频共享抽样，Seen/Unseen 共享视频的查询整体抽样；")
    protocol += "\n本次数据修订未改变 Train 与 Seen validation，两者文件与 v1 逐字节一致。复用原最佳 checkpoint、原 Seen-validation 原生预测和冻结阈值；仅对 v2 全部测试行重新推理，未利用测试结果调参。测试负例的目标视频也按联合候选池重采样，所以不得将 v1 的旧 Unseen 分数拼接为 v2 结果。\n\n"
    statements = []
    for bb in BACKBONES:
        parts = []
        for _, title in METRICS:
            r = next(r for r in full if r["backbone"] == bb and r["metric"] == title)
            evidence = "区间全部高于 0" if r["gap_pp_ci_low"] > 0 else "区间全部低于 0" if r["gap_pp_ci_high"] < 0 else "区间跨越或包含 0"
            parts.append(f'{title} Gap 为 {r["gap_pp"]:+.2f} pp（95% CI {ci(r, "gap_pp", signed=True)}，{evidence}）')
        statements.append(NAMES[bb] + "：" + "；".join(parts) + "。")
    lines = ["# Charades-CG-GMR v2 C3_CG：数据制作与 Seen→Unseen 退化测评", "",
             f"更新日期：2026-10-11。数据来自 [`charades_cg_gmr_v2`]({RELEASE_REL}/README.md)，重新评估来自 `charades_cg_v2_evaluation_20261011`。**3/3 个 backbone 全部完成，失败 0 个**。完成记录：`{status.get('finished', status.get('updated_at', '见完成状态文件'))}`。本报告覆盖此前仅有 Unseen Test 的 v1 本地审阅稿；旧报告已完整归档。当前仍为本地审阅包，未上传。", "",
             "## 1. 这套数据想测什么？", "",
             "在固定下游训练数据与模型后，同时观察官方 Test-Trivial（Seen）和 Novel-Composition（Unseen）查询的事件存在判断、拒绝和时间定位。Seen/Unseen 沿用官方 Charades-CG 子集身份；这里的 Unseen 指下游训练未见组合，不声称预训练模型从未见过其词语或概念。本包仅含 C3_CG 一个划分，不是 Balanced v3 的五划分宏平均。", "",
             table(["分区", "官方查询来源", "事件标签", "期望输出"], [["S+", "Test-Trivial", "存在", "时间区间"], ["S−", "Test-Trivial", "构造缺席", "空集合"], ["U+", "Novel-Composition", "存在", "时间区间"], ["U−", "Novel-Composition", "构造缺席", "空集合"]]), "",
             "## 2. 数据怎样制作与修订？", "", f"![数据构建管线]({ASSET_REL}/construction_pipeline.svg)", "",
             f"1. 保留官方来源、提交、原句、视频、时间窗与组合标记。v2 纳入 Train、Test-Trivial、Novel-Composition；Novel-Word 单独保留在来源目录，不进入本包主评估。按 `0 ≤ start < end ≤ duration` 机械剔除 {stats['removed_rows']:,} 条非法或越界时间窗，分别为 Train 1,255、Test-Trivial 412、Novel-Composition 452 条；不截断窗口。清理后正例分别为 {source_counts['train.json']:,}、{source_counts['test_trivial.json']:,} 和 {source_counts['novel_composition.json']:,}。",
             "2. 复用 seed 3407 的 Train 视频分配：训练 6,342 正例、Seen validation 684 正例。两者与 v1 文件逐字节一致；训练、验证、测试视频互斥。Test-Trivial 与 Novel-Composition 可以共享测试视频。",
             "3. 参考 [Moment of Untruth §3.3](https://arxiv.org/html/2502.08544v2#S3.SS3) 的同域文本重配对，使用 CLIP ViT-B/32 归一化文本向量。查询与每个同 split 候选视频全部正例描述比较，取最大余弦相似度；排除 donor 视频和含完全相同查询的视频，按相似度、视频 ID 排序，保留最低 `floor(N/2)`，从可用目标均匀采样。最低 50% 是视频排名比例，不是余弦阈值 0.5。",
             "4. v2 的 Test 候选池是两类干净正例视频的并集，同视频的 Seen 和 Unseen 正描述共同进入最大相似度。每个查询保留原文本、S/U 身份和来源，在另一视频构造一个负例；测试 S−、U− 都按联合候选池重新采样。负例 `relevant_windows=[]`，源正例时间窗只用于追溯。",
             f"5. 总计 {stats['pair_rows']:,} 对，采样缺额 {stats['sampling_deficits']['total']}；机械校验重算候选排名、来源对应、窗口、标签、配对和视频划分。剔除记录保存在 [removed_rows.jsonl]({RELEASE_REL}/removed_rows.jsonl)。", "",
             "**全部负例是基于文本与已有标注的构造标签，未逐视频确认实际缺席。** 低文本相似度不能证明视频里没有该事件，报告结论仅针对这一构造分布。", "",
             "## 3. 划分规模与测试组成", "",
             table(["划分", "S+", "S−", "U+", "U−", "总行数", "视频数"], quad_rows), "",
             f"![数据四象限组成]({ASSET_REL}/dataset_composition.svg)", "",
             "Seen Test 为 5,368 行，Unseen Test 为 5,980 行，合计 11,348 行；两子集各自正负 1:1。总体指标按全部测试行计算，Seen/Unseen 指标按各自子集计算。Seen validation 仅用于模型与阈值选择，不作为 Seen Test 替代。", "",
             "Test-Trivial 与 Novel-Composition 正例的源视频交集为 1,087 个；纳入重配负例后，Seen 与 Unseen 实际评测目标视频交集为 2,084 个，总测试目标视频为 2,589 个。Bootstrap 按全部目标视频联合抽样，保留共享视频上两类查询的依赖。", "",
             "三个模型共享经过精确查询 SHA-256 匹配核验的视频与文本特征：复用 7,734 个既有 token 文本特征，新增编码 161 个文本；来源见 TEXT_FEATURE_MANIFEST。这里是模型推理 token 特征数，与构造负例时 CLIP 句向量缓存的新增文本数不同。", "",
             "### 冻结测试集中的真实查询示例", "",
             table(["分区", "qid", "目标视频", "查询原文", "GT 时间段（秒）", "负例 donor 视频"],
                   [[r["partition"].replace("-", "−"), r["qid"], r["vid"], r["query"], json.dumps(r["relevant_windows"]), r.get("source_vid", "—")] for r in examples]), "",
             f"这些是标注中的原句和构造实例，未重新人工修改。[QUERY_EXAMPLES.json]({REPORT_REL}/QUERY_EXAMPLES.json) 保存完整来源字段。", "", protocol,
             "## 5. 最新测试结果", "", "### Seen、Unseen 与三项退化的完整 95% CI", "", full_table, "",
             f"![Seen/Unseen三项绝对指标]({ASSET_REL}/seen_unseen_performance.svg)", "",
             f"![三项带符号退化及区间]({ASSET_REL}/generalization_gaps.svg)", "", *statements, "",
             "以上区间反映固定 checkpoint、固定阈值、单次训练种子下的视频抽样不确定性，不代表跨训练种子波动。区间包含 0 时，不将对应点估计方向称为明确退化或改善。本次未做 backbone 之间优越性的成对显著性检验。", "",
             "### 整体拒绝、真实正例误拒和端到端定位", "", overall_table, "",
             "RR 为全部测试查询的拒绝比例，S+/U+ FRR 为对应真实正例被拒绝的比例。G-mIoU 中正确拒绝负例贡献 1、误拒正例贡献 0；因此高 G-mIoU 或负 Gap 仍需结合 AUROC 与正例误拒率解释，不直接等同于正例定位改善。虽然当前两个子集都固定为 1:1，Rej-F1 与 G-mIoU 的数值和退化仍随部署时正负比例改变。", "",
             "作为公式推导的确定性参照：在当前任一子集的正负 1:1 组成下，若对全部查询一律拒绝，则 Rej-F1 为 66.67%、G-mIoU@1 为 50%、S+/U+ FRR 为 100%；若存在分数也恒定，AUROC 为 0.5。这不是额外训练或模型实验，仅说明拒绝相关数值应与排序能力和真实正例误拒率共同阅读。", "",
             "## 6. 从哪里查数据和完整结果？", "",
             table(["内容", "入口"], [
                 ["数据、来源、划分与构造", f"[数据 README]({RELEASE_REL}/README.md) · [splits]({RELEASE_REL}/splits/)"],
                 ["发布校验", f"[checksums]({RELEASE_REL}/checksums.sha256) · [validation]({RELEASE_REL}/validation_report.json)"],
                 ["评估总表", f"[STANDARD_EVALUATION]({REPORT_REL}/STANDARD_EVALUATION.md) · [GENERALIZATION_DROP_COMPARISON]({REPORT_REL}/GENERALIZATION_DROP_COMPARISON.md)"],
                 ["三项绝对值、Gap与CI", f"[Markdown]({REPORT_REL}/ALL_METRICS_WITH_CI.md) · [CSV]({REPORT_REL}/ALL_METRICS_WITH_CI.csv) · [JSON]({REPORT_REL}/ALL_METRICS_WITH_CI.json)"],
                 ["Overall、RR、FRR与CI", f"[Markdown]({REPORT_REL}/OVERALL_METRICS_WITH_CI.md) · [CSV]({REPORT_REL}/OVERALL_METRICS_WITH_CI.csv) · [JSON]({REPORT_REL}/OVERALL_METRICS_WITH_CI.json)"],
                 ["未舍入原始汇总", f"[metrics]({REPORT_REL}/metrics.json) · [degradation_metrics]({REPORT_REL}/degradation_metrics.json) · [bootstrap]({REPORT_REL}/bootstrap.json) · [degradation_bootstrap]({REPORT_REL}/degradation_bootstrap.json)"],
                 ["冻结预测、原生窗口、校准与抽样", f"[frozen]({REPORT_REL}/frozen/)"],
                 ["协议、状态与复核", f"[PROTOCOL]({REPORT_REL}/PROTOCOL.json) · [完成状态]({REPORT_REL}/FINAL_EVALUATION_STATUS.json) · [LOCAL_VERIFICATION]({REPORT_REL}/LOCAL_VERIFICATION.json) · [独立验收]({REPORT_REL}/INDEPENDENT_VERIFICATION.json)"],
                 ["执行源码与哈希", f"[source_snapshot]({REPORT_REL}/source_snapshot/) · [SOURCE_MANIFEST]({REPORT_REL}/SOURCE_MANIFEST.json)"],
                 ["图表与可移植重绘", f"[assets]({ASSET_REL}/) · [render_figures]({ASSET_REL}/render_figures.py)"],
                 ["本地覆盖包清单", "[PUBLICATION_MANIFEST](PUBLICATION_MANIFEST.json) · [PACKAGING](PACKAGING.json)"]]), "",
             "本次本地复核逐项检查全部测试标注与预测的 qid、视频、标签和分区，重放原 Seen-validation 阈值选择，逐条核对原生 top-1 窗口形成的 IoU，并从冻结预测重算点估计及已保存 bootstrap draws 的 95% CI。源码快照用于追溯实际推理与评估代码；模型权重、视频、特征不进入发布包，保留 checkpoint 哈希与校准元数据。", "",
             "核心字段：`qid`、`vid`、`query`、`duration`、`relevant_windows`、`exist_label`、`partition`。同名 qid 的 v1/v2 测试负例可能对应不同目标视频，版本之间不能混用预测。当前审阅包的图表、指标和冻结预测均来自 v2。", "",
             "在本覆盖包根目录校验数据 SHA-256：", "", "```bash\npython scripts/restore_release.py\n```", ""]
    (package / "README.md").write_text("\n".join(lines))
    (report / "ALL_METRICS_WITH_CI.md").write_text("# C3_CG v2 三项指标与完整置信区间\n\nAUROC 单位为 0–1，Rej-F1/G-mIoU 为 %，Gap 为百分点。\n\n" + full_table + "\n")


def archive_previous():
    archive = REPO / "experiments/agy_test/publication_review_history" / ("charades_cg_v1_before_v2_" + datetime.now().strftime("%Y%m%dT%H%M%S"))
    archive.mkdir(parents=True)
    shutil.copytree(REVIEW / "charades_cg", archive / "charades_cg")
    for filename in ("README.md", "REVIEW_STATUS.json", "FINAL_AUDIT.json", "FIGURE_AUDIT.md", "PLOT_SMOKE_CHECK.json", "build_review.py", "audit_review.py"):
        if (REVIEW / filename).exists():
            shutil.copy2(REVIEW / filename, archive / filename)
    dump(archive / "ARCHIVE_MANIFEST.json", file_state(archive))
    return archive


def update_index(full):
    index = (REVIEW / "README.md").read_text()
    index = index.replace("3/3，只有 Unseen Test，Seen/Gap 明确 N/A。", "3/3，v2 已补入 Seen Test，含 Seen/Unseen 三项退化与 CI；复用原 checkpoint 和阈值重新推理。")
    start = index.index("## Charades-CG")
    before = index[:start]
    fast_rows = []
    for bb in BACKBONES:
        row = [NAMES[bb]]
        for _, title in METRICS:
            r = next(r for r in full if r["backbone"] == bb and r["metric"] == title)
            row += [fmt(r["seen"], title) + " / " + fmt(r["unseen"], title), f'{r["gap_pp"]:+.2f}']
        fast_rows.append(row)
    tail = ["## Charades-CG v2 Seen / Unseen 速览", "",
            "C3_CG 单划分，Test-Trivial 作为 Seen、Novel-Composition 作为 Unseen；两者正负各自 1:1。Train/Seen validation 与 v1 不变，复用原 checkpoint 和冻结阈值，联合池重新生成的测试负例已重新推理。", "",
            table(["Backbone", "Seen / Unseen AUROC", "AUROC Gap pp", "Seen / Unseen Rej-F1", "F1 Gap pp", "Seen / Unseen G-mIoU", "G-mIoU Gap pp"], fast_rows), "",
            "![Charades-CG v2 绝对值](charades_cg/assets/charades_cg_gmr/seen_unseen_performance.png)", "",
            "![Charades-CG v2 退化](charades_cg/assets/charades_cg_gmr/generalization_gaps.png)", "",
            "Gap 为 Seen − Unseen，负值保留为 Unseen 点估计较高。完整 95% CI、整体拒绝率、正例误拒率和数据边界见 Charades-CG 完整 README；负例仍为构造标签。C3_CG 不参与 Balanced 五划分宏平均。", "",
            "全部图均提供 SVG/PDF/PNG，共 9 张；Balanced 的 5 张及其全部内容保持不变。各设置保存机器可读指标、冻结预测、阈值、checkpoint 哈希与视频聚类 bootstrap draws。数据 release manifest 和 checksums 保持原样，Balanced 超大 master 文件沿用可恢复 SHA-256 的 gzip 封装。", "",
            "刷新 Charades-CG v2：从原仓库运行 `python experiments/agy_test/charades_cg_v2_evaluation_20261011/refresh_publication.py`。原 Unseen-only Charades-CG 包与父报告元数据已归档至 `experiments/agy_test/publication_review_history/`。当前未执行 commit、push 或上传。", ""]
    (REVIEW / "README.md").write_text(before + "\n".join(tail))


def main():
    status = read(HERE / "FINAL_EVALUATION_STATUS.json")
    assert status["complete"] is True, "Refuse to publish incomplete inference"
    if (REVIEW / "REFRESHED_C3_V2.json").exists():
        auditor = load_module(REVIEW / "audit_review.py", "publication_auditor_existing")
        print(json.dumps(dict(status="PASS", already_current=True,
                              audit=auditor.audit(REVIEW / "charades_cg")), ensure_ascii=False, indent=2))
        return
    independent_path = HERE / "LOCAL_VERIFICATION_INDEPENDENT.json"
    independent = read(independent_path)
    assert independent["status"] == "PASS", "Refuse to publish without independent acceptance"
    balanced_before = file_state(REVIEW / "v3_balanced")
    builder = load_module(REVIEW / "build_review.py", "prior_publication_helpers")
    release = REPO / RELEASE_REL
    checksum_count = builder.verify_release(release)
    source, records, counts, verified = builder.load_experiment(HERE.name, release, ("C3_CG",))
    assert len(records) == 3 and all(r["seen_auc"] is not None for r in records)
    full = builder.unified(records, source, False)
    assert all(r["seen_ci_low"] is not None and r["gap_pp_ci_low"] is not None for r in full)
    stage = HERE / "publication_staging/charades_cg"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    compressed = builder.stage_dataset(release, stage / RELEASE_REL)
    report = builder.stage_artifacts(source, stage, ("C3_CG",), REPORT_REL)
    shutil.copy2(independent_path, report / "INDEPENDENT_VERIFICATION.json")
    dump(report / "ALL_METRICS_WITH_CI.json", full)
    builder.write_csv(report / "ALL_METRICS_WITH_CI.csv", full)
    dump(report / "LOCAL_VERIFICATION.json", dict(status="PASS", dataset_checksum_files=checksum_count, settings=verified,
         dataset_counts=counts, source_annotations_unchanged=True, dataset_version="charades_cg_gmr_v2",
         checkpoints_reused=True, calibration_reused=True, training_performed=False))
    dump(stage / "PACKAGING.json", dict(datasets=[dict(path=RELEASE_REL, compressed=compressed)], source=str(release),
         source_read_only=True, publication_state="local_review_only", experiment=str(source), checkpoints_included=False,
         replaces="charades_cg_gmr_v1 Unseen-only report", dataset_version="charades_cg_gmr_v2"))
    (stage / "scripts/restore_release.py").write_text(builder.UNPACK_SCRIPT)
    output = stage / ASSET_REL
    plot_performance(full, output)
    plot_gaps(full, output)
    plot_counts(counts, output)
    plot_pipeline(output)
    write_portable_plotter(stage)
    write_report(builder, stage, records, full, counts, status)
    subprocess.run([sys.executable, str(output / "render_figures.py")], check=True)
    assert not any(p.suffix in (".ckpt", ".pt", ".pth", ".mp4") for p in stage.rglob("*") if p.is_file())
    manifest = file_state(stage)
    assert all(v["bytes"] < 100 * 1024 * 1024 for v in manifest.values())
    dump(stage / "PUBLICATION_MANIFEST.json", manifest)
    auditor = load_module(REVIEW / "audit_review.py", "publication_auditor")
    stage_audit = auditor.audit(stage)
    archive = archive_previous()
    shutil.rmtree(REVIEW / "charades_cg")
    shutil.copytree(stage, REVIEW / "charades_cg")
    update_index(full)
    review_status = read(REVIEW / "REVIEW_STATUS.json")
    entry = next(r for r in review_status["packages"] if r["package"] == "charades_cg")
    entry.update(settings=3, files=len(manifest), bytes=sum(v["bytes"] for v in manifest.values()),
                 dataset_checksum_files=checksum_count, max_file_bytes=max(v["bytes"] for v in manifest.values()),
                 dataset_version="charades_cg_gmr_v2", re_evaluation=True)
    dump(REVIEW / "REVIEW_STATUS.json", review_status)
    figure_audit = (REVIEW / "FIGURE_AUDIT.md").read_text()
    figure_audit = figure_audit.replace("8 张", "9 张").replace("C3_CG unseen_performance | 三面板柱状图 + 95% CI | 只有 Unseen 的三项绝对成绩", "C3_CG seen_unseen_performance | 三面板分组柱状图 + 95% CI | Seen/Unseen 三项绝对成绩")
    figure_audit = figure_audit.replace("| C3_CG dataset_composition", "| C3_CG generalization_gaps | 三面板带符号点区间图 | 三项 Seen−Unseen Gap、联合视频 bootstrap 95% CI |\n| C3_CG dataset_composition")
    figure_audit = figure_audit.replace("Seen 校准与 Unseen 测试的不同作用", "Seen 校准与四象限测试的不同作用").replace("C3_CG 未绘制不存在的 Seen 数据或 Gap", "C3_CG v2 按实际四象限测试绘制 Seen/Unseen 与 Gap，不混用 v1 结果")
    figure_audit += "\nC3_CG v2 刷新：旧 Unseen-only 图及图表源脚本已随旧包完整归档。4 张新图只读取 v2 冻结 JSON 与计数；Balanced 5 张及其文件哈希保持不变。\n"
    (REVIEW / "FIGURE_AUDIT.md").write_text(figure_audit)
    smoke = read(REVIEW / "PLOT_SMOKE_CHECK.json")
    next(r for r in smoke if r["package"] == "charades_cg").update(figures=4, dataset_version="charades_cg_gmr_v2")
    dump(REVIEW / "PLOT_SMOKE_CHECK.json", smoke)
    final_audit = {"status": "PASS", "packages": [auditor.audit(REVIEW / p) for p in ("v3_balanced", "charades_cg")]}
    dump(REVIEW / "FINAL_AUDIT.json", final_audit)
    assert file_state(REVIEW / "v3_balanced") == balanced_before, "Balanced package was changed"
    original_builder = REVIEW / "build_review.py"
    text = original_builder.read_text()
    old_main = "def main():\n"
    guard = ('def main():\n'
             '    if (HERE / "REFRESHED_C3_V2.json").exists():\n'
             '        raise SystemExit("Charades-CG now uses v2. Run experiments/agy_test/charades_cg_v2_evaluation_20261011/refresh_publication.py; this historical builder would overwrite it with v1.")\n')
    assert text.count(old_main) == 1
    original_builder.write_text(text.replace(old_main, guard, 1))
    dump(REVIEW / "REFRESHED_C3_V2.json", dict(status="PASS", dataset_version="charades_cg_gmr_v2", archive=str(archive),
         experiment=str(HERE), refresh_script_sha256=sha(Path(__file__)), balanced_files_unchanged=len(balanced_before),
         publication_stage_audit=stage_audit, uploaded=False))
    dump(HERE / "PUBLICATION_REFRESH_STATUS.json", read(REVIEW / "REFRESHED_C3_V2.json"))
    print(json.dumps({"status": "PASS", "archive": str(archive), "output": str(REVIEW / "charades_cg"),
                      "settings": len(verified), "figures": 4, "balanced_files_unchanged": len(balanced_before)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
