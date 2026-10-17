"""Self-contained runtime environment for Moment-Conditioned Event Verification (MCEV)."""
from pathlib import Path
import hashlib
import json
import os
import random
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path('/home/guoxiangyu/VLMbasedIter_momentretrival/generalized-moment-retrieval/Soccergmr')

# Point to the 4 verified E0 baseline checkpoints
E0_CHECKPOINTS = {
    2024: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2024/best.ckpt'),
    2025: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2025/best.ckpt'),
    2026: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2026/best.ckpt'),
    2027: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2027/best.ckpt'),
}

E0_VAL_PREDICTIONS = {
    2024: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2024/validation_predictions.jsonl'),
    2025: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2025/validation_predictions.jsonl'),
    2026: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2026/validation_predictions.jsonl'),
    2027: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/baseline/runs/E0_s2027/validation_predictions.jsonl'),
}

E0_TEST_PREDICTIONS = {
    2024: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/audit/pre_mechanism_diagnostics_20261017_155247/baseline_runs/E0_s2024/test_predictions.jsonl'),
    2025: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/audit/pre_mechanism_diagnostics_20261017_155247/baseline_runs/E0_s2025/test_predictions.jsonl'),
    2026: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/audit/pre_mechanism_diagnostics_20261017_155247/baseline_runs/E0_s2026/test_predictions.jsonl'),
    2027: Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_kim_mechanism_20261016/multiseed_reproduction/audit/pre_mechanism_diagnostics_20261017_155247/baseline_runs/E0_s2027/test_predictions.jsonl'),
}

for name, value in {
    'PYTHONDONTWRITEBYTECODE': '1',
    'TMPDIR': str(ROOT / 'tmp'),
    'XDG_CACHE_HOME': str(ROOT / 'cache'),
    'TORCH_HOME': str(ROOT / 'cache/torch'),
    'MPLCONFIGDIR': str(ROOT / 'cache/matplotlib'),
    'OMP_NUM_THREADS': '4',
    'MKL_NUM_THREADS': '4',
    'MKL_THREADING_LAYER': 'GNU',
}.items():
    os.environ[name] = value

for directory in ('tmp', 'cache', 'logs', 'runs', 'tests', 'reports'):
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

sys.dont_write_bytecode = True
tempfile.tempdir = str(ROOT / 'tmp')
sys.path.insert(0, str(ROOT / 'baseline_source'))

import numpy as np
import torch


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write_json(path, value):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    temp.replace(path)


def write_rows(path, rows):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    temp.replace(path)


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def options(job, device):
    from types import SimpleNamespace
    import nncore

    values = read_json(ROOT / 'configs/protocol.json')
    values.update(
        n_epoch=job.get('epochs', 100),
        seed=job['seed'],
        lr=job.get('lr', 3e-5),
        grad_clip=job.get('grad_clip', 0.1),
        wd=job.get('wd', 1e-4),
        device=torch.device(device),
        config=str(ROOT / 'baseline_source/configs/flash_vtg_gmr/model.py'),
        train_path=str(ROOT / 'data/train.jsonl'),
        eval_path=str(ROOT / 'data/val.jsonl'),
        v_feat_dirs=[str(ASSETS / 'slowfast'), str(ASSETS / 'clip')],
        t_feat_dir=str(ASSETS / 'clip_text'),
        use_plurality_gating=False,
    )
    values['lr_drop'] = job.get('lr_drop', 12)
    opt = SimpleNamespace(**values)
    opt.cfg = nncore.Config.from_file(opt.config)
    return opt


def make_dataset(opt, split, smoke=False):
    from training.flash_vtg_gmr.dataset import StartEndDataset

    assert split in ('train', 'val', 'test'), split
    path = ROOT / 'data' / f'{split}.jsonl'
    dataset = StartEndDataset(
        dset_name=opt.dset_name,
        data_path=str(path),
        v_feat_dirs=opt.v_feat_dirs,
        q_feat_dir=opt.t_feat_dir,
        q_feat_type=opt.q_feat_type,
        max_q_l=opt.max_q_l,
        max_v_l=opt.max_v_l,
        ctx_mode=opt.ctx_mode,
        normalize_v=True,
        normalize_t=True,
        load_labels=split == 'train',
        clip_len=opt.clip_length,
        max_windows=opt.max_windows,
        span_loss_type=opt.span_loss_type,
        mr_only=True,
        keep_empty_gt=True,
    )
    return dataset
