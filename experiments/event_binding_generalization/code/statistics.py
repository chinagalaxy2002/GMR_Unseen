"""Shared original-video paired bootstrap; exact tie-aware metrics."""
from common import *
import collections

class AUC:
    def __init__(self,y,s,mask):
        self.index=np.flatnonzero(mask);self.y=np.asarray(y)[self.index];score=np.asarray(s)[self.index]
        self.order=np.argsort(score,kind='stable');self.ys=self.y[self.order]
        self.starts=np.r_[0,np.flatnonzero(np.diff(score[self.order]))+1] if len(score) else np.array([],dtype=int)
    def __call__(self,w):
        if not len(self.index):return None
        ww=w[self.index][self.order]
        wp=np.add.reduceat(ww*(self.ys==1),self.starts);wn=np.add.reduceat(ww*(self.ys==0),self.starts)
        if wp.sum()==0 or wn.sum()==0:return None
        return float(np.sum(wp*(np.cumsum(wn)-wn/2))/(wp.sum()*wn.sum()))

class Mean:
    def __init__(self,values,mask):
        self.index=np.flatnonzero(mask);self.values=np.asarray(values)[self.index]
    def __call__(self,w):
        ww=w[self.index]
        return float(np.average(self.values,weights=ww)) if ww.sum()>0 else None

class Pairs:
    """All eligible cross-video positive-negative pairs without materializing them."""
    def __init__(self,rows,score,group):
        y=np.array([x['exist_label'] for x in rows]);s=np.asarray(score);group=np.asarray(group)
        inds=np.flatnonzero(group>=0);order=np.lexsort((s[inds],group[inds]));self.inds=inds[order]
        g=group[self.inds];ss=s[self.inds];self.yy=y[self.inds]
        self.starts=np.r_[0,np.flatnonzero((np.diff(ss)!=0)|(np.diff(g)!=0))+1] if len(inds) else np.array([],dtype=int)
        self.grouplabel=g[self.starts] if len(inds) else np.array([])
        self.gstarts=np.r_[0,np.flatnonzero(np.diff(self.grouplabel))+1] if len(inds) else np.array([],dtype=int)
        samep=[];samen=[];wins=[];coverage=set();npairs=0;groups=0
        by=collections.defaultdict(list)
        for i in inds:by[int(group[i])].append(i)
        for values in by.values():
            p=[i for i in values if y[i]==1];n=[i for i in values if y[i]==0]
            good=sum(rows[i]['vid']!=rows[j]['vid'] for i in p for j in n)
            if good:
                npairs+=good;groups+=1;coverage.update(values)
            byvid=collections.defaultdict(list)
            for i in values:byvid[rows[i]['vid']].append(i)
            for vv in byvid.values():
                pp=[i for i in vv if y[i]==1];nn=[i for i in vv if y[i]==0]
                for i in pp:
                    for j in nn:
                        samep.append(i);samen.append(j);wins.append(float(s[i]>s[j])+.5*float(s[i]==s[j]))
        self.samep=np.array(samep,dtype=int);self.samen=np.array(samen,dtype=int);self.wins=np.array(wins)
        self.coverage={'eligible_pairs':npairs,'mixed_groups':groups,'rows':len(coverage),
                       'positive_videos':len({rows[i]['vid'] for i in coverage if y[i]==1}),
                       'negative_videos':len({rows[i]['vid'] for i in coverage if y[i]==0})}
    def __call__(self,w):
        if not len(self.inds):return None
        ww=w[self.inds];wp=np.add.reduceat(ww*(self.yy==1),self.starts);wn=np.add.reduceat(ww*(self.yy==0),self.starts)
        cum=np.cumsum(wn);prefix=np.r_[0,cum[:-1]][self.gstarts]
        grouplen=np.diff(np.r_[self.gstarts,len(wp)])
        prefix=np.repeat(prefix,grouplen)
        numerator=float(np.sum(wp*(cum-wn/2-prefix)))
        gp=np.add.reduceat(wp,self.gstarts);gn=np.add.reduceat(wn,self.gstarts);denominator=float(np.sum(gp*gn))
        samew=w[self.samep]*w[self.samen]
        numerator-=float(np.sum(samew*self.wins));denominator-=float(samew.sum())
        return numerator/denominator if denominator>0 else None

