"""Independent metric/integrity checks and explicit terminal decision; no next-stage launch."""
from common import *
import collections

def verify():
    from sklearn.metrics import roc_auc_score
    from statistics import AUC, Pairs
    status('verification','running')
    rng=np.random.default_rng(SEED);checks=0
    for _ in range(50):
        y=rng.integers(2,size=20);s=rng.integers(5,size=20).astype(float);w=rng.integers(4,size=20).astype(float)
        if w[y==0].sum() and w[y==1].sum():
            assert abs(AUC(y,s,np.ones(20,bool))(w)-roc_auc_score(y,s,sample_weight=w))<1e-12
        group=rng.integers(-1,4,size=20);vid=rng.integers(6,size=20)
        rs=[{'exist_label':int(yy),'vid':str(vv)} for yy,vv in zip(y,vid)]
        pair=Pairs(rs,s,group);num=0.;den=0.
        for i in range(20):
            for j in range(20):
                if y[i]==1 and y[j]==0 and group[i]>=0 and group[i]==group[j] and vid[i]!=vid[j]:
                    ww=w[i]*w[j];num+=ww*(float(s[i]>s[j])+.5*float(s[i]==s[j]));den+=ww
        expected=num/den if den else None;actual=pair(w)
        assert expected is None and actual is None or expected is not None and actual is not None and abs(expected-actual)<1e-12
        checks+=1
    stats=json.loads((BASE/'report/PAIRED_STATISTICS.json').read_text());checked_rows=0;loc_rows=0;pool_rows=0
    for fam in FAMILIES:
        for split in ['seen','pseudo']:
            rr=read(BASE/f'runs/minimal_validation/{fam}_{split}_predictions.jsonl');source=rows(fam,split)
            original={str(x['qid']):x for x in read(RUNS[fam]/('best_seen_predictions.jsonl' if split=='seen' else 'pseudo_predictions.jsonl'))}
            assert len(rr)==len(source) and {x['qid'] for x in rr}=={str(x['qid']) for x in source}
            ys=np.array([x['label'] for x in rr])
            for kind in ['baseline']+MODULES:
                scores=[x['baseline_score'] if kind=='baseline' else x['modules'][kind]['score'] for x in rr]
                assert abs(roc_auc_score(ys,scores)-stats['metrics'][fam][split]['AUROC'][kind]['estimate'])<1e-12
                if kind=='baseline':continue
                maps=np.load(BASE/f'runs/minimal_validation/{fam}_{kind}_{split}_maps.npz')
                for i,x in enumerate(rr):
                    mp=maps['values'][maps['offset'][i]:maps['offset'][i+1]];k=max(1,int(np.ceil(.2*len(mp))))
                    expected=float(np.sort(mp)[-k:].mean())
                    assert abs(expected-x['modules'][kind]['score'])<2e-5;pool_rows+=1
                    if x['label']==1 and kind!='T':
                        candidates=original[x['qid']]['pred_relevant_windows_pre_exist'];scores=[]
                        for l,r,_ in candidates:
                            positions=[t for t in range(len(mp)) if l<=t+.5<r]
                            if not positions:positions=[t for t in range(len(mp)) if t<r and t+1>l]
                            scores.append(float(np.mean(mp[positions])) if positions else -1e6)
                        assert np.allclose(scores,x['modules'][kind]['candidate_scores'],atol=1e-5)
                        chosen=max(range(len(scores)),key=lambda t:scores[t]) if scores else None
                        assert chosen==x['modules'][kind]['chosen_candidate'];loc_rows+=1
            pos=ys==1
            for kind in ['H','P','C','J']:
                hit=np.array([x['modules'][kind]['hit'] if x['label']==1 else False for x in rr])
                expected=float(hit[pos].mean());actual=stats['metrics'][fam][split]['raw_R1'][kind]['estimate']
                assert abs(expected-actual)<1e-12
                d=json.loads((BASE/'report/LOCALIZATION_REPAIRS_DAMAGE.json').read_text())[fam][split][kind]
                base=np.array([x['baseline_hit'] if x['label']==1 else False for x in rr])
                assert int(hit[pos].sum()-base[pos].sum())==d['repairs']-d['damage']
            checked_rows+=len(rr)
    freeze=json.loads((BASE/'EXECUTION_FREEZE.json').read_text())
    protected=freeze['protected_files_sha256'];unchanged={};changed=[]
    for p,h in protected.items():
        same=sha(p)==h;unchanged[p]=same
        if not same:changed.append(p)
    assert not changed,changed
    dump('report/INTEGRITY.json',{'all_original_protected_assets_unchanged':True,'protected_assets':len(protected),'checks':unchanged,
                                  'independent_metric_toy_checks':checks,'evaluated_rows_verified':checked_rows,'candidate_specific_reads_verified':loc_rows,
                                  'map_aggregation_rows_verified':pool_rows,'original_model_updates':0,'original_loader_imported':False,
                                  'new_fits':{'action_probes':12,'event_modules':15},'original_model_training_epochs_added':0,'original_sit_resumed':False})
    status('verification','completed',protected_assets=len(protected),evaluated_rows=checked_rows)

