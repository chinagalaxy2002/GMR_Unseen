"""Editable vector overview of the actual frozen Seen Guard algorithm."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(18,12));ax.set_xlim(0,18);ax.set_ylim(0,12);ax.axis('off')
BLUE='#0072B2';ORANGE='#D55E00';DARK='#25364A';GRAY='#68788B'

def box(x,y,w,h,title,lines,color=BLUE,fill='#F1F7FB'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.10',linewidth=1.7,edgecolor=color,facecolor=fill))
    ax.text(x+w/2,y+h-.37,title,ha='center',va='center',fontsize=23,fontweight='bold',color=DARK)
    ax.text(x+w/2,y+(h-.55)/2,'\n'.join(lines),ha='center',va='center',fontsize=21,color=DARK,linespacing=1.5)

def arrow(points,dashed=False,color=DARK):
    for a,b in zip(points[:-2],points[1:-1]):ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1.9,ls='--' if dashed else '-')
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=22,lw=1.9,color=color,linestyle='--' if dashed else '-'))

ax.text(.35,11.65,'DEC-Power-CDF + Seen Guard',fontsize=29,fontweight='bold',color=DARK)
ax.text(.35,11.1,'A. Offline calibration: train references and Seen validation only',fontsize=24,color=BLUE)
box(.4,8.8,4.1,1.95,'Train references',['Midpoint CDFs: '+r'$F_d, F_E$','Positive-query inventory '+r'$\mathcal{I}$'])
box(5.1,8.8,6.1,1.95,'Seen validation',['41 fusion weights; AUC / G / F','FRR guard: 5 pp validation margin'])
box(12.0,8.8,5.4,1.95,'Frozen policy per setting',['Fusion, constrained threshold,','or fixed DEC decisions'],ORANGE,'#FFF5EE')
arrow([(4.55,9.7),(5.05,9.7)]);arrow([(11.25,9.7),(11.95,9.7)])
ax.plot([.35,17.6],[8.4,8.4],color='#C4CED8',lw=1.0)
ax.text(.35,8.0,'B. Inference: query-text routing, no target labels or semantic graphs',fontsize=24,color=BLUE)
box(.4,5.4,3.5,1.8,'Cached inputs',['Query '+r'$Q$'+'; detector '+r'$d$','DEC evidence '+r'$E$'])
box(.4,2.4,3.5,1.8,'Fixed text parser',['Action-object pair '+r'$p(Q)$','Parse failure: uncovered'])
box(4.5,5.4,5.1,1.8,'Original DEC',[r'$x=F_d(d),\quad y=F_E(E)$',r'$s_D=x^{0.65}\,y^{0.85}$'])
diamond=Polygon([(6.2,4.2),(7.4,3.3),(6.2,2.4),(5.0,3.3)],closed=True,edgecolor=BLUE,facecolor='#F1F7FB',lw=1.7);ax.add_patch(diamond)
ax.text(6.2,3.3,r'$p(Q)\in\mathcal{I}$'+'?',fontsize=23,ha='center',va='center',color=DARK)
ax.text(6.2,2.0,'Train-covered pair?',fontsize=21,ha='center',color=DARK)
box(10.2,5.4,3.8,1.8,'Uncovered query',[r'$m_D=(s_D-\tau_D)/\sigma_D$','Preserve rank + decision'])
ax.add_patch(FancyBboxPatch((9.0,1.05),5.0,3.9,boxstyle='round,pad=0.04,rounding_size=0.1',linewidth=1.7,edgecolor=ORANGE,facecolor='#FFF5EE'))
ax.text(11.5,4.53,'Covered: frozen policy',ha='center',fontsize=22,fontweight='bold',color=DARK)
ax.text(11.5,3.85,'Fusion',ha='center',fontsize=22,fontweight='bold',color=ORANGE)
ax.text(11.5,3.38,r'$f_\alpha=(1-\alpha)x^{0.65}+\alpha s_D$',ha='center',fontsize=21,color=DARK)
ax.text(11.5,2.8,'FRR-constrained Baseline',ha='center',fontsize=22,fontweight='bold',color=ORANGE)
ax.text(11.5,2.36,r'Raw $d$; calibrated $\tau_R$',ha='center',fontsize=21,color=DARK)
ax.text(11.5,1.79,'Fixed-decision re-rank',ha='center',fontsize=21,fontweight='bold',color=ORANGE)
ax.text(11.5,1.34,r'Fix $A_D$; sort $d$ within each group',ha='center',fontsize=21,color=DARK)
box(14.7,3.7,2.85,1.8,'Final score',['Covered: '+r'$m_K$','Uncovered: '+r'$m_D$'],GRAY,'#F5F6F8')
box(14.7,1.0,2.85,1.8,'Accept if '+r'$S\geq0$',['Window / empty','No window changes'],GRAY,'#F5F6F8')
arrow([(3.95,6.3),(4.45,6.3)]);arrow([(2.15,5.35),(2.15,4.25)]);arrow([(3.95,3.3),(4.95,3.3)])
arrow([(7.45,3.3),(8.95,3.3)]);ax.text(8.14,3.55,'covered',fontsize=21,ha='center',color=ORANGE)
arrow([(6.2,4.25),(6.2,5.12),(10.7,5.12),(10.7,5.35)]);ax.text(7.5,4.80,'uncovered',fontsize=21,ha='center',color=BLUE)
arrow([(9.65,6.3),(10.15,6.3)]);arrow([(9.55,5.35),(9.55,5.0)])
arrow([(14.05,6.3),(16.15,6.3),(16.15,5.55)]);arrow([(14.05,3.2),(14.35,3.2),(14.35,4.6),(14.65,4.6)])
arrow([(16.15,3.65),(16.15,2.85)])
arrow([(2.45,8.75),(2.45,7.65),(6.6,7.65),(6.6,7.25)],True,BLUE)
arrow([(12.55,8.75),(12.55,7.55),(9.85,7.55),(9.85,5.0)],True,ORANGE)
ax.text(.4,.3,'FRR = positive false rejection rate; G = G-mIoU; F = rejection F1. Dashed arrows: frozen calibration.',fontsize=21,color=GRAY)
fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
for extension in ('svg','pdf','png'):fig.savefig(ROOT/('algorithm_overview.'+extension),dpi=160,bbox_inches='tight',pad_inches=.13)
svg=ROOT/'algorithm_overview.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
plt.close(fig)
print('Saved SVG, vector PDF and PNG preview:',ROOT)
