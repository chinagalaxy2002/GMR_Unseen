"""Exploratory localization/readout associations; no new labels or thresholds."""
import collections
import json
from pathlib import Path
import numpy as np
from phase2 import STAGE,dump,rows,sha,iou
from readout_collect import DEST,RUNS


def auc(y,s,w):
    _,inv=np.unique(s,return_inverse=True)
    p=np.bincount(inv,weights=w*(y==1));n=np.bincount(inv,weights=w*(y==0),minlength=len(p))
    return float(np.dot(p,np.cumsum(n)-.5*n)/(p.sum()*n.sum())) if p.sum() and n.sum() else np.nan


def tie_rate(y,s,w):
    _,inv=np.unique(s,return_inverse=True)
    p=np.bincount(inv,weights=w*(y==1));n=np.bincount(inv,weights=w*(y==0),minlength=len(p))
    return float(np.dot(p,n)/(p.sum()*n.sum())) if p.sum() and n.sum() else np.nan


def mean(s,w):return float(np.dot(s,w)/w.sum()) if w.sum() else np.nan


def spearman(x,y,w):
    def rank(a):
        _,inv=np.unique(a,return_inverse=True);mass=np.bincount(inv,weights=w)
        return (np.cumsum(mass)-mass/2)[inv]
    if not w.sum():return np.nan
    x=rank(x);y=rank(y);x=x-mean(x,w);y=y-mean(y,w)
    den=np.sqrt(np.dot(w,x*x)*np.dot(w,y*y))
    return float(np.dot(w,x*y)/den) if den else np.nan


