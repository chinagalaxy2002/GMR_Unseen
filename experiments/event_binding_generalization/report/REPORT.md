# A/A1/B 最小验证报告

结论：**INCONCLUSIVE**。本阶段已结束，没有启动 R、共享 map 完整模型训练、真实 U/test 或原 sit 续训。

本轮问题是 primitive 已相关时，J 是否仍提供跨未见语义的额外视觉证据。以下 pseudo 结果是原 S 的训练侧开发证据，单 seed3407；不是正式 U 确认或跨训练种子稳定性。

## 动作可读性

| 族 | S_train 动词数 | motion temporal | motion mean | motion static | appearance mean |
|---|---:|---:|---:|---:|---:|
| throw | 33 | 0.1938 | 0.2099 | 0.2069 | 0.2245 |
| open_close | 29 | 0.2174 | 0.2285 | 0.2181 | 0.2514 |
| sit | 32 | 0.2169 | 0.2380 | 0.2281 | 0.2529 |

上表为 seen 平衡准确率。闭集词表仅由各族 S_train≥10 个可用 S+ GT segment 的类别定义；held-out verb 不补标签拟合。12 个128维 affine probe，20轮上限，seen选点。SlowFast静态控制仍有clip内部运动；时间统计没有稳定超过外观/时间均值控制。不能由该结果宣布未见动作理解成立，也不能宣布冻结表示无动作信息。逐类词表、OOV覆盖、共同视频paired区间见 [ACTION_PROBE.json](../audit/ACTION_PROBE.json)。

## 输入与覆盖

核验 9860 个唯一文本缓存、4107 个视频。BPE长度全部匹配，SOT/EOT和32-token截断逐行审计；动作有效跨度 9836，实体 9818。原图跨度缺失时采用唯一词形匹配；失败回退整个非特殊token query并保留分母。角色token为上下文化表征，不是去耦primitive标签。

实际流序 CLIP512 | SlowFast2304 | TEF2；语义模块仅用投影前两路raw values，排除TEF。缓存只有features、没有时间戳，现有提取脚本不能与这些数组建立可核验来源联系。保留原min_len及一秒bin假设；**真实双流时间对齐未认证，全部B结果受此限制，不能PASS。** 正例旧文本encoder来源也未在cache中嵌入token IDs/weights；长度一致不能替代完整encoder来源认证。

S−只确认完整事件缺席。正事件注释可提供同视频动作/实体的规范化蕴含证据，但不确认实体身份/角色绑定；同时报告两路P分数控制，不能称人工primitive真标签。

| 族 | pseudo正/负 | 标注视频primitive支持负例 | 高P支持正/负 | 匹配对数 | 匹配正/负视频 | actual-text组/对 |
|---|---:|---:|---:|---:|---:|---:|
| throw | 464/106 | 0 | 229/36 | 2183 | 167/34 | 10/37 |
| open_close | 1888/939 | 18 | 205/68 | 4266 | 148/60 | 158/7367 |
| sit | 625/351 | 0 | 128/2 | 66 | 30/1 | 45/359 |

P动作/实体分支均由原完整事件标签训练，仅是 operational support。高支持门槛为S_train正例中位数，联合quartile分箱由S_train固定；pseudo不按J筛选。actual-text控制固定相同实际cached特征、mask及角色vectors，T组内必须严格tie。配对bootstrap使用两个原视频端点权重乘积；不把组合对数当独立样本量。

## 冻结小模块与总体存在结果

每模块参数量：{"H": 127697, "P": 127298, "C": 127298, "J": 127649, "T": 102593}。15个独立fit，宽度32，AdamW lr=.001，8轮上限，seen AUROC选点；P/C不共享训练参数。相同event监督、GT支持局部训练和top20%均值主读出；S+窗外不标负，GT不进入存在或定位推理。单对J依赖两路visual values和乘积交互；架构与实际相同文本跨视频变化检查均单列。

