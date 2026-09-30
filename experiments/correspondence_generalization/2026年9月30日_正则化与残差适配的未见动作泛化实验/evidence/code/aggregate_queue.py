"""Per-split reports, separate video intervals and seed variation, no U selection."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE/'code'))
from diagnostic_metrics import iou
root=Path(sys.argv[1]).resolve();assert root.is_relative_to(HERE/'runs')
state=json.loads((root/'queue_state.json').read_text());frozen=json.loads((root/'SELECTION_FROZEN.json').read_text())
out=root/'report';out.mkdir(exist_ok=True)
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines()]
def intervals(run,baseline,track):
    rr=rows(run/'views/test.jsonl');pred={str(p['qid']):p for p in rows(run/'test/test_predictions.jsonl')};ref={str(p['qid']):p for p in rows(baseline/'test/test_predictions.jsonl')} if baseline else None
    vids=np.array([r['vid'] for r in rr]);unique=np.unique(vids);g={v:np.flatnonzero(vids==v) for v in unique};rng=np.random.default_rng(3407)
    def features(pp):
        score=np.array([pp[str(r['qid'])].get('pred_exist_score',0) for r in rr]);hit=[]
        for r in rr:
            ww=pp[str(r['qid'])].get('pred_relevant_windows_pre_exist',pp[str(r['qid'])]['pred_relevant_windows']);ww=sorted(ww,key=lambda z:z[2],reverse=True)
            hit.append(max((iou(ww[0],gt) for gt in r['relevant_windows']),default=0) if ww else 0)
        return score,np.array(hit)
    x,h=features(pred);rx,rh=features(ref) if ref else (None,None)
    matched=[]
    if track=='gmr':
        split=json.loads((run/'result.json').read_text())['args']['split'];qindex={str(r['qid']):i for i,r in enumerate(rr)}
        for pair in rows(HERE.parents[1]/'data/release/semantic_existence_v2'/split/'matched_u_pairs.jsonl'):
            pi=qindex[str(pair['positive_qid'])];ni=qindex[str(pair['negative_qid'])];assert vids[pi]==vids[ni];matched.append((pi,ni,vids[pi]))
    part=np.array([r['partition'] for r in rr]);label=np.array([r['exist_label'] for r in rr]);th=json.loads((run/'threshold_frozen.json').read_text())['threshold'] if track=='gmr' else None;rth=json.loads((baseline/'threshold_frozen.json').read_text())['threshold'] if ref and track=='gmr' else None
    def measure(ix,s,v,threshold):
        result={}
        for name,parts in [('seen',('S+','S-')),('unseen',('U+','U-'))]:
            use=ix[np.isin(part[ix],parts)];pos=use[label[use]==1];neg=use[label[use]==0]
            if track=='gmr' and len(pos) and len(neg):result[name+'_AUROC']=float(roc_auc_score(label[use],s[use]));result[name+'_FRR']=float((s[pos]<threshold).mean());result[name+'_RR']=float((s[neg]<threshold).mean())
            for iou_th in (.5,.7):
                if len(pos):result[name+f'_raw_R1@{iou_th}']=float((v[pos]>=iou_th).mean())
                if track=='gmr' and len(pos):result[name+f'_hard_R1@{iou_th}']=float(((v[pos]>=iou_th)&(s[pos]>=threshold)).mean())
            if track=='gmr' and len(pos):
                correct=pos[v[pos]>=.5]
                if len(correct):result[name+'_raw_correct_FRR@.5']=float((s[correct]<threshold).mean())
        if track=='gmr':
            pair=[]
            # Repeated videos from bootstrap retain their repeated weight.
            for video in np.unique(vids[ix]):
                local=ix[vids[ix]==video];pos=local[label[local]==1];neg=local[label[local]==0]
                if len(pos) and len(neg):
                    # Original rows may repeat with a sampled video; normalize
                    # duplicate multiplicity so each sampled video weighs once.
                    count=len(local)//len(g[video]);pp=np.unique(pos);nn=np.unique(neg)
                    pair.extend([float(a>b)+.5*float(a==b) for a in s[pp] for b in s[nn]]*count)
            if pair:result['all_same_video_PairAcc']=float(np.mean(pair))
            multiplicity={video:len(ix[vids[ix]==video])//len(g[video]) for video in np.unique(vids[ix])};official_pairs=[]
            for pi,ni,video in matched:
                official_pairs.extend([float(s[pi]>s[ni])+.5*float(s[pi]==s[ni])]*multiplicity.get(video,0))
            if official_pairs:result['matched_U_PairAcc']=float(np.mean(official_pairs))
        return result
    values={};gains={}
    for _ in range(1000):
        ix=np.concatenate([g[v] for v in rng.choice(unique,len(unique),replace=True)]);m=measure(ix,x,h,th);b=measure(ix,rx,rh,rth) if ref else {}
        for k,v in m.items():values.setdefault(k,[]).append(v)
        for k,v in m.items():
            if k in b:gains.setdefault(k,[]).append(v-b[k])
    return {'unit':'video','paired':bool(ref),'resamples':1000,'seed':3407,'absolute_ci95':{k:np.quantile(v,[.025,.975]).tolist() for k,v in values.items()},'gain_over_same_seed_baseline_ci95':{k:np.quantile(v,[.025,.975]).tolist() for k,v in gains.items()},'limitations':'All same-video pair metric differs from official matched_u_pairs PairAcc; both labeled separately. Seed variation is separate.'}

records=[];lookup={}
for ident,t in state['tasks'].items():
    if t.get('phase')!='formal' or t.get('state')!='completed':continue
    run=Path(t['run'])
    if not (run/'test/report.json').exists():continue
    report=json.loads((run/'test/report.json').read_text());record={k:t[k] for k in ('backbone','split','track','method','seed')};record.update(run=str(run),report=report);records.append(record);lookup[(t['backbone'],t['split'],t['track'],t['method'],t['seed'])]=run
for r in records:
    if r['seed']!=3407:continue
    run=Path(r['run']);base=lookup.get((r['backbone'],r['split'],r['track'],'baseline',r['seed']))
    ci=intervals(run,base,r['track']);(out/(run.name+'_video_ci.json')).write_text(json.dumps(ci,indent=2))
lines=['# 固定样本对应关系泛化：自动队列最终报告','',f"冻结简单控制：{frozen['strongest_simple']}；候选 window 正式进入：{frozen['candidate_formal_enabled']}。真实 U 从未参与选择。",'', '## GMR 逐组结果','', '| split | model | method | seed | S AUROC | U AUROC | gap | U+ FRR | U− RR | matched U PairAcc | raw U R1 .5/.7 | hard U R1 .5/.7 |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
for r in records:
    if r['track']!='gmr':continue
    q=r['report']['quadrants'];s=q['seen'];u=q['unseen'];p=r['report']
    lines.append(f"| {r['split']} | {r['backbone']} | {r['method']} | {r['seed']} | {s['auroc']:.4f} | {u['auroc']:.4f} | {p['auroc_gap']:.4f} | {u['positive_frr']:.4f} | {u['negative_rr']:.4f} | {p['matched_u_pairacc']:.4f} | {u['raw']['R1@0.5']:.4f}/{u['raw']['R1@0.7']:.4f} | {u['diagnostic_hard']['R1@0.5']:.4f}/{u['diagnostic_hard']['R1@0.7']:.4f} |")
lines+=['','## 独立正例 VTG（没有存在头，只有原 S+）','', '| split | model | method | seed | seen R1 .5/.7 | unseen R1 .5/.7 |','|---|---|---|---:|---|---|']
for r in records:
    if r['track']!='vtg':continue
    q=r['report']['positive_vtg'];s=q['S+'];u=q['U+'];lines.append(f"| {r['split']} | {r['backbone']} | {r['method']} | {r['seed']} | {s['R1@0.5']:.4f}/{s['R1@0.7']:.4f} | {u['R1@0.5']:.4f}/{u['R1@0.7']:.4f} |")
# Equal-weight groups; never pool rows to obscure a failed split.
summary={};seed_variation={}
for r in records:
    key=(r['track'],r['backbone'],r['method']);axis='action' if r['split'].startswith('A') else 'composition';k='|'.join((*key,axis,str(r['seed'])))
    if r['track']=='gmr':value=r['report']['quadrants']['unseen']['auroc']
    else:value=r['report']['positive_vtg']['U+']['R1@0.5']
    summary.setdefault(k,[]).append(value)
for k,v in summary.items():summary[k]={'equal_weight_mean':float(np.mean(v)),'groups':len(v),'complete_axis':len(v)==(3 if '|action|' in k else 2)}
for k,v in summary.items():
    stem=k.rsplit('|',1)[0];seed_variation.setdefault(stem,[]).append(v['equal_weight_mean'])
seed_variation={k:{'seed_means':v,'std_ddof1':float(np.std(v,ddof=1)) if len(v)>1 else None,'n_seeds':len(v)} for k,v in seed_variation.items()}
mechanism=[]
for r in records:
    if r['method']=='baseline':continue
    base=next((x for x in records if all(x[k]==r[k] for k in ('backbone','split','track','seed')) and x['method']=='baseline'),None)
    if not base:continue
    item={k:r[k] for k in ('backbone','split','track','method','seed')}
    if r['track']=='gmr':
        cur=r['report']['quadrants'];ref=base['report']['quadrants'];sg=cur['seen']['auroc']-ref['seen']['auroc'];ug=cur['unseen']['auroc']-ref['unseen']['auroc'];rr=cur['unseen']['negative_rr']-ref['unseen']['negative_rr'];fr=cur['unseen']['positive_frr']-ref['unseen']['positive_frr']
        item.update(seen_auroc_gain=sg,unseen_auroc_gain=ug,unseen_rr_gain=rr,unseen_frr_change=fr,gap_shrink_from_seen_loss_only=ug<=0 and sg<0,acceptance_gain_with_rejection_loss=fr<0 and rr<0)
        item['descriptive_generalization_pass']=ug>0 and sg>=-.01 and rr>=-.03 and fr<=.03
    else:
        cur=r['report']['positive_vtg'];ref=base['report']['positive_vtg'];item.update(unseen_R1_05_gain=cur['U+']['R1@0.5']-ref['U+']['R1@0.5'],unseen_R1_07_gain=cur['U+']['R1@0.7']-ref['U+']['R1@0.7'],seen_R1_05_gain=cur['S+']['R1@0.5']-ref['S+']['R1@0.5']);item['descriptive_generalization_pass']=item['unseen_R1_05_gain']>0 and item['unseen_R1_07_gain']>=0
    item['causal_correspondence_mechanism_proven']=False;mechanism.append(item)
(out/'MECHANISM_ANALYSIS.json').write_text(json.dumps({'training_side_gate':frozen['mechanism_decision'],'formal_descriptive_checks':mechanism,'seed':3407,'multi_seed_experiments':False,'interpretation':'Association and downstream controls only. No proven causality, no novelty inferred, no test-driven model reselection.'},indent=2))
failed={k:v for k,v in state['tasks'].items() if v['state'] in ('failed','skipped')};lines+=['','## 完整性与机制限制','', '各组视频 paired bootstrap 区间保存为 *_video_ci.json；summary.json 为动作轴/组合轴等权摘要，本次仅 seed=3407，不进行或估计多种子变化。缺少组的摘要明确标 complete_axis=false。','', '冻结的 gate 仅支持关联，不证明因果。候选若被跳过，原因记录在 MECHANISM_GATE.json 和任务状态；不能宣称新算法或通用对应机制已成立。普通正则/适配层若同样有效，报告简洁控制结论。任何 U+ 接受提高但 U− RR 崩溃、U 不提高而 S 降低的现象均不计为泛化成功。','', 'Flash 原评测对没有 proposal 的正例可能跳过 R1 分母；本报告 raw/hard R1 固定完整正例分母。原官方选 checkpoint 规则仍保留，官方指标另存各 test 报告。复制后的评测仅补齐空预测 qid，不造 proposal。','', 'workers=0 与历史配置不同；历史报告不能混充当前比较。训练日志与来源记录保留，精确全部 FLOPs 与活跃 GPU 总时间未测量。','',f"失败/条件跳过任务 {len(failed)} 个，详见 failed_or_skipped.json；机制与失败模式见 MECHANISM_ANALYSIS.json。完成矩阵条目 {len(records)} 个。"]
if state.get('budget_audit_enabled') is False:
    cancelled={k:v for k,v in state['tasks'].items() if v['state']=='cancelled_by_user'}
    (out/'cancelled_by_user.json').write_text(json.dumps(cancelled,indent=2))
    lines[0]='# A1/QD 六组双轨实验最终报告'
    lines+=['','## 用户更新后的范围','', '仅 A1/QD，baseline/regularized/adapter × GMR/正例 VTG，共六组，seed=3407。其他正式训练及评测已取消。按用户要求不执行同预算核验，不声明初始化、batch 顺序、更新或曝光已通过成对核验。原已完成/运行任务的旧日志仅保留历史记录。']
(out/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n');(out/'records.json').write_text(json.dumps(records,indent=2));(out/'summary.json').write_text(json.dumps(summary,indent=2));(out/'failed_or_skipped.json').write_text(json.dumps(failed,indent=2));print(out/'FINAL_REPORT.md')
