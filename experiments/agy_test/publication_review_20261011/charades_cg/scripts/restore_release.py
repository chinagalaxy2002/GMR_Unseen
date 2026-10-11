#!/usr/bin/env python3
"""Restore oversized annotation files losslessly, then verify original checksums."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()
for dataset in json.loads((ROOT / 'PACKAGING.json').read_text())['datasets']:
    release = ROOT / dataset['path']
    for item in dataset['compressed']:
        target = release / item['original']
        if not target.exists():
            temporary = target.with_name(target.name + '.tmp')
            with gzip.open(release / item['gzip'], 'rb') as src, temporary.open('wb') as out:
                shutil.copyfileobj(src, out)
            assert sha(temporary) == item['sha256'], str(temporary)
            temporary.replace(target)
        assert sha(target) == item['sha256'], str(target)
    for line in (release / 'checksums.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert sha(release / name.lstrip('*')) == digest, name
    print('PASS:', dataset['path'])
