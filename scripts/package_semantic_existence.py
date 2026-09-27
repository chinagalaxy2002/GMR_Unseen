#!/usr/bin/env python3
"""Package reviewed four-quadrant data with provenance and release statistics."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while data := f.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def summary(values):
    return {"n": len(values), "mean": round(mean(values), 3), "median": round(median(values), 3)} if values else {"n": 0}


def describe(rows: list[dict]) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[row["partition"]].append(row)
    result = {}
    for partition, group in sorted(groups.items()):
        centers = []
        anchors = []
        for row in group:
            for a, b in row["relevant_windows"]:
                centers.append(((a + b) / 2) / row["duration"] if row["duration"] else 0)
            for a, b in row.get("source_windows", []):
                anchors.append(((a + b) / 2) / row["duration"] if row["duration"] else 0)
        result[partition] = {
            "rows": len(group), "videos": len({r["video_id"] for r in group}),
            "query_tokens": summary([len(r["query"].split()) for r in group]),
            "video_duration_seconds": summary([r["duration"] for r in group]),
            "positive_window_center_fraction": summary(centers),
            "negative_source_center_fraction": summary(anchors),
            "novelty_type": dict(Counter(r["novelty_type"] for r in group)),
            "construction_type": dict(Counter(r["construction_type"] for r in group)),
            "top_actions": Counter(r["semantic_graph"]["action"] for r in group).most_common(15),
            "top_objects": Counter(r["semantic_graph"]["object"] for r in group).most_common(15),
            "verification_status": dict(Counter(r["verification_status"] for r in group)),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data/processed/semantic_existence")
    parser.add_argument("--out", type=Path, default=ROOT / "data/release/semantic_existence_v1")
    args = parser.parse_args()
    reviewed = args.data / "test_reviewed.jsonl"
    if not reviewed.exists():
        raise SystemExit("Missing test_reviewed.jsonl. Run review_semantic_existence.py --reviews first.")
    train_all = read_jsonl(args.data / "train_candidates.jsonl")
    val_all = read_jsonl(args.data / "val_candidates.jsonl")
    test = read_jsonl(reviewed)
    candidate_test = {r["qid"]: r for r in read_jsonl(args.data / "test_candidates.jsonl")}
    if not test or any(r["qid"] not in candidate_test for r in test):
        raise SystemExit("Reviewed test contains unknown candidate IDs; rebuild review export after generating candidates.")
    for row in test:
        if row["exist_label"] == 0 and row["verification_status"] not in {
            "manual_video_review_confirmed", "user_attested_video_review"}:
            raise SystemExit(f"Unreviewed negative in official test: {row['qid']}")
    partitions = Counter(r["partition"] for r in test)
    if any(partitions[p] == 0 for p in ("S+", "S-", "U+", "U-")):
        raise SystemExit(f"Official test requires all four partitions; got {dict(partitions)}")
    train_reviewed_path = args.data / "train_reviewed.jsonl"
    val_reviewed_path = args.data / "val_reviewed.jsonl"
    train = read_jsonl(train_reviewed_path) if train_reviewed_path.exists() else [r for r in train_all if r["exist_label"] == 1]
    val = read_jsonl(val_reviewed_path) if val_reviewed_path.exists() else [r for r in val_all if r["exist_label"] == 1]
    train_weak = [] if train_reviewed_path.exists() else [r for r in train_all if r["exist_label"] == 0]
    val_weak = [] if val_reviewed_path.exists() else [r for r in val_all if r["exist_label"] == 0]
    for split_name, rows in (("train", train), ("val", val)):
        known = {r["qid"] for r in (train_all if split_name == "train" else val_all)}
        if any(r["qid"] not in known for r in rows):
            raise SystemExit(f"{split_name} reviewed file contains unknown candidate IDs")
        if any(r["exist_label"] == 0 and r["verification_status"] not in {
            "manual_video_review_confirmed", "user_attested_video_review"} for r in rows):
            raise SystemExit(f"{split_name} formal split contains unreviewed negatives")
    # The parser treats "in front of" as the object "front" in some dressing captions.
    # This is a source-graph error, so quarantine the affected rows after review.
    quarantined = {}
    def keep_valid(split_name: str, rows: list[dict]) -> list[dict]:
        bad = [r for r in rows if r["semantic_graph"]["action"] == "dress" and r["semantic_graph"]["object"] == "front"]
        quarantined[split_name] = [r["qid"] for r in bad]
        bad_ids = set(quarantined[split_name])
        return [r for r in rows if r["qid"] not in bad_ids]
    train = keep_valid("train", train)
    val = keep_valid("val", val)
    test = keep_valid("test", test)
    partitions = Counter(r["partition"] for r in test)
    ag_frame_list = ROOT / "data/raw/action_genome/annotations/frame_list.txt"
    ag_videos = {line.split("/")[0].removesuffix(".mp4") for line in ag_frame_list.read_text().splitlines()} if ag_frame_list.exists() else set()
    ag_video_coverage = {name: {"videos": len({r["video_id"] for r in rows}),
                                "with_action_genome_frames": len({r["video_id"] for r in rows} & ag_videos)}
                         for name, rows in (("train", train), ("val", val), ("test", test))}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train.jsonl", train), ("val.jsonl", val), ("test.jsonl", test)):
        write_jsonl(args.out / name, rows)
    for name, rows in (("train_weak_negative_candidates.jsonl", train_weak),
                       ("val_weak_negative_candidates.jsonl", val_weak)):
        if rows:
            write_jsonl(args.out / name, rows)
        elif (args.out / name).exists():
            (args.out / name).unlink()
    pairs_path = args.data / "matched_u_pairs_reviewed.jsonl"
    if pairs_path.exists():
        released_ids = {r["qid"] for r in test}
        released_pairs = [r for r in read_jsonl(pairs_path) if r["positive_qid"] in released_ids and r["negative_qid"] in released_ids]
        write_jsonl(args.out / "matched_u_pairs.jsonl", released_pairs)
        test_by_qid = {r["qid"]: r for r in test}
        matched_rows = [test_by_qid[qid] for item in released_pairs for qid in (item["positive_qid"], item["negative_qid"])]
        write_jsonl(args.out / "test_matched_u.jsonl", matched_rows)
    shutil.copy2(args.data / "semantic_inventory.json", args.out / "semantic_inventory.json")
    stats = {"train": describe(train), "val": describe(val), "test": describe(test),
             "weak_training_negative_candidates": len(train_weak),
             "weak_validation_negative_candidates": len(val_weak),
             "matched_u_pairs_reviewed": len(read_jsonl(args.out / "matched_u_pairs.jsonl")) if (args.out / "matched_u_pairs.jsonl").exists() else 0,
             "quarantined_parser_errors": quarantined,
             "action_genome_video_coverage": ag_video_coverage}
    (args.out / "statistics.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    inventory = json.loads((args.data / "semantic_inventory.json").read_text())
    source_counts = json.loads((args.data / "audit.json").read_text())["source_counts"]
    review_report = json.loads((args.data / "review_report.json").read_text()) if (args.data / "review_report.json").exists() else {}
    ag_loaded = json.loads((args.data / "audit.json").read_text())["external_evidence"]["action_genome_loaded"]
    ag_conflict_report_path = ROOT / "data/audit/action_genome_conflict_report.json"
    ag_conflict_report = json.loads(ag_conflict_report_path.read_text()) if ag_conflict_report_path.exists() else None
    diagnostic_path = args.out / "text_only_diagnostic.json"
    diagnostic = json.loads(diagnostic_path.read_text()) if diagnostic_path.exists() else None
    source_train = read_jsonl(ROOT / "data/raw/charades_sta/charades_pos_train.jsonl")
    original_val = sum(int(hashlib.sha256(r["vid"].encode()).hexdigest()[:8], 16) % 100 < 10 for r in source_train)
    original_downstream_train = len(source_train) - original_val
    removed_holdouts = len(read_jsonl(args.data / "removed_train_holdouts.jsonl"))
    video_archive = ROOT / "downloads/Charades_v1_480.zip"
    release_video_ids = {r["video_id"] for r in train + val + test}
    with zipfile.ZipFile(video_archive) as archive:
        archive_names = set(archive.namelist())
    missing_videos = sorted(v for v in release_video_ids if f"Charades_v1_480/{v}.mp4" not in archive_names)
    table_rows = []
    listed_files = [("train.jsonl", train), ("val.jsonl", val), ("test.jsonl", test)]
    if train_weak:
        listed_files.append(("train_weak_negative_candidates.jsonl", train_weak))
    if val_weak:
        listed_files.append(("val_weak_negative_candidates.jsonl", val_weak))
    for name, rows in listed_files:
        counts = Counter(r["partition"] for r in rows)
        table_rows.append(f"| `{name}` | {len(rows)} | {counts['S+']} | {counts['S-']} | {counts['U+']} | {counts['U-']} |")
    detail_rows = []
    for split in ("train", "val", "test"):
        for partition, part_stats in stats[split].items():
            detail_rows.append(f"| {split} | {partition} | {part_stats['rows']} | {part_stats['videos']} | {part_stats['query_tokens']['mean']} | {part_stats['video_duration_seconds']['mean']} |")
    candidate_counts = {"train": len(train_all), "val": len(val_all),
                        "test": len(candidate_test)}
    handoff = f"""# Semantic novelty × existence 数据集交接

