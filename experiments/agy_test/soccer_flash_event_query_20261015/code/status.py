from common import ROOT,save,scope_audit
import json,time

def main():
    records=[]
    for variant in ['E0','E2']:
        run=ROOT/'runs'/variant
        status=json.loads((run/'STATUS.json').read_text()) if (run/'STATUS.json').exists() else {'state':'pending'}
        row={'variant':variant,'status':status}
        if (run/'COMPLETE.json').exists():
            row['complete']=json.loads((run/'COMPLETE.json').read_text())
            row['metrics']=json.loads((run/'metrics.json').read_text())['brief']
        records.append(row)
    delta={}
    if all('metrics' in r for r in records):
        delta={k:records[1]['metrics'][k]-records[0]['metrics'][k] for k in records[0]['metrics']}
    result={'updated':time.time(),'completed':sum('metrics' in r for r in records),'total_trainings':2,
        'dataset':'Soccer-GMR Standard','records':records,'paired_point_change_pp':delta,
        'single_seed':2024,'outside_source':scope_audit()}
    if (ROOT/'reference/metrics.json').exists():
        result['released_checkpoint_reference']=json.loads((ROOT/'reference/metrics.json').read_text())['brief']
    save(ROOT/'RESULTS.json',result)
    lines=['# Soccer-GMR Standard：FlashVTG Event Query','',
        f"完成 {result['completed']}/2 项训练。只运行 E0/E2，seed2024。",'',
        '| 模型 | 状态 | epoch | 验证最优MR-full-mAP（NMS前） |','|---|---|---:|---:|']
    for r in records:
        s=r['status'];lines.append(f"| {r['variant']} | {s['state']} | {s.get('epoch','')} | {s.get('best','')} |")
    if any('metrics' in r for r in records):
        lines+=['','| 指标 | E0 | E2 | E2−E0(pp) |','|---|---:|---:|---:|']
        for k in ['G-mIoU@1','G-mIoU@3','mAP','mR@5','mR+@5','AUROC','AUROC_raw','Rej-F1@0.4','N-acc@0.4','PositiveRecall@0.4']:
            a=[r.get('metrics',{}).get(k) for r in records]
            fmt=lambda x:'' if x is None else f'{x:.2f}'
            lines.append('| '+' | '.join([k,*map(fmt,a),fmt(delta.get(k))])+' |')
    lines+=['','按原生训练代码的Val MR-full-mAP（NMS前）严格提升选模和早停；Test不参与选择。',
        'G-mIoU报告阈值固定0.4，与选模分离。每轮Train/Val诊断保存在runs/<variant>/diagnostics/。',
        '成对训练使用修正mask的相同副本；与公开论文数字比较需另看复现环境差异。',
        '公开参考：FlashVTG-GMR Standard G-mIoU@1=39.58、G-mIoU@3=33.53、mAP=24.62、AUROC=74.00。',
        '来源：https://github.com/dymm9977/generalized-moment-retrieval#main-results']
    if 'released_checkpoint_reference' in result:
        lines+=['','## 已发布checkpoint的本地评价','',
            '固定配置一次推理，不用于调整E2；与上面的两项scratch训练分开。','',
            '| 指标 | 已发布checkpoint本地复算 |','|---|---:|']
        for k in ['G-mIoU@1','G-mIoU@3','mAP','mR@5','mR+@5','AUROC','AUROC_raw','Rej-F1@0.4']:
            lines.append(f"| {k} | {result['released_checkpoint_reference'][k]:.2f} |")
    (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'completed':result['completed'],'records':records}),flush=True)
if __name__=='__main__':main()
