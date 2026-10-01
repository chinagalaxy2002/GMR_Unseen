from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
D=Path(__file__).resolve().parents[1]/'temporal_representation_analysis';r=json.loads((D/'RESULTS.json').read_text());families=['throw','open_close','sit']
fig,axes=plt.subplots(1,3,figsize=(13,3.9),layout='constrained')
configs=[('Pseudo: video-level discrimination','pseudo',[('Original','original_native/AUROC'),('Early mean','early_global/mean/AUROC'),('Text only','text_global/mean/AUROC')],.5),('Pseudo: relative temporal evidence','pseudo',[('Window-supervised probe','memory_window/peak_minus_duration_chance')],0),('Same actual text: visual pair ranking','canonical',[('Original','original_native/max/same_query_PairAcc_query_equal'),('Early max','early_global/max/same_query_PairAcc_query_equal'),('Memory max','memory_global/max/same_query_PairAcc_query_equal')],.5)]
for ax,(title,split,metrics,ref) in zip(axes,configs):
 for j,(name,key) in enumerate(metrics):
  vals=[r['groups'][f+'/'+split]['metrics'][key] for f in families];x=np.arange(3)+(j-(len(metrics)-1)/2)*.16;y=np.array([v['point'] for v in vals]);lo=np.array([v['ci95'][0] for v in vals]);hi=np.array([v['ci95'][1] for v in vals]);ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt='o',capsize=3,label=name,markersize=4)
 ax.axhline(ref,color='gray',linestyle='--',linewidth=1);ax.set_xticks(range(3),families);ax.set_title(title,fontsize=10);ax.legend(fontsize=8,loc='best');ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('AUROC');axes[1].set_ylabel('Peak in GT minus GT temporal fraction');axes[2].set_ylabel('Query-equal PairAcc');axes[2].set_ylim(-.03,1)
fig.suptitle('Frozen models, matched 257-parameter probes; exploratory shared-video 95% intervals',fontsize=11)
fig.savefig(D/'REPRESENTATION_READOUT.png',dpi=180);fig.savefig(D/'REPRESENTATION_READOUT.pdf');plt.close(fig)
