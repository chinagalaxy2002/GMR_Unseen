"""Durable feature preparation -> validation -> 15 baseline runs and reports."""
import datetime
import fcntl
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path
from common import ROOT, REPO, NUMERICAL, GMR, environment, save_json
from prepare_experiment import inventory


def status(stage, **kwargs):
    save_json(ROOT / 'BACKGROUND_STATUS.json', dict(stage=stage, updated=datetime.datetime.now().isoformat(), **kwargs))
    print(datetime.datetime.now().isoformat(), stage, kwargs, flush=True)


def run(command, log, gpu=None):
    with (ROOT / log).open('a') as out:
        subprocess.run(command, cwd=REPO, env=environment(gpu), stdout=out, stderr=subprocess.STDOUT, check=True)


def main():
    extractor = str(ROOT / 'prepare_features.py')
    status('validating_release')
    run([GMR, str(REPO / 'scripts/validate_soccer_gmr_unseen.py'), '--source', str(REPO / 'data/label/Full'), '--release', str(REPO / 'data/release/soccer_gmr_unseen_v1')], 'validation.log')
    if not (ROOT / 'MISSING_VIDEO_FEATURES.json').exists():
        run([NUMERICAL, extractor, 'initialize'], 'feature_initialize.log')
    if not (ROOT / 'FEATURE_COMPATIBILITY.json').exists():
        status('checking_feature_extractor')
        if not (ROOT / 'FEATURE_PROBE.json').exists():
            run([NUMERICAL, extractor, 'probe'], 'feature_probe.log', 0)
        probe = json.loads((ROOT / 'FEATURE_PROBE.json').read_text())
        compatible = all(v['mean_cosine'] >= .98 and v['existing_shape'] == v['new_shape'] for v in probe['results'].values())
        if not compatible:
            # Never mix different feature recipes or overwrite source features.
            stems = sorted({Path(r['vid']).stem for r in inventory().values()})
            for name in ('clip', 'slowfast'):
                for path in (ROOT / 'features' / name).glob('*.npz'):
                    if path.is_symlink():
                        path.unlink()
            save_json(ROOT / 'MISSING_VIDEO_FEATURES.json', stems)
        save_json(ROOT / 'FEATURE_COMPATIBILITY.json', dict(probe=probe, reuse_existing=compatible,
            protocol='Reuse original features only if both modalities have matching shape and mean cosine >=0.98; otherwise extract all videos uniformly.'))
    status('extracting_text_features')
    run([NUMERICAL, extractor, 'text'], 'text_features.log', 0)
    feature_workers = int(os.environ.get('SOCCER_FEATURE_WORKERS', '12'))
    assert 1 <= feature_workers <= 12
    status('extracting_video_features', workers=feature_workers, gpus=[0,1], workers_per_gpu='round-robin')
    children = []
    streams = []
    try:
        for worker in range(feature_workers):
            out = (ROOT / ('video_features_%d.log' % worker)).open('a')
            streams.append(out)
            children.append(subprocess.Popen([NUMERICAL, extractor, 'video', '--worker', str(worker),
                '--num_workers', str(feature_workers)], cwd=REPO,
                env=environment(worker % 2), stdout=out, stderr=subprocess.STDOUT))
        codes = [p.wait() for p in children]
        if any(codes):
            raise RuntimeError('Video feature workers failed: ' + str(codes))
    finally:
        for p in children:
            if p.poll() is None:
                p.terminate()
        for out in streams:
            out.close()
    records = inventory()
    missing_videos = sorted({Path(r['vid']).stem for r in records.values()
        if not all((ROOT/'features'/n/(Path(r['vid']).stem+'.npz')).is_file() for n in ('clip','slowfast'))})
    missing_set = set(missing_videos)
    missing_qids = sorted(qid for qid,r in records.items() if Path(r['vid']).stem in missing_set)
    missing_text = sorted(qid for qid in records if not (ROOT/'features/clip_text'/('qid'+qid+'.npz')).is_file())
    save_json(ROOT/'FEATURE_COVERAGE.json',dict(total_queries=len(records),missing_videos=missing_videos,
        missing_video_qids=missing_qids,missing_text_qids=missing_text,full_coverage=not (missing_videos or missing_text)))
    status('training_and_evaluating', settings=15,missing_videos=len(missing_videos),
        affected_queries=len(missing_qids),feature_policy='exclude affected qids in frozen experiment snapshots')
    run([GMR, str(ROOT / 'run_baselines.py')], 'baseline_queue.log')
    status('complete', settings=15)


if __name__ == '__main__':
    with (ROOT / 'background.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            main()
        except Exception as error:
            status('failed', error=str(error))
            traceback.print_exc()
            sys.exit(1)
