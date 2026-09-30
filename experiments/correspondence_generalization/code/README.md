# 对应关系泛化：实际开发实现

所有代码、配置在本目录；所有运行产物留在上一级实验目录。仓库其余部分只读。

当前活动运行为 `../runs/qd_throw_diagnostic_20260930_0916/`。先读该目录 `status.json`、`diagnostics_status.json` 和 `PROGRESS_REPORT.md`，检查 PID 与 GPU，不能重复启动。

## 实现与版本来源

- `vendor/qd_train.py`：复制自原 `training/qd_detr_gmr/train.py`。保留任务损失、AdamW、原 loader 随机采样与 seen checkpoint 规则；新增原行曝光/batch 账本、初始化和阶段 checkpoint、配置与参数记录。
- `vendor/qd_dataset.py`：逐字节复制原 dataset；不改变标签、时间窗、采样或特征标准化。
- `vendor/qd_evaluate.py`：复制原评测，改为导入本地 dataset 并适配路径；保持官方 gate 和定位后处理。
- 原模型与原 YAML 配置只读导入，全部实际源文件 hash 与原数据/特征/旧 checkpoint hash 记录于运行 `provenance.json`。用户要求的新增冻结配置保存在 `configs/`；运行目录保留快照。
- 与历史配置的显式偏离：workers=0（未来所有配对运行必须一致）、torch CPU threads=4。不是声称与历史训练 batch 序列完全一致。

## 入口

`run_development.py <新运行绝对路径>` 在独立目录冻结协议、验证所有视图/五组 train/15 个旧 checkpoint/此次访问特征，随后从头启动 A1/throw 100-epoch 开发训练。若目录存在则拒绝覆盖。不要从 CPU smoke 或旧 checkpoint 续训。

`diagnose.py <运行绝对路径> --stage 1 --device cuda:1` 对指定阶段提取原输入、投影与 decoder 表示，执行固定容量/固定曝光的线性读出、文本/视频单模态对照、一维 affine 校准，以及视频 paired bootstrap；输出官方定位与独立 seen 阈值诊断硬拒绝。可用阶段为 0/1/10/30/100/best。

`watch_diagnostics.py <运行绝对路径>` 等待训练阶段 checkpoint 并依次执行 1/10/30/100/best 的诊断；失败记录后不会伪报成功。不运行未知候选，不访问真实 U。

`monitor_progress.py <运行绝对路径>` 每 30 秒更新报告并核查完整 epoch 暴露；完成或失败后停止。`summarize_progress.py` 可执行单次同样报告。

`profile_compute.py <运行绝对路径>` 只对固定 seen batch 测量独立推理计算量，不产生训练曝光。算子 FLOPs 是下界；CUDA event 时间不是完整训练活跃 GPU 时间。

运行使用 `/home/guoxiangyu/miniconda3/envs/gmr/bin/python`，设置 `PYTHONDONTWRITEBYTECODE=1`，将 XDG/TORCH/TMP 缓存环境变量指向本实验 `cache/runtime/`。保留仓库 `training/qd_detr_gmr` 在 Python import path，以兼容只读原 standalone_eval 的绝对导入。

## 阶段判断限制

readout 增益和 joint-over-unimodal 是独立条件；单个 probe 增益不会自动变成因果结论。raw_joint 是随机投影后的可加模型，能力不足不能证明输入无证据。教师参考来源/预算尚未通过，L2/KL 暂停；Witness-DETR 不属于主线。真实 U、全五划分/三骨干正式对照、独立正例 VTG 与多种子仍未执行。

## 自动执行队列（已启动）

用户已要求持久化自动衔接，且明确禁止多种子。`configs/execution_queue.json` 唯一 seed=3407，worker 同样拒绝其他 seed。`execution_queue.py` 在本实验自有 tmux socket 中运行，接管当前诊断后的全部任务，不需要人工启动每个阶段。

队列状态：`../runs/autonomous_queue_20260930/queue_state.json`。检查 tmux 时在 `../cache/runtime/` 执行 `tmux -S queue.sock ls`。不要再次执行 `launch_queue.sh` 或另起队列；queue.lock 也阻止重复调度。

固定单 seed 正式比较 75 个训练任务，支持条件候选最多再加 25 个；没有 3408/3409 任务。两条 GPU lane 顺序执行自己的任务，显存/磁盘不足等待，任务失败最多独立重试一次。真实 U 测试完全位于选择冻结之后。最终报告路径为 `../runs/autonomous_queue_20260930/report/FINAL_REPORT.md`。

## 语义隔离审计后的当前入口

旧 throw 视图存在 3 条 throw 词形查询与 2 条 toss 查询，已作废为严格机制证据。当前训练视图 `../runs/pseudo_unseen_a1_throw_strict/` 保留7559行，排除5个额外视频的8行；dev/seen val不变，正式原train不变。只声称词形和标注动作族的隔离，不声称完全概念隔离。

当前活动训练 `../runs/qd_throw_strict_diagnostic_20260930/`，当前活动队列 `../runs/autonomous_queue_20260930_strict/queue_state.json`。两个 tmux 会话分别为 `correspondence_strict_diagnostic` 和 `correspondence_queue`，均通过本实验 cache/runtime/queue.sock 检查。之前不带 strict 的运行/队列只保留追溯，不再用于进入门槛。唯一 seed=3407。
