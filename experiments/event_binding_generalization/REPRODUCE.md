# 复核与复现

本目录交付的是已经完成的 A/A1/B 最小验证。首先阅读 [REPORT.md](report/REPORT.md)、[DECISION.md](report/DECISION.md)和[协议偏差记录](audit/PROTOCOL_INCIDENT.json)。不因下载此目录而启动新训练或下一阶段。

## 无原特征的结果复核

最终 JSON、JSONL 和 NPZ 已上传，能够复核主要存在/定位统计、分母和 paired 结果。逐族预测与 `PREDICTIONS.jsonl` 是重复组织形式；累计条数只计一次。局部 map 以 `offset[i]:offset[i+1]` 对应同族同 split 第 i 行。

Bootstrap 使用原视频聚类；seen/pseudo 六组共享2302个视频的同一组采样权重，seed3407、1000次。族等权，原 query 权重保持；配对端点 multiplicity 相乘。sit primitive 条件只有一个负视频，等权 primitive 区间只在653次同时保留有效三族支持的重采样上可计算，不能当覆盖充分的结论。

## 需要的原只读资产

重新拟合或原候选复算需要原工程的三族 S_train/seen/training-side pseudo 视图、CLIP/SlowFast 和 CLIP 文本缓存、冻结原候选与 seen 阈值。路径定义见 [common.py](code/common.py)，原资产 SHA-256 见 `EXECUTION_FREEZE.json` 和 `report/INTEGRITY.json`。这些大型外部资产没有再次上传。

代码使用 Python 3.10、PyTorch 2.6.0+cu124、scikit-learn 1.7.2；完整执行环境版本记录在 `publication/ENVIRONMENT.json`。Tokenizer 使用原 CLIP BPE 实现和词表，代码路径、词表 hash 与跨度规则在审计和 freeze 中记录。额外 `regex`/`ftfy` 安装于本目录 `cache/deps/`，重跑时也只允许安装到该隔离位置。

原双流缓存没有时间戳或可关联的提取记录。现有结果沿用 min_len 截断和 `clip_length=1`，**不能用复现数值证明真实时间对齐**。正例文本 cache 未嵌入 encoder/token IDs 来源；长度匹配也不是完整来源认证。

## 执行入口与顺序

下面是已有执行入口的索引，不是当前继续训练指令。现有脚本有防覆盖检查；不要删除 freeze、状态、结果或 checkpoint 来绕过它们。

| 顺序 | 入口 | 作用 |
|---|---|---|
| 1 | `code/freeze.py` | 原资产检查与执行冻结；修正后的源码使用已有 S-only seen 文件，原执行时的 U 读取偏差保留在审计中 |
| 2 | `code/action_probe.py` | 仅各族 S_train 上的 GT segment→verb probe，词表不从 held-out 定义 |
| 3 | `code/input_audit.py` | token/span、缓存来源、时间来源和 primitive 标签覆盖 |
| 4 | `code/event_modules.py prepare` | 缓存和单对 J visual path/C AND 架构契约 |
| 5 | `code/run_fits.py` | 固定15个 H/P/C/J/T fit；每GPU最多2，总最多4；无超参/变体扫描 |
| 6 | `code/evaluate.py` | 全部模型 seen 选点完成后冻结门槛，再评估 pseudo/actual-text 与既有候选 |
| 7 | `code/statistics.py` | 共同视频 paired bootstrap |
| 8 | `code/closeout.py` | 独立指标、原资产检查和 STOP/INCONCLUSIVE/PASS 决策 |

新的训练需要另行明确范围和新运行目录，保持当前原始记录不可覆盖。R、共享 map 完整训练、边界头、真实 U/test、原 sit 续训、多 seed 和额外方法不属于本阶段。
