"""Read-only DAO diagnosis. Original features, weights and reports are not changed."""
from pathlib import Path
from collections import defaultdict, Counter
import argparse
import hashlib
import importlib.util
import json
import sys
import numpy as np
import torch
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'experiments/agy_test/decomposed_action_object_verifier'
OUT = Path(__file__).resolve().parent
SPLITS = ['A1', 'A2_alt', 'A3', 'C1', 'C2_alt']
CLIP_CODE = Path('/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video')
WEIGHTS = Path('/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt')
VIDEO = Path('/home/guoxiangyu/paper/新建文件夹/charades')
VIS = ['v_sf_cand','v_sf_start','v_sf_end','v_sf_glob','v_clip_cand','v_clip_glob']
FIELDS = VIS + ['q_act','q_obj','h_pool','orig_logits','fg_max']
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE))
torch.set_num_threads(2)

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def write(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def norm(x):
    return x/np.maximum(np.linalg.norm(x,axis=-1,keepdims=True),1e-12)

def cosine(a,b):
    return (norm(a)*norm(b)).sum(-1)

def auc(y,s):
    return float(roc_auc_score(y,s)) if len(np.unique(y))==2 else None

def pair_indices(d, split):
    ix={str(q):i for i,q in enumerate(d['qids'])}
    pp=rows(ROOT/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl')
    assert all(str(p['positive_qid']) in ix and str(p['negative_qid']) in ix for p in pp)
    return np.array([(ix[str(p['positive_qid'])],ix[str(p['negative_qid'])]) for p in pp])

def pair_acc(s,pp):
    a,b=s[pp[:,0]],s[pp[:,1]]
    return float(np.mean((a>b)+.5*(a==b))) if len(pp) else None

def exact_pairs(d, meta):
    groups=defaultdict(list)
    for i,q in enumerate(d['qids']):
        if d['partitions'][i] in ['U+','U-']: groups[meta[str(q)]['query']].append(i)
    pp=[]; sizes=[]
    for ii in groups.values():
        pairs=[(a,b) for a in ii for b in ii if d['labels'][a]==1 and d['labels'][b]==0 and d['vids'][a]!=d['vids'][b]]
        if pairs: pp.extend(pairs);sizes.append(len(pairs))
    return np.array(pp,dtype=int).reshape(-1,2),sizes

def metrics(s,d,pp,ep=None):
    r={}
    for name,parts in [('Seen',['S+','S-']),('Unseen',['U+','U-'])]:
        m=np.isin(d['partitions'],parts);r[name+'_AUROC']=auc(d['labels'][m],s[m])
    r['Matched_PairAcc']=pair_acc(s,pp)
    if ep is not None:r['Exact_query_cross_video_PairAcc']=pair_acc(s,ep)
    return r

def feature_audit():
    ex=module('clean_extractor_audit',BASE/'extract_clean_features.py')
    tm=module('clip_tokenizer_audit',CLIP_CODE/'clip/simple_tokenizer.py')
    tok=tm.SimpleTokenizer();basic_clean=tm.basic_clean;whitespace_clean=tm.whitespace_clean
    all_groups=defaultdict(list);report={}
    mapping_cache={}
    for split in SPLITS:
        for subset in ['train','val','test']:
            z=np.load(BASE/'clean_features'/split/(subset+'.npz'))
            d={k:z[k] for k in ['qids','vids','labels','partitions','q_act','q_obj','q_sent','actions','objects','best_spans','v_sf_start','v_sf_end']}
            meta={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl'))}
            info={'n':len(d['qids']),'partitions':dict(Counter(d['partitions'].tolist())),
                  'distance_label_AUROC':auc(d['labels'],np.linalg.norm(d['q_act']-d['q_obj'],axis=1)),
                  'zero_flow_fraction':float(np.mean(np.all(d['v_sf_start']==d['v_sf_end'],axis=1))),
                  'text_mapping':{},'same_text_metadata_variants':0,'same_text_vector_variants':0}
            counts=Counter();examples=[];local=defaultdict(list)
            for i,qid in enumerate(d['qids']):
                r=meta[str(qid)];query=r['query'];a=str(d['actions'][i]);o=str(d['objects'][i]);key=(query,a,o)
                hashes=tuple(hashlib.sha256(d[k][i].tobytes()).hexdigest() for k in ['q_act','q_obj','q_sent'])
                item=(key,hashes,split,subset,str(qid),int(d['labels'][i]))
                all_groups[query].append(item);local[query].append(item)
                if key not in mapping_cache:
                    clean=whitespace_clean(basic_clean(query)).lower();act=ex.find_term_span(query,a,True);obj=ex.find_term_span(query,o,False)
                    spans=ex.extract_spans(query);L=len(tok.encode(query))+2;q_len=len(query)
                    expected=[];cursor=1
                    for m in tok.pat.finditer(clean):
                        encoded=''.join(tok.byte_encoder[b] for b in m.group().encode('utf-8'))
                        n=len(tok.bpe(encoded).split(' '));expected.append((m.start(),m.end(),list(range(cursor,cursor+n))));cursor+=n
                    issues=[]
                    for tag,span in [('action',act),('object',obj)]:
                        if not span: issues.append(tag+'_not_found');continue
                        if len(spans)+2==L:
                            picked=[j+1 for j,(s,e,_) in enumerate(spans) if not(e<=span[0] or s>=span[1])]
                        else:
                            picked=[j for j in range(1,L-1) if span[0]<=(j-.5)/(L-2)*q_len<=span[1]]
                            if not picked:picked=[max(1,min(L-2,int(round(((span[0]+span[1])/2/q_len)*(L-2)+.5))))]
                        if clean==query.lower():
                            correct=[j for s,e,ii in expected if not(e<=span[0] or s>=span[1]) for j in ii]
                            issues.append(tag+'_mapping_checked')
                            if picked!=correct:issues.append(tag+'_wrong_BPE_indices')
                        else:issues.append('normalization_changed_offsets')
                    mapping_cache[key]=issues
                counts.update(mapping_cache[key])
            for query,items in local.items():
                if len(set(v[0] for v in items))>1:info['same_text_metadata_variants']+=1
                if len(set(v[1] for v in items))>1:
                    info['same_text_vector_variants']+=1
                    if len(examples)<3:examples.append({'query':query,'rows':[{'qid':v[4],'label':v[5],'terms':v[0][1:]} for v in items[:8]]})
            info['text_mapping']=dict(counts);info['same_text_mismatch_examples']=examples
            hq=np.load(ROOT/'experiments/agy_test/cache/hq'/split/(subset+'.npz'));fg=hq['fg'];sp=hq['spans'];best=sp[np.arange(len(fg)),fg.argmax(1)]
            expected=np.clip(np.stack([best[:,0]-best[:,1]/2,best[:,0]+best[:,1]/2],axis=1),0,1)
            info['cxw_conversion_max_error']=float(np.max(np.abs(expected-d['best_spans'])))
            report[split+'/'+subset]=info
            print('FEATURE',split,subset,json.dumps(info),flush=True)
    mismatch=[(q,v) for q,v in all_groups.items() if len(set(i[1] for i in v))>1]
    write('feature_audit.json',{'subsets':report,'global_unique_queries':len(all_groups),
        'global_same_text_vector_mismatch_groups':len(mismatch),
        'global_mismatches_cross_label':sum(len(set(i[5] for i in v))==2 for q,v in mismatch),
        'examples':[{'query':q,'rows':[{'split':i[2],'subset':i[3],'qid':i[4],'label':i[5],'terms':i[0][1:]} for i in v[:8]]} for q,v in mismatch[:10]]})

def frozen_audit():
    mod=module('dao_clean_training',BASE/'train_and_eval.py')
    dev=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu');report={}
    for split in SPLITS:
        z=np.load(BASE/'clean_features'/split/'test.npz');d={k:z[k] for k in FIELDS+['qids','vids','labels','partitions']}
        meta={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/'test.jsonl')};pp=pair_indices(d,split);ep,sizes=exact_pairs(d,meta)
        model=mod.GatedDAOVerifier().to(dev);ckpt=torch.load(BASE/'clean_runs'/split/'verifier_checkpoint.pt',map_location='cpu',weights_only=False)
        model.load_state_dict(ckpt['state_dict']);model.eval();b={k:torch.tensor(d[k],device=dev,dtype=torch.float32) for k in FIELDS}
        with torch.no_grad():res=model(b)
        sg={k:v.cpu().numpy() for k,v in res.items()};aa=float(sg['alpha_act']);ao=float(sg['alpha_obj']);gate=torch.sigmoid(5*(b['fg_max']-.2)).cpu().numpy()
        scores={'baseline':d['orig_logits'],'full':sg['s_exist'],'detector_only':sg['s_det'],
            'detector_plus_action':sg['s_det']+gate*aa*sg['ev_act'],'detector_plus_object':sg['s_det']+gate*ao*sg['ev_obj'],
            'action_evidence':sg['ev_act'],'object_evidence':sg['ev_obj'],
            'action_raw':sg['raw_act'],'object_raw':sg['raw_obj'],
            'negative_text_prior':-aa*sg['prior_act']-ao*sg['prior_obj'],
            'new_branch_residual':sg['s_exist']-sg['s_det']}
        for q in ['q_act','q_obj','q_sent']:
            qv=z[q]
            for v in ['v_clip_cand','v_clip_glob']:scores[q+'_'+v+'_unprojected_cosine']=cosine(qv,d[v])
        # Existing 'text-only' zeroes new streams but retains detector video inputs.
        zero={k:torch.zeros_like(v) if k in VIS else v for k,v in b.items()}
        truezero={k:torch.zeros_like(v) if k in VIS+['h_pool','orig_logits'] else torch.full_like(v,.5) if k=='fg_max' else v for k,v in b.items()}
        with torch.no_grad():
            scores['new_streams_zero_detector_retained']=model(zero)['s_exist'].cpu().numpy()
            scores['all_visual_zero_frozen']=model(truezero)['s_exist'].cpu().numpy()
        permresults=[];rng=np.random.default_rng(3407)
        for rep in range(5):
            order=rng.permutation(len(d['qids']));bad=d['vids'][order]==d['vids']
            for attempt in range(40):
                if not bad.any():break
                order[bad]=rng.integers(len(order),size=int(bad.sum()));bad=d['vids'][order]==d['vids']
            assert not bad.any();idx=torch.tensor(order,device=dev)
            perm={k:v[idx] if k in VIS else v for k,v in b.items()}
            with torch.no_grad():s=model(perm)['s_exist'].cpu().numpy()
            permresults.append(metrics(s,d,pp,ep))
        saved={str(r['qid']):r['final_logit'] for r in rows(BASE/'clean_runs'/split/'predictions.jsonl')}
        pred_err=float(np.max(np.abs(np.array([saved[str(q)] for q in d['qids']])-scores['full'])))
        r={'prediction_max_abs_error':pred_err,'pair_n':len(pp),'pair_same_video_fraction':float(np.mean(d['vids'][pp[:,0]]==d['vids'][pp[:,1]])),
            'pair_identical_query_fraction':float(np.mean([meta[str(d['qids'][a])]['query']==meta[str(d['qids'][b])]['query'] for a,b in pp])),
            'exact_query_cross_video_pair_n':len(ep),'exact_query_groups':len(sizes),'weights':{'alpha_action':aa,'alpha_object':ao,'w_base':float(model.w_base),'w_fg':float(model.w_fg)},
            'metrics':{k:metrics(s,d,pp,ep) for k,s in scores.items()},'new_stream_different_video_controls':permresults}
        # Video-cluster CI for the matched-pair score (not independent-pair binomial).
        pair_vid=d['vids'][pp[:,0]];uv,iv=np.unique(pair_vid,return_inverse=True)
        deltas={};rng=np.random.default_rng(20261005)
        vals={k:(s[pp[:,0]]>s[pp[:,1]]).astype(float)+.5*(s[pp[:,0]]==s[pp[:,1]]) for k,s in scores.items()}
        sums={k:np.bincount(iv,weights=v,minlength=len(uv)) for k,v in vals.items()};counts=np.bincount(iv,minlength=len(uv));boots={k:[] for k in vals}
        for rep in range(2000):
            w=np.bincount(rng.integers(len(uv),size=len(uv)),minlength=len(uv));den=w@counts
            for k in boots:boots[k].append(float(w@sums[k]/den))
        r['matched_pair_video_cluster_95ci']={k:np.quantile(v,[.025,.975]).tolist() for k,v in boots.items()}
        report[split]=r
        np.savez_compressed(OUT/(split+'_frozen_scores.npz'),qids=d['qids'],vids=d['vids'],labels=d['labels'],partitions=d['partitions'],**scores)
        print('FROZEN',split,json.dumps({k:r[k] for k in ['prediction_max_abs_error','pair_n','weights','metrics']}),flush=True)
    write('frozen_diagnosis.json',report)

def clip_diagnosis(split):
    # No fitting, direction flipping, threshold selection, or architecture selection.
    tm=module('clip_tokenizer_diagnosis',CLIP_CODE/'clip/simple_tokenizer.py')
    cm=module('clip_model_diagnosis',CLIP_CODE/'clip/model.py')
    tokenizer=tm.SimpleTokenizer()
    def tokenize(texts):
        output=torch.zeros((len(texts),77),dtype=torch.long)
        for i,text in enumerate(texts):
            ids=[tokenizer.encoder['<|startoftext|>']]+tokenizer.encode(text)+[tokenizer.encoder['<|endoftext|>']]
            if len(ids)>77:raise ValueError('Query exceeds CLIP context')
            output[i,:len(ids)]=torch.tensor(ids)
        return output
    dev=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    ex=module('clean_extractor_clip_audit',BASE/'extract_clean_features.py')
    bysubset={};texts=set()
    for subset in ['train','val','test']:
        z=np.load(BASE/'clean_features'/split/(subset+'.npz'))
        rs={str(r['qid']):r for r in rows(ROOT/'data/release/semantic_existence_v2'/split/(subset+'.jsonl'))}
        d={k:z[k] for k in ['qids','vids','labels','partitions','best_spans','q_sent','q_act','q_obj','actions','objects','v_clip_cand','v_clip_glob']}
        rlist=[rs[str(q)] for q in d['qids']];byquery=[]
        for i,r in enumerate(rlist):
            q=r['query'];a=ex.find_term_span(q,str(d['actions'][i]),True);o=ex.find_term_span(q,str(d['objects'][i]),False)
            # Metadata-derived phrases are diagnostic only, not a clean method proposal.
            aq=q[a[0]:a[1]] if a else q;oq=q[o[0]:o[1]] if o else q
            qs=[q,aq,oq];texts.update(qs);byquery.append(qs)
        bysubset[subset]=(d,rlist,byquery)
    state=torch.jit.load(str(WEIGHTS),map_location='cpu').state_dict()
    model=cm.build_model(state).to(dev);model.eval()
    if dev.type=='cpu':model.float()
    vocabulary=sorted(texts);lookup={};means={};acts={};eots={};projection=model.text_projection.detach().float().cpu().numpy()
    with torch.no_grad():
        for start in range(0,len(vocabulary),128):
            batch=vocabulary[start:start+128];tokens=tokenize(batch).to(dev)
            hidden=model.encode_text(tokens)['last_hidden_state'].float();last=tokens.argmax(-1);ii=torch.arange(len(batch),device=dev)
            projected=hidden[ii,last]@model.text_projection.float()
            values=projected.cpu().numpy();hs=hidden.cpu().numpy();ls=last.cpu().numpy()
            for i,q in enumerate(batch):lookup[q]=norm(values[i]);means[q]=hs[i,1:ls[i]].mean(0);eots[q]=hs[i,ls[i]]
            if start%2048==0:print('ENCODE',start,len(vocabulary),flush=True)
    del model
    report={'split':split,'scope':'diagnostic only; no weights trained and no sign selected on Unseen','CLIP_checkpoint':str(WEIGHTS),
            'image_checkpoint_identity':'cached image encoder weight identity is not independently proven','unique_texts':len(vocabulary),'subsets':{}}
    video_cache={};sf_lengths={}
    train_d=bysubset['train'][0];_,unique_ix=np.unique(train_d['vids'],return_index=True)
    reference=norm(train_d['v_clip_glob'][unique_ix]).mean(0)
    for subset,(d,rs,qs) in bysubset.items():
        q=np.stack([lookup[v[0]] for v in qs]);qa=np.stack([lookup[v[1]] for v in qs]);qo=np.stack([lookup[v[2]] for v in qs]);qm=np.stack([means[v[0]] for v in qs]);qe=np.stack([eots[v[0]] for v in qs])
        scores={
            'cached_mean_hidden_candidate':cosine(d['q_sent'],d['v_clip_cand']),
            'fresh_mean_hidden_candidate':cosine(qm,d['v_clip_cand']),
            'fresh_mean_hidden_projected_candidate':cosine(qm@projection,d['v_clip_cand']),
            'fresh_EOT_hidden_candidate':cosine(qe,d['v_clip_cand']),
            'fresh_EOT_projected_candidate':cosine(q,d['v_clip_cand']),
            'fresh_EOT_projected_global':cosine(q,d['v_clip_glob']),
            'query_only_fixed_train_video_reference':cosine(q,np.broadcast_to(reference,q.shape)),
            'fresh_action_phrase_projected_candidate':cosine(qa,d['v_clip_cand']),
            'fresh_object_phrase_projected_candidate':cosine(qo,d['v_clip_cand'])}
        local_norm=[];frame_max=[];global_norm=[];oracle=[];ious=[];length_stats=Counter()
        for i,r in enumerate(rs):
            vid=str(d['vids'][i])
            if vid not in video_cache:
                video_cache[vid]=np.load(VIDEO/'vid_clip'/(vid+'.npz'))['features'].astype(np.float32)
                sf_lengths[vid]=len(np.load(VIDEO/'vid_slowfast'/(vid+'.npz'))['features'])
            v=video_cache[vid];T=min(len(v),sf_lengths[vid]);vn=norm(v[:T]);s,e=d['best_spans'][i];st=max(0,min(T-1,int(np.floor(s*T))));ed=min(T,max(st+1,int(np.ceil(e*T))))
            local_norm.append(cosine(q[i],vn[st:ed].mean(0)));global_norm.append(cosine(q[i],vn.mean(0)));frame_max.append(float((vn@q[i]).max()))
            length_stats['streams_unequal']+=int(len(v)!=sf_lengths[vid]);length_stats['length_gt200']+=int(T>200)
            gt=r.get('relevant_windows',[])
            if gt:
                duration=float(r['duration']);ious.append(max(max(0,min(e,b/duration)-max(s,a/duration))/max(1e-12,max(e,b/duration)-min(s,a/duration)) for a,b in gt))
                a,b=gt[0];gst=max(0,min(T-1,int(np.floor(a/duration*T))));ged=min(T,max(gst+1,int(np.ceil(b/duration*T))))
                oracle.append(cosine(q[i],vn[gst:ged].mean(0)))
            else:oracle.append(np.nan)
        scores['fresh_EOT_projected_perframe_normalized_candidate']=np.array(local_norm)
        scores['fresh_EOT_projected_perframe_normalized_global']=np.array(global_norm)
        scores['fresh_EOT_projected_max_frame']=np.array(frame_max)
        pp=pair_indices(d,split) if subset=='test' else np.empty((0,2),int)
        meta={str(r['qid']):r for r in rs};ep,sizes=exact_pairs(d,meta)
        m={k:metrics(v,d,pp,ep) for k,v in scores.items()}
        if subset=='test':
            rng=np.random.default_rng(3407);controls=[]
            for rep in range(5):
                order=rng.permutation(len(q));bad=d['vids'][order]==d['vids']
                for attempt in range(40):
                    if not bad.any():break
                    order[bad]=rng.integers(len(q),size=int(bad.sum()));bad=d['vids'][order]==d['vids']
                assert not bad.any()
                sc=cosine(q,d['v_clip_cand'][order]);controls.append(metrics(sc,d,pp,ep))
                if rep==0:scores['fresh_EOT_projected_wrong_video_candidate']=sc
            # For both queries of a matched pair, use the positive GT window.
            # This is an oracle localization diagnostic, never deployable evaluation.
            oracle_scores=[];local_scores=[];global_scores=[]
            for a,b in pp:
                assert d['vids'][a]==d['vids'][b]
                r=rs[a];vid=str(d['vids'][a]);v=video_cache[vid];T=min(len(v),sf_lengths[vid]);vn=norm(v[:T]);dur=float(r['duration']);gs,ge=r['relevant_windows'][0]
                st=max(0,min(T-1,int(np.floor(gs/dur*T))));ed=min(T,max(st+1,int(np.ceil(ge/dur*T))))
                oracle_scores.append(float(cosine(q[a],vn[st:ed].mean(0))-cosine(q[b],vn[st:ed].mean(0))))
                s,e=d['best_spans'][a];st=max(0,min(T-1,int(np.floor(s*T))));ed=min(T,max(st+1,int(np.ceil(e*T))))
                local_scores.append(float(cosine(q[a],vn[st:ed].mean(0))-cosine(q[b],vn[st:ed].mean(0))))
                global_scores.append(float(cosine(q[a],vn.mean(0))-cosine(q[b],vn.mean(0))))
            m['same_positive_window_oracle_pair']={'Matched_PairAcc':float(np.mean(np.array(oracle_scores)>0))}
            m['same_positive_predicted_window_pair']={'Matched_PairAcc':float(np.mean(np.array(local_scores)>0))}
            m['same_global_video_pair']={'Matched_PairAcc':float(np.mean(np.array(global_scores)>0))}
            pair_vid=d['vids'][pp[:,0]];uv,iv=np.unique(pair_vid,return_inverse=True);counts=np.bincount(iv,minlength=len(uv))
            vals={k:(s[pp[:,0]]>s[pp[:,1]]).astype(float)+.5*(s[pp[:,0]]==s[pp[:,1]]) for k,s in scores.items()}
            sums={k:np.bincount(iv,weights=v,minlength=len(uv)) for k,v in vals.items()};boots={k:[] for k in vals};rng=np.random.default_rng(20261005)
            for rep in range(2000):
                w=np.bincount(rng.integers(len(uv),size=len(uv)),minlength=len(uv));den=w@counts
                for k in boots:boots[k].append(float(w@sums[k]/den))
            report['test_projected_wrong_video_controls']=controls
            report['test_pair_video_cluster_95ci']={k:np.quantile(v,[.025,.975]).tolist() for k,v in boots.items()}
        report['subsets'][subset]={'metrics':m,'video_length_counts':dict(length_stats),'positive_proposal_R1_IoU05':float(np.mean(np.array(ious)>=.5)),
            'cached_vs_fresh_mean_hidden_max_abs':float(np.max(np.abs(d['q_sent']-qm))),
            'oracle_scope':'GT pooled features are diagnostic only and never used for fitting or reported method scores'}
        np.savez_compressed(OUT/(split+'_'+subset+'_clip_scores.npz'),qids=d['qids'],vids=d['vids'],labels=d['labels'],partitions=d['partitions'],query_EOT_projected=q,**scores)
        print('CLIP',subset,json.dumps(report['subsets'][subset]),flush=True)
    write(split+'_clip_diagnosis.json',report)

def fit_diagnosis():
    mod=module('dao_clean_fit',BASE/'train_and_eval.py');dev=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu');report={}
    for split in SPLITS:
        ckpt=torch.load(BASE/'clean_runs'/split/'verifier_checkpoint.pt',map_location='cpu',weights_only=False)
        model=mod.GatedDAOVerifier().to(dev);model.load_state_dict(ckpt['state_dict']);model.eval();report[split]={}
        for subset in ['train','val']:
            z=np.load(BASE/'clean_features'/split/(subset+'.npz'));d={k:z[k] for k in FIELDS+['qids','labels','partitions','construction_types','source_qids']}
            b={k:torch.tensor(d[k],dtype=torch.float32,device=dev) for k in FIELDS}
            with torch.no_grad():res=model(b)
            sg={k:v.cpu().numpy() for k,v in res.items()};ix={str(q):i for i,q in enumerate(d['qids'])};pp=[];types=[]
            for i,src in enumerate(d['source_qids']):
                if d['labels'][i]==0 and str(src) in ix:
                    pp.append((ix[str(src)],i));types.append(d['construction_types'][i])
            pp=np.array(pp,int).reshape(-1,2);types=np.array(types)
            scores={'baseline':d['orig_logits'],'full':sg['s_exist'],'detector_only':sg['s_det'],
                    'action_raw':sg['raw_act'],'action_evidence':sg['ev_act'],'object_raw':sg['raw_obj'],'object_evidence':sg['ev_obj'],
                    'negative_action_prior':-sg['prior_act'],'negative_object_prior':-sg['prior_obj']}
            m={}
            for k,s in scores.items():
                seen=np.isin(d['partitions'],['S+','S-'])
                sp=seen[pp[:,0]]&seen[pp[:,1]]
                m[k]={'all_AUROC':auc(d['labels'],s),'Seen_AUROC':auc(d['labels'][seen],s[seen]),'std':float(s.std()),
                    'action_cf_pairs':pair_acc(s,pp[types=='action_counterfactual']),
                    'object_cf_pairs':pair_acc(s,pp[types=='object_counterfactual']),
                    'Seen_action_cf_pairs':pair_acc(s,pp[(types=='action_counterfactual')&sp]),
                    'Seen_object_cf_pairs':pair_acc(s,pp[(types=='object_counterfactual')&sp])}
            pair_counts=dict(Counter(types.tolist()));missing=int(np.sum(d['labels']==0))-len(pp)
            r={'n':len(d['qids']),'pair_counts':pair_counts,'negatives_source_absent':missing,'metrics':m}
            report[split][subset]=r;print('FIT',split,subset,json.dumps(r),flush=True)
    write('fit_diagnosis.json',report)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['features','frozen','clip','fit']);p.add_argument('--split',default='A1',choices=SPLITS);a=p.parse_args()
    {'features':feature_audit,'frozen':frozen_audit,'clip':lambda:clip_diagnosis(a.split),'fit':fit_diagnosis}[a.stage]()
