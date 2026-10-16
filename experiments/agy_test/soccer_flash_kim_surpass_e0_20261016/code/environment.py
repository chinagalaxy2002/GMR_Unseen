"""Experiment-local I/O and baseline environment for Kim replication and surpassing E0."""
from pathlib import Path
import os, sys, json, hashlib, tempfile, random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path('/home/guoxiangyu/VLMbasedIter_momentretrival/generalized-moment-retrieval/Soccergmr')

# Ensure all cache, tmp, and runtime paths are self-contained
for name, value in {
    'PYTHONDONTWRITEBYTECODE': '1',
    'TMPDIR': str(ROOT / 'tmp'),
    'XDG_CACHE_HOME': str(ROOT / 'cache'),
    'TORCH_HOME': str(ROOT / 'cache/torch'),
    'MPLCONFIGDIR': str(ROOT / 'cache/matplotlib'),
    'OMP_NUM_THREADS': '4',
    'MKL_NUM_THREADS': '4',
    'MKL_THREADING_LAYER': 'GNU'
}.items():
    os.environ[name] = value

sys.dont_write_bytecode = True
tempfile.tempdir = str(ROOT / 'tmp')
sys.path.insert(0, str(ROOT / 'baseline_source'))

import numpy as np
import torch

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1048576), b''):
            h.update(part)
    return h.hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def read_rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def write_json(path, obj):
    path = Path(path).resolve()
    assert path.is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    tmp.replace(path)

def write_rows(path, rows):
    path = Path(path).resolve()
    assert path.is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    tmp.replace(path)

def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def options(job, device):
    from types import SimpleNamespace
    import nncore
    d = read_json(ROOT / 'configs/protocol.json')
    d.update(
        n_epoch=job['epochs'],
        seed=job['seed'],
        lr=job['lr'],
        grad_clip=job['grad_clip'],
        wd=job['wd'],
        device=torch.device(device),
        config=str(ROOT / 'baseline_source/configs/flash_vtg_gmr/model.py'),
        train_path=str(ROOT / 'data/train.jsonl'),
        eval_path=str(ROOT / 'data/val.jsonl'),
        v_feat_dirs=[str(ASSETS / 'slowfast'), str(ASSETS / 'clip')],
        t_feat_dir=str(ASSETS / 'clip_text'),
        use_plurality_gating=job.get('use_plurality_gating', False)
    )
    if 'lr_drop' in job:
        d['lr_drop'] = job['lr_drop']
    opt = SimpleNamespace(**d)
    opt.cfg = nncore.Config.from_file(opt.config)
    return opt

def make_dataset(opt, split, smoke=False):
    from training.flash_vtg_gmr.dataset import StartEndDataset
    assert split in ('train', 'val', 'test'), f'Unknown split: {split}'
    path = ROOT / 'tests/fixture_val.jsonl' if smoke else ROOT / 'data' / f'{split}.jsonl'
    ds = StartEndDataset(
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
        keep_empty_gt=True
    )
    assert len(ds) == len(read_rows(path)), 'Missing feature examples are not permitted'
    return ds
