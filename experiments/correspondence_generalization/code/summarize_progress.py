"""Auditable progress report. No model or threshold choices are made here."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
run=Path(sys.argv[1]).resolve();assert run.is_relative_to(HERE/'runs')
status=json.loads((run/'status.json').read_text());epochs=[json.loads(l) for l in (run/'epochs.jsonl').read_text().splitlines()] if (run/'epochs.jsonl').exists() else []
expected={str(json.loads(l)['qid']) for l in Path(json.loads((run/'resolved_config.json').read_text())['train_path']).read_text().splitlines()}
for e in epochs:assert set(e['exposures'])==expected and set(e['exposures'].values())=={1} and e['rows']==len(expected) and e['updates']==(len(expected)+15)//16
batches=[json.loads(l) for l in (run/'batches.jsonl').read_text().splitlines()] if (run/'batches.jsonl').exists() else []
text=['# A1/throw 训练侧阶段诊断进展','',f"训练状态：`{status['state']}`。本报告快照包含 {len(epochs)} 个完整 epoch、{len(batches)} 个已完成更新、{sum(len(b['qids']) for b in batches)} 行曝光。完整 100-epoch 预算为 47,300 更新、755,900 行曝光（修复后 strict view）；尚未完成时不得作为正式结果。",'','已逐 epoch 核实每条 7559 行 strict 训练数据恰好暴露一次，batch size=16、尾 batch=7，无丢弃、无新增样本。训练视频与 throw 开发视频隔离；仅 seen validation 参与原 checkpoint 选择。真实 U 未读取。','', '新实现位于 code/，原训练/数据/评测接口已复制到 code/vendor/；模型本体与配置只读导入，哈希见 provenance.json。实际两个 CUDA 设备均已通过张量运算测试。','']
for stage in ('0','1','10','30','100','best'):
    p=run/f'diagnostic_{stage}/metrics.json'
    if not p.exists():continue
    m=json.loads(p.read_text());text += [f'## 阶段 {stage}（checkpoint epoch={m["checkpoint_epoch"]}）','', '| 读出 | seen AUROC | pseudo-unseen AUROC | 相对原头差值 95% 视频 paired CI |','|---|---:|---:|---|']
    for k,v in m['metrics'].items():
        ci=m['pseudo_video_bootstrap']['paired_gain_over_head_ci95'].get(k)
        text.append(f"| {k} | {v['seen']['auroc']:.4f} | {v['pseudo']['auroc']:.4f} | {str([round(x,4) for x in ci]) if ci else '—'} |")
    if stage=='0':text += ['','**可靠性限制**：初始化阶段运行期间补充了诊断代码，早期报告的最终文件 hash 不代表完整执行版本；此阶段仅作探索性初始化参照，不用于通过机制门槛。stage 1 起在启动时记录所有执行源文件哈希。']
    if 'localization' in m:
        text += ['','| 原头定位（正例） | raw R@1 IoU .5 | raw R@1 IoU .7 | seen 阈值硬拒绝 .5 | raw 正确 .5 的误拒率 |','|---|---:|---:|---:|---:|']
        for n,v in m['localization'].items():text.append(f"| {n} | {v['raw_R1@0.5']:.4f} | {v['raw_R1@0.7']:.4f} | {v['hard_R1@0.5']:.4f} | {v['raw_correct_positive_false_reject_0.5']} |")
    text += ['','阶段判断：联合读出优于原头只是关联证据；还必须显著优于同容量单模态控制，且 seen 代价符合冻结协议。当前报告不将任何阶段 probe 自动宣称为因果机制。']
text += ['','## 机制与范围限制','','初始化的 text-only probe seen AUROC 较高，说明文本表面/构造线索足以完成部分存在分类；它不能证明模型在跨模态交互中实际采用该捷径。raw_joint 是随机压缩后线性可加读出，无法覆盖任意图文交互；projection_joint 的乘积坐标也不是已验证 CLIP 对齐空间。失败不能据此证明输入缺少动作证据。','','scalar_calibration 是训练拟合的一维 affine logistic，可反转排序；它不等同于保序 temperature scaling。所有 probe 固定预算 100 epochs，批顺序 hash 与每行 100 次曝光见各 probe 记录。bootstrap 以视频为单位，与训练种子变化不同；当前只有 seed=3407。','','原官方 gate 为 threshold=0.5、soft multiplier；诊断硬拒绝阈值由 seen validation 最大 Youden J 选择。官方指标保存在各阶段 *_official_predictions_metrics.json，不与诊断硬拒绝定位混用。','','没有执行候选方法、同预算正式对照、真实 U 四象限测试或无存在头独立正例 VTG；这些均未完成。参考投影来源/预算尚未通过，所以没有进入教师 L2/KL 分支，没有恢复 Witness-DETR。','','计算量账本已含参数量、forward/update/逐行曝光、墙钟时间、GPU 峰值内存；准确 FLOPs 与 GPU 活跃时间仍未测量，不能把墙钟时间叫作 GPU kernel 时间。','','诊断 watcher 将等待 1/10/30/100/best checkpoint，GPU 1 自动执行固定 probe 与 seen/pseudo 评测。当前不会自动跨越机制门槛启动未知候选。']
if (run/'compute_profile.json').exists():
    cp=json.loads((run/'compute_profile.json').read_text())
    text += ['',f"独立计算量测量：参数 {cp['parameters']:,}，固定 seen batch 的已计数 forward 算子 FLOPs={cp['torch_profile_reported_forward_flops']:,}，20 次 CUDA event 平均 {cp['cuda_event_ms_per_forward_20_repeats']:.3f} ms/forward；未支持算子/attention 可能未计入，不外推完整训练。详见 compute_profile.json。"]
if (run/'verification.json').exists():
    v=json.loads((run/'verification.json').read_text())
    text += ['',f"冻结资产复核：{v['frozen_assets_checked']:,} 个资产、{v['readonly_source_checked']} 个原实现/配置，hash 变化 {len(v['hash_changes'])}。阶段 1 等容量/等更新/等曝光/batch 顺序已核实。"]
(run/'PROGRESS_REPORT.md').write_text('\n'.join(text)+'\n')
print(run/'PROGRESS_REPORT.md')
