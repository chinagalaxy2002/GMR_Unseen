# 五组语义划分说明图

每组一张：A1、A2、A3、C1、C2。展示未补充版 v3 的 Unseen 语义、训练排除规则、Test 的 Seen/Unseen 正负数量、实际查询与退化评估方式。数量直接统计自各组冻结的 `test.jsonl`，`counts.json` 保存细分类计数和输入文件 SHA-256。

- SVG：README 展示，可编辑文字。
- PDF：矢量导出，适合论文与汇报；缩放后请保持字号可读。
- PNG：180 dpi 预览。

在仓库根目录运行：

```bash
python assets/semantic_existence_v3/split_figures/render_split_figures.py
```

需要 Matplotlib 和 Noto Sans CJK 字体，也可用 `--release` 指定未补充版数据目录。C1 对象统一 sofa/couch，并归并带修饰的床、椅子、沙发；C2 归并明确柜子上下文的柜门与抽屉。图中数量均为视频–查询配对数，不是不同文本数。新增的 balanced 伪负例未包含在这些图中。
