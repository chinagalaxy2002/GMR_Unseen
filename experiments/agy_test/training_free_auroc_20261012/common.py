"""Immutable baseline registry for the three-dataset training-free transfer."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASE = ROOT.parent
BACKBONES = ('moment', 'qd', 'flash')
SPECS = {
    'clean_v3': ('v3_release_baselines_20261009', 'v3_release_baselines_20261009',
                 ('A1_v3', 'A2_v3', 'A3_v3', 'C1_v3', 'C2_v3')),
    'charades_cg_v2': ('charades_cg_v2_evaluation_20261011', 'charades_cg_baselines_20261010', ('C3_CG',)),
    'soccer': ('soccer_unseen_baselines_20261011', 'soccer_unseen_baselines_20261011',
               ('A1_soccer', 'A2_soccer', 'A3_soccer', 'C1_soccer', 'C2_soccer')),
}


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def paths(dataset, split, bb):
    evaluation, training, _ = SPECS[dataset]
    task = BASE / evaluation / 'groups' / split
    frozen = BASE / training / 'groups' / split / 'frozen_checkpoints' / bb
    validation_name = ('best_hl_val_preds.jsonl' if bb == 'flash' else 'best_soccer_gmr_val_preds.jsonl') if dataset == 'soccer' else ('best_charadesSTA_val_preds.jsonl' if bb == 'flash' else 'best_charades_semantic_existence_val_preds.jsonl')
    return dict(task=task, native=BASE / training / 'native_source', frozen=frozen,
                checkpoint=frozen / ('model_best.ckpt' if bb == 'flash' else 'best.ckpt'),
                validation=frozen / validation_name,
                baseline=task / 'evaluation' / bb / 'predictions.npz',
                release=task / 'release' / split,
                text=BASE / evaluation / 'features' / 'clip_text',
                output=ROOT / 'inputs' / dataset / split / 'detectors' / bb)


def video_dirs(dataset):
    if dataset == 'soccer':
        p = BASE / SPECS[dataset][0] / 'features'
        return p / 'clip', p / 'slowfast'
    p = Path('/home/guoxiangyu/paper/新建文件夹/charades')
    return p / 'vid_clip', p / 'vid_slowfast'


def inventory():
    result = []
    for dataset, (_, _, splits) in SPECS.items():
        for split in splits:
            for bb in BACKBONES:
                p = paths(dataset, split, bb)
                manifest = json.loads((p['frozen'] / 'MANIFEST.json').read_text())
                assert sha(p['checkpoint']) == manifest[p['checkpoint'].name]
                assert sha(p['validation']) == manifest[p['validation'].name]
                assert p['baseline'].exists()
                result.append(dict(dataset=dataset, split=split, backbone=bb,
                                   **{k: str(v) for k, v in p.items()},
                                   checkpoint_sha256=manifest[p['checkpoint'].name],
                                   prediction_sha256=sha(p['baseline']),
                                   validation_sha256=sha(p['release'] / 'val_seen.jsonl'),
                                   test_sha256=sha(p['release'] / 'test.jsonl')))
    save(ROOT / 'BASELINE_PATHS.json', result)
    lines = ['# 本轮 33 个冻结 baseline 路径', '',
             '| 数据 | 划分 | 骨干 | 权重（本机绝对路径） | SHA256 |', '|---|---|---|---|---|']
    for r in result:
        lines.append(f"| {r['dataset']} | {r['split']} | {r['backbone']} | `{r['checkpoint']}` | `{r['checkpoint_sha256']}` |")
    (ROOT / 'BASELINE_PATHS.md').write_text('\n'.join(lines) + '\n')
    print('Verified frozen checkpoints and validation manifests:', len(result), flush=True)


if __name__ == '__main__':
    inventory()
