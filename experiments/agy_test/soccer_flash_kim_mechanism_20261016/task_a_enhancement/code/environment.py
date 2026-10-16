"""Self-contained runtime helpers for Task-A head-only enhancement experiments."""
from pathlib import Path
import hashlib
import json
import os
import random
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
ASSETS = Path('/home/guoxiangyu/VLMbasedIter_momentretrival/generalized-moment-retrieval/Soccergmr')
E0_RUN = Path('/home/guoxiangyu/GMR_Unseen/experiments/agy_test/soccer_flash_event_query_20261015/runs/E0')

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

for directory in ('tmp', 'cache', 'logs', 'runs', 'tests'):
    (ROOT / directory).mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
tempfile.tempdir = str(ROOT / 'tmp')
sys.path.insert(0, str(PARENT / 'baseline_source'))

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
    assert path.is_relative_to(ROOT), path
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    temp.replace(path)


def write_rows(path, rows):
    path = Path(path).resolve()
    assert path.is_relative_to(ROOT), path
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

    values = read_json(PARENT / 'configs/protocol.json')
    values.update(
        n_epoch=job['epochs'],
        seed=job['seed'],
        lr=job['lr'],
        grad_clip=job['grad_clip'],
        wd=job['wd'],
        device=torch.device(device),
        config=str(PARENT / 'baseline_source/configs/flash_vtg_gmr/model.py'),
        train_path=str(PARENT / 'data/train.jsonl'),
        eval_path=str(PARENT / 'data/val.jsonl'),
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
    path = PARENT / 'tests/fixture_val.jsonl' if smoke else PARENT / 'data' / f'{split}.jsonl'
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
    assert len(dataset) == len(read_rows(path))
    return dataset
