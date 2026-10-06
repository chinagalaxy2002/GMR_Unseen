"""Connect restored shared evidence caches with portable relative symlinks."""
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[1]
for split in ['A1','A2_alt','A3','C1','C2_alt']:
    source=ROOT/'experiments/agy_test/semantic_directional_calibrated_verifier/cache'/split
    for name in ['train.npz','val.npz','test.npz']:
        if not (source/name).is_file():
            raise SystemExit('Missing restored asset: '+str(source/name)+'; restore Drive bundle first.')
    target=ROOT/'experiments/agy_test/detr_decoder_gmr/cache'/split
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_symlink() or target.exists():
        if target.resolve()!=source.resolve():
            raise SystemExit('Existing cache differs: '+str(target))
    else:
        target.symlink_to(os.path.relpath(source,target.parent),target_is_directory=True)
    print(split, '->', os.path.relpath(source,ROOT))
