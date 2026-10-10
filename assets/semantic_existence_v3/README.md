# v3 数据管线图

- `clean_release_pipeline.svg`：未补充版的语义审核、划分发布与严格评估。
- `balanced_pipeline.svg`：补充版的查询/视频准备、排名与语义筛选、配额生成与验收。
- 同名 PNG 为已视觉检查的预览；GitHub 正文使用可缩放 SVG。
- `render_pipelines.py` 使用 Python 标准库生成原生 SVG 文本和图形；`--png` 可选依赖 `cairosvg`。

```bash
python assets/semantic_existence_v3/render_pipelines.py
python assets/semantic_existence_v3/render_pipelines.py --png
```

设计检查：两图均采用从左至右的三阶段管线，阶段内从上至下；数字和文字与配色共同区分阶段。画布 1280 × 700，主标题 30px，卡片标题 21px，正文 17px；蓝/青/琥珀三色，白底及高对比文字。原生矢量图形，无嵌入位图、渐变或阴影。SVG 提供 title/desc，Markdown 提供替代文本与自包含说明。PNG 预览已检查文字、连接线和边界，未见重叠或裁切。没有统计坐标轴；图中数字追溯到已发布协议和结果。设计审计：0 CRITICAL、0 MAJOR、0 MINOR。