def pack(family,split):
    run=RUNS[family];rr=rows(run/'views'/('pseudo.jsonl' if split=='pseudo' else 'val_seen.jsonl'))
    pp={str(p['qid']):p for p in rows(run/('pseudo_predictions.jsonl' if split=='pseudo' else 'best_seen_predictions.jsonl'))}
    native={str(p['qid']):p for p in rows(DEST/f'{family}_{split}_native.jsonl')}
    result=[]
    for r in rr:
        p=pp[str(r['qid'])];n=native[str(r['qid'])]
        windows=sorted(p['pred_relevant_windows_pre_exist'],key=lambda a:a[2],reverse=True)
        overlaps=[max((iou(win,gt) for gt in r['relevant_windows']),default=0) for win in windows] if r['exist_label'] else []
        result.append({**n,'label':r['exist_label'],'raw_top_iou':overlaps[0] if overlaps else None,
            'raw_oracle_iou':max(overlaps) if overlaps else None,'raw_max_foreground_probability':windows[0][2],
            'raw_foreground_top2_gap':windows[0][2]-windows[1][2] if len(windows)>1 else None})
    (DEST/f'{family}_{split}_rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in result))
    d={key:np.array([r[key] for r in result]) for key in result[0]}
    byvideo=collections.defaultdict(list)
    for i,r in enumerate(result):
        if r['label']:byvideo[r['vid']].append(i)
    vindex=[];wins=[];paircounts=[]
    for indices in byvideo.values():
        good=[i for i in indices if result[i]['raw_top_iou']>=.5]
        bad=[i for i in indices if result[i]['raw_top_iou']<.5]
        if good and bad:
            comparisons=[float(result[a]['exist_logit']>result[b]['exist_logit'])+.5*float(result[a]['exist_logit']==result[b]['exist_logit']) for a in good for b in bad]
            vindex.append(indices[0]);wins.append(sum(comparisons));paircounts.append(len(comparisons))
    d['within_video_index']=np.array(vindex,dtype=int);d['within_video_wins']=np.array(wins);d['within_video_pairs']=np.array(paircounts)
    return d,result


def metrics(d,w):
    y=d['label'];pos=y==1;correct=pos&np.array([v is not None and v>=.5 for v in d['raw_top_iou']]);bad=pos&~correct
    oracle=pos&np.array([v is not None and v>=.5 for v in d['raw_oracle_iou']]);neg=y==0
    original=d['original_saved_score'];logit=d['exist_logit'];sigmoid=d['exist_sigmoid_fp32'];serialized=d['exist_sigmoid_serialized']
    result={
        'original_AUROC':auc(y,original,w),'native_logit_AUROC':auc(y,logit,w),
        'native_sigmoid_AUROC':auc(y,sigmoid,w),'recomputed_serialized_AUROC':auc(y,serialized,w),
        'logit_minus_original_AUROC':auc(y,logit,w)-auc(y,original,w),
        'logit_minus_native_sigmoid_AUROC':auc(y,logit,w)-auc(y,sigmoid,w),
        'native_sigmoid_minus_serialized_AUROC':auc(y,sigmoid,w)-auc(y,serialized,w),
        'original_pos_neg_tie_rate':tie_rate(y,original,w),'native_sigmoid_pos_neg_tie_rate':tie_rate(y,sigmoid,w),
        'native_logit_pos_neg_tie_rate':tie_rate(y,logit,w),
        'positive_native_sigmoid_exact_one_fraction':mean((sigmoid[pos]==1).astype(float),w[pos]),
        'negative_native_sigmoid_exact_one_fraction':mean((sigmoid[neg]==1).astype(float),w[neg]),
        'raw_R1_05':mean(correct[pos].astype(float),w[pos]),'oracle_any_candidate_R_05':mean(oracle[pos].astype(float),w[pos]),
        'ranking_error_fraction_of_positives':mean((oracle&~correct)[pos].astype(float),w[pos]),
        'candidate_miss_fraction_of_positives':mean((~oracle)[pos].astype(float),w[pos]),
        'ranking_error_fraction_of_raw_errors':mean(oracle[bad].astype(float),w[bad]),
        'native_exist_quality_AUC_Splus':auc(correct[pos].astype(int),logit[pos],w[pos]),
        'foreground_quality_AUC_Splus':auc(correct[pos].astype(int),d['raw_max_foreground_probability'][pos],w[pos]),
        'native_logit_mean_correct_minus_incorrect_Splus':mean(logit[correct],w[correct])-mean(logit[bad],w[bad]),
        'native_logit_top_iou_spearman_Splus':spearman(logit[pos],d['raw_top_iou'][pos].astype(float),w[pos]),
        'native_logit_foreground_spearman_Splus':spearman(logit[pos],d['raw_max_foreground_probability'][pos],w[pos]),
    }
    clusterweights=w[d['within_video_index']]
    denominator=np.dot(clusterweights,d['within_video_pairs'])
    result['within_video_exist_quality_PairAcc_Splus']=float(np.dot(clusterweights,d['within_video_wins'])/denominator) if denominator else np.nan
    # Exact decomposition of saved-score AUC by positive localization strata.
    result['original_AUC_correct_positive_vs_negative']=auc(y,original,w*(correct|neg))
    result['original_AUC_incorrect_positive_vs_negative']=auc(y,original,w*(bad|neg))
    rate=result['raw_R1_05']
    result['original_AUC_strata_reconstruction']=rate*result['original_AUC_correct_positive_vs_negative']+(1-rate)*result['original_AUC_incorrect_positive_vs_negative']
    return result


def ci(point,samples):
    valid=np.array([v for v in samples if np.isfinite(v)])
    return {'point':float(point) if np.isfinite(point) else None,'ci95':np.quantile(valid,[.025,.975]).tolist() if len(valid) else None,'valid_resamples':len(valid)}


def main():
    assert json.loads((DEST/'state.json').read_text())['state']=='inference_completed'
    assert not (DEST/'RESULTS.json').exists()
    data={};records={}
    for family in RUNS:
        for split in ('seen','pseudo'):data[family,split],records[family,split]=pack(family,split)
    videos=sorted({v for d in data.values() for v in d['vid']});index={v:i for i,v in enumerate(videos)}
    indices={k:np.array([index[v] for v in d['vid']]) for k,d in data.items()}
    points={k:metrics(d,np.ones(len(d['label']))) for k,d in data.items()};samples={k:collections.defaultdict(list) for k in data}
    rng=np.random.default_rng(3407)
    for _ in range(1000):
        vw=np.bincount(rng.integers(0,len(videos),len(videos)),minlength=len(videos))
        for k,d in data.items():
            m=metrics(d,vw[indices[k]])
            for key,value in m.items():samples[k][key].append(value)
    result={'state':'completed','training_updates':0,'new_training_epochs':0,'seed':3407,'resamples':1000,
        'intervals':'Exploratory 95% cluster intervals, no multiplicity correction and no confirmatory candidate claim; original video union weights shared across all families/splits',
        'source_sha256':sha(Path(__file__)),'families':{},'equal_family_mean':{}}
    for family in RUNS:
        result['families'][family]={}
        for split in ('seen','pseudo'):
            key=(family,split);d=data[key];y=d['label'];pos=y==1
            good=pos&np.array([v is not None and v>=.5 for v in d['raw_top_iou']]);byv=collections.defaultdict(set)
            for v,yes,c in zip(d['vid'],pos,good):
                if yes:byv[v].add(bool(c))
            result['families'][family][split]={'coverage':{'rows':len(y),'positive':int(pos.sum()),'negative':int((y==0).sum()),'raw_correct_positive':int(good.sum()),'raw_incorrect_positive':int((pos&~good).sum()),'mixed_localization_quality_positive_videos':sum(len(v)==2 for v in byv.values()),'within_video_quality_pairs':int(d['within_video_pairs'].sum())},
                'metrics':{name:ci(value,samples[key][name]) for name,value in points[key].items()}}
            assert abs(points[key]['original_AUROC']-points[key]['original_AUC_strata_reconstruction'])<1e-12
    aggregate=['original_AUROC','native_logit_AUROC','logit_minus_original_AUROC','logit_minus_native_sigmoid_AUROC','native_sigmoid_minus_serialized_AUROC','raw_R1_05','oracle_any_candidate_R_05','ranking_error_fraction_of_positives','candidate_miss_fraction_of_positives','native_exist_quality_AUC_Splus']
    for split in ('seen','pseudo'):
        result['equal_family_mean'][split]={name:ci(np.mean([points[f,split][name] for f in RUNS]),np.mean([samples[f,split][name] for f in RUNS],axis=0)) for name in aggregate}
    result['limitations']=['Oracle uses existing S+ ground-truth windows solely for coverage; it is not achievable retrieval performance or visual support proof.',
        'Loc-correct/incorrect strata are outcome-conditioned and queries differ; cluster intervals do not remove semantic/query confounding or establish causation.',
        'Full native logit and sigmoid precision diagnosis changes no original reported endpoint, gate, threshold or checkpoint; no new labels.',
        'Three saved models, sit truncated at 77 logged epochs; no training seed or equal-completed-budget claim.']
    dump(DEST/'RESULTS.json',result)
    print(json.dumps(result['equal_family_mean'],indent=2))


if __name__=='__main__':main()
