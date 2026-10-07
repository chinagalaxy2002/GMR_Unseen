#!/usr/bin/env python3
"""Render all ablation tables from archived JSON, after a successful replay audit."""
import json
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAMES = {'moment': 'Moment-DETR', 'qd': 'QD-DETR', 'flash': 'FlashVTG'}
LABELS = {
    'base_bacc': 'Baseline + BAcc', 'base_shifted': 'Baseline + TPR target',
    'cog_bacc': 'CoG + BAcc', 'cog_shifted': 'CoG + TPR target',
    'full_heuristic': '经验权重', 'equal_weights': '分支内等权', 'peak_alone': '显著帧单通道',
    'obj_align_alone': '物体匹配单通道', 'vel_diff_alone': 'SlowFast 变化单通道',
    'learned_val_logistic': 'Seen-Val 逻辑回归',
    '3_branch_routing': '三分支', 'no_routing_unified': '统一证据 + 全局 CDF',
    'scrambled_routing': '交换运动/交互证据', '2_branch_routing': '二分支',
}


def macro(records):
    assert len(records) == 5
    return {key: sum(row[key] for row in records) / len(records) for key in records[0]}


def table(group):
    lines = ['| Backbone | 配置 | U−正确拒绝率 ↑ | U+误拒率 ↓ | U+门控 R@1≥0.5 ↑ | U+门控 G-mIoU ↑ | Unseen Rej-F1 ↑ | Unseen AUROC ↑ |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for backbone, arms in group.items():
        for arm, records in arms.items():
            metrics = macro(records)
            values = [metrics[key] for key in ['u_neg_rec', 'u_pos_frr', 'u_rec05', 'u_gmiou', 'u_rej_f1', 'u_auc']]
            lines.append('| ' + NAMES[backbone] + ' | ' + LABELS.get(arm, 'w_det=' + arm) + ' | ' + ' | '.join(f'{v:.2f}' for v in values) + ' |')
    return '\n'.join(lines)


def main():
    audit = json.loads((ROOT / 'docs/cog/ablation_audit/verification.json').read_text())
    if audit['verified_fixed_variants']['status'] != 'PASS':
        raise SystemExit('A successful verify_ablations.py audit is required.')
    archive = HERE / 'ablation_results.json'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != audit['archived_results_sha256']:
        raise SystemExit('Archived JSON changed since verification; rerun verify_ablations.py.')
    if hashlib.sha256((HERE / 'ablation_and_mechanism_study.py').read_bytes()).hexdigest() != audit['script_sha256']:
        raise SystemExit('Ablation script changed since verification; rerun verify_ablations.py.')
    results = json.loads((ROOT / 'docs/cog/ablation_audit/verified_ablation_results.json').read_text())
    checked = audit['verified_fixed_variants']
    sections = [
        '# CoG 消融：核验后的结果与结论边界',
        '本报告从独立核验后的 `docs/cog/ablation_audit/verified_ablation_results.json` 自动生成，替代原说明中与落盘结果不一致的表格。原始 `ablation_results.json` 保留用于追溯，其中逻辑回归对照未通过重放，排除在本报告的已核验表格之外。五划分顺序为 A1、A2_alt、A3、C1、C2_alt，采用等权宏平均；表内全部数字为 %，差值单位为百分点 pp。',
        f"独立调用四组原实验函数，共检查 1,890 个指标；以下已核验的固定规则变体共 {checked['metric_comparisons']} 个指标，最大绝对误差 {checked['max_absolute_error']:.3g} pp，容差 {audit['tolerance']:.3g} pp。15 份缓存与查询的 QID、标签顺序通过检查，缓存含 partition 字段时另核对分区。日志是本次重放日志，不冒充原始实验运行日志。逻辑回归对照共 90 个指标，其中 49 项差异超过容差，最大约 2.083 pp；单线程和默认线程均未重现归档，原因未确认，需固定依赖版本并保存拟合系数后复查。",
        '## 1. 阈值政策与多模态证据',
        table(results['exp1_threshold_decoupling']),
        '使用相同 Seen-Val TPR 目标时，CoG 相对平移基线的 U−正确拒绝率提高 5.45 / 10.15 / 8.38 pp（Moment / QD / Flash）。但这不是相同 Unseen TPR：CoG 的 U+误拒率为 25.95 / 15.89 / 21.19%，平移基线为 26.65 / 14.31 / 18.17%。QD 和 Flash 仍以更多误拒换取更多负例拒绝。Moment 的 CoG+BAcc 点估计在本表全部指标上优于 CoG+TPR target，因此不能将保护规则称为普遍必要或最优。',
        '阈值函数选择与目标 TPR 最接近的候选，而不是严格满足下界的约束优化。AUROC 增益证明排序改善，不证明整条 ROC 曲线处处支配基线。新增消融没有配对置信区间，原 Bootstrap 区间不能直接移用。',
        '## 2. 两路融合权重敏感性',
        table(results['exp2_fusion_weight_sweep']),
        '实际评估 7 个离散权重，不是连续扫描。0–0.5 范围内 Unseen AUROC 相对稳定，但 Rej-F1 仍有明显变化。该扫描未计算 Seen/All 指标，不能据此证明 0.5 最保护 Seen，也不能证明该设置处于 Pareto frontier。w=1 先通过经验 CDF 再定阈值，与原始检测器分数直接定阈值不完全相同；训练参考分布边界可能引入并列。',
        '## 3. 证据通道与分支内权重（排除未复现的逻辑回归）',
        table(results['exp3_evidence_weight_ablations']),
        '等权相对经验权重的 Unseen AUROC 差值约为 -0.201 / -0.193 / -0.180 pp，支持对这组权重替换不敏感，不能称全部严格小于 0.2 pp。单通道使用全局 CDF，而完整/等权方案使用分支 CDF，因此比较同时改变了证据和校准，尚未完全隔离多通道互补性。',
        '物体通道是 CLIP 候选窗口物体短语匹配，不是物体框检测；SlowFast 差分是特征变化代理，不是实际光流。逻辑回归在同一 Seen-Val 拟合和选阈值；本次未通过重放，不能用归档指标支持共现偏差或监督学习必然负迁移，需训练集拟合、独立 Seen-Val 校准对照。',
        '## 4. 路由机制',
        table(results['exp4_routing_rule_ablations']),
        '二分支保留大部分 Unseen AUROC 增益。统一方案同时改变证据组合和 CDF 条件，不能把全部下降归因于路由。交换方案破坏特征对应，支持语义选择有用，但不能建立物理因果解释或排除当前数据集的词汇捷径。需要保持证据组合不变的 CDF 消融，以及冻结规则后的新动作、组合和同义改写测试。',
        '## 5. 主实验代价与未解决问题',
        '| Backbone | ΔSeen AUROC，pp | All Rej-F1，Baseline → CoG | All G-mIoU，Baseline → CoG |\n|---|---:|---|---|\n| Moment-DETR | -1.84 | 58.03 → 54.77 | 37.99 → 36.22 |\n| QD-DETR | -1.76 | 56.27 → 50.13 | 38.06 → 35.31 |\n| FlashVTG | -3.15 | 58.70 → 54.69 | 43.34 → 41.71 |',
        '这些是主实验 JSON 的观测代价，不证明噪声“必然”增加。Seen 查询占比也不独立解释 AUROC 下降；F1 不是 Seen/Unseen F1 的线性加权均值。当前结果展示性能权衡，尚未证明帕累托最优。',
        '已知限制：A3 训练中多动作查询仍出现 run/walk；substring 规则误路由 breakfast、running shoes 等；A3 运动参考仅 11 条；多模态局部证据沿用共享 HQ 候选缓存；接受后的时间边界未改变。主实验的既有 Bootstrap 为固定模型/阈值的名义区间，未覆盖反复测试反馈、语义标注误差或新增消融的选择不确定性。',
        '## 6. 复现',
        '在仓库根目录恢复数据后运行：\n\n```bash\npython reproduction/prepare_evidence_calibration.py\n# 重跑原消融，会覆盖其 ablation_results.json\npython experiments/agy_test/co_generalization_gmr/ablation_and_mechanism_study.py\n# 不覆盖归档结果；重放并与归档 JSON 比较\n# 当前为 PARTIAL / exit 1：逻辑回归未通过，固定规则变体 PASS\npython experiments/agy_test/co_generalization_gmr/verify_ablations.py\n# 从已核验 JSON 生成本报告\npython experiments/agy_test/co_generalization_gmr/render_ablation_report.py\n```',
        '核验资料：`docs/cog/ablation_audit/verification.json`、`replay.log`、`ASSET_MANIFEST.json`。核验是同一实现的数值重放，不是重新训练、不包含新增 Bootstrap，也不保证数据构造与科学解释均无误。',
    ]
    (HERE / 'MECHANISM_AND_ABLATION_STUDY.md').write_text('\n\n'.join(sections) + '\n')
    def compact_auroc(group):
        lines = ['| 配置 | Moment-DETR | QD-DETR | FlashVTG |', '|---|---:|---:|---:|']
        for arm in group['moment']:
            vals = [macro(group[bb][arm])['u_auc'] for bb in NAMES]
            lines.append('| ' + LABELS.get(arm, 'w_det=' + arm) + ' | ' + ' | '.join(f'{v:.2f}' for v in vals) + ' |')
        return '\n'.join(lines)

    block = '\n\n'.join([
        '<!-- COG_ABLATIONS_START -->',
        '### 新增：四组消融与独立重放核验',
        f"已重放四组消融；已核验的固定规则变体共 {checked['metric_comparisons']} 个数值指标，最大误差 {checked['max_absolute_error']:.3g} pp；15 份缓存与查询 QID、标签顺序一致。逻辑回归另有 90 项指标，其中 49 项未重放一致，最大差 2.083 pp，排除在已核验表格之外。这里只确认固定规则变体数值复算一致，不意味着数据构造或机制解释均已无误。",
        '[完整核验后报告](experiments/agy_test/co_generalization_gmr/MECHANISM_AND_ABLATION_STUDY.md) · [已核验逐划分 JSON](docs/cog/ablation_audit/verified_ablation_results.json) · [原始完整 JSON（含未通过项）](experiments/agy_test/co_generalization_gmr/ablation_results.json) · [重放日志](docs/cog/ablation_audit/replay.log) · [核验结果](docs/cog/ablation_audit/verification.json)',
        '**阈值与证据分开比较：** 下表来自实际 JSON，修正了原说明中的部分 FRR、Recall 和 Rej-F1。两种方法使用相同 Seen-Val TPR 目标，测试集 TPR 仍可能不同。',
        table(results['exp1_threshold_decoupling']),
        '相比平移基线，CoG 的 U−正确拒绝率提升 5.45 / 10.15 / 8.38 pp；但 QD 和 Flash 的 U+误拒率也更高。Moment 的 CoG+BAcc 在本表指标上优于 CoG+TPR target，保护阈值不是所有骨干的最优选项。新增对照尚未做配对 Bootstrap。',
        '**两路融合权重：Unseen AUROC，%。** 实际扫描 7 个离散权重；不能据此证明 50/50 最优，也未测该扫描的 Seen 保留。',
        compact_auroc(results['exp2_fusion_weight_sweep']),
        '**证据通道：Unseen AUROC，%。** 分支内等权与经验权重相近，最大差约 0.201 pp。单通道使用全局 CDF，完整模型使用分支 CDF，尚未完全隔离通道贡献。',
        compact_auroc(results['exp3_evidence_weight_ablations']),
        '**路由：Unseen AUROC，%。** 二分支保留多数收益；无路由对照同时改了证据组合和 CDF，交换路由也不证明物理因果。',
        compact_auroc(results['exp4_routing_rule_ablations']),
        '当前能说的是经验校准在这组冻结划分上改善了 Unseen 排序，存在 Seen/All 代价。尚未证明帕累托最优；不能将词汇规则对当前数据集的适应排除。新动作/组合、同义改写、原生候选和严格留出审计仍需补充。',
        '```bash\n# 不覆盖归档结果：重放四组消融并核对 JSON\n# 当前返回 PARTIAL / exit 1，表示逻辑回归未通过；固定规则变体 PASS\npython experiments/agy_test/co_generalization_gmr/verify_ablations.py\n# 从核验后的 JSON 生成报告和本节\npython experiments/agy_test/co_generalization_gmr/render_ablation_report.py\n# 如需重新运行原实验（会覆盖 ablation_results.json）\npython experiments/agy_test/co_generalization_gmr/ablation_and_mechanism_study.py\n```',
        '<!-- COG_ABLATIONS_END -->',
    ])
    readme_path = ROOT / 'README.md'
    text = readme_path.read_text()
    if '<!-- COG_ABLATIONS_START -->' in text:
        start = text.index('<!-- COG_ABLATIONS_START -->')
        end = text.index('<!-- COG_ABLATIONS_END -->', start) + len('<!-- COG_ABLATIONS_END -->')
        text = text[:start] + block + text[end:]
    else:
        text = text.replace('## 5. 已知问题与下一步', block + '\n\n## 5. 已知问题与下一步', 1)
    text = text.replace('现有收益包含校准与阈值政策变化，不能全部归因于多模态算法。', '新增消融已给 Baseline 应用相同的 Seen-Val TPR 目标，见第 4 节；相同目标不保证相同测试集 TPR，也不证明 ROC 曲线处处优于基线。')
    text = text.replace('**阈值公平性**：补充 Baseline 的相同正例保护规则，并做“全局/分流 CDF × 原阈值/保护阈值”四组对照，分开两类贡献。', '**阈值公平性**：已补 Baseline/CoG × BAcc/TPR target 对照；仍需固定证据组合的全局/分流 CDF 对照、严格守卫和配对区间，不能把相同 Seen TPR 目标称为相同 Unseen 灵敏度。')
    text = text.replace('**机制与新语义**：分流、等权融合和 +4 pp TPR 目标都需要消融与敏感性分析；固定规则后用新动作/组合评估。', '**机制与新语义**：本次补充路由、分支权重及两路融合扫描；+4 pp TPR 目标仍缺敏感性分析，现有消融仍有混杂。固定规则后用新动作/组合及同义改写评估。')
    text = text.replace('| [run_bootstrap_significance.py]', '| [消融脚本](experiments/agy_test/co_generalization_gmr/ablation_and_mechanism_study.py) | 阈值、融合权重、证据通道、路由四组对照 |\n| [消融报告](experiments/agy_test/co_generalization_gmr/MECHANISM_AND_ABLATION_STUDY.md) | 由已核验 JSON 生成的全部结果与解释边界 |\n| [核验脚本](experiments/agy_test/co_generalization_gmr/verify_ablations.py) | 重放四组消融，不覆盖归档 JSON |\n| [run_bootstrap_significance.py]', 1) if '| [消融脚本]' not in text else text
    readme_path.write_text(text)
    print('Rendered audited report and README ablation tables')


if __name__ == '__main__':
    main()
