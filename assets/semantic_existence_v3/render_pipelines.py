#!/usr/bin/env python3
"""Render compact pipeline strips. Optional --png requires cairosvg."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
FONT='Noto Sans CJK SC, Microsoft YaHei, PingFang SC, Arial, sans-serif'


def element(parent,tag,**attrs):
    return ET.SubElement(parent,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attrs.items()})


def text(parent,x,y,value,size=19,color='#334155',weight=400):
    el=element(parent,'text',x=x,y=y,fill=color,font_family=FONT,font_size=size,font_weight=weight,text_anchor='middle')
    el.text=value


def draw(path,title,steps):
    svg=ET.Element('{'+NS+'}svg',{'width':'1100','height':'154','viewBox':'0 0 1100 154','role':'img','aria-labelledby':'title desc'})
    element(svg,'title',id='title').text=title
    element(svg,'desc',id='desc').text=' → '.join(a+'：'+b for a,b in steps)
    element(svg,'rect',width=1100,height=154,rx=12,fill='#FFFFFF')
    colors=[('#EFF6FF','#BFDBFE'),('#F0FDFA','#99D9D0'),('#F0FDFA','#99D9D0'),('#F0FDFA','#99D9D0'),('#FFFBEB','#F4D79D')]
    for i,((label,sub),(fill,stroke)) in enumerate(zip(steps,colors)):
        x=12+i*220
        element(svg,'rect',x=x,y=24,width=196,height=104,rx=12,fill=fill,stroke=stroke,stroke_width=1.3)
        text(svg,x+98,67,label,22,'#0F172A',600)
        text(svg,x+98,101,sub,17,'#475569')
        if i<4:
            element(svg,'path',d=f'M {x+201} 76 H {x+214} M {x+208} 70 L {x+214} 76 L {x+208} 82',fill='none',stroke='#64748B',stroke_width=2,stroke_linecap='round',stroke_linejoin='round')
    ET.indent(svg,space='  ')
    ET.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--png',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parent
    draw(root/'clean_release_pipeline.svg','未补充版 v3 管线',[
        ('正例与改写候选','同视频替换动作/对象'),('语义审核','归一事件 · 排除冲突'),('五组划分','视频互斥 · 语义留出'),('Seen-only 训练','Seen 验证选模型/阈值'),('退化评估','三项指标 · Gap · CI')])
    draw(root/'balanced_pipeline.svg','Balanced v3 管线',[
        ('原始 v3','保留全部原始样本'),('跨视频配对','原查询 + 另一视频'),('CLIP 文本排名','保留最低一半视频'),('语义过滤','去重 · 排除标注冲突'),('补齐与校验','追加伪负例至正负 1:1')])
    if args.png:
        import cairosvg
        for path in root.glob('*_pipeline.svg'):cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))

if __name__=='__main__':main()
