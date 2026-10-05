"""Paths, data helpers, and metrics for isolated cross-confirmation."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STUDY = BASE.parent
REPO = STUDY.parents[1]
SPLITS = ("A2_alt", "A3", "C1", "C2_alt")
BACKBONES = ("qd", "moment", "flash")
VIDEO_ROOT = Path("/home/guoxiangyu/paper/新建文件夹/charades")

os.environ.setdefault("TMPDIR", str(BASE / "cache/tmp"))
os.environ.setdefault("XDG_CACHE_HOME", str(BASE / "cache/xdg"))
os.environ.setdefault("TORCH_HOME", str(BASE / "cache/torch"))
os.environ.setdefault("HF_HOME", str(BASE / "cache/huggingface"))
os.environ.setdefault("MPLCONFIGDIR", str(BASE / "cache/matplotlib"))
os.environ.setdefault("PYTHONPYCACHEPREFIX", str(BASE / "cache/pycache"))
sys.dont_write_bytecode = True


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def auc(labels, scores) -> float | None:
    import numpy as np
    y = np.asarray(labels, dtype=np.int8)
    s = np.asarray(scores, dtype=np.float64)
    if not np.any(y == 1) or not np.any(y == 0):
        return None
    order = np.argsort(s, kind="stable")
    s, y = s[order], y[order]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    positives = np.add.reduceat((y == 1).astype(np.float64), starts)
    negatives = np.add.reduceat((y == 0).astype(np.float64), starts)
    return float((positives * (np.cumsum(negatives) - 0.5 * negatives)).sum() /
                 ((y == 1).sum() * (y == 0).sum()))


def youden_threshold(labels, scores) -> float:
    import numpy as np
    y = np.asarray(labels, dtype=np.int8)
    s = np.asarray(scores, dtype=np.float64)
    thresholds = np.r_[np.unique(s), np.nextafter(np.max(s), np.inf)]
    best = (-np.inf, -np.inf)
    for threshold in thresholds:
        accepted = s >= threshold
        tpr = float(accepted[y == 1].mean())
        fpr = float(accepted[y == 0].mean())
        best = max(best, (tpr - fpr, float(threshold)))
    return best[1]


def checkpoint_path(split: str, backbone: str) -> Path:
    root = REPO / "results/semantic_existence/multi_split_v2" / split
    if backbone == "qd":
        return root / "qd/best.ckpt"
    if backbone == "moment":
        return root / "moment/best.ckpt"
    candidates = sorted((root / "flash").glob("*/model_best.ckpt"))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one FlashVTG best checkpoint for {split}, got {candidates}")
    return candidates[0]


def release_dir(split: str) -> Path:
    return REPO / "data/release/semantic_existence_v2" / split


def seen_source(split: str) -> Path:
    return REPO / "features/semantic_existence_v2" / split / "val_seen.jsonl"


def view_path(split: str, subset: str) -> Path:
    return BASE / "data_views" / split / f"{subset}.jsonl"


def feature_path(split: str, backbone: str, subset: str) -> Path:
    return BASE / "cache/features" / split / backbone / f"{subset}.npz"