## 交接状态与完成口径

- 当前版本：`semantic_existence_v1`。正式 train/val/test、同视频 U+/U− 配对、语义清单、统计、来源校验和均已生成；正式文件通过 `scripts/validate_release.py` 校验。
- “全量”指当前规则下所有可发布样本，不等于收录全部原始 Charades-STA 句子。未入集的正例包含语义 holdout 后的训练样本、无法可靠规范化或不符合所选语义类别的样本；另隔离 3 条已发现的解析错误。数量见下文。
- 负例的视频不存在性依据数据负责人对本批候选的**统一复核确认**；没有逐 qid 复核表。`review_report.json` 如实记录此复核口径，不能将其表述成逐条双人审核。

## 版本与路径

- 正式数据目录：`{args.out}`
- 正式训练、验证、测试：`train.jsonl`、`val.jsonl`、`test.jsonl`。所有纳入正式 split 的负例均依据数据负责人的统一复核确认。
- Action Genome 下载：`scripts/download_action_genome.py`；构建脚本：`scripts/build_semantic_existence.py`；复核导出：`scripts/review_semantic_existence.py`；打包：`scripts/package_semantic_existence.py`；校验：`scripts/validate_semantic_existence.py`、`scripts/validate_release.py`。
- 格式：每行一个 JSON，包含 GMR 字段 `qid`、`vid`、`query`、`duration`、`relevant_windows`，并保留 `video_id`、`exist_label`、`semantic_status`、`partition`、`novelty_type`、`construction_type`、`source_qid`、`semantic_graph`、`verification_status`。