def main():
    assert (BASE/'runs/minimal_validation/EVALUATION_DONE.json').exists()
    status('statistics','running')
    rules=json.loads((BASE/'PRIMITIVE_CONTROL_FREEZE.json').read_text())
    witness=read(BASE/'audit/PRIMITIVE_LABEL_COVERAGE.jsonl')
    videos=sorted({x['vid'] for f in FAMILIES for sp in ['seen','pseudo'] for x in rows(f,sp)})
    vid_index={v:i for i,v in enumerate(videos)};functions={};datasets={};coverage={};diagnostics={}
    for fam in FAMILIES:
        coverage[fam]={};diagnostics[fam]={}
        for split in ['seen','pseudo']:
            rs=rows(fam,split);data=np.load(BASE/f'runs/minimal_validation/{fam}_{split}_evaluation.npz')
            y=np.array([x['exist_label'] for x in rs]);ids=np.array([vid_index[x['vid']] for x in rs]);datasets[fam,split]=ids
            allmask=np.ones(len(rs),bool);pos=y==1;neg=y==0
            rule=rules['rules'][fam]
            high=(data['action']>=rule['action_median_positive'])&(data['object']>=rule['object_median_positive'])
            bins=np.digitize(data['action'],rule['action_quartiles_all_train'])*4+np.digitize(data['object'],rule['object_quartiles_all_train'])
            group=np.where(high,bins,-1)
            witness_qids={x['qid'] for x in witness if x['family']==fam and x['split']==split and x['both_video_level_entailments']}
            witnessed=pos|np.array([str(x['qid']) in witness_qids for x in rs])
            coverage[fam][split]={'rows':len(rs),'positive':int(pos.sum()),'negative':int(neg.sum()),
                                  'primitive_high_positive':int((high&pos).sum()),'primitive_high_negative':int((high&neg).sum()),
                                  'primitive_high_positive_videos':len({x['vid'] for i,x in enumerate(rs) if high[i] and pos[i]}),
                                  'primitive_high_negative_videos':len({x['vid'] for i,x in enumerate(rs) if high[i] and neg[i]}),
                                  'annotated_video_primitive_negative':len(witness_qids),
                                  'annotated_video_primitive_negative_videos':len({x['vid'] for x in rs if str(x['qid']) in witness_qids})}
            diagnostics[fam][split]={}
            for kind in ['baseline']+MODULES:
                score=data[kind]
                functions[fam,split,'AUROC',kind]=AUC(y,score,allmask)
                functions[fam,split,'primitive_high_AUROC',kind]=AUC(y,score,high)
                functions[fam,split,'annotated_video_primitive_AUROC',kind]=AUC(y,score,witnessed)
                pairs=Pairs(rs,score,group)
                functions[fam,split,'primitive_matched_PairAcc',kind]=pairs
                if kind=='J':coverage[fam][split]['primitive_matching']=pairs.coverage
                th=rules['calibrations'][fam][kind]['threshold'] if kind!='baseline' else json.loads((RUNS[fam]/'threshold_frozen.json').read_text())['threshold']
                functions[fam,split,'FRR',kind]=Mean(score<th,pos)
                functions[fam,split,'RR',kind]=Mean(score<th,neg)
                if kind!='T':
                    hit=data['baseline_hit'] if kind=='baseline' else data['hit_'+kind]
                    functions[fam,split,'raw_R1',kind]=Mean(hit,pos)
                    if kind!='baseline':
                        original=data['baseline_hit']
                        pred=read(BASE/f'runs/minimal_validation/{fam}_{split}_predictions.jsonl')
                        diagnostics[fam][split][kind]={'positive_denominator':int(pos.sum()),'repairs':int((pos&hit&~original).sum()),'damage':int((pos&~hit&original).sum()),
                                                      'candidate_missing':sum(x['modules'][kind]['missing_candidates'] for x in pred if x['label']==1),
                                                      'no_correct_candidate':sum(not x['modules'][kind]['oracle_hit'] for x in pred if x['label']==1),
                                                      'empty_candidate_support':sum(x['modules'][kind]['empty_candidate_support'] for x in pred if x['label']==1)}
                if split=='pseudo' and kind!='baseline':
                    functions[fam,split,'actual_text_PairAcc',kind]=Pairs(rs,data['canonical_'+kind],data['canonical_group'])
                    if kind=='J':coverage[fam][split]['actual_text']=functions[fam,split,'actual_text_PairAcc',kind].coverage
                    chigh=(data['canonical_action']>=rule['action_median_positive'])&(data['canonical_object']>=rule['object_median_positive'])
                    cbins=np.digitize(data['canonical_action'],rule['action_quartiles_all_train'])*4+np.digitize(data['canonical_object'],rule['object_quartiles_all_train'])
                    cg=np.where(chigh&(data['canonical_group']>=0),data['canonical_group']*16+cbins,-1)
                    functions[fam,split,'actual_text_primitive_matched_PairAcc',kind]=Pairs(rs,data['canonical_'+kind],cg)
                    if kind=='J':coverage[fam][split]['actual_text_primitive_matching']=functions[fam,split,'actual_text_primitive_matched_PairAcc',kind].coverage
    dump('audit/CONTROL_COVERAGE.json',coverage);dump('report/LOCALIZATION_REPAIRS_DAMAGE.json',diagnostics)
    ones=np.ones(len(videos));point={key:fn(ones[datasets[key[0],key[1]]]) for key,fn in functions.items()}
    samples={key:[] for key in functions};rng=np.random.default_rng(SEED)
    for repeat in range(1000):
        weights=np.bincount(rng.integers(len(videos),size=len(videos)),minlength=len(videos)).astype(float)
        for key,fn in functions.items():samples[key].append(fn(weights[datasets[key[0],key[1]]]))
        if repeat%200==0:print('bootstrap',repeat,flush=True)
    metrics={};paired={};overall={};overallpaired={};traces={}
    for key,values in samples.items():
        fam,split,metric,kind=key
        metrics.setdefault(fam,{}).setdefault(split,{}).setdefault(metric,{})[kind]={'estimate':point[key],'ci95':ci(values),'valid_bootstrap':sum(v is not None for v in values)}
        traces['/'.join(key)]=np.array([np.nan if v is None else v for v in values])
    def differences(ka,kb):
        pp=point[ka]-point[kb] if point[ka] is not None and point[kb] is not None else None
        vals=[a-b if a is not None and b is not None else None for a,b in zip(samples[ka],samples[kb])]
        return {'estimate':pp,'ci95':ci(vals),'valid_bootstrap':sum(v is not None for v in vals)}
    for fam in FAMILIES:
        for split in ['seen','pseudo']:
            metricnames=metrics[fam][split]
            for metric,kinds in metricnames.items():
                for control in kinds:
                    if control=='J':continue
                    paired.setdefault(fam,{}).setdefault(split,{}).setdefault(metric,{})['J-'+control]=differences((fam,split,metric,'J'),(fam,split,metric,control))
    for split in ['seen','pseudo']:
        for metric,kinds in metrics[FAMILIES[0]][split].items():
            for kind in kinds:
                keys=[(fam,split,metric,kind) for fam in FAMILIES]
                pp=[point[k] for k in keys]
                vv=[np.mean([samples[k][i] for k in keys]) if all(samples[k][i] is not None for k in keys) else None for i in range(1000)]
                overall.setdefault(split,{}).setdefault(metric,{})[kind]={'estimate':float(np.mean(pp)) if all(x is not None for x in pp) else None,'ci95':ci(vv),'valid_bootstrap':sum(x is not None for x in vv)}
                traces['overall/'+split+'/'+metric+'/'+kind]=np.array([np.nan if v is None else v for v in vv])
            for control in kinds:
                if control=='J':continue
                aa=overall[split][metric]['J']['estimate'];bb=overall[split][metric][control]['estimate']
                arr=traces['overall/'+split+'/'+metric+'/J']-traces['overall/'+split+'/'+metric+'/'+control]
                vv=[None if np.isnan(x) else float(x) for x in arr]
                overallpaired.setdefault(split,{}).setdefault(metric,{})['J-'+control]={'estimate':aa-bb if aa is not None and bb is not None else None,'ci95':ci(vv),'valid_bootstrap':sum(x is not None for x in vv)}
    np.savez_compressed(BASE/'report/BOOTSTRAP_TRACES.npz',**traces)
    dump('report/PAIRED_STATISTICS.json',{'seed':SEED,'bootstrap_repeats':1000,'video_union':len(videos),'interval':'exploratory95%','family_aggregation':'equal weight',
                                        'metrics':metrics,'paired_J_minus_control':paired,'overall':overall,'overall_paired_J_minus_control':overallpaired,'coverage':coverage})
    status('statistics','completed',bootstrap_repeats=1000,video_union=len(videos))

if __name__=='__main__':
    try:main()
    except Exception as e:status('statistics','failed',error=repr(e));raise
