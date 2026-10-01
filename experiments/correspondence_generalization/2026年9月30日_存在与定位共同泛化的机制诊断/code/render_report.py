"""Render evidence tables after all baseline and supplemental diagnostics finish."""
import datetime
import argparse
import json
from phase2 import STAGE, dump, sha

FAMILIES=('throw','open_close','sit')


def load(p):return json.loads(p.read_text())


def number(x):return '不可用' if x is None else f'{x:.4f}'


def with_ci(d):
    ci=d.get('ci')
    return number(d['point'])+(f" [{ci[0]:.4f}, {ci[1]:.4f}]" if ci else ' [不可用]')


def main():
    baseline=load(STAGE/'diagnostics/BASELINE_METRICS.json')
    coverage=load(STAGE/'report/CROSS_FAMILY_COVERAGE.json')
    control=load(STAGE/'report/CONTROLLED_QUERY_SUMMARY.json')
    parser=argparse.ArgumentParser();parser.add_argument('--closeout',action='store_true');args=parser.parse_args()
    if args.closeout:
        assert load(STAGE/'closeout_state.json')['state']=='summary_completed_report_pending'
    else:
        mainqueue=load(STAGE/'queue_state.json');followup=load(STAGE/'followup_state.json')
        assert mainqueue['state']=='diagnostics_completed_decision_pending'
        assert followup['state']=='supplemental_diagnostics_completed_decision_pending'
    lines=['# 第二阶段多族机制诊断报告','',f"生成时间：{datetime.datetime.now().astimezone().isoformat()}。",'',
           '本报告仅用 A1/QD、seed3407 的训练侧留族视图。Throw/open_close完成100epochs；sit训练按用户要求停止，保留77轮账本，以原seen-only best（编号11）补评测，latest为编号76。本次新增训练为零，原停止状态与checkpoint不变；跨族均值描述保存模型，不代表三个族都完成100轮。没有新候选训练、正式U确认、多seed或种子稳定性结论。决策见 DECISION.md。','',
           '## 来源与覆盖','',
           '| 族 | 伪未见行 | 正/负 | 视频 | query字符串 | 混合标签视频 | 同句控制组/行/对 |','|---|---:|---:|---:|---:|---:|---:|']
    for f in FAMILIES:
        d=coverage[f]['pseudo'];c=coverage[f]['same_query_control']
        lines.append(f"| {f} | {d['rows']} | {d['positive']}/{d['negative']} | {d['videos']} | {d['unique_query_strings']} | {d['mixed_label_videos']} | {c['query_groups']}/{c['rows']}/{c['pairs']} |")
    lines += ['',f"跨族伪未见视频交集：{coverage['pseudo_video_overlap']}。视图保留原行字节，训练/开发视频无重叠，冻结词形规则在训练行上无命中（ASSET_REVALIDATION.json）。隔离基于主动作标注和词形，不声称完整概念隔离。共享视频与负例构造使三个族不能视作独立域或独立重复试验。",'',
              '## Baseline指标与不确定性','',
              '比率使用0–1单位。AUROC、raw R1@.5为97.5%原视频bootstrap区间，其他指标为95%区间；1000次、seed3407。跨族使用共同视频权重并等权汇总。这些是baseline绝对区间，不能当作候选改善或paired增益区间。','']
    for split,label in [('pseudo','伪未见'),('seen','Seen')]:
        lines += [f'### {label}','', '| 族 | AUROC | raw R1@.5 | 官方gated R1@.5 | FRR | RR |','|---|---|---|---|---|---|']
        for f in FAMILIES:
            d=baseline['families'][f][split]['metrics']
            lines.append('| '+f+' | '+' | '.join(with_ci(d[k]) for k in ('AUROC','raw_R1_05','gated_R1_05','FRR','RR'))+' |')
        d=baseline['equal_family_mean'][split]
        lines.append('| 等权族均值 | '+' | '.join(with_ci(d[k]) for k in ('AUROC','raw_R1_05','gated_R1_05','FRR','RR'))+' |')
    lines += ['','主要指标显著为正、gated收益与不劣及seen/拒绝护栏只适用于同族候选对baseline的比较；本轮没有候选，不能宣称通过或未通过候选的冻结改善门槛。区间跨界应记不确定；界限未调整。','',
              '## D3：失败分解与best/latest','',
              '| 族 | raw错 | raw对且接受 | raw对且硬拒 | 负例错误接受 | raw错/hard失败 | raw对中硬拒率 |','|---|---:|---:|---:|---:|---:|---:|']
    for f in FAMILIES:
        d=load(STAGE/'diagnostics'/f/'baseline/FAILURE_DECOMPOSITION.json')['pseudo'];c=d['counts']
        lines.append(f"| {f} | {c['raw_incorrect']} | {c['raw_correct_accepted']} | {c['raw_correct_rejected']} | {c['negative_accepted']}/{c['negative']} | {number(d['raw_errors_over_hard_failures'])} | {number(d['raw_correct_rejected_over_raw_correct'])} (n={c['raw_correct']}) |")
    lines += ['','诊断硬拒绝使用各模型seen-only Youden阈值；官方soft gate与此不同。最新checkpoint阈值另用其seen预测拟合，仅作描述；未用伪未见重新挑checkpoint或阈值。','',
              '| 族/模型 | best epoch（1-based） | latest epoch | latest权重等同best | best→latest伪未见AUROC | raw R1@.5 | gated R1@.5 |','|---|---:|---:|---|---:|---:|---:|']
    combinations=[(f,'baseline') for f in FAMILIES]+[('throw','adapter')]
    for f,m in combinations:
        base=load(STAGE/'diagnostics'/f/m/'FAILURE_DECOMPOSITION.json')['pseudo']
        latest=load(STAGE/'diagnostics'/f/m/'LATEST_FAILURE_DECOMPOSITION.json')
        detail=load(STAGE/'diagnostics'/f/m/'GRADIENT_DETAIL.json')['checkpoints']
        d=latest['results']['pseudo']
        lines.append(f"| {f}/{m} | {detail['best']['checkpoint_epoch_zero_based']+1} | {latest['checkpoint_epoch_zero_based']+1} | {latest['same_model_tensors_as_best']} | {base['AUROC']:.4f}→{d['AUROC']:.4f} | {base['raw_R1_05']:.4f}→{d['raw_R1_05']:.4f} | {base['gated_R1_05']:.4f}→{d['gated_R1_05']:.4f} |")
    lines += ['','### 官方gate与后处理归因','',
              'QD官方soft gate对每条query的全部候选分数乘同一个非负标量，正标量本身保持候选排序。源码只对gated保存窗应用clip_ts/round_multiple，raw保存窗没有这一步。以下是原冻结raw与gated的命中变化，以及对齐后剩余坐标差异；对齐raw仅作辅助，未替换raw主指标。','',
              '| 族/模型 | raw命中→gated不命中 | raw不命中→gated命中 | 对齐后全部排序窗坐标不一致行 |','|---|---:|---:|---:|']
    for f,m in combinations:
        failure=load(STAGE/'diagnostics'/f/m/'FAILURE_DECOMPOSITION.json')['pseudo']['counts']
        audit=load(STAGE/'diagnostics'/f/m/'GATE_POSTPROCESS_AUDIT.json')['results']['pseudo']
        lines.append(f"| {f}/{m} | {failure['raw_correct_gated_wrong']} | {failure['raw_wrong_gated_correct']} | {audit['all_ranked_coordinate_mismatches']} |")
    lines += ['','当对齐坐标全部一致时，命中差异由时间后处理解释，不能写成gate否决或重排。','',
              '## D1：相同文本的跨视频控制与分数可比性','',
              '同句输入统一为canonical缓存特征及mask。只比较原标签已确认的正/负视频；ties记.5。下面区间使用跨族共同原视频权重、配对端点乘积权重。','',
              '| 族 | 同句控制PairAcc及95%区间 | 同视频PairAcc（原输入） | 跨视频PairAcc（原输入） | 同视频对数 |','|---|---|---:|---:|---:|']
    for f in FAMILIES:
        d=load(STAGE/'diagnostics'/f/'baseline/FAILURE_DECOMPOSITION.json')['pseudo']
        lines.append(f"| {f} | {with_ci(control['families'][f])} | {number(d['same_video_pairacc'])} | {number(d['cross_video_pairacc'])} | {d['same_video_pairs']} |")
    lines += [f"| 等权族均值 | {with_ci(control['equal_family_mean'])} | — | — | — |",'',
              '输入响应与有助于正确排序是两个不同问题。同视频/跨视频统计受query和视频构成影响，差异不能直接证明视频偏置。Throw覆盖稀疏，不能将全部配对组合视作独立样本；各族覆盖及有效bootstrap次数在CONTROLLED_QUERY_SUMMARY.json中。','',
              '### 辅助敏感性','',
              '所有伪未见行都参与。冻结原视频特征；全遮蔽或屏蔽单分支保留text、mask和TEF，乱序只打乱有效visual行，同视频共享固定排列。恒等复算须通过。这里只报告变化，无扰动后的AUROC/R1/FRR/RR或反事实准确率。','',
              '| 族/模型 | 恒等最大误差 | 全遮蔽Δ存在分数 | 乱序Δ存在分数 | CLIP屏蔽Δ存在分数 | SlowFast屏蔽Δ存在分数 |','|---|---:|---:|---:|---:|---:|']
    for f,m in combinations:
        d=load(STAGE/'diagnostics'/f/m/'INPUT_SENSITIVITY.json')
        lines.append(f"| {f}/{m} | {d['identity_max_abs_error']:.1g} | "+' | '.join(number(d['summaries'][k]['exist_abs_delta']['video_mean']) for k in ('zero_visual','shuffle_time','zero_clip','zero_slowfast'))+' |')
    lines += ['','表中Δ为原视频内行均值再按视频等权的绝对变化；区间、top-slot变化、归一化时间端点变化与逐行产物见INPUT_SENSITIVITY.json及sensitivity_*.jsonl。遮蔽是分布外输入；输入敏感性不构成视觉必要性或泛化因果证明。','',
              '## D2：局部梯度关系','',
              '沿用各checkpoint已冻结的同一S+诊断批次，eval关闭dropout，不做参数更新。Loc严格包含实际加权分类/span/gIoU及aux项；saliency权重0、无有效目标，因此不推断saliency冲突或一致。Full-block cosine将未使用参数视为0，并在范数中包含每任务实际有梯度的全部参数；原GRADIENT_RELATIONS使用共同有梯度的张量交集，其幅值不同但符号规则需核对。','',
              '| 族/模型/ckpt | epoch | batches | input投影 median/负比 | interaction median/负比 | decoder median/负比 | 符合规则的共享块数 |','|---|---:|---:|---|---|---|---:|']
    grad_summary={}
    for f,m in combinations:
        detail=load(STAGE/'diagnostics'/f/m/'GRADIENT_DETAIL.json')['checkpoints'];grad_summary[f'{f}/{m}']={}
        for ck,d in detail.items():
            cells=[];qualifying=[]
            for block in ('input_projection','interaction','decoder'):
                v=d['summary'][block+'|exist_vs_loc']
                cells.append(number(v['median_cosine'])+'/'+number(v['negative_fraction']))
                if v['median_cosine'] is not None and v['median_cosine']<0 and v['negative_fraction']>.5:qualifying.append(block)
            grad_summary[f'{f}/{m}'][ck]={'epoch_zero_based':d['checkpoint_epoch_zero_based'],'qualifying_shared_blocks':qualifying,'model_tensor_sha256':d['model_tensor_sha256']}
            lines.append(f"| {f}/{m}/{ck} | {d['checkpoint_epoch_zero_based']+1} | {d['batches']} | "+' | '.join(cells)+f' | {len(qualifying)} |')
    lines += ['','预登记线索要求至少两个共享块median<0且负比>.5，并跨best/latest及至少两个族稳定。相同模型权重不能计作两个独立训练阶段。局部梯度结果本身不证明因果；可修复性必须由后续普通干预的联合目标改善检验。未使用/零/非有限梯度比例、范数、loss keys及固定qids见GRADIENT_DETAIL.json。','',
              '## 执行边界与产物','',
              '三个保存模型的训练侧pseudo评测、D0/D3/D1/D2及补充审计完成；sit训练仍为用户主动停止，不能记作100轮完成。报告的机制判断由DECISION.md给出。模型、原数据、特征和第一阶段六组未覆盖；全部新增代码、日志和结果写在本阶段。','',
              '执行来源：EXECUTION_FREEZE.json、EXECUTION_CODE_REVISION.json、SUPPLEMENT_FREEZE.json、SUPPLEMENT_CODE_REVISION.json、GRADIENT_DETAIL_FREEZE.json、CLOSEOUT_FREEZE.json。停止的旧队列状态保留；本次任务返回码见closeout_state.json。冻结界限仍为seen 1个百分点、FRR/RR 3个百分点、raw-correct硬拒5个百分点；低分母和跨界区间分别标注。']
    dump(STAGE/'report/GRADIENT_DETAIL_SUMMARY.json',grad_summary)
    dest=STAGE/'report/DIAGNOSTIC_REPORT.md'
    assert not dest.exists(),dest
    dest.write_text('\n'.join(lines)+'\n')
    print(dest)


if __name__=='__main__':main()
