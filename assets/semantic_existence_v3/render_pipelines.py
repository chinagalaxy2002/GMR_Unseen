#!/usr/bin/env python3
"""Generate editable, accessible SVG pipeline figures using the standard library.

Run: python assets/semantic_existence_v3/render_pipelines.py
Optional PNG previews: install cairosvg, then pass --png.
"""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
FONT='Noto Sans CJK SC, Microsoft YaHei, PingFang SC, Arial, sans-serif'
PALETTE=[('#1D4ED8','#EFF6FF','#BFDBFE'),('#0F766E','#F0FDFA','#99D9D0'),('#9A5809','#FFFBEB','#F4D79D')]


def element(parent,tag,**attrs):
    return ET.SubElement(parent,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})


def text(parent,x,y,value,size=20,color='#334155',weight=400,anchor='start'):
    node=element(parent,'text',x=x,y=y,fill=color,font_family=FONT,font_size=size,font_weight=weight,text_anchor=anchor)
    node.text=value
    return node


def arrow(parent,x1,y1,x2,y2):
    element(parent,'path',d=f'M {x1} {y1} L {x2} {y2}',fill='none',stroke='#94A3B8',stroke_width=2,marker_end='url(#arrow)')


def draw(path,title,subtitle,stages,footer_title,footer_lines,desc):
    svg=ET.Element('{'+NS+'}svg',{'width':'1280','height':'700','viewBox':'0 0 1280 700','role':'img','aria-labelledby':'title description'})
    element(svg,'title',id='title').text=title
    element(svg,'desc',id='description').text=desc
    defs=element(svg,'defs')
    marker=element(defs,'marker',id='arrow',viewBox='0 0 10 10',refX=9,refY=5,markerWidth=7,markerHeight=7,orient='auto-start-reverse')
    element(marker,'path',d='M 1 1 L 9 5 L 1 9',fill='none',stroke='#94A3B8',stroke_width=1.7,stroke_linecap='round',stroke_linejoin='round')
    element(svg,'rect',x=0,y=0,width=1280,height=700,rx=18,fill='#FFFFFF')
    text(svg,36,50,title,30,'#0F172A',650)
    text(svg,36,86,subtitle,19,'#64748B')
    positions=[36,450,864]
    for i,(x,stage) in enumerate(zip(positions,stages)):
        color,tint,border=PALETTE[i]
        element(svg,'rect',x=x,y=120,width=380,height=426,rx=16,fill=tint,stroke=border,stroke_width=1.2)
        element(svg,'rect',x=x+20,y=140,width=42,height=34,rx=9,fill=color)
        text(svg,x+41,164,f'{i+1:02}',18,'#FFFFFF',650,'middle')
        text(svg,x+75,165,stage['title'],24,color,650)
        text(svg,x+20,196,stage['subtitle'],17,'#64748B')
        for j,(heading,lines) in enumerate(stage['cards']):
            cy=216+j*104
            element(svg,'rect',x=x+20,y=cy,width=340,height=84,rx=10,fill='#FFFFFF',stroke=border,stroke_width=1)
            element(svg,'rect',x=x+20,y=cy+15,width=4,height=54,rx=2,fill=color)
            text(svg,x+36,cy+29,heading,21,'#0F172A',600)
            for k,line in enumerate(lines):text(svg,x+36,cy+53+k*21,line,17,'#475569')
            if j<2:arrow(svg,x+190,cy+87,x+190,cy+101)
        if i<2:arrow(svg,x+385,158,positions[i+1]-7,158)
    element(svg,'rect',x=36,y=568,width=1208,height=104,rx=12,fill='#F8FAFC',stroke='#CBD5E1',stroke_width=1)
    text(svg,56,600,footer_title,20,'#334155',650)
    for i,line in enumerate(footer_lines):text(svg,56,627+i*25,line,18,'#475569')
    ET.indent(svg,space='  ')
    ET.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--png',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parent
    draw(root/'clean_release_pipeline.svg','未补充版 v3：从语义审核到泛化评估','先完成数据制作，再冻结划分与输入，最后训练和评估；三个阶段从左到右阅读。',[
        dict(title='语义审核',subtitle='原始正例 + 旧版反事实候选',cards=[
            ('整理原始查询',['保留视频、查询与正例 GT 时间窗']),
            ('归一化完整事件',['区分动作词义、对象别名与语义角色']),
            ('逐 qid 审核与冲突检查',['剔除重合、蕴含、歧义及构造错误','形成 15,034 正例 / 2,869 负例母池'])]),
        dict(title='划分与发布',subtitle='视频互斥 · 完整查询语义留出',cards=[
            ('固定视频级划分',['Train / Val / Test 共用视频分配']),
            ('构建五组语义留出',['A1–A3 动作；C1–C2 动作×对象','训练仅 S+ / S−，同轴共享审核负例']),
            ('发布并冻结输入',['保存标注、配对、统计与校验记录','每组完整 Test：4,611 条'])]),
        dict(title='训练与评估',subtitle='3 个 backbone × 5 个划分',cards=[
            ('Seen-only 从头训练',['Moment-DETR / QD-DETR / FlashVTG']),
            ('仅 Seen validation 选择',['冻结最佳 checkpoint 与拒绝阈值']),
            ('完整测试集与 Bootstrap',['汇总 AUROC / Rej-F1 / G-mIoU@1','Seen、Unseen、Gap 与 95% CI'])])],
        '数据与结论的边界',[
            '本版没有追加跨视频伪负例；文本语义审核通过，不等于逐视频确认事件缺席。',
            '2,000 次视频级聚类 Bootstrap；模型和阈值固定，五划分等权计算宏平均。'],
        '未补充版三阶段流程：语义审核、划分与发布、Seen-only训练和泛化评估。每个阶段内部从上到下阅读。')
    draw(root/'balanced_pipeline.svg','Balanced v3：怎样补充跨视频伪负例？','保留原始数据，把已有正例查询配给另一段视频；按规则筛选后追加，补齐完整 split 的正负数量。',[
        dict(title='准备查询与视频',subtitle='每个组、每个 split 独立处理',cards=[
            ('保留原始行，计算缺额',['需要新增的负例数 = 正例数 − 负例数']),
            ('借用同 split 的正例查询',['相同文本选一个来源，查询保持不变']),
            ('选择同 split 的其他视频',['排除查询原视频','参考目标视频全部干净正例描述'])]),
        dict(title='排名与语义筛选',subtitle='CLIP 比较文本，不直接比较画面',cards=[
            ('为每个候选视频打分',['查询与各正例描述的余弦相似度','取其中最高值作为视频分数']),
            ('保留升序排名最低一半',['对每条查询单独排名','这是排名条件，不是相似度 < 0.5']),
            ('排除重复与已有标注冲突',['语义重合、对象不明确等保守过滤','不从原排名后一半补位'])]),
        dict(title='抽样、生成与验收',subtitle='只补够名额，保留每条来源证据',cards=[
            ('按 S/U 名额轮流抽样',['Train 只加 S−；Val/Test 按正例比例','完整 split 补到正负 1:1']),
            ('写入新视频—查询记录',['目标视频与时长 + 空 GT 窗口','保存新 qid、来源、排名和伪负例标记']),
            ('追加原始行之后并校验',['重算全部新增配对的 CLIP 排名','合计新增 58,844 条伪负例'])])],
        '两条必须保留的解释边界',[
            '低文本相似度 + 无已知标注冲突，不能证明事件缺席；新增标签未逐视频核验。',
            '1:1 只针对完整 Train / Val / Test，不保证 Seen 与 Unseen 子集分别平衡。'],
        'Balanced三阶段流程：同组同split准备来源查询与目标视频；文本打分、保留最低半区并排除冲突；按配额抽样、生成和校验伪负例。')
    if args.png:
        import cairosvg
        for path in root.glob('*_pipeline.svg'):
            cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))
    print('Generated clean_release_pipeline.svg and balanced_pipeline.svg')

if __name__=='__main__':main()
