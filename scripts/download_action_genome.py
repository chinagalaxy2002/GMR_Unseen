#!/usr/bin/env python3
"""Fetch the five Action Genome annotation files linked by the official GitHub README."""

from pathlib import Path

import gdown


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/raw/action_genome/annotations"
EXPECTED = {
    "frame_list.txt", "object_bbox_and_relationship.pkl", "object_classes.txt",
    "person_bbox.pkl", "relationship_classes.txt",
}
FOLDER_ID = "1LGGPK_QgGbh9gH9SDFv_9LIhBliZbZys"


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    if not all((TARGET / name).is_file() and (TARGET / name).stat().st_size > 0 for name in EXPECTED):
        # gdown's default cookie mode can incorrectly list this public folder as empty.
        gdown.download_folder(id=FOLDER_ID, output=str(TARGET), use_cookies=False,
                              quiet=False, resume=True, timeout=60)
    missing = sorted(name for name in EXPECTED if not (TARGET / name).is_file() or (TARGET / name).stat().st_size == 0)
    if missing:
        raise SystemExit(f"Action Genome download incomplete: {missing}")
    print("Action Genome annotations ready:", TARGET)
    for name in sorted(EXPECTED):
        print(name, (TARGET / name).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
