"""Generate the independent Chinese report from audited machine-readable metrics."""
import json
from pathlib import Path
P = Path(__file__).resolve().parent

def main():
    d = json.loads((P/'audit_metrics.json').read_text())
    b = json.loads((P/'bootstrap.json').read_text())
    r = json.loads((P/'route_diagnostics.json').read_text())
    rejection = json.loads((P/'rejection_comparison.json').read_text())
    m = d['macro']
    def interval(value, pp=False):
        lo, hi = value['ci95']
        return f'[{lo*100:+.2f}, {hi*100:+.2f}] pp' if pp else f'[{lo:.4f}, {hi:.4f}]'
    lines = ['# SDCV 独立产物审计：2026-10-06', '',
             '## 结论', '',
             '**落盘 SDCV 相对两种 QD 基线，达到了五划分宏平均上的 Unseen AUROC 提升和 Seen−Unseen Gap 缩小目标，且 Seen 没有被牺牲。**', '',
             '**原报告中的 0.6164 / Gap 0.1356 未获得现有检查点和逐样本预测支持。可复现版本为 Unseen 0.5775 / Gap 0.2016。** 本轮没有证明超过 FlashVTG 的未见泛化，也没有超过前轮 DDV。实际固定阈值拒绝仍存在严重的划分差异。', '',
             '审计只读取原实验。重放全部 15 个检查点；核对 15 份特征的 qid、视频、标签和前 12 维；按原始 CLIP 帧与检测器候选坐标抽查 450 组带符号特征；独立执行 2,000 次共享视频聚类 Bootstrap。没有重新训练。', '',
             '## 1. 可复现结果', '',
             '| 模型 | Seen AUROC | Unseen AUROC | Gap | Matched PairAcc | 动作 Unseen | 组合 Unseen |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name, label in [('hq_qd','Base1 HQ QD'),('release_qd','Base2 Release QD'),('flash_logit','FlashVTG raw logit'),('ddv','前轮 DDV'),('det_mlp','DetectorOnlyMLP'),('mm_mlp','MultimodalOnlyMLP'),('sdcv','本轮落盘 SDCV')]:
        v=m[name]
        lines.append(f"| {label} | {v['seen']:.4f} | {v['unseen']:.4f} | {v['gap']:.4f} | {100*v['pair_acc']:.2f}% | {v['action_unseen']:.4f} | {v['composition_unseen']:.4f} |")
    lines += ['', '| Split | Base1 Unseen | SDCV Unseen | Δ Unseen | SDCV Seen | SDCV Gap | Gap 缩小量 | PairAcc |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for split, v in d['splits'].items():
        sm, qm = v['metrics']['sdcv'], v['metrics']['hq_qd']
        lines.append(f"| {split} | {qm['unseen']:.4f} | {sm['unseen']:.4f} | {sm['unseen']-qm['unseen']:+.4f} | {sm['seen']:.4f} | {sm['gap']:.4f} | {qm['gap']-sm['gap']:+.4f} | {sm['pair_acc']*100:.2f}% |")
    lines += ['', '正的 Gap 缩小量表示退化缓解。A1 的 Unseen 点估计略降、Gap 明显增大；C2_alt 的 Unseen 点估计上升，但 Seen 上升更多，Gap 反而增大。因此“宏平均目标实现”成立，“全部划分都实现”不成立。', '',
              '## 2. 独立统计检验', '', f"SDCV Unseen AUROC 95% CI：{interval(b['sdcv_unseen'])}。", '',
              '| 比较 | Δ Unseen 点估计 | Δ Unseen 95% CI | Gap 缩小点估计 | Gap 缩小 95% CI |', '|---|---:|---:|---:|---:|']
    for name in ['hq_qd','release_qd','flash_logit','ddv','det_mlp','mm_mlp']:
        c=b['comparisons']['sdcv_minus_'+name]
        lines.append(f"| SDCV − {name} | {(m['sdcv']['unseen']-m[name]['unseen'])*100:+.2f} pp | {interval(c['unseen'],True)} | {(m[name]['gap']-m['sdcv']['gap'])*100:+.2f} pp | {interval(c['gap_reduction'],True)} |")
    lines += ['', f"动作均值相对 FlashVTG 为 {(m['sdcv']['action_unseen']-m['flash_logit']['action_unseen'])*100:+.2f} pp，95% CI {interval(b['comparisons']['sdcv_minus_flash_logit']['action_unseen'],True)}。原报告的“动作显著超过 FlashVTG”不能成立。", '',
              'Bootstrap 覆盖测试视频采样波动，不覆盖训练种子或反复试验选方法的波动。本审计报告的是百分点点估计与配对区间，没有从 2,000 次重抽样宣称 p<0.0001。原报告 [.5961,.6373] 的下界也小于 .60，不能证明“严格超过 .60”。', '',
              '## 3. 必须修正的报告与方法问题', '',
              '### 3.1 报告与产物不一致（严重）', '',
              '`generate_audit_report.py:36` 直接追加固定的 0.7519/0.6164/0.1356；逐划分与 Bootstrap 表同样是固定文字，没有读取 JSON、检查点或预测文件。仓库实验文本搜索未找到对应 .6164 版本的可执行预测程序或逐查询结果。不能据此认定这些数值绝不存在，但目前它们不可复验。', '',
              '15 个检查点重放与保存分数的最大差异低于 3e-7；Unseen AUROC 与落盘 summary 一致。CPU/GPU 浮点差异带来的个别 Seen AUROC 变化小于 3e-7，解释不了 .6164 与 .5775 的差距。', '',
              '原报告将 FlashVTG 的动作均值 .5514 误写为宏平均；正确 raw-logit 宏平均为 .5714。Release QD 和 FlashVTG 的 PairAcc 也被复制为 HQ QD 的 .5181；正确值见表。C1 是 sit 与 bed/chair/couch 的组合留出，C2_alt 是 open/close 与 box/cabinet 的组合留出，应按数据定义描述。', '',
              '### 3.2 路由并非纯查询，仍有划分特定参数', '',
              '`model.py:101` 的路由器输入为 CLIP 视频相似度、SlowFast 速度/位移和端点差分等九个视觉相关量；它没有读取 query 文本或缓存的 `q_proj_sent`。它可以称为“查询与视频联合证据路由”，不能称为“仅由语言属性驱动的路由”，代码没有 run/walk 的词汇识别分支。', '',
              '`train_and_eval.py:171` 对 A3 设置 alpha_max=.60，其他划分 .55。模型 forward 已移除 split 通路选择，但整个流水线并非完全无 split 条件。每折各自训练本身是正常协议；此超参数差异需要披露和 Seen-only 的选择依据，不能仅凭分支认定标签泄漏。', '',
              '### 3.3 容量与机制归因尚不充分', '',
              '实际可训练参数为 SDCV=611、DetectorOnlyMLP=801、MultimodalOnlyMLP=929，数量不完全匹配。对照组更大，并不会自动使结果无效，但“容量严格相同”不准确。结构、非负权重约束、路由、门控和输入都一起改变，无法将全部差异归因于视觉或动力学特征。', '',
              '三组采用相同采样批次、损失、训练步数和 Seen 验证集选模，属于有效的初步对照。SDCV 相对 DetectorOnlyMLP 宏平均 Unseen 提升显著；相对 MultimodalOnlyMLP 的 Unseen 增益区间跨零。另有简单 rank mean/median 三检测器融合达到 .5478/.5508，故不能用一个 .5215 的 MLP 断言“所有检测器融合都无效”。输入实际为 CLIP 与 SlowFast，没有独立音频通路，“视听”不符合实现。', '',
              '### 3.4 带符号特征正确，但方向性贡献未被证实', '',
              '450 组端点特征抽查全部与原始 CLIP 和候选坐标一致；15 份样本连接与标签核对通过。原始 delta_act/obj 保留了符号，端点交换在代数上会使它取负。但这并不等价于完整模型已识别 put/take 的物理逆向关系。', '',
              f"A1 的 delta_act 单独 Unseen AUROC={d['splits']['A1']['direction_only_diagnostic']['delta_act']['unseen']:.4f}，PairAcc={d['splits']['A1']['direction_only_diagnostic']['delta_act']['pair_acc']*100:.2f}%；.6314 是完整模型 PairAcc，不能当成单特征证据。abs(delta_act) 的 A1 AUROC={d['splits']['A1']['direction_only_diagnostic']['abs_delta_act']['unseen']:.4f}，高于保留符号的单特征值。", '',
              'CDF 将有符号原始值映射到 [0,1]：顺序被保留，但零点不是固定 .5，也不保持正反的反对称关系。需要重新训练的“去方向/绝对值/带符号”对照和时间反转实验，才能证明符号的独立价值。', '',
              '### 3.5 校准使用整个测试分布，排序与拒绝必须分别报告', '',
              '`train_and_eval.py:335` 从全测试集计算 mu_test/std_test。它没有使用测试标签，但实际阈值变成 tau_test=mu_test+std_test*(tau_seen−mu_val)/std_val，属于测试分布适配。应与严格 Seen-only 固定阈值分别报告。仅用 Seen 的同一均值方差同时标准化 val/test 时，决策与原始阈值完全相同；本审计已核对五划分均为零条决策变化。', '',
              '同一批分数作正向线性标准化不会改变 AUROC，无法用它解释 .5775 到 .6164 的排序增益。以下拒绝率与误拒率是不同操作点，不能混为一套标准协议：', '',
              '| 协议 | U− 拒绝率 RR | U+ 误拒率 FRR | 拒绝 F1 |', '|---|---:|---:|---:|']
    for name, label in [('sdcv','Seen-only 固定阈值'),('sdcv_transductive','无标签全测试批次 Z-score 适配')]:
        v=m[name]
        lines.append(f"| {label} | {v['u_neg_rr']*100:.2f}% | {v['u_pos_frr']*100:.2f}% | {v['rej_f1']*100:.2f}% |")
    lines += ['', '基线统一按各自 Seen 验证阈值比较（QD/Flash/DDV 阈值沿用前轮独立审计的冻结结果）：', '', '| 模型 | 固定 RR | 固定 FRR | 固定拒绝 F1 | 固定 Balanced Accuracy |', '|---|---:|---:|---:|---:|']
    for name, v in rejection['macro'].items():
        ba=.5*(1-v['u_pos_frr']+v['u_neg_rr'])
        lines.append(f"| {name} | {v['u_neg_rr']*100:.2f}% | {v['u_pos_frr']*100:.2f}% | {v['rej_f1']*100:.2f}% | {ba*100:.2f}% |")
    lines += ['', '固定阈值下，SDCV 相对 HQ QD 的拒绝 F1 提高，但正例误拒也提高；Balanced Accuracy 从约 51.13% 降至 50.38%。因此宏平均 AUROC 缓解已经得到证据支持，固定操作点的实用拒绝改进仍不能由这些数值充分确立。应比较相同 FRR/TPR 条件下的拒绝率，并确保阈值选择只依赖 Seen 验证。']
    lines += ['', '| Split | 固定 RR | 固定 FRR | 测试适配 RR | 测试适配 FRR |', '|---|---:|---:|---:|---:|']
    for split, v in d['splits'].items():
        raw, trans = v['metrics']['sdcv'], v['metrics']['sdcv_transductive']
        lines.append(f"| {split} | {raw['u_neg_rr']*100:.2f}% | {raw['u_pos_frr']*100:.2f}% | {trans['u_neg_rr']*100:.2f}% | {trans['u_pos_frr']*100:.2f}% |")
    lines += ['', '宏平均固定 RR 是 28.62%，不是报告所称的 1.6%。A2_alt 固定阈值拒绝率为零，测试适配后仅 1.28%；C2_alt 测试适配仍误拒 66.09% 的真实存在查询。不能把宏平均 30.87% 称为已经达到健康的拒绝平衡。', '',
              '全部五折 Seen 验证负例均可解析到 source_qid，且与源正例是同视频：510/589/609/508/521 条。它们的 construction_type 是动作、物体或组合反事实。因此“Seen val 大部分跨视频随机负例”这一数据根因解释不成立；训练损失中随机配对不等于数据集负例由跨视频替换生成。', '',
              '### 3.6 G-mIoU 实现不符合仓库定义', '',
              '`train_and_eval.py:95` 在预测为空时直接返回零，漏掉预测与 GT 同为空时应记为 1；它将多个预测窗口包成一个凸包再取最佳 GT IoU，不是仓库集合匹配公式。本审计使用 `eval/metrics.py` 重新计算并与官方函数交叉核对；逐折结果在 audit_metrics.json 的 official_gmiou 中。原脚本 G-mIoU 不宜继续引用。', '',
              '## 4. 退化根因：A3 路由偏向物体通路', '',
              f"冻结 A3 检查点时，Unseen 路由均值 kinetic/object/manual={r['splits']['A3']['routing_and_gate']['unseen']['mean_route_kin_obj_manual']}。物体通路占约 70%，动力学仅约 22%。完整模型 Unseen={r['splits']['A3']['metrics']['trained']['unseen']:.4f}，检测器通路={r['splits']['A3']['metrics']['detector_stream']['unseen']:.4f}，新证据通路={r['splits']['A3']['metrics']['evidence_stream']['unseen']:.4f}。新证据本身在此划分反向，固定下限门控强制混入它，拖低排序。", '',
              f"冻结权重改为均匀路由时 A3={r['splits']['A3']['metrics']['uniform']['unseen']:.4f}；只走动力学通路时={r['splits']['A3']['metrics']['kinetic_only']['unseen']:.4f}。这支持优先检查语义路由的泛化失效。上述干预仅是诊断，不是重新训练的正式消融，也不能依据测试结果为 A3 配置专属通路。", '',
              '## 5. 建议下一轮最小实验矩阵', '',
              '优先修复产物一致性与评估协议，再训练新架构：', '',
              '| 优先级 | 实验或整改 | 控制要求 | 回答的问题 |', '|---|---|---|---|',
              '| P0 | 报告自动从预测/JSON 生成；冻结统一配置并记录选模 epoch、Seen 阈值、训练 CDF、SHA256 | .6164 若来自另一个版本，保存它的程序、权重和逐查询预测，单独命名 | 哪个版本实际实现目标 |',
              '| P0 | 官方 G-mIoU；固定阈值与测试批次适配分开；QD/Flash/DDV 同协议比较 RR/FRR/F1 | 固定阈值仅在 Seen val 选择；测试统计适配标为独立实验 | AUROC 改善是否转化为可用拒绝 |',
              '| P1 | 同结构与同参数预算的 detector-only / detector+CLIP / detector+SlowFast / 两者融合 | 相同初始化种子、训练步数、候选、归一化和选模规则；至少 3 个种子 | 新视觉与动力学贡献分别来自哪里 |',
              '| P1 | 固定统一路由 / 当前联合路由 / 真正 query-only 路由 | query-only 只能读取冻结文本向量或文本属性；全划分统一 gate 上限 | A3 的物体路由偏置能否解决 |',
              '| P1 | 去端点差分 / abs(delta) / signed(delta)；原时间/反转时间 | 每组独立 Seen-only 训练，反转时同步候选时间映射 | 带符号方向是否有独立作用 |',
              '| P2 | Seen 内构造难反事实验证子集，验证拒绝阈值稳健性 | 仅 Seen 语义，按视频隔离；报告 RR 对应 FRR 或 TPR 条件；不使用 U 测试调阈值 | A2 全接受与 C2 高误拒能否同时改善 |', '',
              '测试集已经用于多轮方法诊断，因此“盲评”不能由现有代码与最后一轮 Seen 选模单独证明。最终论文结果应冻结方法后在保留的未用测试集或嵌套验证协议上评估；当前 Bootstrap 是条件于这一版固定模型的区间。', '',
              '## 6. 文件与复验', '',
              '- audit_sdcv.py：独立检查点重放、特征/标注连接、官方 G-mIoU 和视频 Bootstrap。',
              '- route_diagnostics.py：冻结路由与端点差分干预，不执行训练。',
              '- source_diagnostics.py：Seen 验证负例的源视频核对。',
              '- rejection_comparison.py：按各模型自己的 Seen 验证阈值比较拒绝操作点。',
              '- audit_metrics.json / bootstrap.json：数值依据；bootstrap_draws.npz：全部 2,000 次抽样的 AUC。',
              '- A1_replay.npz 等：逐查询重放分数；input_manifest.json：主要输入和源代码 SHA256。', '',
              '主审计复验：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/sdcv_audit_20261006/audit_sdcv.py`。随后依次运行同目录 route_diagnostics.py、source_diagnostics.py、rejection_comparison.py、write_report.py。', '',
              '边界：没有重新训练或确认硬件/400 epochs 历史日志；带符号特征检查是 450 行抽样，并非全部原始视频特征重提取；没有发现此特征代码直接读取测试标签或 GT 窗口入模，但这不等价于证明所有上游及研究过程完全不存在泄漏。']
    (P/'INDEPENDENT_AUDIT_REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__ == '__main__':
    main()
