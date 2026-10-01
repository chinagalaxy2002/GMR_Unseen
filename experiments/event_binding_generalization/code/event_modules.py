"""Five comparable small heads. Original backbone/model is never imported."""
from common import *
import torch
from torch import nn

class EventHead(nn.Module):
    def __init__(self, kind):
        super().__init__(); self.kind = kind
        if kind == 'T':
            self.text = nn.Sequential(nn.Linear(1536,64), nn.GELU(), nn.Linear(64,64), nn.GELU(), nn.Linear(64,1))
        else:
            self.motion = nn.Linear(2304,32); self.appearance = nn.Linear(512,32)
            self.action = nn.Linear(512,32, bias=False); self.entity = nn.Linear(512,32, bias=False)
            if kind in ['P','C']:
                self.a_read = nn.Sequential(nn.Linear(32,64), nn.GELU(), nn.Linear(64,1))
                self.e_read = nn.Sequential(nn.Linear(32,64), nn.GELU(), nn.Linear(64,1))
            elif kind == 'H':
                self.read = nn.Sequential(nn.Linear(64,72), nn.GELU(), nn.Linear(72,1))
            else:
                self.read = nn.Sequential(nn.Linear(96,48), nn.GELU(), nn.Linear(48,1))

    def forward(self, a, m, q, v, n, components=False):
        if self.kind == 'T':
            out = self.text(torch.cat([q,v,n],-1)).expand(-1,a.shape[1])
            return (out, None, None) if components else out
        usev, usen = (q,q) if self.kind=='H' else (v,n)
        za = torch.tanh(self.motion(m * (2304**.5)) + self.action(usev * (512**.5))[:,None,:])
        ze = torch.tanh(self.appearance(a * (512**.5)) + self.entity(usen * (512**.5))[:,None,:])
        if self.kind in ['P','C']:
            sa, se = self.a_read(za).squeeze(-1), self.e_read(ze).squeeze(-1)
            if self.kind == 'P':
                out = (sa+se)/(2**.5)
            else:
                lp = nn.functional.logsigmoid(sa)+nn.functional.logsigmoid(se)
                # log(p/(1-p)), stable and differentiable; explicit same-time AND.
                out = lp-torch.log(-torch.expm1(lp).clamp_max(-1e-7))
            return (out, sa, se) if components else out
        values = torch.cat([za,ze],-1) if self.kind=='H' else torch.cat([za,ze,za*ze],-1)
        out = self.read(values).squeeze(-1)
        return (out, None, None) if components else out

def pool(logits, lengths):
    valid = torch.arange(logits.shape[1], device=logits.device)[None,:] < lengths[:,None]
    sorted_scores = logits.masked_fill(~valid, -1e6).sort(-1, descending=True).values
    k = torch.ceil(lengths.float()*.2).long().clamp_min(1)
    selected = torch.arange(logits.shape[1],device=logits.device)[None,:] < k[:,None]
    return (sorted_scores*selected).sum(-1)/k

def params():
    return {kind:sum(p.numel() for p in EventHead(kind).parameters()) for kind in MODULES}

