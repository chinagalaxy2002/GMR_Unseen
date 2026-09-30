"""Freeze train/seen-only assets for the unattended queue; never read U labels."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];REPO=HERE.parents[1]
root=Path(sys.argv[1]).resolve();assert root.is_relative_to(HERE/'runs');root.mkdir(exist_ok=True)
path=root/'FROZEN_ASSETS.json';assert not path.exists()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
prior=json.loads((HERE/'runs/stage0/manifest.json').read_text());files=set()
for split,item in prior['splits'].items():
 train=REPO/'data/release/semantic_existence_v2'/split/'train.jsonl';val=REPO/'features/semantic_existence_v2'/split/'val_seen.jsonl';assert sha(train)==item['train_sha256']
 for p in (train,val):
  files.add(p)
  for row in map(json.loads,p.read_text().splitlines()):
   files.add(REPO/'features/semantic_existence_v2'/split/'clip_text'/f"qid{row['qid']}.npz")
   for kind in ('vid_clip','vid_slowfast'):files.add(Path('/home/guoxiangyu/paper/新建文件夹/charades')/kind/f"{Path(row['vid']).stem}.npz")
 for b in item['baselines'].values():
  for p,h in zip(b['checkpoint_paths'],b['checkpoint_sha256']):assert sha(p)==h;files.add(Path(p))
view=HERE/'runs'/json.loads((HERE/'code/configs/execution_queue.json').read_text())['development_view'];manifest=json.loads((view/'view_manifest.json').read_text())
for p in manifest['derived'].values():
 q=Path(p['path']);assert sha(q)==p['sha256'];files.add(q)
for folder in ('models','training','configs'):
 for p in (REPO/folder).rglob('*'):
  if p.is_file() and p.suffix in ('.py','.yml'):files.add(p)
result={'scope':'original train and seen validation only; original checkpoint/config assets; training-side pseudo view','assets_sha256':{str(p):sha(p) for p in sorted(files)},'source_stage0_sha256':sha(HERE/'runs/stage0/manifest.json')}
path.write_text(json.dumps(result,indent=2));print(path,len(files))
