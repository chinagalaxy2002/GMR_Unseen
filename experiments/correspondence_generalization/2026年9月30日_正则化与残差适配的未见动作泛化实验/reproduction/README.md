# 第一阶段结果与训练复现

## 1. 无需GPU重新计算已发布结果

从仓库根目录执行（Python环境需安装scikit-learn）：

```bash
python 'experiments/correspondence_generalization/2026年9月30日_正则化与残差适配的未见动作泛化实验/reproduction/recompute_results.py'
```

脚本从logs/的压缩GT和预测重新计算六组结果，逐一比对原test/report.json中的S/U AUROC、正例FRR、负例RR、raw/官方gate/诊断硬拒绝R1@0.5和R1@0.7、raw正确正例误拒率，以及VTG的定位与mIoU。不是只读取CSV复述指标。已在本地运行，六组全部通过，误差要求小于1e-12。

每组视频paired bootstrap区间保存于evidence/report/*_video_ci.json；重算脚本不声称重新估计区间或多seed方差。原bootstrap实现见[aggregate_queue.py](../../code/aggregate_queue.py)。

## 2. 从头训练复现

需要：支持CUDA的PyTorch环境、仓库requirements.txt、原发布A1标注、已有CLIP文本/视频与SlowFast视频缓存。视频目录包含vid_clip/和vid_slowfast/；文本缓存位于仓库features/semantic_existence_v2/A1/clip_text/。特征及checkpoint不随本次提交发布。

新脚本使用evidence/run_configs.json中的实际运行配置作为模板，无需历史基线checkpoint；覆盖机器路径，从头随机初始化模型。保留原模型、损失、seen-only选择、固定seed3407和100epochs。关闭同预算核验；普通训练日志仍保存。

先进行只读前置检查：

```bash
python 'experiments/correspondence_generalization/2026年9月30日_正则化与残差适配的未见动作泛化实验/reproduction/reproduce_training.py' \
  --track gmr --method baseline --action check --video-root /path/to/charades
```

确认资产后，复现一个任务（此命令会实际训练与评测）：

```bash
python 'experiments/correspondence_generalization/2026年9月30日_正则化与残差适配的未见动作泛化实验/reproduction/reproduce_training.py' \
  --track gmr --method baseline --action all --video-root /path/to/charades --gpu 0
```

track可取gmr/vtg，method可取baseline/regularized/adapter，共六组。建议逐项串行执行，不要每卡超过两个任务。--action train只训练，evaluate只评测已有新checkpoint；all按顺序完成训练和评测。--run-name用于选择新的复现目录，脚本拒绝覆盖已有训练或test目录。

产物位于experiments/correspondence_generalization/runs/reproductions/<run-name>/jobs/。脚本按归档GMR的seen视图恢复本地val_seen.jsonl，仅在缺失时写入，若已有内容不同则停止；VTG由worker按原规则过滤正例。复现的选择冻结记录复制到新目录，不修改旧队列与原结果。

## 3. 验证范围与限制

本次完成归档预测的数值重算、脚本语法和本地资产路径检查，未为上传重跑六个100epoch任务。新训练包装脚本复用本次worker和vendor实现，执行代码hash可能与早期训练worker不同；实际历史hash保存在logs/的provenance及evidence/run_configs.json。不承诺不同软件、CUDA、GPU环境逐位一致。

日志保留历史本机绝对路径和数据/模型hash用于追溯；阅读GitHub归档时使用logs/及evidence/内的相对入口，本地ARTIFACT_INDEX中的旧runs路径不代表GitHub包含checkpoint。空VTG batches.jsonl符合本次关闭预算账本的设置。训练复现需要自行准备资产，不会访问目标U进行超参选择。
