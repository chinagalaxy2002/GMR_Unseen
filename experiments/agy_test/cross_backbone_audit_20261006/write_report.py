"""Generate independent report from replayed metrics and paired bootstrap."""
import json
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
BBS=['flash','moment','qd']

def main():
    d=json.loads((P/'audit_metrics.json').read_text())
    b=json.loads((P/'bootstrap.json').read_text())
    m=d['macro']
    def ci(v):
        lo,hi=v['ci95']
        return f'[{100*lo:+.2f}, {100*hi:+.2f}] pp'
    lines=['# 跨骨干实验独立审计：2026-10-06','',
           '## 结论','',
           '**3×3 迁移矩阵、逐划分 AUROC 和 PairAcc 能由现有检查点与预测文件复现。** 本轮报告生成器读取 JSON，未发现上一轮 SDCV 那种报告表与产物不一致的问题。','',
           '**实验支持：在共用候选与多模态证据、以目标 Seen 训练分数做无标签 CDF 标准化的条件下，冻结验证器权重可以迁移到另一检测器分数通路。** 宏平均未见判别能力普遍改善，迁移与目标自验证的 AUROC 差距较小。','',
           '**实验不支持：所有路径都有显著增益、严格无损、所有划分无负迁移、端到端候选与特征均骨干无关、已经学到物理因果规则。** 需要限定结论范围并修正原报告的统计判断。','',
           '审计重放 15 个冻结检查点，对照 45 组源→目标分数；核对 15 个缓存的 qid/视频/标签及 Seen-only train/val；独立完成 2,000 次共享视频聚类 Bootstrap（1217 个视频，seed3407）。没有重新训练，没有写入原实验。','',
           '## 1. 数值复验','',
           '| 目标骨干 | 基线 Seen | 基线 Unseen | 自验证 Seen | 自验证 Unseen | 基线 Gap | 自验证 Gap | Δ Unseen 95% CI | Gap 缩小 95% CI |',
           '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for tgt in BBS:
        base,v=m[tgt+'_base'],m[tgt+'_to_'+tgt]
        bs=b['cells'][tgt+'_to_'+tgt]
        lines.append(f"| {tgt} | {base['seen']:.4f} | {base['unseen']:.4f} | {v['seen']:.4f} | {v['unseen']:.4f} | {base['gap']:.4f} | {v['gap']:.4f} | {ci(bs['unseen_gain_vs_target'])} | {ci(bs['gap_reduction_vs_target'])} |")
    lines += ['', '三种自验证的 Seen 都提高、Unseen 提升更多，Gap 点估计均缩小。Moment/QD 的 Gap 缩小区间排除零；Flash 自验证的 Gap 缩小区间跨零，因此不宜称三种退化缩减都已达到统计显著。','',
              '| 来源→目标 | Unseen AUROC | 相对目标基线 ΔU | ΔU 95% CI | 相对目标自验证 ΔU | 相对自验证 95% CI |', '|---|---:|---:|---:|---:|---:|']
    for src in BBS:
        for tgt in BBS:
            n=src+'_to_'+tgt
            v=m[n];bs=b['cells'][n]
            lines.append(f"| {src}→{tgt} | {v['unseen']:.4f} | {(v['unseen']-m[tgt+'_base']['unseen'])*100:+.2f} pp | {ci(bs['unseen_gain_vs_target'])} | {(v['unseen']-m[tgt+'_to_'+tgt]['unseen'])*100:+.2f} pp | {ci(bs['unseen_difference_vs_target_self'])} |")
    lines += ['', '点估计与原 summary 的最大误差为零；CPU 重放分数与原预测最大绝对误差小于 2e-7。Flash .5715 与此前 raw-logit .5714 的小差异来自经验 CDF 合并少量不同分数为同一秩，不能把非严格单调的分位数映射称为绝对不改变 AUROC；这不影响本表内部的可复验比较。','',
              '## 2. 原统计判断错误，独立重算后的证据','',
              '`train_and_transfer.py` 的 bootstrap 只重采样验证器的 Unseen AUROC；虽然创建 boot_matrix_gain 和 split_base_u，但没有保存或计算配对基线增益。`generate_report.py` 仅以 b_mean > base_u 标注“显著正增益 (p<0.01)”。这不是显著性检验。AUROC 本身的区间不包含零，也不能说明它比目标基线显著更好。','',
              '独立重算后：9 条宏平均路径有 8 条 Δ Unseen 的 95% 区间排除零；QD→Flash 跨零。总体改进不是被此统计错误全部否定，但“所有路径 p<.01”必须撤回。这里提供的是逐项 95% 区间，没有多重比较校正，也没有重新推导原 p 值。','',
              '## 3. “近乎无损”应如何表述','',
              '非对角线相对目标自验证的宏平均差异介于 −0.36 和 +0.45 个百分点，确实较小。Flash→Moment 的差异区间跨零；Moment→Flash 点估计略高，但区间也跨零，不能宣称它显著胜过自验证。Flash→QD、Moment→QD 的差异区间为正，支持在本次固定模型与测试样本上优于 QD 自验证；QD→Flash 的差异区间为负，支持存在小幅迁移损失。','',
              '六条非对角线差异的 95% 区间都落在 ±1 个百分点内。这与“允许 1 pp 的近似无损”相容，但 1 pp 是本次审计中的解释范围，不能把事后选择的容差当成预注册的等效性结论。正式实验应预先设定非劣界，并跨种子评估。','',
              '## 4. 候选与证据共享限制了迁移结论的范围','',
              '五折 cache 均软链接到 semantic_directional_calibrated_verifier/cache。训练和推理使用同一份 14 维矩阵。更换目标时仅替换前三列中的检测器分数列；全部目标使用同一个 `mm_te=t_te[:,3:]`。','',
              '共享项包括 CLIP 候选窗口/峰值/动作/物体相似度、SlowFast 候选速度和位移、带符号端点差分、前景 fg_max 与窗口宽度。其中候选、fg_max 和宽度来自已有 HQ 检测器缓存，不是每个目标骨干独立产生的证据。`aligned_calibration_verifier/extract_aligned_features.py:213` 读取 HQ fg/spans，随后按这些候选提取局部特征；MCV 与 SDCV 沿用它们。本实验没有对 Flash/Moment/QD 分别重新提取各自候选证据。','',
              '这不是直接标签泄漏，也不使矩阵失效；它把被验证的假设限制为“共享候选和证据时，分数接口及验证器权重具有迁移性”。若要证明整个验证过程骨干无关，必须交换目标候选、前景及局部特征，并重新评估。','',
              '此外，每个目标检测器的 CDF 参考来自该目标在 Seen train 上的输出，属于目标数据的无标签适配。检验权重没有在目标上重训，但并非“完全不接触目标训练数据”的纯直接迁移。归一化使用 train 而不是 test，没有发现这里使用测试标签。','',
              '路由器仍读取视觉相似度和动力学特征，没有纯语言输入。它是查询与视频联合证据路由，不是实现了 run/walk 词汇识别的纯查询路由。','',
              '## 5. 逐划分的负增益与原报告过度表述','',
              '| A3 目标 | 基线 U | Flash 来源 U | Moment 来源 U | QD 来源 U |', '|---|---:|---:|---:|---:|']
    mm=d['splits']['A3']['metrics']
    for tgt in BBS:
        lines.append(f"| {tgt} | {mm[tgt+'_base']['unseen']:.4f} | {mm['flash_to_'+tgt]['unseen']:.4f} | {mm['moment_to_'+tgt]['unseen']:.4f} | {mm['qd_to_'+tgt]['unseen']:.4f} |")
    lines += ['', 'A3 全部 9 条路径相对目标基线的点估计下降；三条作用于 Flash 的路径，其下降的 95% 区间也都排除零。故宏平均增益不能推出各划分不存在有害验证。A1/A2 相对各自目标基线的点估计均为正，这部分原观察成立；“相对目标自验证不下降”是另一比较，不能混用。','',
              'C1 中 Moment 自验证 AUROC=.6404，低于声称“全部>.645”；作用于 Moment 的三条路径 PairAcc 为 .7778/.7778/.7917，没有全部超过 85%。','',
              '集成并非各目标最高：Flash 集成 .5873 < 最佳单来源 .5891；Moment .5611 < .5615；QD .5521 < .5534。QD 集成 PairAcc=.6234，也不符合报告中“所有目标>.64”。稳定性需要跨种子或区间宽度检验，不能由一次平均推断。','',
              '## 6. 不能从迁移推出物理因果规则','',
              '所有来源共享 Seen 数据、候选和视觉表征；网络还预置了相同的流通道、非负权重与门控范围。这些共同设计足以解释来源差异较小，无需假定它学到了物理因果关系。','',
              '| 目标 | 原始秩基线 U | 冻结未训练初始化 U（诊断） | 对角线训练后 U |', '|---|---:|---:|---:|']
    for tgt in BBS:
        initial=np.mean([v['untrained_initialization_diagnostic'][tgt]['unseen'] for v in d['splits'].values()])
        lines.append(f"| {tgt} | {m[tgt+'_base']['unseen']:.4f} | {initial:.4f} | {m[tgt+'_to_'+tgt]['unseen']:.4f} |")
    lines += ['', '上述未训练初始化用 seed3407 固定，只作诊断，不是另一个已经验证的正式模型。特别是 QD 在不训练验证器时已达 .5461，训练后 .5490；它提示增益可能有较大的固定融合先验成分。需要参数无关固定融合、同预算 detector-only、去方向/绝对值/保留符号、视频置换和时间反转实验，才能识别学习与物理证据各自贡献。','',
              '每折 worker 只在训练三种来源之前设一次 seed3407，三种来源顺序训练，随机数状态持续前进；它们不是同初始化和完全相同训练批次的严格成对对照。Seen 选模规则在代码与缓存上符合声明，但状态字典没有最佳 epoch、选择日志和配置，不能单靠最终权重证明训练历史的硬件、400 epochs 或研究过程严格盲评。视频 Bootstrap 也不覆盖训练随机性。','',
              '当前实验没有保存或评估拒绝阈值、RR/FRR/F1 与 G-mIoU。因此它证明的是未见存在性排序与部分 Gap 改进，还不能证明实际拒绝操作点也具有无损迁移。','',
              '## 7. 建议的最小后续实验','',
              '1. 自动生成配对 ΔAUROC、ΔGap、Transfer−Self 区间，修正 p 值与“所有路径/集成最高”等文字；保留这一版矩阵为共享证据的分数接口迁移实验。',
              '2. 构造两种迁移设置：固定共享候选；目标骨干自身候选+自身 fg/宽度+重新提取局部多模态证据。明确目标 Seen CDF 适配是否允许。',
              '3. 全部来源采用至少 3 个种子，匹配初始化和训练批次；提前指定非劣界，例如 1 pp；避免依据测试集为某个划分定制通路。',
              '4. 加入未训练/固定融合、同结构 detector-only 与方向性消融，优先排查 A3 的错误证据路由。',
              '5. 在源 Seen val 上确定阈值后原样迁移，报告各目标 RR/FRR/F1 和官方 G-mIoU；如允许目标 Seen 校准，单列适配实验。','',
              '## 8. 产物与复验','',
              '- audit_transfer.py：冻结检查点重放、连接审计、全部 AUROC/PairAcc 和共享视频 Bootstrap。',
              '- audit_metrics.json：逐划分与宏平均结果、最大重放误差、Seen 验证 AUROC。',
              '- bootstrap.json：配对基线增益、Gap 缩小、迁移相对自验证区间；bootstrap_draws.npz：2,000 次抽样全记录。',
              '- {split}_audited_scores.npz：逐查询分数；input_manifest.json：主要输入 SHA256。','',
              '复验：`/home/guoxiangyu/miniconda3/envs/univtg/bin/python experiments/agy_test/cross_backbone_audit_20261006/audit_transfer.py`，随后运行同目录 write_report.py。原特征的物理与端点检查沿用本日独立 SDCV 审计的 450 行抽样；本轮新核对所有缓存连接，没有重新提取原始视频特征。']
    (P/'INDEPENDENT_TRANSFER_AUDIT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__': main()
