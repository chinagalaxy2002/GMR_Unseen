"""Check every baseline train/Seen-val/test input before starting training."""
import json
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ['A1', 'A2_alt', 'A3', 'C1', 'C2_alt']

def main():
    global ROOT
    p = argparse.ArgumentParser()
    p.add_argument('--raw-videos', action='store_true')
    p.add_argument('--repo-root', type=Path, default=ROOT)
    a = p.parse_args()
    ROOT = a.repo_root.resolve()
    missing = set()
    for split in SPLITS:
        for subset in ['train', 'val', 'test']:
            path = ROOT / ('features/semantic_existence_v2/' + split + '/val_seen.jsonl' if subset == 'val'
                           else 'data/release/semantic_existence_v2/' + split + '/' + subset + '.jsonl')
            if not path.exists():
                missing.add(str(path.relative_to(ROOT))); continue
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            if subset != 'test':
                assert all(r['partition'] in ['S+', 'S-'] for r in rows), str(path) + ': Unseen training/validation row'
            for r in rows:
                vid = str(r['vid'])
                if vid.endswith('.mp4'): vid = vid[:-4]
                paths = [ROOT / f'features/semantic_existence_v2/{split}/clip_text/qid{r["qid"]}.npz']
                paths += [ROOT / f'features/charades_semantic_existence/{stream}/{vid}.npz' for stream in ['clip', 'slowfast']]
                if a.raw_videos: paths.append(ROOT / f'downloads/Charades_v1_480/{vid}.mp4')
                for f in paths:
                    if not f.is_file(): missing.add(str(f.relative_to(ROOT)))
            print(f'{split}/{subset}: {len(rows)} queries checked')
        for bb in ['flash', 'moment', 'qd']:
            for subset in ['train', 'val', 'test']:
                f = ROOT / f'experiments/agy_test/independent_candidate_transfer_suite/cache/{split}/{bb}/{subset}.npz'
                if not f.is_file(): missing.add(str(f.relative_to(ROOT)))
    if missing:
        raise SystemExit('Missing inputs (' + str(len(missing)) + '):\n' + '\n'.join(sorted(missing)[:50]))
    print('All baseline query/video inputs and 45 verifier caches are present.')

if __name__ == '__main__': main()