def prepare():
    assert (BASE / 'audit/INPUT_AUDIT.json').exists()
    status('event_cache', 'running')
    torch.manual_seed(SEED)
    a=torch.randn(2,7,512,requires_grad=True);m=torch.randn(2,7,2304,requires_grad=True)
    q=torch.randn(2,512);v=torch.randn(2,512);n=torch.randn(2,512)
    jj=EventHead('J');z=jj(a,m,q,v,n);z.sum().backward()
    assert a.grad.abs().sum()>0 and m.grad.abs().sum()>0 and torch.isfinite(z).all()
    cc=EventHead('C');out,sa,se=cc(a.detach(),m.detach(),q,v,n,components=True)
    error=float((out.sigmoid()-sa.sigmoid()*se.sigmoid()).abs().max().detach())
    assert error<1e-5 and torch.isfinite(out).all()
    dump('audit/ARCHITECTURE_CONTRACT.json',{'single_primary_pair_J_visual_appearance_gradient_norm':float(a.grad.norm()),
                                         'single_primary_pair_J_visual_motion_gradient_norm':float(m.grad.norm()),
                                         'C_probability_product_max_error':error,'original_model_imported':False,'backbone_updates':0,
                                         'meaning':'architecture contract only, not evidence of event correctness'})
    decomposition = {x['qid']: x for x in read(BASE / 'audit/QUERY_DECOMPOSITION.jsonl')}
    textcache = {}; visualcache = {}
    def text(x):
        qid = str(x['qid'])
        if qid not in textcache:
            feat = normalized(np.load(TEXT / f'qid{qid}.npz')['last_hidden_state'][:32])
            d = decomposition[qid]
            textcache[qid] = (feat.mean(0), feat[d['action_indices']].mean(0), feat[d['object_indices']].mean(0))
        return textcache[qid]
    for fam in FAMILIES:
        for split in ['train','seen','pseudo']:
            out = BASE / 'cache/event' / fam / split
            if (out / 'DONE.json').exists():
                continue
            out.mkdir(parents=True, exist_ok=True); rs = rows(fam,split)
            for x in rs:
                if x['vid'] not in visualcache:
                    visualcache[x['vid']] = visual(x['vid'])
            maxlen = max(len(visualcache[x['vid']][0]) for x in rs)
            # Disk arrays remain isolated; mmap lets parallel fits share the OS page cache.
            aa = np.lib.format.open_memmap(out/'appearance.npy', mode='w+', dtype=np.float32, shape=(len(rs),maxlen,512))
            mm = np.lib.format.open_memmap(out/'motion.npy', mode='w+', dtype=np.float32, shape=(len(rs),maxlen,2304))
            aa[:] = 0; mm[:] = 0
            q=[]; v=[]; n=[]; length=[]; gt=[]
            for i,x in enumerate(rs):
                a,m = visualcache[x['vid']]; ll=len(a); aa[i,:ll]=a; mm[i,:ll]=m
                qq,vv,nnn = text(x); q.append(qq); v.append(vv); n.append(nnn); length.append(ll)
                mask = np.zeros(maxlen,dtype=bool)
                if x['exist_label']==1:
                    mask[:ll] = gtmask(x,ll)
                gt.append(mask)
            aa.flush(); mm.flush(); del aa,mm
            for name, arr in [('query',q),('verb',v),('noun',n),('length',length),('gt',gt),('label',[x['exist_label'] for x in rs])]:
                np.save(out/(name+'.npy'),np.array(arr))
            jsonl(str((out/'rows.jsonl').relative_to(BASE)), rs)
            dump(str((out/'DONE.json').relative_to(BASE)), {'rows':len(rs), 'maxlen':maxlen, 'time_alignment':'original assumed one-second indices', 'text_role_source':'audited graph/BPE spans'})
            print('cached',fam,split,len(rs),maxlen,flush=True)
    # Source revision recorded before any event fitting; no pseudo scores inspected.
    dump('EVENT_CODE_FREEZE.json', {'at':now(), 'parent_freeze_sha256':sha(BASE/'EXECUTION_FREEZE.json'),
                                  'code_sha256':{str(p.relative_to(BASE)):sha(p) for p in (BASE/'code').glob('*.py')},
                                  'parameters_per_module':params(), 'total_event_parameters_fitted':3*sum(params().values()),
                                  'span_rule_revision':'before token audit/event fitting: graph spans or unique lexical/regular+fixed irregular match; action probe unchanged',
                                  'resources':'2 GPUs, up to 2 fit processes per GPU, at most4; no variants or multiseed'})
    status('event_cache','completed', parameters_per_module=params())

