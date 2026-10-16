"""All output is confined to this independent experiment."""
from pathlib import Path
import os,sys,json,hashlib,tempfile
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
ASSETS=Path('/home/guoxiangyu/VLMbasedIter_momentretrival/generalized-moment-retrieval/Soccergmr')
os.chdir(ROOT)
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'native_source'))
tempfile.tempdir='tmp'
for k,v in {'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(ROOT/'tmp'),'XDG_CACHE_HOME':str(ROOT/'cache'),
            'TORCH_HOME':str(ROOT/'cache/torch'),'MPLCONFIGDIR':str(ROOT/'cache/matplotlib'),
            'OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','MKL_THREADING_LAYER':'GNU'}.items():os.environ[k]=v

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()

def save(path,obj):
    p=Path(path).resolve();assert p.is_relative_to(ROOT),p
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');tmp.replace(p)

def rows(path):return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

def options(device='cpu'):
    import torch,nncore
    from types import SimpleNamespace
    d=json.loads((ROOT/'configs/protocol.json').read_text())
    d.update(device=torch.device(device),config=str(ROOT/'native_source/configs/flash_vtg_gmr/model.py'),
             train_path=str(ROOT/'data/train.jsonl'),eval_path=str(ROOT/'data/val.jsonl'),
             v_feat_dirs=[str(ASSETS/'slowfast'),str(ASSETS/'clip')],t_feat_dir=str(ASSETS/'clip_text'))
    opt=SimpleNamespace(**d);opt.cfg=nncore.Config.from_file(opt.config)
    return opt

def dataset(opt,split,labels,fixture=False):
    from training.flash_vtg_gmr.dataset import StartEndDataset
    path=ROOT/'tests/fixture_val.jsonl' if fixture else ROOT/'data'/f'{split}.jsonl'
    data=StartEndDataset(dset_name=opt.dset_name,data_path=str(path),
        v_feat_dirs=opt.v_feat_dirs,q_feat_dir=opt.t_feat_dir,q_feat_type=opt.q_feat_type,
        max_q_l=opt.max_q_l,max_v_l=opt.max_v_l,ctx_mode=opt.ctx_mode,normalize_v=True,normalize_t=True,
        load_labels=labels,clip_len=opt.clip_length,max_windows=opt.max_windows,
        span_loss_type=opt.span_loss_type,mr_only=True,keep_empty_gt=True)
    assert len(data)==len(rows(path)),'Missing examples are forbidden'
    return data

def scope_audit():
    before=json.loads((ROOT/'provenance/OUTSIDE_BEFORE.json').read_text())
    changed=[p for p,h in before.items() if sha(p)!=h]
    assert not changed,changed
    return {'checked':len(before),'changed':changed}
