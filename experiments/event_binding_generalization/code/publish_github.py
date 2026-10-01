"""Publish only this experiment through an isolated Git index and worktree.

Uses a credential FILE via askpass, never a credential in a command line or URL.
No research fitting, evaluation, or original-worktree mutations occur here.
"""
from common import *
import argparse, re, subprocess, shutil, urllib.request, urllib.error, platform

PREFIX='experiments/event_binding_generalization'
REPOSITORY='chinagalaxy2002/GMR_Unseen'
REMOTE='https://github.com/'+REPOSITORY+'.git'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--token-file',type=Path,required=True)
    args=parser.parse_args();raw=args.token_file.read_text().strip()
    match=re.search(r'(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+',raw);token=match.group(0) if match else raw
    if not token or '\n' in token or '\r' in token:raise RuntimeError('Invalid credential file')
    publication=BASE/'publication';publication.mkdir(exist_ok=True)
    workspace=publication/'.local/git_upload'
    if workspace.exists():raise RuntimeError('Publication workspace already exists; inspect prior state rather than overwrite.')
    workspace.mkdir(parents=True)
    def api(path):
        # curl uses the working machine's network route; credentials enter stdin,
        # not command arguments, URLs, logs or files.
        config='header = '+json.dumps('Authorization: Bearer '+token)+'\n'
        config+='header = "Accept: application/vnd.github+json"\n'
        config+='header = "User-Agent: event-binding-publication"\n'
        proc=subprocess.run(['curl','--silent','--show-error','--retry','2','--retry-all-errors','--retry-delay','1',
                             '--max-time','30','--config','-','--write-out','\n%{http_code}',
                             'https://api.github.com/repos/'+REPOSITORY+path],input=config,capture_output=True,text=True)
        if proc.returncode:raise RuntimeError('GitHub API network error (curl exit '+str(proc.returncode)+')')
        body,code=proc.stdout.rsplit('\n',1)
        if not 200<=int(code)<300:raise RuntimeError('GitHub API HTTP '+code)
        return json.loads(body)
    metadata=api('')
    if not metadata.get('permissions',{}).get('push'):raise RuntimeError('Authenticated account lacks push permission.')
    if metadata['default_branch']!='main':raise RuntimeError('Unexpected default branch; do not select another branch silently.')
    env={**os.environ,'GIT_ASKPASS':str(BASE/'code/github_askpass.py'),'GIT_TERMINAL_PROMPT':'0',
         'EVENT_BINDING_TOKEN_FILE':str(args.token_file.resolve()),'TMPDIR':str(BASE/'cache/tmp')}
    def git(arguments,cwd=workspace):
        proc=subprocess.run(['git','-c','credential.helper=']+arguments,cwd=cwd,env=env,capture_output=True,text=True)
        if proc.returncode:
            reason=(proc.stderr or proc.stdout).replace(token,'[redacted]')[-1800:]
            raise RuntimeError('Git operation failed: '+reason)
        return proc.stdout.strip()
    original_index=REPO/'.git/index';index_before=sha(original_index)
    original_head=git(['rev-parse','HEAD'],cwd=REPO)
    parent=api('/git/ref/heads/main')['object']['sha']
    print('Preparing isolated publication against',parent,flush=True)
    git(['init','--initial-branch=main'])
    git(['remote','add','origin',REMOTE])
    git(['fetch','--depth=1','--filter=blob:none','origin','main'])
    fetched=git(['rev-parse','FETCH_HEAD'])
    if fetched!=parent:raise RuntimeError('Remote advanced during fetch; inspect before publishing.')
    git(['update-ref','refs/heads/main',parent]);git(['read-tree','HEAD'])
    git(['config','user.name',metadata['owner']['login']])
    git(['config','user.email',metadata['owner']['login']+'@users.noreply.github.com'])
    import torch, sklearn, regex, ftfy
    dump('publication/ENVIRONMENT.json',{'recorded_at':now(),'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,
                                       'scikit_learn':sklearn.__version__,'regex':regex.__version__,'ftfy':ftfy.__version__,
                                       'platform':platform.platform(),'execution_python':'/home/guoxiangyu/miniconda3/envs/gmr/bin/python',
                                       'experiment_seed':3407,'no_training_during_publication':True})
    dump('publication/PUBLICATION_PLAN.json',{'created_at':now(),'repository':REPOSITORY,'branch':'main','parent_sha':parent,
                                             'scope':PREFIX+' only','decision':'INCONCLUSIVE','include':'plans, code, audit, reports, individual predictions, maps, traces, small heads and execution/failure logs',
                                             'exclude':['cache/','**/.local/','Python bytecode','credentials','original external datasets/features/backbones/checkpoints','other local uncommitted changes'],
                                             'isolated_git_worktree':True,'local_receipt':'publication/UPLOAD_RECEIPT.json (not included in the commit it describes)'})
    def selected(p):
        rel=p.relative_to(BASE)
        if any(part in ['cache','.local','__pycache__'] for part in rel.parts):return False
        if p.suffix in ['.pyc','.pyo','.tmp','.temp']:return False
        if p.name in ['UPLOAD_STATUS.json','UPLOAD_RECEIPT.json','upload.log','UPLOAD_MANIFEST.json']:return False
        return p.is_file()
    files=sorted(p for p in BASE.rglob('*') if selected(p))
    # Selection walks directories but copies only a concrete allowlisted snapshot.
    records=[]
    for p in files:
        assert not p.is_symlink(), 'Unexpected symlink in publication payload'
        content=p.read_bytes()
        if token.encode() in content:raise RuntimeError('Credential bytes detected in selected payload: '+str(p.relative_to(BASE)))
        if len(content)>=100*1024*1024:raise RuntimeError('File exceeds GitHub regular Git limit: '+str(p.relative_to(BASE)))
        rel=str(p.relative_to(BASE));blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        records.append({'path':PREFIX+'/'+rel,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'git_blob_sha1':blob})
    dump('publication/UPLOAD_MANIFEST.json',{'created_at':now(),'repository':REPOSITORY,'branch':'main','parent_sha':parent,'files':records,
                                           'file_count_excluding_manifest':len(records),'bytes_excluding_manifest':sum(x['bytes'] for x in records),
                                           'credential_bytes_detected':False,'self_hash':'manifest intentionally does not hash itself'})
    files.append(BASE/'publication/UPLOAD_MANIFEST.json')
    expected={r['path']:r['git_blob_sha1'] for r in records}
    mp=BASE/'publication/UPLOAD_MANIFEST.json';content=mp.read_bytes()
    expected[PREFIX+'/publication/UPLOAD_MANIFEST.json']=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    for p in files:
        dst=workspace/PREFIX/p.relative_to(BASE);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    git(['add','--force','--',PREFIX])
    staged=git(['diff','--cached','--name-only']).splitlines()
    if not staged:raise RuntimeError('No new publication changes')
    if not all(p.startswith(PREFIX+'/') and p in expected for p in staged):raise RuntimeError('Unexpected staged path')
    print('Snapshot:',len(files),'files,',sum(p.stat().st_size for p in files),'bytes;',len(staged),'changed paths',flush=True)
    git(['commit','-m','Publish A/A1/B event-binding validation: controls, localization and inconclusive decision'])
    commit=git(['rev-parse','HEAD'])
    listing=git(['ls-tree','-r','HEAD','--',PREFIX])
    local_blobs={line.split('\t',1)[1]:line.split('\t',1)[0].split()[2] for line in listing.splitlines()}
    if any(local_blobs.get(p)!=h for p,h in expected.items()):raise RuntimeError('Snapshot blob verification failed')
    if api('/git/ref/heads/main')['object']['sha']!=parent:raise RuntimeError('Remote branch advanced; refusing overwrite')
    # Normal fast-forward push only; no force push, source checkout or source index changes.
    git(['push','origin','HEAD:refs/heads/main'])
    remote_head=api('/git/ref/heads/main')['object']['sha']
    if remote_head!=commit:raise RuntimeError('Remote head differs after push')
    tree=api('/git/trees/'+commit+'?recursive=1')
    if tree.get('truncated'):raise RuntimeError('Remote tree truncated; cannot verify all files')
    remote_blobs={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
    if any(remote_blobs.get(p)!=h for p,h in expected.items()):raise RuntimeError('Remote file verification failed')
    diff=api('/commits/'+commit)
    changed=[x['filename'] for x in diff.get('files',[])]
    if not set(changed).issubset(expected):raise RuntimeError('Unexpected remote changed path')
    if sha(original_index)!=index_before or git(['rev-parse','HEAD'],cwd=REPO)!=original_head:raise RuntimeError('Original local Git state unexpectedly changed')
    receipt={'state':'uploaded_and_verified','at':now(),'repository':REPOSITORY,'branch':'main','parent_sha':parent,'commit_sha':commit,
             'commit_url':'https://github.com/'+REPOSITORY+'/commit/'+commit,'directory_url':'https://github.com/'+REPOSITORY+'/tree/main/'+PREFIX,
             'report_url':'https://github.com/'+REPOSITORY+'/blob/main/'+PREFIX+'/report/REPORT.md',
             'files_uploaded_or_verified':len(expected),'changed_files':len(changed),'bytes_uploaded_snapshot':sum(p.stat().st_size for p in files),
             'remote_blob_hashes_verified':True,'only_this_experiment_changed':True,'local_original_index_unchanged':True,
             'local_original_branch_unchanged':True,'credentials_in_payload':False,'new_training_started':False,
             'excluded_cache_bytes':sum(p.stat().st_size for p in (BASE/'cache').rglob('*') if p.is_file()),
             'manifest_sha256':sha(BASE/'publication/UPLOAD_MANIFEST.json')}
    dump('publication/UPLOAD_RECEIPT.json',receipt);dump('publication/UPLOAD_STATUS.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['state','commit_url','directory_url','files_uploaded_or_verified','changed_files']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Exceptions never include request headers or the credential file contents.
        dump('publication/UPLOAD_STATUS.json',{'state':'failed','at':now(),'reason':str(exc)})
        raise SystemExit(str(exc)) from None
