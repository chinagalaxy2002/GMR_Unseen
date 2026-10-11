# v3 简要管线图

两套管线均采用单行五步布局，画布为 1100 × 154；README 和详细说明引用同一份 SVG。点击正文图片可放大。保留同名 PNG 预览和可编辑生成脚本。

- `clean_release_pipeline.svg`：原始数据 → 语义审核 → 五组划分 → Seen-only 训练 → 退化评估。
- `balanced_pipeline.svg`：原始 v3 → 跨视频配对 → CLIP 文本排名 → 语义过滤 → 补齐与校验。

```bash
python assets/semantic_existence_v3/render_pipelines.py
# 可选 PNG 预览，需安装 cairosvg
python assets/semantic_existence_v3/render_pipelines.py --png
```