| 族 | baseline | H | P | C | J | T |
|---|---:|---:|---:|---:|---:|---:|
| throw | 0.5731 | 0.6027 | 0.5721 | 0.5862 | 0.5973 | 0.6027 |
| open_close | 0.5346 | 0.5034 | 0.5240 | 0.4259 | 0.5662 | 0.5788 |
| sit | 0.6540 | 0.6863 | 0.7271 | 0.7143 | 0.6620 | 0.6763 |
| 等权 | 0.5873 | 0.5975 | 0.6077 | 0.5755 | 0.6085 | 0.6193 |

族间证据不一致：J对P在throw/open_close的点估计较高，但sit较低；不能挑族加权或概括为组合/身份绑定成立。

| 等权 paired 差值 | AUROC estimate [95%] |
|---|---:|
| J−H | 0.0110 [-0.0097, 0.0279] |
| J−P | 0.0008 [-0.0081, 0.0094] |
| J−C | 0.0331 [0.0215, 0.0444] |
| J−T | -0.0108 [-0.0225, -0.0002] |

所有区间来自1000次seed3407共同原视频paired bootstrap，族等权，探索性95%；逐族差值、seen结果及FRR/RR均保存在 [PAIRED_STATISTICS.json](PAIRED_STATISTICS.json)。

## primitive 条件与真实文本控制

| pseudo指标（等权） | H | P | C | J | T |
|---|---:|---:|---:|---:|---:|
| primitive_high_AUROC | 0.6122 [0.5707, 0.6571] | 0.6138 [0.5769, 0.6544] | 0.5917 [0.5469, 0.6360] | 0.6142 [0.5721, 0.6539] | 0.6545 [0.6145, 0.6951] |
| primitive_matched_PairAcc | 0.5984 [0.5347, 0.6571] | 0.6434 [0.5920, 0.6949] | 0.6081 [0.5441, 0.6722] | 0.6401 [0.5858, 0.6840] | 0.7027 [0.6562, 0.7493] |
| annotated_video_primitive_AUROC | NA [NA] | NA [NA] | NA [NA] | NA [NA] | NA [NA] |
| actual_text_PairAcc | 0.5011 [0.3886, 0.6081] | 0.4561 [0.3631, 0.5753] | 0.4737 [0.3658, 0.6108] | 0.4538 [0.3447, 0.5631] | 0.5000 [0.5000, 0.5000] |
| actual_text_primitive_matched_PairAcc | NA [NA] | NA [NA] | NA [NA] | NA [NA] | NA [NA] |

primitive匹配等权区间仅有 653/1000 次bootstrap同时保留三族有效正负支持；sit的匹配负例只有1个视频。该区间是有效重采样子集上的描述，不能当覆盖充分的跨族证据。

| 族 | J primitive匹配PairAcc [95%] | J actual-text PairAcc [95%] |
|---|---:|---:|
| throw | 0.4714 [0.3573, 0.5739] | 0.3784 [0.0714, 0.6793] |
| open_close | 0.4794 [0.4074, 0.5550] | 0.4592 [0.4156, 0.5039] |
| sit | 0.9697 [0.9027, 1.0000] | 0.5237 [0.4188, 0.6250] |

| primitive匹配 paired 差值 | estimate [95%] |
|---|---:|
| J−H | 0.0418 [-0.0346, 0.1136] |
| J−P | -0.0033 [-0.0507, 0.0463] |
| J−C | 0.0320 [-0.0390, 0.0940] |
| J−T | -0.0625 [-0.1182, -0.0143] |

actual-text与primitive同时匹配项使用同一冻结规则，为更严格但通常更小的控制覆盖。标注支持项是视频级primitive蕴含，不能当同时实例/身份绑定真标签。覆盖不足或bootstrap缺类时记NA/未决，不填0.5。

## 冻结原候选上的真实定位

| 族 | baseline raw | H raw | P raw | C raw | J raw | J修复/破坏 | 无正确候选 |
|---|---:|---:|---:|---:|---:|---:|---:|
| throw | 0.2672 | 0.1810 | 0.1853 | 0.1875 | 0.1918 | 49/84 | 161/464 |
| open_close | 0.2632 | 0.1827 | 0.1647 | 0.1631 | 0.1541 | 150/356 | 669/1888 |
| sit | 0.3504 | 0.2656 | 0.2208 | 0.2224 | 0.1840 | 56/160 | 113/625 |
| 等权 | 0.2936 | 0.2098 | 0.1903 | 0.1910 | 0.1766 | — | — |

