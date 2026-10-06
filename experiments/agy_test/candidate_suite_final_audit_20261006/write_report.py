"""Generate an evidence-based verdict from independently replayed artifacts."""
import json
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
BBS=['flash','moment','qd']
SEEDS=[3407,42,2024]

def main():
    d=json.loads((P/'audit_metrics.json').read_text());b=json.loads((P/'bootstrap.json').read_text())
    def interval(v):
        lo,hi=v['ci95'];return f'[{100*lo:+.2f}, {100*hi:+.2f}] pp'
    def average(src,tgt,regime='target_specific'):
        vals=[d['macro'][f'{regime}_{seed}_{src}_to_{tgt}'] for seed in SEEDS]
        return {k:float(np.mean([v[k] for v in vals])) for k in vals[0]}
    def opaverage(tgt):
        vals=[d['macro_operating'][f'target_specific_{seed}_{tgt}_to_{tgt}'] for seed in SEEDS]
        return {k:float(np.mean([v[k] for v in vals])) for k in vals[0]}
    lines=['# 最终候选验证器独立审计：2026-10-06','',
           '## 结论：宏平均目标获得证据支持','',
           '**可以证明 work 的有限而明确的含义：在这五个语义划分和三个固定种子上，目标自身预测候选机制的自验证，对三个骨干均提升宏平均 Unseen AUROC、缩小 Seen−Unseen Gap，且 Seen 同时改善。独立视频聚类区间排除零。**','',
           '**不能由此证明：方向性是必要贡献、纯 SlowFast 已解释 A3 物理机理、A 显著优于 B、每个划分都受益或实际拒绝操作点全面优于基线。** 这些结论需分别检验，不影响已验证的宏平均效果。','',
           '审计只读取原实验，不重新训练。完成全部 125 个检查点（90 个迁移、35 个消融）重放，覆盖 270 条迁移路径及 35 个消融模型；样本连接核对通过，train/val 均只有 Seen；从保存分数重新计算 AUROC、PairAcc、Seen-val 阈值和拒绝指标。独立执行 2,000 次共享视频聚类 Bootstrap，1217 个视频，seed3407。','',
           f"最大重放误差：{d['replay_counts']['max_error']:.9g} < 1e-6。迁移与原 JSON 数值逐项一致，拒绝指标重算一致。较原声明 1.8e-7 更大的误差来自本审计额外覆盖消融，但仍在容差内。",'',
           '## 1. 3-seed 自验证的实际效果','',
           '| 目标 | 基线 Seen | 自验证 Seen | 基线 Unseen | 自验证 Unseen | 基线 Gap | 自验证 Gap | ΔU 95% CI | Gap 缩小 95% CI |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for tgt in BBS:
        base=d['macro'][tgt+'_base'];v=average(tgt,tgt);bs=b['transfer'][tgt+'_to_'+tgt]
        lines.append(f"| {tgt} | {base['seen']:.4f} | {v['seen']:.4f} | {base['unseen']:.4f} | {v['unseen']:.4f} | {base['gap']:.4f} | {v['gap']:.4f} | {interval(bs['unseen_gain'])} | {interval(bs['gap_reduction'])} |")
    lines += ['', '此处 mean 是先按五折算宏平均 AUROC、再平均三个种子的指标，不是将三份预测平均成集成模型。Bootstrap 在每次抽样中用相同视频权重重算模型与基线、Seen 与 Unseen；区间条件于三个现有训练种子，未重新抽样训练过程，不是所有可能训练种子的总体置信区间。逐项 95% 区间没有多重比较校正。','',
              '## 2. 跨骨干迁移','', '| 路径 | 3-seed Unseen | ΔU vs 目标基线 | ΔU 95% CI | Gap 缩小 95% CI |', '|---|---:|---:|---:|---:|']
    for src in BBS:
        for tgt in BBS:
            v=average(src,tgt);base=d['macro'][tgt+'_base'];bs=b['transfer'][src+'_to_'+tgt]
            lines.append(f"| {src}→{tgt} | {v['unseen']:.4f} | {(v['unseen']-base['unseen'])*100:+.2f} pp | {interval(bs['unseen_gain'])} | {interval(bs['gap_reduction'])} |")
    lines += ['', '9 条路径的 Unseen 点估计均提高，8 条逐项 95% 区间排除零；QD→Flash 区间跨零。迁移得到支持，但不能称所有路径都已显著改善。不同来源相对目标自验证也存在差异，不能自动称严格无损。', '',
              '本轮确实使用目标自身预测候选及独立重提取的局部证据。候选物理抽查沿用上一轮对同一提取逻辑的 90 行审计；本轮新核对全部缓存身份与 Seen 标签隔离。目标 CDF 用目标 Seen 训练分数，阈值用目标 Seen val 标签：属于允许目标数据校准的权重迁移，尚非完全不接触目标 Seen 数据的源阈值直接迁移。','',
              '## 3. A vs B：趋势成立，显著优势尚未成立','', '| 自验证目标 | A | B | A−B | 配对视频 95% CI |', '|---|---:|---:|---:|---:|']
    for tgt in BBS:
        aa,bb=average(tgt,tgt),average(tgt,tgt,'shared')
        lines.append(f"| {tgt} | {aa['unseen']:.4f} | {bb['unseen']:.4f} | {(aa['unseen']-bb['unseen'])*100:+.2f} pp | {interval(b['A_minus_B'][tgt])} |")
    lines += ['', 'Moment/QD 的区间均跨零。三种子点估计较稳定，仍不足以宣称 A 全面显著优于 B；0.35/0.45 pp 很可能值得继续研究，但需要更多独立证据。B 的训练仍使用各来源自己的候选，仅验证/测试换为 Flash 特征；它不是上一轮共享候选训练协议的完整复刻。替换的还有 fg、宽度及对应 CDF，原因尚未完全解耦。','',
              '## 4. 方向性、训练与模态机制','', '| 对照 | Full−对照的 Unseen 点估计 | 配对视频 95% CI |', '|---|---:|---:|']
    full=d['macro']['aba_none']
    for mode,label in [('unsigned','原始绝对值差分'),('no_direction','去端点差分'),('visual_only','所谓 CLIP-only'),('kinetic_only','所谓 SlowFast-only')]:
        alt=d['macro']['aba_'+mode]
        lines.append(f"| {label} | {(full['unseen']-alt['unseen'])*100:+.2f} pp | {interval(b['ablation']['full_minus_'+mode]['unseen'])} |")
    lines += ['', 'unsigned 修复有效，按 raw abs 后重建 CDF 的流程能重放检查点；但方向增益区间跨零。绝对值模型 PairAcc=.6395 还略高于 Full=.6387。因此“方向必要性”尚未得到支持；可称方向通道有小幅点估计增益、独立作用待验证。','',
              f"Full 相对未训练初始化的提升约 {(full['unseen']-d['macro']['fixed_prior']['unseen'])*100:.2f} pp，95% CI {interval(b['ablation']['full_minus_fixed_prior']['unseen'])}，支持整体监督训练的额外贡献。它同时包含 rank loss、BCE 与优化过程，缺少 BCE-only/去同视频对实验，不能将全部训练增益单独归因于反事实对监督。", '',
              '模态隔离问题仍未修复：visual_only 将 SlowFast 速度/位移清零，但保留 CLIP 时间端点差分；kinetic_only 仍保留 CLIP 的 d_act。它们都是与检测器融合的网络分数，不是单独 CLIP/SlowFast 特征相关性。现有结果不能证明静态 CLIP 的物理负相关或 SlowFast 速度的独立因果作用。建议重新定义输入通道、补单特征诊断和时间反转实验。','',
              '## 5. A3 仍有退化','', '| A3 自验证目标 | ΔU 相对基线 95% CI |', '|---|---:|']
    for tgt in BBS:lines.append(f"| {tgt} | {interval(b['A3'][tgt]['self_unseen_gain'])} |")
    lines += ['', 'Flash/Moment 的 A3 自验证下降区间排除零，QD 的下降点估计区间跨零。宏平均 work 与 A3 局部失败同时成立；不能将 A3 掉点写成已解决。','',
              '## 6. 实际拒绝：定义修复通过，全面操作点优势未成立','',
              '拒绝 F1 现在以 U−为正类，RR、S+ FRR 与 U+ FRR 已分别实现；独立重算与 summary 一致。下表使用每个骨干自己的 Seen-val Youden J 网格阈值，与验证器目标 Seen-val 校准作同规则比较。','',
              '| 目标 | 模型 | U− RR | U+ FRR | 拒绝 F1 | U Balanced Accuracy |', '|---|---|---:|---:|---:|---:|']
    for tgt in BBS:
        for label,v in [('Detector-only',d['macro_operating'][tgt+'_base']),('A 自验证，3-seed',opaverage(tgt))]:
            lines.append(f"| {tgt} | {label} | {v['unseen_rr']*100:.2f}% | {v['unseen_frr']*100:.2f}% | {v['rejection_f1']:.4f} | {v['balanced_accuracy']*100:.2f}% |")
    lines += ['', 'Flash 的拒绝 F1 提高，但 U+ 误拒从约 12.80% 升至 21.84%，Balanced Accuracy 从 52.96% 降至 51.92%。Moment 的拒绝 F1 改善很小；QD 的 F1 提高伴随较多误拒。因此 AUROC/Gap 的改善不能替代相同 FRR/TPR 条件下的实用拒绝验证。补拒绝率曲线、Seen-only 操作点和官方 G-mIoU 后再判断部署收益。','',
              '## 7. 复验脚本与表述问题','',
              '原 verify_suite.py 只重放 90 个迁移权重、270 路径，未覆盖 35 个消融；计算 diff 后没有 assert diff<1e-6，却打印 PASSED；指标部分只核对宏平均 Unseen AUROC，没有核对其 docstring 所称 PairAcc/F1。本审计已补全这些断言与指标重算，因此结果通过是实际计算结论，但不应以原脚本本身宣称“所有审计100%完成”。','',
              '“连续 sigmoid 完全消除 ties”不准确：float32 概率仍会饱和并列，例如 Flash A1/A3/C2_alt 分别有 154/599/773 个分数等于 1。基线已大幅恢复，与 raw-logit U 指标接近；Full 相对原 raw-logit Flash 的 Unseen 提升区间也排除零，所以这不推翻方法有效性。正式输入仍建议使用 raw logits 的 train-CDF，并保留 raw-logit 基线。','',
              '固定初始化和 Full 使用同一 none 路径，Full 会覆盖未训练预测；固定先验可按种子重建，但最好独立保存。检查点尚缺完整配置、最佳 epoch 和选模日志，当前能认证冻结推理与数据身份，不能仅凭最终权重认证完整训练历史或多轮研发严格盲评。','',
              '## 8. 推荐的研究结论与后续工作','',
              '> 在五个语义留出划分和三个随机种子下，采用目标骨干预测候选及 Seen 数据校准的多模态验证器，提高了 FlashVTG、Moment-DETR、QD-DETR 的宏平均 Unseen AUROC，并缩小 Seen−Unseen Gap，且 Seen AUROC 同时提升；共享视频聚类 Bootstrap 支持这些改善。跨骨干权重迁移在多数路径上有效。方向性独立贡献、目标候选相对共享候选的显著优势及固定阈值拒绝稳健性仍需进一步验证。','',
              '优先补实验：纯 SlowFast vs CLIP 时间差分的独立通道；BCE-only/无同视频对；预先定义非劣界的多种子迁移；相同 Seen-only FRR/TPR 操作点及官方 G-mIoU；方法冻结后的独立测试。当前宏平均有效性已获支持，不需要为了宣称“work”继续堆叠新架构。','',
              '## 9. 产物','',
              '- audit_final.py：全部 checkpoint 重放、标签/身份连接、指标与阈值重算、2000 视频抽样。',
              '- audit_metrics.json：全部实际核验结果；bootstrap.json：配对数值区间；bootstrap_draws.npz：全部抽样 AUC。',
              '- input_manifest.json：主要输入 SHA256；原目录只读，本审计单独落盘。',
              '- 复验：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/candidate_suite_final_audit_20261006/audit_final.py`，随后运行同目录 write_report.py。']
    (P/'FINAL_INDEPENDENT_AUDIT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