def fmt(v):
    return 'NA' if v is None else f'{v:.4f}'

def estimate(v):
    return fmt(v['estimate'])+(' ['+', '.join(fmt(x) for x in v['ci95'])+']' if v['ci95'] else ' [NA]')

def write_report():
    stats=json.loads((BASE/'report/PAIRED_STATISTICS.json').read_text());audit=json.loads((BASE/'audit/INPUT_AUDIT.json').read_text())
    action=json.loads((BASE/'audit/ACTION_PROBE.json').read_text());repairs=json.loads((BASE/'report/LOCALIZATION_REPAIRS_DAMAGE.json').read_text())
    eventfreeze=json.loads((BASE/'EVENT_CODE_FREEZE.json').read_text());overall=stats['overall'];delta=stats['overall_paired_J_minus_control'];coverage=stats['coverage']
    reasons=[]
    if (BASE/'audit/PROTOCOL_INCIDENT.json').exists():reasons.append('来源成员检查误读取含真实 U 行的 val 发布文件（只用 S 行核对，U 未进入训练/前向/选点/指标）；违反不读取边界，不能认证完全未接触 U。')
    if audit['temporal_alignment']['status']!='VERIFIED':reasons.append('原双流真实时间来源未核实；仅沿用 min_len 与 clip_length=1 索引假设。')
    if any(coverage[f]['pseudo']['primitive_matching']['positive_videos']<20 or coverage[f]['pseudo']['primitive_matching']['negative_videos']<20 for f in FAMILIES):
        reasons.append('至少一族 primitive 高支持匹配缺少预定的20个正/负独立视频覆盖。')
    if any(coverage[f]['pseudo']['actual_text']['positive_videos']<20 or coverage[f]['pseudo']['actual_text']['negative_videos']<20 for f in FAMILIES):
        reasons.append('至少一族相同实际文本跨视频控制覆盖不足；配对数不能替代独立视频数。')
    gains={k:delta['pseudo']['AUROC']['J-'+k] for k in ['H','P','C','T']}
    pass_auroc=all(v['estimate'] is not None and v['estimate']>0 and v['ci95'] and v['ci95'][0]>0 for v in gains.values())
    if not pass_auroc:reasons.append('J 相对 H/P/C/T 的 pseudo AUROC 未全部取得正向且 paired 区间支持的增量。')
    pmetric=overall['pseudo']['primitive_matched_PairAcc']['J'];tmetric=overall['pseudo']['actual_text_PairAcc']['J']
    controlled=all(x['estimate'] is not None and x['ci95'] and x['ci95'][0]>.5 for x in [pmetric,tmetric])
    condition_deltas=delta['pseudo']['primitive_matched_PairAcc']
    controlled=controlled and all(condition_deltas['J-'+k]['ci95'] and condition_deltas['J-'+k]['ci95'][0]>0 for k in ['H','P','C','T'])
    if not controlled:reasons.append('primitive 条件与实际文本控制未同时支持 J 的额外视觉证据。')
    loc=delta['pseudo']['raw_R1']['J-baseline']
    locgood=loc['ci95'] and loc['ci95'][0]>0
    if not locgood:reasons.append('冻结候选上的无 GT map 未取得 paired 区间支持的 raw R1@.5 增益。')
    guardrails={}
    for fam in FAMILIES:
        mm=stats['metrics'][fam]
        guardrails[fam]={
            'seen_AUROC_noninferior_point':mm['seen']['AUROC']['J']['estimate']>=mm['seen']['AUROC']['baseline']['estimate'],
            'seen_raw_noninferior_point':mm['seen']['raw_R1']['J']['estimate']>=mm['seen']['raw_R1']['baseline']['estimate'],
            'pseudo_FRR_noninferior_point':mm['pseudo']['FRR']['J']['estimate']<=mm['pseudo']['FRR']['baseline']['estimate'],
            'pseudo_RR_noninferior_point':mm['pseudo']['RR']['J']['estimate']>=mm['pseudo']['RR']['baseline']['estimate']}
    guardgood=all(all(g.values()) for g in guardrails.values())
    if not guardgood:reasons.append('原 seen/拒绝护栏未全部满足；不以更有利 pseudo 阈值修复结论。')
    # Temporal source and precision gaps take priority over a mechanism rejection.
    input_or_coverage_gap=((BASE/'audit/PROTOCOL_INCIDENT.json').exists() or audit['temporal_alignment']['status']!='VERIFIED' or
                           any(coverage[f]['pseudo']['primitive_matching']['positive_videos']<20 or coverage[f]['pseudo']['primitive_matching']['negative_videos']<20 or
                               coverage[f]['pseudo']['actual_text']['positive_videos']<20 or coverage[f]['pseudo']['actual_text']['negative_videos']<20 for f in FAMILIES))
    precise_no_increment=any(v['ci95'] and v['ci95'][1]<=0 for v in gains.values())
    decision=('PASS_FOR_NEXT_STAGE_PROPOSAL' if not reasons else 'STOP' if not input_or_coverage_gap and precise_no_increment else 'INCONCLUSIVE')
    summary={'decision':decision,'at':now(),'scientific_question':'primitive 已相关时，J 是否提供跨未见语义的额外视觉证据？',
             'reasons':reasons,'guardrails':guardrails,'pseudo_J_minus_controls':gains,'pseudo_raw_J_minus_baseline':loc,
             'next_stage_started':False,'R_started':False,'full_model_training_started':False,
             'training_authorization_note':'用户追加条件性继续训练意向；本轮未达到通过门槛，因此不触发下一阶段。所有拟合每GPU<=2，总<=4，不增加变体或多seed。'}
    dump('report/DECISION.json',summary)
    lines=['# A/A1/B 最小验证报告','',f'结论：**{decision}**。本阶段已结束，没有启动 R、共享 map 完整模型训练、真实 U/test 或原 sit 续训。','',
           '本轮问题是 primitive 已相关时，J 是否仍提供跨未见语义的额外视觉证据。以下 pseudo 结果是原 S 的训练侧开发证据，单 seed3407；不是正式 U 确认或跨训练种子稳定性。','',
           '## 动作可读性','', '| 族 | S_train 动词数 | motion temporal | motion mean | motion static | appearance mean |', '|---|---:|---:|---:|---:|---:|']
    for fam in FAMILIES:
        aa=action[fam];pp=aa['probes']
        lines.append('| '+fam+' | '+str(len(aa['vocab_from_train_only']))+' | '+' | '.join(fmt(pp[k]['seen_balanced_accuracy']) for k in ['motion_temporal','motion_mean','motion_static','appearance_mean'])+' |')
    lines += ['', '上表为 seen 平衡准确率。闭集词表仅由各族 S_train≥10 个可用 S+ GT segment 的类别定义；held-out verb 不补标签拟合。12 个128维 affine probe，20轮上限，seen选点。SlowFast静态控制仍有clip内部运动；时间统计没有稳定超过外观/时间均值控制。不能由该结果宣布未见动作理解成立，也不能宣布冻结表示无动作信息。逐类词表、OOV覆盖、共同视频paired区间见 [ACTION_PROBE.json](../audit/ACTION_PROBE.json)。','',
              '## 输入与覆盖','',f"核验 {audit['token_coverage']['total']} 个唯一文本缓存、{audit['unique_videos']} 个视频。BPE长度全部匹配，SOT/EOT和32-token截断逐行审计；动作有效跨度 {audit['token_coverage']['action_span_valid']}，实体 {audit['token_coverage']['object_span_valid']}。原图跨度缺失时采用唯一词形匹配；失败回退整个非特殊token query并保留分母。角色token为上下文化表征，不是去耦primitive标签。",'',
              '实际流序 CLIP512 | SlowFast2304 | TEF2；语义模块仅用投影前两路raw values，排除TEF。缓存只有features、没有时间戳，现有提取脚本不能与这些数组建立可核验来源联系。保留原min_len及一秒bin假设；**真实双流时间对齐未认证，全部B结果受此限制，不能PASS。** 正例旧文本encoder来源也未在cache中嵌入token IDs/weights；长度一致不能替代完整encoder来源认证。','',
              'S−只确认完整事件缺席。正事件注释可提供同视频动作/实体的规范化蕴含证据，但不确认实体身份/角色绑定；同时报告两路P分数控制，不能称人工primitive真标签。','',
              '| 族 | pseudo正/负 | 标注视频primitive支持负例 | 高P支持正/负 | 匹配对数 | 匹配正/负视频 | actual-text组/对 |','|---|---:|---:|---:|---:|---:|---:|']
    for fam in FAMILIES:
        c=coverage[fam]['pseudo'];p=c['primitive_matching'];t=c['actual_text']
        lines.append(f"| {fam} | {c['positive']}/{c['negative']} | {c['annotated_video_primitive_negative']} | {c['primitive_high_positive']}/{c['primitive_high_negative']} | {p['eligible_pairs']} | {p['positive_videos']}/{p['negative_videos']} | {t['mixed_groups']}/{t['eligible_pairs']} |")
    lines+=['','P动作/实体分支均由原完整事件标签训练，仅是 operational support。高支持门槛为S_train正例中位数，联合quartile分箱由S_train固定；pseudo不按J筛选。actual-text控制固定相同实际cached特征、mask及角色vectors，T组内必须严格tie。配对bootstrap使用两个原视频端点权重乘积；不把组合对数当独立样本量。','',
            '## 冻结小模块与总体存在结果','',f"每模块参数量：{json.dumps(eventfreeze['parameters_per_module'],ensure_ascii=False)}。15个独立fit，宽度32，AdamW lr=.001，8轮上限，seen AUROC选点；P/C不共享训练参数。相同event监督、GT支持局部训练和top20%均值主读出；S+窗外不标负，GT不进入存在或定位推理。单对J依赖两路visual values和乘积交互；架构与实际相同文本跨视频变化检查均单列。",'',
            '| 族 | baseline | H | P | C | J | T |','|---|---:|---:|---:|---:|---:|---:|']
    for fam in FAMILIES:
        mm=stats['metrics'][fam]['pseudo']['AUROC']
        lines.append('| '+fam+' | '+' | '.join(fmt(mm[k]['estimate']) for k in ['baseline']+MODULES)+' |')
    lines.append('| 等权 | '+' | '.join(fmt(overall['pseudo']['AUROC'][k]['estimate']) for k in ['baseline']+MODULES)+' |')
    lines+=['','族间证据不一致：J对P在throw/open_close的点估计较高，但sit较低；不能挑族加权或概括为组合/身份绑定成立。']
    lines+=['','| 等权 paired 差值 | AUROC estimate [95%] |','|---|---:|']
    for k,v in gains.items():lines.append('| J−'+k+' | '+estimate(v)+' |')
    lines+=['','所有区间来自1000次seed3407共同原视频paired bootstrap，族等权，探索性95%；逐族差值、seen结果及FRR/RR均保存在 [PAIRED_STATISTICS.json](PAIRED_STATISTICS.json)。','',
            '## primitive 条件与真实文本控制','', '| pseudo指标（等权） | H | P | C | J | T |','|---|---:|---:|---:|---:|---:|']
    for metric in ['primitive_high_AUROC','primitive_matched_PairAcc','annotated_video_primitive_AUROC','actual_text_PairAcc','actual_text_primitive_matched_PairAcc']:
        lines.append('| '+metric+' | '+' | '.join(estimate(overall['pseudo'][metric][k]) for k in MODULES)+' |')
    lines+=['',f"primitive匹配等权区间仅有 {pmetric['valid_bootstrap']}/1000 次bootstrap同时保留三族有效正负支持；sit的匹配负例只有1个视频。该区间是有效重采样子集上的描述，不能当覆盖充分的跨族证据。",'',
            '| 族 | J primitive匹配PairAcc [95%] | J actual-text PairAcc [95%] |','|---|---:|---:|']
    for fam in FAMILIES:
        mm=stats['metrics'][fam]['pseudo']
        lines.append('| '+fam+' | '+estimate(mm['primitive_matched_PairAcc']['J'])+' | '+estimate(mm['actual_text_PairAcc']['J'])+' |')
    lines+=['','| primitive匹配 paired 差值 | estimate [95%] |','|---|---:|']
    for k in ['H','P','C','T']:lines.append('| J−'+k+' | '+estimate(delta['pseudo']['primitive_matched_PairAcc']['J-'+k])+' |')
    lines+=['','actual-text与primitive同时匹配项使用同一冻结规则，为更严格但通常更小的控制覆盖。标注支持项是视频级primitive蕴含，不能当同时实例/身份绑定真标签。覆盖不足或bootstrap缺类时记NA/未决，不填0.5。','',
            '## 冻结原候选上的真实定位','', '| 族 | baseline raw | H raw | P raw | C raw | J raw | J修复/破坏 | 无正确候选 |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for fam in FAMILIES:
        mm=stats['metrics'][fam]['pseudo']['raw_R1'];d=repairs[fam]['pseudo']['J']
        lines.append('| '+fam+' | '+' | '.join(fmt(mm[k]['estimate']) for k in ['baseline','H','P','C','J'])+f" | {d['repairs']}/{d['damage']} | {d['no_correct_candidate']}/{d['positive_denominator']} |")
    lines.append('| 等权 | '+' | '.join(fmt(overall['pseudo']['raw_R1'][k]['estimate']) for k in ['baseline','H','P','C','J'])+' | — | — |')
    lines+=['','| 定位 paired 差值 | raw R1@.5 estimate [95%] |','|---|---:|']
    for k in ['baseline','H','P','C']:lines.append('| J−'+k+' | '+estimate(delta['pseudo']['raw_R1']['J-'+k])+' |')
    lines+=['','读出固定为候选窗内map均值，map-only重排；无系数搜索，空支撑−1e6，平局保持原顺序。候选坐标/数量来自原冻结输出，GT只计算IoU，全部原pseudo正例为分母。T没有真实时序map，定位NA；不以峰入GT或候选oracle替代定位性能。','',
            '## 决策、护栏与交付','']
    lines += ['- '+r for r in reasons]
    lines += ['', '护栏（J对原baseline点估计）：`'+json.dumps(guardrails,ensure_ascii=False)+'`。阈值仅由seen固定，原baseline阈值保留；护栏失败不会通过降低S表现或调pseudo阈值掩盖。','',
              '核心问题尚未获得可继续完整训练的充分支持。**停止本阶段；不宣布joint机制已成立或被完全否定，不扫超参/损失挽救。** 若以后另开阶段，应先补齐可核验的双流时间来源及足够primitive条件/相同文本控制，单独明确范围；目前不触发下一阶段训练。','',
              '代码、freeze、12个动作probe与15个head checkpoint、逐行原预测/控制得分、局部map、paired统计和失败日志均位于本新目录。所有受保护原代码/数据/feature/checkpoint/旧输出hash通过终检；原loader未导入，临时目录/依赖缓存/pycache也隔离。训练并发为两张GPU各最多两个任务，最多4，不增加变体、多seed或额外教师。来源检查的U读取偏差已单独保存在 [PROTOCOL_INCIDENT.json](../audit/PROTOCOL_INCIDENT.json)，不能声称完全未接触U；所有实际拟合、评估、阈值与checkpoint选择仍只使用原S训练侧视图。','',
              '入口：[执行冻结](../EXECUTION_FREEZE.json)、[模块代码冻结](../EVENT_CODE_FREEZE.json)、[输入审计](../audit/INPUT_AUDIT.json)、[控制覆盖](../audit/CONTROL_COVERAGE.json)、[逐行预测](../runs/minimal_validation/PREDICTIONS.jsonl)、[完整性](INTEGRITY.json)、[决策](DECISION.json)。']
    (BASE/'report/REPORT.md').write_text('\n'.join(lines)+'\n')
    (BASE/'report/DECISION.md').write_text('# A/A1/B 决策\n\n**'+decision+'**。验证与拟合已结束，未启动下一阶段。\n\n'+'\n'.join('- '+r for r in reasons)+'\n\n完整证据见 [REPORT.md](REPORT.md)。追加的条件性继续训练意向未触发：本阶段不满足通过门槛。原始时间来源和primitive条件覆盖不足不能当机制否定；也不能以总体AUROC或GT条件信号宣称成功。\n')
    banner=f"更新 {now()}：**A/A1/B 已完成，结论 {decision}；本阶段停止，未启动 R/共享 map 完整训练。**\n\n本轮结果见 [REPORT.md](report/REPORT.md)、[DECISION.md](report/DECISION.md)、[STATUS.json](STATUS.json)。新增代码与全部产物仅位于本目录；旧队列和原代码/数据均只读。下方方案/历史状态保留为执行前记录，当前状态以上述报告为准。\n\n---\n\n"
    for name in ['README.md','HANDOFF.md']:
        path=BASE/name;oldtext=path.read_text()
        if oldtext.startswith('更新 ') and '\n\n---\n\n' in oldtext:
            oldtext=oldtext.split('\n\n---\n\n',1)[1]
        path.write_text(banner+oldtext)
    status('report','completed',decision=decision,next_stage_started=False)
    dump('runs/minimal_validation/DELIVERY_MANIFEST.json',{'at':now(),'decision':decision,'artifacts_sha256':{str(p.relative_to(BASE)):sha(p) for directory in ['code','audit','report'] for p in (BASE/directory).rglob('*') if p.is_file()},'next_stage_started':False})
    print(decision,flush=True)

if __name__=='__main__':
    try:verify();write_report()
    except Exception as e:status('closeout','failed',error=repr(e));raise