| 定位 paired 差值 | raw R1@.5 estimate [95%] |
|---|---:|
| J−baseline | -0.1170 [-0.1444, -0.0898] |
| J−H | -0.0331 [-0.0541, -0.0090] |
| J−P | -0.0136 [-0.0333, 0.0066] |
| J−C | -0.0144 [-0.0354, 0.0059] |

读出固定为候选窗内map均值，map-only重排；无系数搜索，空支撑−1e6，平局保持原顺序。候选坐标/数量来自原冻结输出，GT只计算IoU，全部原pseudo正例为分母。T没有真实时序map，定位NA；不以峰入GT或候选oracle替代定位性能。

## 决策、护栏与交付

- 来源成员检查误读取含真实 U 行的 val 发布文件（只用 S 行核对，U 未进入训练/前向/选点/指标）；违反不读取边界，不能认证完全未接触 U。
- 原双流真实时间来源未核实；仅沿用 min_len 与 clip_length=1 索引假设。
- 至少一族 primitive 高支持匹配缺少预定的20个正/负独立视频覆盖。
- 至少一族相同实际文本跨视频控制覆盖不足；配对数不能替代独立视频数。
- J 相对 H/P/C/T 的 pseudo AUROC 未全部取得正向且 paired 区间支持的增量。
- primitive 条件与实际文本控制未同时支持 J 的额外视觉证据。
- 冻结候选上的无 GT map 未取得 paired 区间支持的 raw R1@.5 增益。
- 原 seen/拒绝护栏未全部满足；不以更有利 pseudo 阈值修复结论。

护栏（J对原baseline点估计）：`{"throw": {"seen_AUROC_noninferior_point": true, "seen_raw_noninferior_point": false, "pseudo_FRR_noninferior_point": true, "pseudo_RR_noninferior_point": true}, "open_close": {"seen_AUROC_noninferior_point": true, "seen_raw_noninferior_point": false, "pseudo_FRR_noninferior_point": true, "pseudo_RR_noninferior_point": false}, "sit": {"seen_AUROC_noninferior_point": true, "seen_raw_noninferior_point": false, "pseudo_FRR_noninferior_point": false, "pseudo_RR_noninferior_point": true}}`。阈值仅由seen固定，原baseline阈值保留；护栏失败不会通过降低S表现或调pseudo阈值掩盖。

核心问题尚未获得可继续完整训练的充分支持。**停止本阶段；不宣布joint机制已成立或被完全否定，不扫超参/损失挽救。** 若以后另开阶段，应先补齐可核验的双流时间来源及足够primitive条件/相同文本控制，单独明确范围；目前不触发下一阶段训练。

代码、freeze、12个动作probe与15个head checkpoint、逐行原预测/控制得分、局部map、paired统计和失败日志均位于本新目录。所有受保护原代码/数据/feature/checkpoint/旧输出hash通过终检；原loader未导入，临时目录/依赖缓存/pycache也隔离。训练并发为两张GPU各最多两个任务，最多4，不增加变体、多seed或额外教师。来源检查的U读取偏差已单独保存在 [PROTOCOL_INCIDENT.json](../audit/PROTOCOL_INCIDENT.json)，不能声称完全未接触U；所有实际拟合、评估、阈值与checkpoint选择仍只使用原S训练侧视图。

入口：[执行冻结](../EXECUTION_FREEZE.json)、[模块代码冻结](../EVENT_CODE_FREEZE.json)、[输入审计](../audit/INPUT_AUDIT.json)、[控制覆盖](../audit/CONTROL_COVERAGE.json)、[逐行预测](../runs/minimal_validation/PREDICTIONS.jsonl)、[完整性](INTEGRITY.json)、[决策](DECISION.json)。
