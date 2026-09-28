"""Compare a positive-only localizer with the raw windows from its GMR counterpart."""
import argparse
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).open(encoding="utf-8")]


def iou(a, b):
    overlap = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return overlap / union if union > 0 else 0.0


def score(rows, predictions, window_key):
    result = {}
    for part in ("S+", "U+"):
        selected = [r for r in rows if r["partition"] == part]
        values = []
        for row in selected:
            windows = predictions[str(row["qid"])].get(window_key, [])
            if windows:
                top = max(windows, key=lambda w: w[2])
                values.append(max(iou(top, gt) for gt in row["relevant_windows"]))
            else:
                values.append(0.0)
        result[part] = {
            "n": len(values),
            "R1_iou05": sum(v >= 0.5 for v in values) / len(values),
            "R1_iou07": sum(v >= 0.7 for v in values) / len(values),
            "mean_top1_iou": sum(values) / len(values),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth", required=True)
    parser.add_argument("--plain", required=True)
    parser.add_argument("--gmr", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = read_jsonl(args.ground_truth)
    expected = {str(r["qid"]) for r in rows}
    if len(expected) != 2971 or {r["partition"] for r in rows} != {"S+", "U+"}:
        raise ValueError("Expected the fixed 2,971-row positive test view")
    plain = {str(r["qid"]): r for r in read_jsonl(args.plain)}
    gmr = {str(r["qid"]): r for r in read_jsonl(args.gmr)}
    if not expected.issubset(plain) or not expected.issubset(gmr):
        raise ValueError(f"Prediction coverage mismatch: plain={len(set(plain) & expected)}, gmr={len(set(gmr) & expected)}")
    result = {
        "protocol": "train S+; select on val S+; test S+ and U+; GMR raw uses the same seed checkpoint trained on S+ and S-",
        "plain": score(rows, plain, "pred_relevant_windows"),
        "gmr_raw": score(rows, gmr, "pred_relevant_windows_pre_exist"),
    }
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
