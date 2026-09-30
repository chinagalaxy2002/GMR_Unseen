"""Portable, opt-in rerun of one A1/QD experiment using archived configuration."""
import argparse, copy, gzip, json, os, shutil, sys
from pathlib import Path

STAGE = Path(__file__).resolve().parents[1]
WORK = STAGE.parent
REPO = WORK.parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--track', choices=['gmr', 'vtg'], required=True)
    parser.add_argument('--method', choices=['baseline', 'regularized', 'adapter'], required=True)
    parser.add_argument('--action', choices=['check', 'train', 'evaluate', 'all'], default='check')
    parser.add_argument('--video-root', type=Path, required=True, help='Contains vid_clip and vid_slowfast')
    parser.add_argument('--gpu', default='0')
    parser.add_argument('--run-name', default='stage1_reproduction')
    args = parser.parse_args()
    assert '/' not in args.run_name and args.run_name not in ('.', '..')
    ident = f'formal_A1_qd_{args.track}_{args.method}_s3407'
    config_file = STAGE / 'evidence/run_configs.json'
    saved = json.loads(config_file.read_text())[ident]['config']
    text_dir = REPO / 'features/semantic_existence_v2/A1/clip_text'
    video_dirs = [args.video_root.resolve() / name for name in ('vid_clip', 'vid_slowfast')]
    for path in [text_dir, *video_dirs, REPO / 'data/release/semantic_existence_v2/A1/train.jsonl']:
        assert path.exists(), f'Missing required asset: {path}'
    archive = STAGE / 'logs' / (ident + '_attempt1')
    seen_path = REPO / 'features/semantic_existence_v2/A1/val_seen.jsonl'
    # The archived GMR view contains both labels and works for both tracks.
    seen_archive = STAGE / 'logs/formal_A1_qd_gmr_baseline_s3407_attempt1/views/val_seen.jsonl.gz'
    seen_bytes = gzip.decompress(seen_archive.read_bytes())
    if seen_path.exists():
        assert seen_path.read_bytes() == seen_bytes, 'Existing seen view differs from archived protocol'
    if args.action == 'check':
        print('Asset directories and archived configuration found; no training or file mutation performed.')
        print('Actual worker verifies every selected feature and source-data hash before training.')
        return
    os.environ.update(CUDA_VISIBLE_DEVICES=args.gpu, CORRESPONDENCE_SKIP_BUDGET_AUDIT='1', PYTHONDONTWRITEBYTECODE='1')
    sys.path.insert(0, str(WORK / 'code'))
    import queue_worker as worker
    from easydict import EasyDict
    def template(backbone, split):
        assert backbone == 'qd' and split == 'A1'
        return EasyDict(copy.deepcopy(saved)), config_file
    original_configure = worker.configure
    def configure(a, run):
        opt, source = original_configure(a, run)
        opt.v_feat_dirs = [str(path) for path in video_dirs]
        opt.t_feat_dir = str(text_dir)
        return opt, source
    worker.config_template = template
    worker.configure = configure
    if not seen_path.exists():
        seen_path.parent.mkdir(parents=True, exist_ok=True)
        seen_path.write_bytes(seen_bytes)
    jobs = WORK / 'runs/reproductions' / args.run_name / 'jobs'
    jobs.mkdir(parents=True, exist_ok=True)
    frozen = jobs / 'SELECTION_FROZEN.json'
    source = STAGE / 'evidence/SELECTION_FROZEN.json'
    if frozen.exists():
        assert frozen.read_bytes() == source.read_bytes()
    else:
        shutil.copy2(source, frozen)
    run = jobs / ident
    actions = ('train', 'evaluate') if args.action == 'all' else (args.action,)
    for action in actions:
        if action == 'train':
            assert not run.exists(), f'Refusing to overwrite an existing run: {run}'
        else:
            assert (run / 'best.ckpt').exists() and not (run / 'test').exists()
        sys.argv = ['queue_worker.py', str(run), '--backbone', 'qd', '--split', 'A1', '--track', args.track, '--method', args.method, '--seed', '3407', '--action', action]
        worker.main()

if __name__ == '__main__':
    main()
