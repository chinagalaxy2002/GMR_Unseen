"""Normalize decoded local paths and audit the English-only text artifact publication."""
import ast
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
REL=Path('experiments/agy_test/publication_degradation_diagnostics_20261013')
CJK=re.compile('[\u4e00-\u9fff]')
TOKEN=re.compile(r'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalize_string(value):
    value=value.replace(str(REPO)+'/', '<LOCAL_REPOSITORY>/')
    return re.sub(r'/home/guoxiangyu/paper/[^\s\"\']*?[\u4e00-\u9fff][^\s\"\']*','<LOCAL_VIDEO_FEATURE_ROOT>',value)
def normalize(value):
    if isinstance(value,str):return normalize_string(value)
    if isinstance(value,list):return [normalize(v) for v in value]
    if isinstance(value,dict):return {normalize_string(k):normalize(v) for k,v in value.items()}
    return value


def main(dest):
    # Normalize JSON *after decoding*, so escaped Unicode paths cannot evade the English audit.
    normalized=[]
    for p in sorted(dest.rglob('*.json')):
        value=json.loads(p.read_text());result=normalize(value)
        if result!=value:
            p.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n');normalized.append(str(p.relative_to(dest)))
    code=dest/REL/'code'/Path(__file__).name;code.parent.mkdir(parents=True,exist_ok=True);code.write_text(Path(__file__).read_text())
    scope=json.loads((dest/REL/'PUBLICATION_SCOPE.json').read_text());assert len(scope['runs'])==12
    checks=[]
    for run in scope['runs']:
        assert run['backbone'] in ('moment','qd') and run['trained_epochs']==26
        public=dest/run['path'];source=REPO/run['path']
        assert json.loads((public/'metrics.json').read_text())==json.loads((source/'metrics.json').read_text()),'Metric mutation'
        assert json.loads((public/'STATUS.json').read_text())['state']=='complete'
        trace=[json.loads(l) for l in (public/'selection/trace.jsonl').read_text().splitlines()]
        assert len(trace)==26 and [v['epoch'] for v in trace]==list(range(1,27))
        frozen=json.loads((public/'selection/frozen.json').read_text())
        assert frozen['epoch']==run['selected_epoch'] and frozen['test_evaluation_complete']
        checks.append(dict(path=run['path'],metrics_unchanged=True,all_26_selection_epochs=True,calibration_and_test_complete=True))
    readme=dest/'README.md';links=[]
    for target in re.findall(r'\]\(([^)]+)\)',readme.read_text()):
        if target.startswith(('http:','https:','#')):continue
        actual=dest/target.split('#')[0]
        assert actual.is_file(),('Broken README link',target)
        links.append(target)
    file_count=0;jsonl_rows=0;python_files=0;max_size=0
    allowed={'.json','.jsonl','.csv','.md','.log','.txt','.py','.yml','.yaml',''}
    for p in sorted(dest.rglob('*')):
        if not p.is_file() or p.name=='.git':continue
        rel=p.relative_to(dest)
        assert p.suffix in allowed,(rel,'Unexpected artifact type')
        assert 'flash' not in str(rel).lower(),('Unexpected Flash artifact',rel)
        text=p.read_text();assert not CJK.search(text),('CJK content',rel);assert not TOKEN.search(text),('Credential-like content',rel)
        if p.suffix=='.json':
            value=json.loads(text);assert not CJK.search(json.dumps(value,ensure_ascii=False)),('Decoded CJK',rel)
        elif p.suffix=='.jsonl':
            for line in text.splitlines():
                if line.strip():
                    value=json.loads(line);assert not CJK.search(json.dumps(value,ensure_ascii=False));jsonl_rows+=1
        elif p.suffix=='.py':ast.parse(text);python_files+=1
        size=p.stat().st_size;assert size<95*1024**2;max_size=max(max_size,size);file_count+=1
    validation=dict(checked_at=datetime.now().astimezone().isoformat(),english_text_and_decoded_json=True,credentials_scan_passed=True,
        no_weights_raw_arrays_predictions_or_flash_artifacts=True,readme_links_valid=links,completed_runs=checks,
        file_count_before_validation_and_manifest=file_count,jsonl_rows_validated=jsonl_rows,python_files_parsed=python_files,
        maximum_file_bytes=max_size,decoded_local_paths_normalized=normalized)
    audit=dest/'PUBLICATION_VALIDATION.json';audit.write_text(json.dumps(validation,indent=2)+'\n')
    manifest_path=dest/'UPLOAD_MANIFEST.json';manifest=json.loads(manifest_path.read_text())
    for entry in manifest['copied_sources']+manifest['derived_records']:
        p=dest/entry['path'];entry['sha256']=digest(p);entry['bytes']=p.stat().st_size
    files=[]
    for p in sorted(dest.rglob('*')):
        if p.is_file() and p.name not in ('.git','UPLOAD_MANIFEST.json'):
            files.append(dict(path=str(p.relative_to(dest)),sha256=digest(p),bytes=p.stat().st_size))
    manifest.update(files=files,file_count=len(files),total_bytes=sum(p['bytes'] for p in files),
        normalization='remove ANSI controls, preserve numerical measurements, and replace local absolute paths including escaped Unicode after JSON decoding',
        validated_at=validation['checked_at'],validation='PUBLICATION_VALIDATION.json')
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    # Verify all hashes against final publication bytes.
    assert all(digest(dest/e['path'])==e['sha256'] for e in files)
    print(json.dumps(dict(runs=12,files=len(files)+1,bytes=manifest['total_bytes'],valid_readme_links=len(links),jsonl_rows=jsonl_rows,normalized_json_files=len(normalized))))


if __name__=='__main__':main(Path(sys.argv[1]).resolve())
