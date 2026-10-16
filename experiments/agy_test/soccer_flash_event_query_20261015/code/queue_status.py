"""Report six controlled jobs; compare E2 with E0 within each backbone."""
from common import ROOT,save,rows,scope_audit
import json,time

def read(path,default=None):
    return json.loads(path.read_text()) if path.exists() else default

def main(quiet=False):
    records=[];deltas={}
    for bb in ['flash','moment','qd']:
        pair=[]
        for variant in ['E0','E2']:
            name=variant if bb=='flash' else f'{bb}_{variant}'
            run=ROOT/'runs'/name
            status=read(run/'STATUS.json',{'state':'pending'})
            trace=rows(run/'trace.jsonl') if (run/'trace.jsonl').exists() else []
            selected=read(run/'selected.json',{})
            record={'id':f'{bb}_{variant}','backbone':bb,'variant':variant,'run':str(run),
                'status':status,'completed_epochs':trace[-1]['epoch'] if trace else 0,
                'selected':selected,'seed':2024 if bb=='flash' else 2023}
            if (run/'COMPLETE.json').exists():
                record['complete']=read(run/'COMPLETE.json');record['metrics']=read(run/'metrics.json')['brief']
            pair.append(record);records.append(record)
        if all('metrics' in r for r in pair):
            deltas[bb]={k:pair[1]['metrics'][k]-pair[0]['metrics'][k] for k in pair[0]['metrics']
                if isinstance(pair[0]['metrics'][k],(int,float)) and isinstance(pair[1]['metrics'].get(k),(int,float))}
    result={'updated':time.time(),'dataset':'Soccer-GMR Standard','completed':sum('metrics' in r for r in records),
        'total_trainings':6,'records':records,'paired_point_change_pp':deltas,'outside_source':scope_audit(),
        'selection':'native Val MR-full-mAP; strict improvement; Test only after frozen best',
        'queue':read(ROOT/'QUEUE_STATUS.json',{}),'single_seed_per_backbone':True}
    reference=read(ROOT/'reference/metrics.json')
    if reference:result['released_flash_checkpoint_reference']=reference['brief']
    save(ROOT/'RESULTS.json',result)
    lines=['# Soccer-GMR Standard：Event Query 跨骨干验证','',f"完成 {result['completed']}/6 项正式训练。",'',
        '| 任务 | 状态 | 已完成epoch | 当前epoch / batch | 最佳Val原生mAP | 选中epoch |',
        '|---|---|---:|---|---:|---:|']
    for r in records:
        s=r['status'];sel=r['selected']
        lines.append(f"| {r['id']} | {s['state']} | {r['completed_epochs']} | {s.get('epoch','')} / {s.get('batch','')} | {sel.get('score','')} | {sel.get('epoch','')} |")
    for bb in ['flash','moment','qd']:
        pair=[r for r in records if r['backbone']==bb]
        if not any('metrics' in r for r in pair):continue
        lines+=['',f'## {bb}：正式Test','', '| 指标 | E0 | E2 | E2−E0（百分点） |','|---|---:|---:|---:|']
        for k in ['AUROC','AUROC_raw','G-mIoU@1','G-mIoU@3','mAP','mR@5','mR+@5','Rej-F1@0.4','N-acc@0.4','PositiveRecall@0.4']:
            values=[r.get('metrics',{}).get(k) for r in pair]+[deltas.get(bb,{}).get(k)]
            lines.append('| '+k+' | '+' | '.join('' if v is None else f'{v:.2f}' for v in values)+' |')
    lines+=['','Flash seed2024；Moment/QD seed2023。同一骨干内E0/E2同协议、相同原生参数初始化。',
        '按验证集原生MR-full-mAP选模；Test不参与训练、选模、阈值选择。中途Val成绩不作为正式Test增益。',
        'E2为方案A：文本读取+多层时序读取的全局Event Query；不包含方案B。',
        '每个骨干当前只有一个seed，不能仅凭一次提升宣称稳定增益。',
        '诊断说明见DIAGNOSTICS.md。正式训练与tests/下的Val fixture流程验证分开。']
    if reference:
        lines+=['','已发布Flash checkpoint的本地复算另见reference/COMPARISON.md；其与论文表格的定位差异不计作E2增益。']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    if not quiet:print(json.dumps({'completed':result['completed'],'total':6,'progress':[
        {'id':r['id'],'state':r['status']['state'],'completed_epochs':r['completed_epochs']} for r in records]}),flush=True)
    return result
if __name__=='__main__':main()
