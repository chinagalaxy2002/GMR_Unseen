"""Frozen Soccer experiment snapshots with explicit missing-feature exclusions."""
import hashlib
import json
import shutil
import numpy as np
from collections import Counter
from pathlib import Path
from common import ROOT, REPO, RELEASE, NATIVE, GROUPS, digest, read_rows, save_json

SOCCER = (REPO / 'Soccergmr').resolve()


def inventory():
    rows = read_rows(RELEASE / 'master/worldcup_clean.jsonl')
    by_qid = {str(r['qid']): r for r in rows}
    assert len(by_qid) == len(rows)
    return by_qid


def prepare():
    records = inventory()
    video_errors = {}
    for stem in sorted({Path(r['vid']).stem for r in records.values()}):
        try:
            lengths = []
            for name, dim in [('clip',512),('slowfast',2304)]:
                with np.load(ROOT/'features'/name/(stem+'.npz')) as data:
                    array = data['features']
                    assert array.ndim == 2 and array.shape[1] == dim and len(array) > 0 and np.isfinite(array).all()
                    lengths.append(len(array))
            assert lengths[0] == lengths[1]
        except Exception as error:
            video_errors[stem] = repr(error)
    text_cache = {}
    excluded = {}
    for qid, row in records.items():
        stem = Path(row['vid']).stem
        if stem in video_errors:
            excluded[qid] = dict(qid=qid,vid=row['vid'],query=row['query'],reason='missing_or_invalid_video_feature',error=video_errors[stem])
        else:
            feature = ROOT/'features/clip_text'/('qid'+qid+'.npz')
            key = str(feature.resolve())
            if key not in text_cache:
                try:
                    with np.load(feature) as data:
                        array = data['last_hidden_state']
                        assert array.ndim == 2 and array.shape[1] == 512 and len(array) > 0 and np.isfinite(array).all()
                    text_cache[key] = None
                except Exception as error:
                    text_cache[key] = repr(error)
            if text_cache[key] is not None:
                excluded[qid] = dict(qid=qid,vid=row['vid'],query=row['query'],reason='missing_or_invalid_text_feature',error=text_cache[key])
    save_json(ROOT/'FEATURE_EXCLUSIONS.json',dict(policy='Exclude affected qids consistently across all splits and backbones; preserve original release',
        source_queries=len(records),excluded_queries=len(excluded),invalid_videos=video_errors,records=list(excluded.values())))
    all_qids = set()
    groups = {}
    for group in GROUPS:
        target = ROOT / 'groups' / group / 'release' / group
        target.mkdir(parents=True, exist_ok=True)
        original = target/'source_annotations'
        original.mkdir(exist_ok=True)
        for source in (RELEASE / 'splits' / group).iterdir():
            if not source.is_file():
                continue
            dest = original / source.name
            if dest.exists() and digest(dest) != digest(source):
                raise ValueError('Frozen annotation changed: ' + str(source))
            shutil.copy2(source, dest)
        exclusions = {}
        for name in ('train','val','test','val_seen'):
            source_rows = read_rows(original/(name+'.jsonl'))
            retained = [r for r in source_rows if str(r['qid']) not in excluded]
            assert retained, 'Empty usable split: '+group+'/'+name
            text = ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in retained)
            dest = target/(name+'.jsonl')
            expected = hashlib.sha256(text.encode()).hexdigest()
            if dest.exists() and digest(dest) != expected:
                raise ValueError('Frozen filtered experiment annotations changed: '+str(dest))
            dest.write_text(text)
            removed = [r for r in source_rows if str(r['qid']) in excluded]
            exclusions[name] = dict(source=len(source_rows),retained=len(retained),excluded=len(removed),
                excluded_partitions=dict(Counter(r['partition'] for r in removed)),qids=[str(r['qid']) for r in removed])
        save_json(target/'FEATURE_FILTERING.json',exclusions)
        parts = {n: read_rows(target / (n + '.jsonl')) for n in ('train', 'val', 'test')}
        assert all(r['partition'] in ('S+', 'S-') for r in parts['train'])
        assert read_rows(target / 'val_seen.jsonl') == [r for r in parts['val'] if r['partition'].startswith('S')]
        for a, b in [('train', 'val'), ('train', 'test'), ('val', 'test')]:
            assert not ({Path(r['vid']).stem for r in parts[a]} & {Path(r['vid']).stem for r in parts[b]})
        for rr in parts.values():
            assert len({str(r['qid']) for r in rr}) == len(rr)
            for r in rr:
                qid = str(r['qid'])
                assert records[qid]['query'] == r['query']
                assert bool(r['relevant_windows']) == bool(r['exist_label'])
                all_qids.add(qid)
                assert (ROOT / 'features/clip_text' / ('qid' + qid + '.npz')).is_file(), qid
                for name in ('clip', 'slowfast'):
                    assert (ROOT / 'features' / name / (Path(r['vid']).stem + '.npz')).is_file(), r['vid']
        feat = ROOT / 'groups' / group / 'features' / group
        feat.mkdir(parents=True, exist_ok=True)
        for name, source in [('clip_text', ROOT / 'features/clip_text'), ('val_seen.jsonl', target / 'val_seen.jsonl')]:
            if not (feat / name).exists():
                (feat / name).symlink_to(source)
        groups[group] = dict(counts={n: dict(Counter(r['partition'] for r in rr)) for n, rr in parts.items()},
                             feature_exclusions=exclusions,
                             videos={n: len({Path(r['vid']).stem for r in rr}) for n, rr in parts.items()},
                             sha256={p.name: digest(p) for p in target.iterdir() if p.is_file()})
    source = {str(p.relative_to(RELEASE)): digest(p) for p in RELEASE.rglob('*') if p.is_file()}
    save_json(ROOT / 'RELEASE_MANIFEST.json', source)
    save_json(ROOT / 'DATA_AUDIT.json', dict(release=str(RELEASE), groups=groups, qids=len(all_qids),
        source_video_splits_preserved=True, normalized_clip_ids_disjoint=True,
        match_level_independence=False, seen_only_train=True, full_feature_coverage=True,
        feature_coverage_scope='retained experiment rows',source_qids=len(records),excluded_qids=len(excluded)))
    save_json(ROOT/'EXPERIMENT_DATA_COUNTS.json',groups)
    save_json(ROOT / 'SOURCE_MANIFEST.json', {str(p.relative_to(NATIVE)): digest(p)
        for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in p.parts})
    print('Prepared soccer annotations and full feature coverage:', len(all_qids), flush=True)


if __name__ == '__main__':
    prepare()
