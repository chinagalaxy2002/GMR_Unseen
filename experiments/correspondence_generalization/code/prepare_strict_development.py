"""Repair training-side semantic isolation, retaining original row bytes."""
import hashlib,json,re,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
old=HERE/'runs/pseudo_unseen_a1_throw';dst=HERE/'runs/pseudo_unseen_a1_throw_strict';dst.mkdir(exist_ok=False)
pattern=re.compile(r'\b(?:throw|throws|throwing|threw|thrown|toss|tosses|tossing|tossed|hurl|hurls|hurling|hurled|fling|flings|flinging|flung|lob|lobs|lobbing|lobbed)\b',re.I)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((old/'view_manifest.json').read_text())
for entry in manifest['derived'].values():assert sha(entry['path'])==entry['sha256']
lines=(old/'train.jsonl').read_text().splitlines(keepends=True);rr=[json.loads(l) for l in lines]
hit=[r for r in rr if pattern.search(r['query'])];vids={r['vid'] for r in hit}
(dst/'train.jsonl').write_text(''.join(l for l,r in zip(lines,rr) if r['vid'] not in vids))
shutil.copyfile(old/'pseudo_unseen_dev.jsonl',dst/'pseudo_unseen_dev.jsonl')
val_lines=(old/'val_seen.jsonl').read_text().splitlines(keepends=True);(dst/'val_seen.jsonl').write_text(''.join(l for l in val_lines if not pattern.search(json.loads(l)['query'])))
result=dict(manifest);result.update(semantic_audit='Annotated primary throw family plus lexical throw/toss/hurl/fling/lob inflections; all extra matching training videos excluded.',lexical_pattern=pattern.pattern,extra_excluded_videos=sorted(vids),extra_lexical_rows=hit,predecessor_manifest_sha256=sha(old/'view_manifest.json'),held_videos=manifest['held_videos']+len(vids),code_sha256=sha(__file__),derived={})
source_lines=set((ROOT/'data/release/semantic_existence_v2/A1/train.jsonl').read_text().splitlines(keepends=True))
for name in ('train.jsonl','pseudo_unseen_dev.jsonl','val_seen.jsonl'):
 p=dst/name;rs=[json.loads(l) for l in p.read_text().splitlines()]
 if name!='val_seen.jsonl':assert all(l in source_lines for l in p.read_text().splitlines(keepends=True))
 result['derived'][name]={'path':str(p),'sha256':sha(p),'rows':len(rs),'labels':{str(k):sum(r['exist_label']==k for r in rs) for k in (0,1)}}
train=[json.loads(l) for l in (dst/'train.jsonl').read_text().splitlines()];dev=[json.loads(l) for l in (dst/'pseudo_unseen_dev.jsonl').read_text().splitlines()]
assert not any(pattern.search(r['query']) for r in train)
assert not {r['vid'] for r in train}&{r['vid'] for r in dev}
assert not {r['qid'] for r in train}&{r['qid'] for r in dev}
result['limitations']='Lexical/annotated-family isolation is audited; no claim of complete conceptual separation or no pretrained exposure. Extra video exclusions introduce a distribution shift. Official full-S train unchanged.'
(dst/'view_manifest.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result['derived'],indent=2))