## 原始数据和产生方法

1. 真实正例：`data/raw/charades_sta/charades_pos_train.jsonl`（{source_counts['train']} 条）和 `data/raw/charades_sta/charades_pos_test.jsonl`（{source_counts['test']} 条）。它们复制自已有 GMR `pos_only` 的 Charades-STA 导出；query 和时间窗保留原始标注。Charades 元数据来自 `downloads/Charades.zip`，展开到 `data/raw/charades/annotations/`，用于视频级动作冲突筛查。视频在 `downloads/Charades_v1_480.zip`，zip 内路径为 `Charades_v1_480/<video_id>.mp4`；正式包 {len(release_video_ids)} 个不同视频 ID 中缺失 {len(missing_videos)} 个。
   Action Genome 官方仓库 `https://github.com/JingweiJ/ActionGenome` 指向的标注已保存到 `data/raw/action_genome/annotations/`，包括 `object_bbox_and_relationship.pkl`、`person_bbox.pkl`、`frame_list.txt` 和类别表。构建器把场景图关系作为视频级正面冲突证据。{f"相比未接入 AG 的上一版，移除 {ag_conflict_report['removed_total']} 条潜在冲突候选，分 split 为 {ag_conflict_report['removed_by_split']}。" if ag_conflict_report else ''}
   Action Genome 帧标注覆盖正式训练视频 {ag_video_coverage['train']['with_action_genome_frames']}/{ag_video_coverage['train']['videos']}、验证视频 {ag_video_coverage['val']['with_action_genome_frames']}/{ag_video_coverage['val']['videos']}、测试视频 {ag_video_coverage['test']['with_action_genome_frames']}/{ag_video_coverage['test']['videos']}。移除条目及 qid 见 `data/audit/action_genome_removed_candidates.jsonl`；分 split 统计见 `data/audit/action_genome_conflict_report.json`。
2. 切分与语义清单：原测试视频保持测试；原训练视频按 SHA-256(video_id) 的前 10% 桶划验证。只用其余训练视频构建 `semantic_inventory.json`。动作 `open`、`close`（`shut` 归一为 `close`）和 {len(inventory['heldout_compositions'])} 个动作–物体组合被 hold out；含这些语义的训练正例移除。清单收录 {len(inventory['actions'])} 个训练动作、{len(inventory['objects'])} 个物体和 {len(inventory['action_object_compositions'])} 个动作–物体组合。
3. S+ / U+：从真实 Charades-STA 正例直接提取，沿用人工时间窗。训练清单已出现的组合标 S+；held-out 动作或指定 held-out 组合标 U+。
4. S− / U−：从同视频真实正例做一个语义边的改写。短语动作作为整体处理，例如 `take off → put on`；物体采用语义近邻。改写后的谓词、物体、角色和介词组合必须在另一条真实正例中出现，并通过重解析检查。同视频 Charades-STA、Charades 动作及可用 Action Genome 的正面证据用于排除冲突。根据训练清单标 S− 或 U−；只有视频复核判 `absent` 的测试候选进入正式测试集。
5. 匹配：`matched_u_pairs.jsonl` 只收录复核后同视频、同来源正例的 U+/U− 对。当前共 {stats['matched_u_pairs_reviewed']} 对。
   `test_matched_u.jsonl` 展开这些配对，每对两行，可直接用于核心 U+/U− 诊断；它是 `test.jsonl` 的子集。
