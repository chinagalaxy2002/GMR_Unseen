"""Frozen selected heads -> existence, actual-text controls, fixed candidate reranking."""
from event_modules import *
import collections
from sklearn.metrics import roc_curve

def threshold(y,s):
    fpr,tpr,t=roc_curve(y,s)
    finite=np.isfinite(t);values=(tpr-fpr)[finite];tt=t[finite]
    return float(tt[np.flatnonzero(values==values.max())[0]])

def iou(a,b):
    inter=max(0.,min(a[1],b[1])-max(a[0],b[0]));union=max(a[1],b[1])-min(a[0],b[0])
    return inter/union if union>0 else 0.

def localization(row,pred,mapvalues):
    candidates=pred.get('pred_relevant_windows_pre_exist',[])
    if row['exist_label'] != 1:
        return {'hit':None,'baseline_hit':None,'oracle_hit':None,'chosen_candidate':None,'candidate_scores':None}
    hit=[any(iou(c,w)>=.5 for w in row['relevant_windows']) for c in candidates]
    t=np.arange(len(mapvalues))+.5;score=[];empty=0
    for l,r,_ in candidates:
        mask=(t>=l)&(t<r)
        if not mask.any():
            mask=(np.arange(len(t))<r)&(np.arange(len(t))+1>l)
        if not mask.any():
            score.append(-1e6);empty+=1
        else:
            score.append(float(mapvalues[mask].mean()))
    chosen=int(np.argmax(score)) if score else None
    return {'hit':bool(hit[chosen]) if chosen is not None else False,'baseline_hit':bool(hit[0]) if hit else False,
            'oracle_hit':bool(any(hit)),'chosen_candidate':chosen,'candidate_scores':score,'missing_candidates':not bool(candidates),'empty_candidate_support':empty}

