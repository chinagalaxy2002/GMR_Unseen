"""Paths and immutable protocol for the V3 addSeen replication."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
NATIVE = ROOT / 'native_source'
RELEASE = REPO / 'data/release/soccer_gmr_unseen_v1'
GROUPS = ('A1_soccer', 'A2_soccer', 'A3_soccer', 'C1_soccer', 'C2_soccer')
BACKBONES = ('moment', 'qd', 'flash')
GMR = '/home/guoxiangyu/miniconda3/envs/gmr/bin/python'
NUMERICAL = '/home/guoxiangyu/miniconda3/envs/univtg/bin/python'
PARSER = '/home/guoxiangyu/miniconda3/envs/owvtg/bin/python'
VIDEO = ROOT / 'features'


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment(gpu=None):
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='2', MKL_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2',
               TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD='1')
    if gpu is not None:
        env['CUDA_VISIBLE_DEVICES'] = str(gpu)
    return env
