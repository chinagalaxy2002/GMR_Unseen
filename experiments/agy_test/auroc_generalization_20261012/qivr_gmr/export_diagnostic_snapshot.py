#!/usr/bin/env python3
"""Export bounded diagnostic records without pausing training or copying weights.

Creates a fresh directory, SHA256 manifest and explicit exclusions. JSONL tails
are trimmed to complete lines; NPZ/JSON must validate. candidate_cache.pt files
are converted to portable JSONL.GZ without model tensors or pickle.
"""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import zipfile

ALLOWED={'.py','.md','.json','.jsonl','.csv','.npz','.log','.sh','.yaml','.yml','.toml','.txt','.gz'}
SKIP_DIRS={'__pycache__','.git','features','cache','results','logs'}


def digest(data):return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[4])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();repo=args.repo.resolve();output=args.output.resolve()
    if output.exists():parser.error('A fresh output directory is required')
    output.mkdir(parents=True)
    relative=Path('experiments/agy_test/auroc_generalization_20261012/qivr_gmr');root=repo/relative
    captured=datetime.now().astimezone().isoformat();entries=[];excluded=[];sources=[]
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if not p.is_file() or p.is_symlink():continue
        # Preserve run results/logs under monitoring; skip historical feature caches.
        if rel.parts[0] in ('cache',) or '__pycache__' in rel.parts:continue
        if p.suffix in ALLOWED or p.name=='candidate_cache.pt' or p.name in ('LICENSE','NOTICE'):sources.append(p)
        else:excluded.append(dict(path=str(p.relative_to(repo)),reason='weights, temporary or non-diagnostic artifact',bytes=p.stat().st_size))
    for folder in ('baseline_slot_diagnostics_20261012','training_free_auroc_20261012'):
        base=repo/'experiments/agy_test'/folder
        for p in base.rglob('*'):
            if p.is_file() and not p.is_symlink() and not any(x in SKIP_DIRS for x in p.relative_to(base).parts) and p.suffix in ALLOWED:sources.append(p)
    # Original native configs referenced by the registry; weights/features remain external.
    for family in ('v3_release_baselines_20261009','charades_cg_baselines_20261010','soccer_unseen_baselines_20261011'):
        base=repo/'experiments/agy_test'/family/'native_source'
        for p in base.rglob('*'):
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.md','.json','.yaml','.yml','.txt'):sources.append(p)
    # Freeze per-file sizes first; subsequent training appends do not enter this export.
    listed=[(p,p.stat().st_size) for p in sorted(set(sources))]
    for p,limit in listed:
        rel=p.relative_to(repo);dest=output/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        if p.name=='candidate_cache.pt':
            import numpy as np
            import torch
            records=torch.load(p,map_location='cpu',weights_only=False)
            def portable(value):
                if isinstance(value,np.ndarray):return value.tolist()
                if isinstance(value,np.generic):return value.item()
                if torch.is_tensor(value):return value.detach().cpu().tolist()
                raise TypeError(type(value).__name__)
            dest=dest.with_suffix('.jsonl.gz')
            with gzip.open(dest,'wt',encoding='utf-8') as stream:
                for row in records:stream.write(json.dumps(row,default=portable,ensure_ascii=False,allow_nan=False)+'\n')
            data=dest.read_bytes();entries.append(dict(path=str(dest.relative_to(output)),source=str(rel),source_format='torch candidate records',format='portable JSONL.GZ',sha256=digest(data),bytes=len(data)))
            continue
        with p.open('rb') as stream:data=stream.read(limit)
        trimmed=0
        if p.suffix=='.jsonl':
            complete=data.rfind(b'\n')+1;trimmed=len(data)-complete;data=data[:complete]
            # Validate a possibly interrupted final record, without scanning enormous rows twice.
            if data:
                try:json.loads(data.rstrip(b'\n').split(b'\n')[-1])
                except (ValueError,UnicodeDecodeError):
                    excluded.append(dict(path=str(rel),reason='in-flight invalid JSONL tail'));continue
        elif p.suffix=='.json':
            try:json.loads(data)
            except (ValueError,UnicodeDecodeError):
                excluded.append(dict(path=str(rel),reason='in-flight invalid JSON'));continue
        elif p.suffix=='.npz':
            import io
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    if archive.testzip() is not None:raise ValueError('CRC failure')
            except (ValueError,zipfile.BadZipFile):
                excluded.append(dict(path=str(rel),reason='in-flight incomplete NPZ'));continue
        if len(data)>=95*1024*1024:raise RuntimeError(f'File needs chunking before GitHub upload: {rel}')
        if p.suffix not in ('.npz','.gz') and re.search(rb'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}',data):
            raise RuntimeError(f'Possible credential in export; file withheld: {rel}')
        dest.write_bytes(data);entries.append(dict(path=str(rel),sha256=digest(data),bytes=len(data),source_size_at_listing=limit,trimmed_incomplete_tail_bytes=trimmed))
    # Root README is the prepared GitHub navigation version.
    readme=(root/'monitoring/GITHUB_README.md').read_text()
    readme=readme.replace('README 与本地记录已准备；此状态不代表记录已上传','本分支附带本次诊断快照；具体范围见上传清单')
    readme=readme.replace('状态快照：**2026-10-13 00:13:55，Asia/Shanghai**。',f'训练进度表的状态快照：**2026-10-13 00:13:55，Asia/Shanghai**。本次归档时间：**{captured}**；最新归档进度见 [上传清单](DIAGNOSTIC_SNAPSHOT.json)。')
    readme+='\n## 本次上传快照\n\n参见 [文件与 SHA256 清单](DIAGNOSTIC_SNAPSHOT.json)。训练没有暂停，不同文件的末端进度可能略有差异；JSONL 仅保留完整行，上传后继续增长的内容不包含在此快照中。candidate_cache.pt 已转换为 candidate_cache.jsonl.gz，内容是候选记录，不包含模型权重。checkpoint、特征与模型缓存未上传；被排除或尚在写入的文件列于清单。\n'
    (output/'README.md').write_text(readme)
    entries.append(dict(path='README.md',sha256=digest((output/'README.md').read_bytes()),bytes=(output/'README.md').stat().st_size))
    queue=root/'monitoring/experiments/baseline_full_diagnostics_20261013/STATUS.json'
    state=json.loads((output/queue.relative_to(repo)).read_text())
    manifest=dict(captured_at=captured,finished_at=datetime.now().astimezone().isoformat(),
        source_root=str(root),queue_state=state['state'],job_counts=dict(Counter(j['state'] for j in state['jobs'].values())),
        scope='Baseline full diagnostics plus separately labelled historical QIVR/cancelled engineering records and script dependencies',
        consistency='bounded per-file snapshot; training not paused; no claim of atomic global training state',
        files=entries,excluded=excluded,file_count=len(entries),total_bytes=sum(e['bytes'] for e in entries))
    (output/'DIAGNOSTIC_SNAPSHOT.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),files=len(entries),bytes=manifest['total_bytes'],excluded=len(excluded),jobs=manifest['job_counts'])))


if __name__=='__main__':main()
