"""Read-only candidate diagnostics. CPU; no model loading, fitting or GT-based inference."""
import collections, datetime, hashlib, json, subprocess
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[2]
STAGE=Path(__file__).resolve().parents[1]
OUT=STAGE/'candidate_geometry_analysis'
FAMILIES=['throw','open_close','sit']; SPLITS=['seen','pseudo']; KS=[1,2,3,5,10]
RUNS={'throw':ROOT/'runs/autonomous_queue_20260930_strict/jobs/dev_A1_qd_gmr_baseline_s3407_attempt1', 'open_close':STAGE/'runs/open_close_qd_gmr_baseline_s3407_attempt1','sit':STAGE/'diagnostics/sit/baseline/evaluation_bundle'}
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def read(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def dump(name,x): (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def iou(a,b):
    inter=max(0,min(a[1],b[1])-max(a[0],b[0])); union=max(0,a[1]-a[0])+max(0,b[1]-b[0])-inter
    return inter/union if union>0 else 0.
def geometry(w,g,duration):
    length=g[1]-g[0]; center=(w[0]+w[1]-g[0]-g[1])/2
    return {'gt_length_seconds':length,'prediction_length_seconds':w[1]-w[0], 'gt_center_video_fraction':(g[0]+g[1])/2/duration if duration>0 else None,
      'prediction_center_video_fraction':(w[0]+w[1])/2/duration if duration>0 else None,
      'center_error_seconds':center,'abs_center_error_over_gt_length':abs(center)/length if length>0 else None,
      'center_error_over_gt_length':center/length if length>0 else None,'prediction_gt_length_ratio':(w[1]-w[0])/length if length>0 else None,
      'start_error_seconds':w[0]-g[0],'end_error_seconds':w[1]-g[1],
      'start_error_over_gt_length':(w[0]-g[0])/length if length>0 else None,'end_error_over_gt_length':(w[1]-g[1])/length if length>0 else None,'max_iou':iou(w,g)}
def summary(point,rep):
    rep=np.asarray(rep); valid=rep[np.isfinite(rep)]
    return {'point':float(point) if np.isfinite(point) else None,'ci95':np.quantile(valid,[.025,.975]).tolist() if len(valid) else None,'valid_resamples':int(len(valid)),'invalid_resamples':int(1000-len(valid))}
def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'FREEZE.json').exists(),'Frozen analysis already exists; do not overwrite.'
    runtime={c:subprocess.run(c,shell=True,text=True,capture_output=True).stdout for c in ['ps -eo pid,etimes,args','nvidia-smi','nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader','tmux list-sessions']}
    dump('RUNTIME_BEFORE.json',{'checked_at':now(),'snapshots':runtime})
    oldfreeze=json.loads((STAGE/'readout_analysis/FREEZE.json').read_text())
    protected=dict(oldfreeze['protected_files_sha256'])
    prechecks={p:sha(p)==h for p,h in protected.items()}; assert all(prechecks.values()),'Previous protected asset hash mismatch'
    for p in (STAGE/'readout_analysis').iterdir():
        if p.is_file():protected[str(p)]=sha(p)
    inputs={}; source={}; coverage={}; allvid=set()
    for fam in FAMILIES:
        run=RUNS[fam]
        for p in [run/'best.ckpt',run/'latest.ckpt',run/'threshold_frozen.json']:
            protected[str(p)]=sha(p)
        for split in SPLITS:
            name=fam+'/'+split;gtpath=run/'views'/('val_seen.jsonl' if split=='seen' else 'pseudo.jsonl');ppath=run/('best_seen_predictions.jsonl' if split=='seen' else 'pseudo_predictions.jsonl')
            gt=read(gtpath); pred=read(ppath); gd={str(x['qid']):x for x in gt};pd={str(x['qid']):x for x in pred}
            assert len(gd)==len(gt) and len(pd)==len(pred) and gd.keys()==pd.keys(),name
            assert all(gd[q]['vid']==pd[q]['vid'] for q in gd),name
            counts=collections.Counter(len(x['pred_relevant_windows_pre_exist']) for x in pred)
            assert all(all(np.isfinite(w)) and len(w)==3 and w[1]>=w[0] for x in pred for w in x['pred_relevant_windows_pre_exist'])
            assert all(all(a[2]>=b[2] for a,b in zip(x['pred_relevant_windows_pre_exist'],x['pred_relevant_windows_pre_exist'][1:])) for x in pred)
            inputs[name]={'gt':str(gtpath),'predictions':str(ppath),'checkpoint':str(run/'best.ckpt'),'gt_sha256':sha(gtpath),'predictions_sha256':sha(ppath),'checkpoint_sha256':protected[str(run/'best.ckpt')]}
            protected[str(gtpath)]=sha(gtpath);protected[str(ppath)]=sha(ppath)
            positives=[x for x in gt if x['exist_label']==1]
            assert all(x['relevant_windows'] for x in positives)
            coverage[name]={'all_queries':len(gt),'positive_queries':len(positives),'all_videos':len({x['vid'] for x in gt}),'positive_videos':len({x['vid'] for x in positives}), 'candidate_count_all_queries':dict(counts),'fewer_than_10_queries':sum(v for k,v in counts.items() if k<10),'qid_vid_exact_alignment':True, 'positive_gt_nonpositive_length_windows':sum(g[1]<=g[0] for x in positives for g in x['relevant_windows']), 'nonpositive_duration_queries':sum(x['duration']<=0 for x in positives)}
            source[name]=(positives,pd);allvid.update(x['vid'] for x in gt)
    frozen={'frozen_at':now(),'scope':'post-readout exploratory candidate diagnostics, not preregistered confirmation','inputs':inputs,'qid_coverage':coverage,'protected_files_sha256':protected,'previous_81_hashes_match':prechecks,'seed':3407,'resamples':1000,'intervals':'exploratory percentile 95%; no multiple-endpoint confirmation','training_updates':0,'new_training_epochs':0,'new_forward_passes':0,'true_U_access':False,'source_sha256':sha(__file__),
      'definitions':{'rank':'original saved raw list order; never resort rounded ties','IoU':[.5,.7],'K':KS,'GT_match':'max IoU; exact ties select first GT in original list; oracle candidate ties select first original rank','PairAcc':'each mixed query: mean(score_correct > score_incorrect + .5 equal), then equal queries within video, equal eligible videos; query-equal auxiliary','correlation':'within-query Spearman with scipy average tied ranks; zero score or IoU variance -> unavailable; all S+ and mixed subset','gap':'top1 foreground minus foreground of first maximum-IoU candidate','geometry':'top1 and first maximum-IoU candidate vs own maximum-IoU GT; signed start/end/center; absolute center / GT length; length ratio; length and center position; no cutpoints','aggregation':'primary: query summary -> available-query mean within video -> equal eligible videos. Auxiliary query-equal top-K reproduces original raw/oracle. Family mean equal across three; unavailable family makes replicate unavailable, never silently drops family','bootstrap':'single multinomial resample of union original videos, reused across all families and splits; no candidate/pair sampling','quantiles':'query distribution p05,p25,p50,p75,p95 descriptive; video-mean continuous metrics receive bootstrap CI','seen_pseudo':'different query sets; shared-video uncertainty for descriptive difference only','limits':'GT only diagnostic; native slot probabilities not joined; no causal loss-conflict or joint-gain inference'}}
    dump('FREEZE.json',frozen);dump('state.json',{'state':'running','started_at':now(),'training_updates':0})
    videos=sorted(allvid); vi={v:i for i,v in enumerate(videos)};rng=np.random.default_rng(3407)
    mult=rng.multinomial(len(videos),np.full(len(videos),1/len(videos)),size=1000)
    np.savez_compressed(OUT/'BOOTSTRAP_WEIGHTS.npz',videos=np.array(videos),multipliers=mult)
    blocks={};rowsout=[]; checks={};distributions={}
    oldresults=json.loads((STAGE/'readout_analysis/RESULTS.json').read_text())
    for name,(gt,pred) in source.items():
        records=[]
        for r in gt:
            wins=pred[str(r['qid'])]['pred_relevant_windows_pre_exist'];candidates=[]
            for rank,w in enumerate(wins,1):
                ovs=[iou(w,g) for g in r['relevant_windows']];j=int(np.argmax(ovs));best=ovs[j]
                candidates.append({'rank':rank,'window':w[:2],'foreground_score':w[2],'max_iou':best,'matched_gt_index':j,'matched_gt':r['relevant_windows'][j],'GT_max_iou_ties':sum(v==best for v in ovs),'geometry':geometry(w,r['relevant_windows'][j],r['duration'])})
            ov=np.array([c['max_iou'] for c in candidates]);s=np.array([c['foreground_score'] for c in candidates]);good=ov>=.5
            mix=good.any() and (~good).any();first={str(t):next((i+1 for i,v in enumerate(ov) if v>=t),None) for t in [.5,.7]}
            pair=((s[good,None]>s[None,~good])+.5*(s[good,None]==s[None,~good])) if mix else np.array([])
            ties=(s[good,None]==s[None,~good]) if mix else np.array([])
            rho=float(spearmanr(s,ov).statistic) if len(s)>1 and np.ptp(s)>0 and np.ptp(ov)>0 else None
            oracle=int(np.argmax(ov)) if len(ov) else None
            typ='top1_correct' if len(ov) and ov[0]>=.5 else 'ranking_error' if good.any() else 'candidate_miss'
            rec={'family':name.split('/')[0],'split':name.split('/')[1],'qid':str(r['qid']),'vid':r['vid'],'duration':r['duration'],'original_gt':r['relevant_windows'],'candidate_count':len(wins),'first_correct_rank':first,'category':typ,'mixed_candidates':bool(mix),'pair_count':int(pair.size),'PairAcc':float(pair.mean()) if mix else None,'mixed_pair_score_tie_rate':float(ties.mean()) if mix else None,'spearman_score_iou':rho,'score_zero_variance':bool(len(s)==0 or np.ptp(s)==0),'iou_zero_variance':bool(len(ov)==0 or np.ptp(ov)==0),'any_score_tie':len(np.unique(s))<len(s),'score_duplicate_pair_fraction':sum(s[i]==s[j] for i in range(len(s)) for j in range(i+1,len(s)))/(len(s)*(len(s)-1)/2) if len(s)>1 else None,'top1_minus_oracle_score':float(s[0]-s[oracle]) if oracle is not None else None,'oracle_rank':oracle+1 if oracle is not None else None,'oracle_max_iou_ties':int(sum(ov==ov[oracle])) if oracle is not None else 0,'candidates':candidates}
            records.append(rec);rowsout.append(rec)
        # A fixed set of per-query summaries, each with an explicit eligible denominator.
        fields={}
        def add(key,values):fields[key]=np.array([np.nan if v is None else float(v) for v in values])
        for t in [.5,.7]:
            for k in KS:add(f'R_at_{k}_iou_{t}',[x['first_correct_rank'][str(t)] is not None and x['first_correct_rank'][str(t)]<=k for x in records])
            for k in [2,3,5]:add(f'gain_K{k}_minus_K1_iou_{t}',[x['first_correct_rank'][str(t)] is not None and 1<x['first_correct_rank'][str(t)]<=k for x in records])
            for k in range(1,11):add(f'first_rank_{k}_iou_{t}',[x['first_correct_rank'][str(t)]==k for x in records])
            add(f'no_correct_candidate_iou_{t}',[x['first_correct_rank'][str(t)] is None for x in records])
        for typ in ['top1_correct','ranking_error','candidate_miss']:add(f'category_{typ}',[x['category']==typ for x in records])
        for field in ['PairAcc','mixed_pair_score_tie_rate','spearman_score_iou','score_zero_variance','iou_zero_variance','any_score_tie','score_duplicate_pair_fraction','top1_minus_oracle_score','mixed_candidates']:
            add(field,[x[field] for x in records])
        add('mixed_spearman_score_iou',[x['spearman_score_iou'] if x['mixed_candidates'] else None for x in records])
        add('spearman_unavailable_fraction',[x['spearman_score_iou'] is None for x in records])
        add('ranking_fraction_of_raw_errors',[x['category']=='ranking_error' if x['category']!='top1_correct' else None for x in records])
        for typ in ['top1_correct','ranking_error','candidate_miss']:
            for window in ['top1','oracle']:
                for field in geometry([0,1],[0,1],1):
                    vals=[x['candidates'][0 if window=='top1' else x['oracle_rank']-1]['geometry'][field] if x['category']==typ and x['candidates'] else None for x in records]
                    add(f'{typ}/{window}/{field}',vals)
        indices=np.array([vi[x['vid']] for x in records]);stats={};reps={};dist={}
        for key,vals in fields.items():
            ok=np.isfinite(vals);ii=indices[ok];vv=vals[ok];cnt=np.bincount(ii,minlength=len(videos));sm=np.bincount(ii,weights=vv,minlength=len(videos));eligible=cnt>0
            vm=np.divide(sm,cnt,out=np.zeros_like(sm),where=eligible)
            numerator=mult@vm;den=mult@eligible.astype(float);boot=np.divide(numerator,den,out=np.full(1000,np.nan),where=den>0)
            point=vm[eligible].mean() if eligible.any() else np.nan
            qden=mult@cnt;qboot=np.divide(mult@sm,qden,out=np.full(1000,np.nan),where=qden>0)
            stats[key]={'video_equal':summary(point,boot),'query_equal':summary(vv.mean() if len(vv) else np.nan,qboot),'eligible_queries':int(ok.sum()),'eligible_videos':int(eligible.sum()),'unavailable_queries':int((~ok).sum())}
            reps[key]=(boot,qboot)
            if '/' in key or key=='top1_minus_oracle_score':dist[key]={'query_count':len(vv),'quantiles_p05_p25_p50_p75_p95':np.quantile(vv,[.05,.25,.5,.75,.95]).tolist() if len(vv) else None,'min':float(vv.min()) if len(vv) else None,'max':float(vv.max()) if len(vv) else None}
        fam,split=name.split('/');old=oldresults['families'][fam][split]['metrics']
        oldrows={x['qid']:x for x in read(STAGE/f'readout_analysis/{fam}_{split}_rows.jsonl')}
        check={'K1_matches_original_raw':abs(stats['R_at_1_iou_0.5']['query_equal']['point']-old['raw_R1_05']['point'])<1e-12,'K10_matches_previous_oracle':abs(stats['R_at_10_iou_0.5']['query_equal']['point']-old['oracle_any_candidate_R_05']['point'])<1e-12,'per_query_top_oracle_IoU_matches':all(abs(x['candidates'][0]['max_iou']-oldrows[x['qid']]['raw_top_iou'])<1e-12 and abs(max(c['max_iou'] for c in x['candidates'])-oldrows[x['qid']]['raw_oracle_iou'])<1e-12 for x in records),'three_categories_partition':sum(stats['category_'+c]['eligible_queries']*stats['category_'+c]['query_equal']['point'] for c in ['top1_correct','ranking_error','candidate_miss'])==len(records),'rank_mass_sums_to_one_05':abs(sum(stats[f'first_rank_{k}_iou_0.5']['query_equal']['point'] for k in range(1,11))+stats['no_correct_candidate_iou_0.5']['query_equal']['point']-1)<1e-12}
        assert all(check.values()),(name,check)
        checks[name]=check; blocks[name]={'metrics':stats,'coverage':coverage[name]};blocks[name]['coverage'].update(mixed_candidate_queries=sum(x['mixed_candidates'] for x in records),mixed_candidate_videos=len({x['vid'] for x in records if x['mixed_candidates']}),candidate_pairs=sum(x['pair_count'] for x in records),unavailable_spearman_queries=sum(x['spearman_score_iou'] is None for x in records),empty_candidate_queries=sum(not x['candidates'] for x in records),GT_match_tied_candidates=sum(c['GT_max_iou_ties']>1 for x in records for c in x['candidates']),oracle_tied_queries=sum(x['oracle_max_iou_ties']>1 for x in records))
        distributions[name]=dist;blocks[name]['_rep']=reps
        print('completed summaries',name,flush=True)
    equal={};differences={}
    for split in SPLITS:
        equal[split]={}
        for key in blocks['throw/'+split]['metrics']:
            equal[split][key]={}
            for j,mode in enumerate(['video_equal','query_equal']):
                points=[blocks[f+'/'+split]['metrics'][key][mode]['point'] for f in FAMILIES]; rr=np.stack([blocks[f+'/'+split]['_rep'][key][j] for f in FAMILIES])
                equal[split][key][mode]=summary(np.mean(points) if all(x is not None for x in points) else np.nan,rr.mean(axis=0))
    for fam in FAMILIES:
        differences[fam]={}
        for key in blocks[fam+'/seen']['metrics']:
            differences[fam][key]={}
            for j,mode in enumerate(['video_equal','query_equal']):
                a=blocks[fam+'/pseudo']['metrics'][key][mode]['point'];b=blocks[fam+'/seen']['metrics'][key][mode]['point']
                differences[fam][key][mode]=summary(a-b if a is not None and b is not None else np.nan,blocks[fam+'/pseudo']['_rep'][key][j]-blocks[fam+'/seen']['_rep'][key][j])
    differences['equal_family']={}
    for key in equal['seen']:
        differences['equal_family'][key]={}
        for j,mode in enumerate(['video_equal','query_equal']):
            pp=equal['pseudo'][key][mode]['point'];ss=equal['seen'][key][mode]['point']
            rr=np.stack([blocks[f+'/pseudo']['_rep'][key][j]-blocks[f+'/seen']['_rep'][key][j] for f in FAMILIES]).mean(axis=0)
            differences['equal_family'][key][mode]=summary(pp-ss if pp is not None and ss is not None else np.nan,rr)
    for b in blocks.values():del b['_rep']
    (OUT/'CANDIDATE_ROWS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n' for x in rowsout))
    dump('COVERAGE.json',{'groups':{k:v['coverage'] for k,v in blocks.items()},'shared_video_union':len(videos),'video_intersections':{a+' & '+b:len({x['vid'] for x in source[a][0]}&{x['vid'] for x in source[b][0]}) for i,a in enumerate(source) for b in list(source)[i+1:]}})
    dump('RESULTS.json',{'state':'completed','aggregation':frozen['definitions']['aggregation'],'seed':3407,'resamples':1000,'groups':blocks,'equal_family':equal,'pseudo_minus_seen_descriptive':differences,'geometry_query_distributions':distributions,'reproduction_checks':checks})
    finalchecks={p:sha(p)==h for p,h in protected.items()};assert all(finalchecks.values())
    dump('INTEGRITY.json',{'state':'completed','protected_files':len(protected),'all_protected_files_unchanged':all(finalchecks.values()),'checks':finalchecks,'reproduction_checks':checks,'source_matches_freeze':sha(__file__)==frozen['source_sha256'],'training_updates':0,'new_forward_passes':0,'sit_training_remains_stopped':json.loads((STAGE/'runs/sit_qd_gmr_baseline_s3407_attempt1/status.json').read_text())['state'] if 'state' in json.loads((STAGE/'runs/sit_qd_gmr_baseline_s3407_attempt1/status.json').read_text()) else 'see protected original status'})
    dump('state.json',{'state':'completed','completed_at':now(),'training_updates':0,'new_training_epochs':0,'new_forward_passes':0,'groups':6,'positive_queries':len(rowsout),'protected_files':len(protected)})
if __name__=='__main__':
    try:main()
    except Exception as e:
        if OUT.exists():dump('state.json',{'state':'failed','error':repr(e),'at':now(),'training_updates':0})
        raise
