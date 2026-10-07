from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager
out=Path(__file__).parent
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')
font=font_manager.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc')
plt.rcParams['font.family']=font.get_name()
plt.rcParams['svg.fonttype']='none'
fig,ax=plt.subplots(figsize=(18,10))
fig.subplots_adjust(left=.015,right=.985,top=.98,bottom=.02)
ax.set_xlim(0,180); ax.set_ylim(0,100); ax.axis('off')
ink='#233447'; blue='#0072B2'; orange='#D55E00'; teal='#008577'
def text(x,y,s,size=15,color=ink,weight='normal',ha='center'):
 ax.text(x,y,s,fontsize=size,color=color,weight=weight,ha=ha,va='center',linespacing=1.6)
def box(x,y,w,h,title,body='',color=blue,fill='#F0F7FC',ts=16,bs=13):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.5,rounding_size=1.1',lw=1.5,ec=color,fc=fill))
 text(x+w/2,y+h-4,title,ts,color,'bold')
 if body:text(x+w/2,y+(h-5)/2,body,bs)
def arrow(x1,y1,x2,y2,color=ink,dashed=False):
 ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=17,lw=1.7,color=color,linestyle='--' if dashed else '-'))
text(90,96,'CoG-Verifier：用视频证据核验“事件是否发生”',24,weight='bold')
text(90,90.7,'免训练后处理校准｜已有骨干找片段，新增校准器决定是否返回',15)
# Offline row
ax.add_patch(FancyBboxPatch((2,64),176,21,boxstyle='round,pad=0.5',ec='#C5CFD9',fc='#F7F9FB',lw=1))
text(5,81.5,'① 离线准备',16,weight='bold',ha='left')
box(5,66,43,11,'已有模型与特征','检索骨干 + CLIP / SlowFast（均已训练）',color='#64748B',fill='white',ts=14,bs=11)
box(55,66,58,11,'训练集 → 冻结参考分布','检测器 CDF；各证据流分别建立 CDF',color=teal,fill='#EDF8F5',ts=14,bs=12)
box(120,66,54,11,'Seen 验证集 → 冻结阈值 τ','依据正例召回目标选择阈值',color=orange,fill='#FFF5ED',ts=14,bs=12)
# online pipeline
text(5,59,'② 测试时：逐查询核验',16,weight='bold',ha='left')
box(4,24,30,29,'视频 + 查询','“把杯子放进柜子”\n\n未见语义也使用同一流程',ts=16,bs=12)
box(43,40,38,13,'已有 GMR 检索骨干','候选窗口 [起点, 终点] + 分数 d',color='#64748B',fill='#F7F9FB',ts=14,bs=12)
box(43,20,38,15,'查询驱动证据路由','运动 / 物体交互 / 状态转换\n固定规则、固定证据权重',color=teal,fill='#EDF8F5',ts=14,bs=12)
box(91,22,41,31,'参考分布校准 + 融合','r_det = CDF_train(d)\nr_ev = CDF_train,流(e)\n\ns = 0.5 r_det + 0.5 r_ev',ts=16,bs=14)
box(143,24,32,27,'固定阈值决策','s ≥ τ：返回原候选片段\n\ns < τ：拒绝返回',color=orange,fill='#FFF5ED',ts=16,bs=12)
arrow(34,44,43,46);arrow(34,31,43,28)
arrow(81,46,91,46);arrow(81,28,91,28)
arrow(132,38,143,38)
arrow(84,66,111,54,teal,True)
arrow(147,66,159,52,orange,True)
text(63,15.5,'CLIP：图文匹配；SlowFast：运动变化',12,color=teal)
text(159,18,'仅改变接受 / 拒绝\n不更新定位窗口',12,color=orange)
# footer
ax.plot([4,176],[11,11],color='#CBD5E1',lw=1)
text(90,7.3,'“免训练” = 新增校准器无反向传播、无新模型权重；仍需训练参考分布和 Seen 验证阈值。',14,weight='bold')
text(90,2.7,'实线：测试数据流   ·   虚线：冻结校准配置   ·   CDF：分数在参考样本中的百分位数',12,color='#526274')
for ext in ['svg','pdf','png']:
 fig.savefig(out/f'cog_verifier_overview.{ext}',dpi=180,facecolor='white')
print(out)
