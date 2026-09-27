"""Prepare seen-only validation and CLIP query features for semantic_existence_v1."""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--old-text", type=Path, required=True)
    parser.add_argument("--clip-code", type=Path, required=True)
    parser.add_argument("--clip-weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    text_dir = args.output / "clip_text"
    text_dir.mkdir(exist_ok=True)
    rows = {}
    for split in ("train", "val", "test"):
        rows[split] = [json.loads(line) for line in (args.release / f"{split}.jsonl").open()]
    seen = [r for r in rows["val"] if r["partition"] in ("S+", "S-")]
    with (args.output / "val_seen.jsonl").open("w") as f:
        for row in seen:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"val_seen: {len(seen)} records", flush=True)

    negatives = []
    for split_rows in rows.values():
        for row in split_rows:
            dest = text_dir / f"qid{row['qid']}.npz"
            if row["exist_label"] == 1:
                source = args.old_text / f"{row['qid']}.npz"
                if not source.is_file():
                    raise FileNotFoundError(source)
                if not dest.exists():
                    dest.symlink_to(source)
            elif not dest.exists():
                negatives.append(row)
    print(f"new negative text features: {len(negatives)}", flush=True)
    if not negatives:
        return
    sys.path.insert(0, str(args.clip_code))
    import clip

    model, _ = clip.load(str(args.clip_weights), device=args.device, jit=False)
    model.eval()
    with torch.no_grad():
        for start in range(0, len(negatives), 64):
            batch = negatives[start:start + 64]
            tokens = clip.tokenize([r["query"] for r in batch], context_length=77).to(args.device)
            states = model.encode_text(tokens)["last_hidden_state"].float().cpu().numpy()
            lengths = (tokens != 0).sum(1).cpu().tolist()
            for row, state, length in zip(batch, states, lengths):
                np.savez_compressed(text_dir / f"qid{row['qid']}.npz", last_hidden_state=state[:length])
            if start % 640 == 0:
                print(f"encoded {min(start + 64, len(negatives))}/{len(negatives)}", flush=True)


if __name__ == "__main__":
    main()
