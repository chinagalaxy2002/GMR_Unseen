"""Isolated, read-only access to original training-side assets."""
import os, sys, json, hashlib, datetime
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parents[1]
os.environ['TMPDIR'] = str(BASE / 'cache/tmp')
os.environ['XDG_CACHE_HOME'] = str(BASE / 'cache')
os.environ['TORCH_HOME'] = str(BASE / 'cache/torch')
os.environ['MPLCONFIGDIR'] = str(BASE / 'cache/matplotlib')
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE / 'cache/deps'))
REPO = BASE.parents[1]
OLD = BASE.parent / 'correspondence_generalization'
STAGE = OLD / '2026年9月30日_存在与定位共同泛化的机制诊断'
RUNS = {
    'throw': OLD / 'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1',
    'open_close': STAGE / 'runs/open_close_qd_gmr_baseline_s3407_attempt1',
    'sit': STAGE / 'diagnostics/sit/baseline/evaluation_bundle',
}
VIDEO = Path('/home/guoxiangyu/paper/新建文件夹/charades')
TEXT = REPO / 'features/semantic_existence_v2/A1/clip_text'
FAMILIES = list(RUNS)
MODULES = ['H', 'P', 'C', 'J', 'T']
SEED = 3407

def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]

def rows(family, split):
    filename = {'train': 'train', 'seen': 'val_seen', 'pseudo': 'pseudo'}[split]
    return read(RUNS[family] / 'views' / (filename + '.jsonl'))

def dump(path, obj):
    path = BASE / path
    assert path.resolve().is_relative_to(BASE)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False,
                              default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x.item() if isinstance(x, np.generic) else str(x)) + '\n')
    tmp.replace(path)

def jsonl(path, objects):
    path = BASE / path
    assert path.resolve().is_relative_to(BASE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, allow_nan=False) + '\n' for x in objects))

def status(stage, state, **extra):
    path = BASE / 'STATUS.json'
    d = json.loads(path.read_text()) if path.exists() else {'started': now(), 'stages': {}}
    d['stages'][stage] = {'state': state, 'at': now(), **extra}
    d['updated'] = now()
    dump('STATUS.json', d)
    with (BASE / 'runs/minimal_validation/events.jsonl').open('a') as f:
        f.write(json.dumps({'stage': stage, **d['stages'][stage]}, ensure_ascii=False) + '\n')

def normalized(x):
    x = np.asarray(x, dtype=np.float32)
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-5)

def visual(vid):
    a = np.load(VIDEO / 'vid_clip' / (vid + '.npz'))['features'][:200]
    m = np.load(VIDEO / 'vid_slowfast' / (vid + '.npz'))['features'][:200]
    n = min(len(a), len(m))
    assert n > 0 and a.shape[1] == 512 and m.shape[1] == 2304
    return normalized(a[:n]), normalized(m[:n])

def gtmask(row, n):
    # Original loader assumes one-second bins. This is NOT verified extraction timing.
    t = np.arange(n) + .5
    mask = np.zeros(n, dtype=bool)
    for l, r in row.get('relevant_windows', []):
        mask |= (t >= l) & (t < r)
    if not mask.any():
        for l, r in row.get('relevant_windows', []):
            mask |= (np.arange(n) < r) & (np.arange(n) + 1 > l)
    return mask

def auc(y, score, weight=None):
    y, score = np.asarray(y), np.asarray(score)
    weight = np.ones(len(y)) if weight is None else np.asarray(weight)
    if weight[y == 1].sum() == 0 or weight[y == 0].sum() == 0:
        return None
    order = np.argsort(score, kind='stable')
    s, yy, w = score[order], y[order], weight[order]
    starts = np.r_[0, np.flatnonzero(np.diff(s)) + 1]
    wp = np.add.reduceat(w * (yy == 1), starts)
    wn = np.add.reduceat(w * (yy == 0), starts)
    return float(np.sum(wp * (np.cumsum(wn) - wn / 2)) / (wp.sum() * wn.sum()))

def ci(values):
    a = np.array([x for x in values if x is not None], dtype=float)
    return [float(x) for x in np.quantile(a, [.025, .975])] if len(a) else None