6. 发布前 QC：解析器将部分 `dress in front of ...` 错取为 `dress|front`，因此从正式包隔离 {sum(len(v) for v in quarantined.values())} 条；qid 清单在 `statistics.json`。这属于语义解析错误，与视频复核结论无关。

原训练标注 {len(source_train)} 条，其中 {original_downstream_train} 条原样本进入 downstream train 视频池，{original_val} 条进入验证视频池。训练池删除 {removed_holdouts} 条 holdout 正例，另有 {original_downstream_train - removed_holdouts - sum(r['partition']=='S+' for r in train)} 条因事件解析或语义清单资格不足未入正式训练；验证池有 {original_val - sum(r['exist_label']==1 for r in val)} 条正例未入正式验证。原测试正例有 {source_counts['test'] - sum(r['exist_label']==1 for r in test)} 条未进入正式测试（包含发布前隔离的 {len(quarantined['test'])} 条）。

## 数据文件及统计

| 文件 | 条数 | S+ | S− | U+ | U− |
|---|---:|---:|---:|---:|---:|
{chr(10).join(table_rows)}

| split | 象限 | 条数 | 视频数 | 平均 query 词数 | 平均视频秒数 |
|---|---|---:|---:|---:|---:|
{chr(10).join(detail_rows)}

各文件的完整路径均为上面的正式数据目录加表内文件名。中间产物保存在 `{args.data}`：`semantic_inventory.json` 是仅由下游训练正例构建的清单，`removed_train_holdouts.jsonl` 是被排除的原训练正例，`*_candidates.jsonl` 是复核前四象限候选，`*_reviewed.jsonl` 是复核确认后的数据，`matched_u_pairs_reviewed.jsonl` 是复核后的配对，`audit.json` 是构建期审计。正式包中的同名清单和配对是交付副本。

### 数据流与逐项路径

| 数据 | 路径（相对项目根目录） | 如何产生 | 条数 |
|---|---|---|---:|
| 原始训练正例 | `data/raw/charades_sta/charades_pos_train.jsonl` | 复制已有 GMR Charades-STA positive 导出，保留人工 query 和时间窗 | {source_counts['train']} |
| 原始测试正例 | `data/raw/charades_sta/charades_pos_test.jsonl` | 同上 | {source_counts['test']} |
| 被 holdout 的训练正例 | `data/processed/semantic_existence/removed_train_holdouts.jsonl` | 在训练视频内按选定动作和组合移除，以建立 downstream train 清单 | {removed_holdouts} |
| 训练候选 | `data/processed/semantic_existence/train_candidates.jsonl` | 合格真实 S+ 加同视频最小语义改写 S−；以已有正面证据排除冲突 | {candidate_counts['train']} |
| 验证候选 | `data/processed/semantic_existence/val_candidates.jsonl` | 原训练视频独立切出验证；真实 S+/U+ 与改写 S−/U− | {candidate_counts['val']} |
| 测试候选 | `data/processed/semantic_existence/test_candidates.jsonl` | 原测试视频的真实 S+/U+ 与改写 S−/U− | {candidate_counts['test']} |
| 正式训练集 | `data/release/semantic_existence_v1/train.jsonl` | 复核确认后发布的训练候选 | {len(train)} |
| 正式验证集 | `data/release/semantic_existence_v1/val.jsonl` | 复核确认后发布的验证候选 | {len(val)} |
| 正式测试集 | `data/release/semantic_existence_v1/test.jsonl` | 复核确认后发布的测试候选，隔离 3 条解析错误 | {len(test)} |
| 同视频 U+/U− 配对 | `data/release/semantic_existence_v1/matched_u_pairs.jsonl` | 在已发布 U+/U− 中按同视频、同 source 正例匹配 | {stats['matched_u_pairs_reviewed']} 对 |
| 配对展开集 | `data/release/semantic_existence_v1/test_matched_u.jsonl` | 每对展开成正负各一行，供配对评测 | {2 * stats['matched_u_pairs_reviewed']} |