def main():
    assert all((BASE/f'runs/minimal_validation/{f}_{k}.pt').exists() for f in FAMILIES for k in MODULES), 'Select all models before inspecting pseudo scores.'
    assert not (BASE/'runs/minimal_validation/EVALUATION_DONE.json').exists()
    torch.set_num_threads(4);status('evaluation','running')
    primitive_rules={};calibrations={};manifest={};device='cuda:0'
    # All train-derived primitive rules and seen thresholds saved BEFORE any pseudo inference.
    for fam in FAMILIES:
        train=Arrays(fam,'train');seen=Arrays(fam,'seen')
        calibrations[fam]={}
        for kind in MODULES:
            ck=torch.load(BASE/f'runs/minimal_validation/{fam}_{kind}.pt',map_location='cpu',weights_only=False)
            model=EventHead(kind).to(device);model.load_state_dict(ck['state']);model.requires_grad_(False)
            score,maps,_,_=predict(model,seen,device)
            calibrations[fam][kind]={'threshold':threshold(seen.arr['label'],score),'selection_epoch':ck['selected_epoch'],'seen_AUROC':auc(seen.arr['label'],score),'checkpoint_sha256':sha(BASE/f'runs/minimal_validation/{fam}_{kind}.pt')}
            np.save(BASE/f'runs/minimal_validation/{fam}_{kind}_seen_scores.npy',score)
            if kind=='P':
                s,_,action,entity=predict(model,train,device)
                positive=np.asarray(train.arr['label'])==1
                primitive_rules[fam]={'action_median_positive':float(np.median(action[positive])), 'object_median_positive':float(np.median(entity[positive])),
                                      'action_quartiles_all_train':np.quantile(action,[.25,.5,.75]).tolist(), 'object_quartiles_all_train':np.quantile(entity,[.25,.5,.75]).tolist(),
                                      'source':'S_train original event-supervised independent P branches; not human primitive labels'}
                np.savez(BASE/f'runs/minimal_validation/{fam}_primitive_train_scores.npz',action=action,entity=entity,score=s)
            del model
    dump('PRIMITIVE_CONTROL_FREEZE.json',{'at':now(),'rules':primitive_rules,'matching':'both scores above S_train-positive medians, same S_train joint quartile bins, all opposite-label different-video pairs; no J sample selection', 'calibrations':calibrations})
    # Original and canonical inference after all choices are frozen.
    prediction_rows=[]
    for fam in FAMILIES:
        manifest[fam]={}
        for split in ['seen','pseudo']:
            data=Arrays(fam,split)
            old={str(x['qid']):x for x in read(RUNS[fam]/('best_seen_predictions.jsonl' if split=='seen' else 'pseudo_predictions.jsonl'))}
            assert set(old)=={str(x['qid']) for x in data.rows}
            baseline_threshold=json.loads((RUNS[fam]/'threshold_frozen.json').read_text())['threshold']
            bas=np.array([old[str(x['qid'])]['pred_exist_score'] for x in data.rows]);output={'baseline':bas}
            baseline_hit=np.array([localization(x,old[str(x['qid'])],np.zeros(int(data.arr['length'][i])))['baseline_hit'] if x['exist_label']==1 else False for i,x in enumerate(data.rows)],dtype=bool)
            output['baseline_hit']=baseline_hit
            allhits={};canonical_scores={}
            byquery=collections.defaultdict(list)
            for i,x in enumerate(data.rows):byquery[x['query']].append(i)
            mapping=np.arange(len(data.rows));canonical_group=np.full(len(data.rows),-1,dtype=int);canon_records=[]
            if split=='pseudo':
                mixed=[inds for inds in byquery.values() if {data.rows[i]['exist_label'] for i in inds}=={0,1} and len({data.rows[i]['vid'] for i in inds})>1]
                for group,inds in enumerate(mixed):
                    idx=min(inds,key=lambda i:str(data.rows[i]['qid']))
                    mapping[inds]=idx;canonical_group[inds]=group
                    canonical_feature=normalized(np.load(TEXT/f"qid{data.rows[idx]['qid']}.npz")['last_hidden_state'][:32])
                    canon_records.append({'group':group,'canonical_qid':str(data.rows[idx]['qid']),'query':data.rows[idx]['query'],'loaded_token_count':len(canonical_feature),
                                          'normalized_feature_and_mask_hash':hashlib.sha256(canonical_feature.tobytes()+np.ones(len(canonical_feature),dtype=np.bool_).tobytes()).hexdigest(),
                                          'role_vector_hash':hashlib.sha256(np.asarray(data.arr['verb'][idx]).tobytes()+np.asarray(data.arr['noun'][idx]).tobytes()).hexdigest(),'qids':[str(data.rows[i]['qid']) for i in inds]})
                jsonl(f'audit/{fam}_ACTUAL_TEXT_CONTROL.jsonl',canon_records)
                output['canonical_group']=canonical_group
            rr=[{'family':fam,'split':split,'qid':str(x['qid']),'vid':x['vid'],'query':x['query'],'label':x['exist_label'],
                 'baseline_score':float(bas[i]),'baseline_threshold':baseline_threshold,'baseline_hit':bool(baseline_hit[i]) if x['exist_label']==1 else None,'modules':{}} for i,x in enumerate(data.rows)]
            for kind in MODULES:
                ck=torch.load(BASE/f'runs/minimal_validation/{fam}_{kind}.pt',map_location='cpu',weights_only=False)
                model=EventHead(kind).to(device);model.load_state_dict(ck['state']);model.requires_grad_(False)
                scores,maps,action,entity=predict(model,data,device)
                output[kind]=scores;hits=[]
                if split=='pseudo':
                    cs,cm,ca,ce=predict(model,data,device,text_mapping=mapping)
                    if kind=='T':
                        # Reuse the one score for each identical text input. This is
                        # exact memoization, eliminating batch-shape floating-point
                        # differences, not a label-based score correction.
                        cs=cs[mapping]
                    output['canonical_'+kind]=cs
                    if kind=='P':output['canonical_action']=ca;output['canonical_object']=ce
                    if kind=='T':
                        for inds in mixed:assert np.ptp(cs[inds])<1e-7
                    if kind=='J':
                        variation=[float(np.ptp(cs[inds])) for inds in mixed]
                        dump(f'audit/{fam}_J_VISUAL_DEPENDENCE.json',{'same_actual_text_groups':len(mixed),'groups_with_score_variation':sum(z>1e-6 for z in variation),'max_within_group_score_variation':max(variation,default=0),
                                                                'time_varying_maps':sum(float(np.ptp(m))>1e-6 for m in maps),'rows':len(maps),'single_primary_graph_pair':True,'meaning':'necessary visual dependence, not binding accuracy'})
                if kind=='P':
                    output['action']=action;output['object']=entity
                for i,(x,mp) in enumerate(zip(data.rows,maps)):
                    loc=localization(x,old[str(x['qid'])],mp) if kind!='T' else {'hit':None,'chosen_candidate':None}
                    hits.append(loc['hit'] if loc['hit'] is not None else False)
                    rr[i]['modules'][kind]={'score':float(scores[i]),'threshold':calibrations[fam][kind]['threshold'],**loc}
                    if split=='pseudo':rr[i]['modules'][kind]['actual_text_score']=float(output['canonical_'+kind][i]) if canonical_group[i]>=0 else None
                if kind!='T':output['hit_'+kind]=np.array(hits,dtype=bool)
                np.savez_compressed(BASE/f'runs/minimal_validation/{fam}_{kind}_{split}_maps.npz',offset=np.r_[0,np.cumsum([len(x) for x in maps])],values=np.concatenate(maps))
                del model
            # Preserve complete original rows and outputs; no positive-denominator filtering.
            np.savez_compressed(BASE/f'runs/minimal_validation/{fam}_{split}_evaluation.npz',**output)
            jsonl(f'runs/minimal_validation/{fam}_{split}_predictions.jsonl',rr)
            prediction_rows.extend(rr)
            manifest[fam][split]={'rows':len(rr),'positive':sum(x['label']==1 for x in rr),'canonical_groups':len(canon_records),'baseline_AUROC':auc(data.arr['label'],bas),'baseline_raw_R1':float(baseline_hit[np.asarray(data.arr['label'])==1].mean())}
            print('evaluated',fam,split,manifest[fam][split],flush=True)
    jsonl('runs/minimal_validation/PREDICTIONS.jsonl',prediction_rows)
    dump('runs/minimal_validation/EVALUATION_DONE.json',{'at':now(),'manifest':manifest,'pseudo_model_selection':False,'original_model_updates':0,'new_full_model_training':False})
    status('evaluation','completed',rows=len(prediction_rows))

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        status('evaluation','failed',error=repr(e));raise