class Arrays:
    def __init__(self,fam,split):
        self.root = BASE/'cache/event'/fam/split
        self.arr = {k:np.load(self.root/(k+'.npy'),mmap_mode='r') for k in ['appearance','motion','query','verb','noun','length','gt','label']}
        self.rows = read(self.root/'rows.jsonl')
    def batch(self,idx,device,text_idx=None):
        lengths = np.array(self.arr['length'][idx]); maxlen=int(lengths.max())
        output = [torch.as_tensor(np.array(self.arr[k][idx,:maxlen]),device=device) for k in ['appearance','motion']]
        tid = idx if text_idx is None else text_idx
        output += [torch.as_tensor(np.array(self.arr[k][tid]),dtype=torch.float32,device=device) for k in ['query','verb','noun']]
        output += [torch.as_tensor(lengths,device=device),torch.as_tensor(np.array(self.arr['label'][idx]),dtype=torch.float32,device=device),torch.as_tensor(np.array(self.arr['gt'][idx,:maxlen]),device=device)]
        return output

def predict(model,data,device,text_mapping=None):
    scores=[]; maps=[]; actions=[]; entities=[]
    model.eval()
    with torch.no_grad():
        for start in range(0,len(data.rows),64):
            idx=np.arange(start,min(start+64,len(data.rows)))
            tid = None if text_mapping is None else text_mapping[idx]
            a,m,q,v,n,ll,y,gt=data.batch(idx,device,tid)
            logits,sa,se=model(a,m,q,v,n,components=True)
            scores.extend(pool(logits,ll).cpu().tolist())
            maps.extend(logits[i,:int(l)].cpu().numpy() for i,l in enumerate(ll))
            if sa is not None:
                actions.extend(pool(sa,ll).cpu().tolist());entities.extend(pool(se,ll).cpu().tolist())
    return np.array(scores),maps,np.array(actions),np.array(entities)

def fit(fam,kind,device):
    assert (BASE/'EVENT_CODE_FREEZE.json').exists()
    checkpoint=BASE/f'runs/minimal_validation/{fam}_{kind}.pt'
    assert not checkpoint.exists(), 'Never reset an existing selected fit.'
    torch.set_num_threads(2);torch.manual_seed(SEED);np.random.seed(SEED)
    tr,va=Arrays(fam,'train'),Arrays(fam,'seen')
    model=EventHead(kind).to(device);opt=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
    weights = {i:len(tr.rows)/(2*sum(x['exist_label']==i for x in tr.rows)) for i in [0,1]}
    history=[];best=-1;best_state=None
    for epoch in range(8):
        model.train();order=np.random.permutation(len(tr.rows));losses=[]
        for idx in [order[start:start+64] for start in range(0,len(order),64)]:
            a,m,q,v,n,ll,y,gt=tr.batch(idx,device)
            logits=model(a,m,q,v,n);score=pool(logits,ll)
            w=torch.where(y==1,weights[1],weights[0])
            bag=nn.functional.binary_cross_entropy_with_logits(score,y,reduction='none')
            valid=torch.arange(logits.shape[1],device=device)[None,:]<ll[:,None]
            support=torch.where((y==1)[:,None],gt,valid)
            sign=torch.where(y==1,-1.,1.)[:,None]
            local=(nn.functional.softplus(sign*logits)*support).sum(-1)/support.sum(-1).clamp_min(1)
            local=local*(support.sum(-1)>0)
            loss=(w*(bag+.5*local)).mean()
            opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),5);opt.step();losses.append(float(loss.detach()))
        scores,_,_,_=predict(model,va,device)
        value=auc(va.arr['label'],scores)
        history.append({'epoch':epoch+1,'loss':float(np.mean(losses)),'seen_AUROC':value})
        print(fam,kind,epoch+1,round(history[-1]['loss'],4),round(value,4),flush=True)
        if value>best:
            best=value;best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};best_epoch=epoch+1
        dump(f'runs/minimal_validation/{fam}_{kind}_history.json',history)
    torch.save({'state':best_state,'family':fam,'module':kind,'selected_epoch':best_epoch,'seen_AUROC':best,'parameters':sum(p.numel() for p in model.parameters()),'seed':SEED,'code_freeze_sha256':sha(BASE/'EVENT_CODE_FREEZE.json')},checkpoint)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['prepare','fit']);parser.add_argument('--family');parser.add_argument('--module');parser.add_argument('--device',default='cuda:0')
    args=parser.parse_args()
    if args.operation=='prepare':
        prepare()
    else:
        fit(args.family,args.module,args.device)
