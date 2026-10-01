# 候选共同支持方向评估

2026-10-01T01:57:22.358463+08:00。使用idea-evaluator，审查的是本次冻结的p_i×候选间平均IoU读出，而不是所有未来局部支持模型。

## 1. First impression

类型：共同存在/定位新设置中的方法假设，尚无新颖方法主张。一句话：检验已有候选的置信度与互相几何支持，能否无GT地同时服务存在判别和raw候选排序。原目标仍要求AUROC/raw共同改善、gated及seen/拒绝护栏，并用独立VTG界定迁移范围。

## 2. Fatal flaws

| 问题 | 严重性 | 证据 |
| --- | --- | --- |
| 冻结的核心共同支持机制被本项目数据与普通控制反驳（F6/data-refuted） | CRITICAL，仅限本实现 | 等权pseudo AUROC差−.0558、raw差−.0251；两项97.5%辅助区间均<0；seen双指标退化；primary还劣于保留原rank的标量控制 |

真实检索近邻：BAM-DETR（Lee/Byun，ECCV2024，边界与quality ranking），RGTR（Sun/Shi/Wang等，AAAI2025，region anchors/IoU scoring），Sim-DETR（Tang/Wei等，ICCV2025，query关系与frame alignment），GMR（Ding/Cao等，2026，多/零窗任务）。元信息和摘要经arXiv与作者仓库核验，完整链接见[REPORT](REPORT.md)。方法对象/机制与本诊断不同，不能据此声称绝对重复，也没有检索证明创新。

## 7. Verdict

**Reject and Pivot：停止这版候选几何一致性共同读出，不启动训练。** 按技能对data-refuted CRITICAL的短路规则，不再给五维高分或设计乐观挽救阈值。这不否定学习式视觉支持的全部可能，也不将原缓存同句控制不可用当作视觉否定。

已执行的动作：完成原S+/S−存在桥接及raw普通控制；独立重算所有7345条候选、全部1000视频权重的五读出AUC和修复/破坏归因；冻结拒绝该训练路线并保留共同机制未决。下一训练方案仍缺一个能作用于原存在/定位双头的机制与普通控制，不能只修定位或改变gate。