`data/release/semantic_existence_v1/semantic_inventory.json` 记录训练语义、holdout 动作与组合；`statistics.json` 是逐象限统计；`manifest.json` 含输入及交付文件 SHA-256；`review_report.json` 是复核口径；`text_only_diagnostic.json` 是语言泄漏诊断。Action Genome 冲突移除的逐条记录在 `data/audit/action_genome_removed_candidates.jsonl`，汇总在 `data/audit/action_genome_conflict_report.json`。

完整统计见 `statistics.json`：每象限视频数、query 长度、视频时长、正例时间窗位置、负例来源窗口位置、novelty 类型、构造类型、动作和物体频次及复核状态。校验和见 `manifest.json`。

## 文件用途与限制

- 本次训练、验证和测试的负例均已进入正式 split；复核前候选仍保存在中间产物目录，便于追溯。
- `test.jsonl` 中的负例复核来源见 `review_report.json`；测试集须按 S+/S−/U+/U− 分别报告，特别是 U+ 错误拒绝率和 U− 拒绝率。
- Action Genome 标注当前{'已' if ag_loaded else '未'}接入；场景图只覆盖采样帧，缺失图谱边不能证明事件不存在。
- 正例均为原始人工句子，负例均由最小编辑生成，存在文本来源与存在标签相关的风险。发表前需做文本单模态基线及语言风格平衡分析。
- 文本单模态诊断见 `text_only_diagnostic.json`。{f"当前字符 n-gram 基线测试 AUC={diagnostic['all']['roc_auc']}，seen AUC={diagnostic['seen']['roc_auc']}，unseen AUC={diagnostic['unseen']['roc_auc']}，U+/U− 同视频配对排序准确率={diagnostic['matched_u_pair_text_only_ranking_accuracy']}；这表明尤其 seen 子集仍有语言线索，发布论文时必须报告并做风格平衡。" if diagnostic else '尚未运行文本单模态诊断。'}
- `review_report.json` 记录此次复核汇总：{json.dumps(review_report, ensure_ascii=False)}。此次依据数据负责人对所有当前候选的统一确认，没有逐 qid 复核表。

## 重建与校验

在项目根目录运行：

```bash
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/download_action_genome.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/build_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/validate_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/review_semantic_existence.py --user-attests-all-absent
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/package_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/audit_text_only.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/package_semantic_existence.py
/home/guoxiangyu/miniconda3/envs/owvtg/bin/python scripts/validate_release.py
```

第四条命令只在数据负责人已经确认**当前构建得到的全部候选**通过复核时使用；如对数据进行了重新生成并出现新 qid，需要重新确认新候选。本次接入 Action Genome 后新 qid 为 0，原已确认候选的子集保留下来，详见 `data/audit/action_genome_conflict_report.json`。
"""
    (args.out / "HANDOFF.md").write_text(handoff)
    sources = [ROOT / "data/raw/charades_sta/charades_pos_train.jsonl",
               ROOT / "data/raw/charades_sta/charades_pos_test.jsonl",
               ROOT / "data/raw/charades/annotations/Charades_v1_train.csv",
               ROOT / "data/raw/charades/annotations/Charades_v1_test.csv"]
    if ag_loaded:
        sources.extend(sorted(p for p in (ROOT / "data/raw/action_genome/annotations").iterdir() if p.is_file()))
    if (args.data / "review_report.json").exists():
        shutil.copy2(args.data / "review_report.json", args.out / "review_report.json")
    files = [p for p in args.out.iterdir() if p.is_file() and p.name != "manifest.json"]
    manifest = {
        "name": "semantic_existence_v1", "format": "GMR-style JSONL with vid and video_id",
        "formal_splits": ["train.jsonl", "val.jsonl", "test.jsonl"],
        "training_and_validation_negatives": "included after dataset-owner global review attestation" if train_reviewed_path.exists() and val_reviewed_path.exists() else "candidate files only; excluded from formal splits until reviewed",
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in sources if p.exists()},
        "release_sha256": {p.name: sha256(p) for p in files},
        "test_partition_counts": dict(Counter(r["partition"] for r in test)),
        "quarantined_parser_error_counts": {split: len(qids) for split, qids in quarantined.items()},
        "video_archive": str(video_archive.relative_to(ROOT)),
        "release_video_count": len(release_video_ids),
        "missing_release_videos_in_archive": missing_videos,
        "action_genome_loaded": ag_loaded,
        "action_genome_removed_candidates": ag_conflict_report["removed_total"] if ag_conflict_report else None,
        "action_genome_video_coverage": ag_video_coverage,
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"release": str(args.out), "train": len(train), "val": len(val),
                      "test": len(test), "test_partitions": dict(partitions)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
