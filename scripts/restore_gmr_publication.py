#!/usr/bin/env python3
"""Restore compressed annotations and verify the publication's frozen bytes."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'docs/gmr_baseline_summary_20261011'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    packaging = json.loads((REPORT / 'PACKAGING.json').read_text())
    for item in packaging['compressed']:
        target, archive = ROOT / item['original'], ROOT / item['gzip']
        if sha256(archive) != item['gzip_sha256']:
            raise ValueError(f'Archive checksum mismatch: {archive}')
        if not target.exists():
            temporary = target.with_name(target.name + '.tmp')
            try:
                with gzip.open(archive, 'rb') as source, temporary.open('wb') as out:
                    shutil.copyfileobj(source, out)
                if sha256(temporary) != item['sha256']:
                    raise ValueError(f'Restored checksum mismatch: {target}')
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        if sha256(target) != item['sha256']:
            raise ValueError(f'Annotation checksum mismatch: {target}')
        print('Restored:', item['original'])
    for relative in packaging['datasets']:
        release = ROOT / relative
        checksum_file = release / 'checksums.sha256'
        if checksum_file.exists():
            for line in checksum_file.read_text().splitlines():
                expected, name = line.split(maxsplit=1)
                if sha256(release / name.lstrip('*')) != expected:
                    raise ValueError(f'Release checksum mismatch: {relative}/{name}')
            print('Release checksums PASS:', relative)
    manifest = REPORT / 'PUBLICATION_MANIFEST.json'
    if manifest.exists():
        files = json.loads(manifest.read_text())['files']
        for item in files:
            if sha256(ROOT / item['path']) != item['sha256']:
                raise ValueError(f'Publication checksum mismatch: {item["path"]}')
        print(f'Publication checksums PASS: {len(files)} files')


if __name__ == '__main__':
    main()
