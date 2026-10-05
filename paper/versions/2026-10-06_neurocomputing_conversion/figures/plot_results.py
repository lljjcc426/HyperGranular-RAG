"""Three vector figures, derived exclusively from the numerical supplement."""
import csv, shutil, time, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

H=Path(__file__).resolve().parents[1]; cpu=time.process_time()
def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
def save(fig,name):
    fig.savefig(H/'figures'/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(H/'figures'/f'{name}.png',dpi=180,bbox_inches='tight')
    shutil.copyfile(H/'figures'/f'{name}.pdf',H/'manuscript'/f'{name}.pdf');plt.close(fig)
rr=read(H/'supplement/derived/PAIRED_TRANSITIONS.csv')
fig,axes=plt.subplots(1,2,figsize=(7.1,3),layout='constrained')
for ax,seed in zip(axes,('1729','2026')):
    z=[[int(next(r['n'] for r in rr if r['dataset']=='equal64+64' and r['model']=='H4' and r['seed']==seed and r['transition']==tr and r['f1_direction']==s)) for s in ('gain','same','harm')] for tr in ('00','01','10','11')]
    ax.imshow(z,cmap='Blues',vmin=0,vmax=65,aspect='auto')
    for y,row in enumerate(z):
        for x,n in enumerate(row):ax.text(x,y,str(n),ha='center',va='center',color='white' if n>35 else 'black',fontsize=12)
    ax.set_xticks(range(3),['F1 increases','Unchanged','F1 decreases']);ax.set_yticks(range(4),['0 → 0','0 → 1','1 → 0','1 → 1'])
    ax.set_ylabel('Annotated full support: static → aligned');ax.set_title(f'H4, seed {seed} · N = 128')
save(fig,'joint_transitions')
rr=read(H/'supplement/derived/SELECTED_SCORE_BINS.csv')
fig,axes=plt.subplots(1,2,figsize=(7.1,3),layout='constrained')
for ax,ds,title in zip(axes,('hotpot','musique'),('HotpotQA · 196 queries','MuSiQue · 542 queries')):
    rows=[r for r in rr if r['dataset']==ds and r['model']=='H4']
    ax.plot([0,1],[0,1],ls=':',color='.5',label='Identity reference')
    present=[r for r in rows if int(r['n'])]
    ax.scatter([float(r['mean_sigmoid']) for r in present],[float(r['annotated_full_rate']) for r in present],marker='o',s=48,color='#0072B2',label='Selected H4 sets')
    for r in present:
        x=float(r['mean_sigmoid']);y=float(r['annotated_full_rate'])
        ax.annotate('n='+r['n'],(x,y),xytext=(-7,8),textcoords='offset points',ha='right',fontsize=8)
    empty=', '.join(f"[{float(r['bin_left']):.1f},{float(r['bin_right']):.1f})" for r in rows if not int(r['n'])) or 'none'
    ax.set_title(title);ax.set_xlim(-.02,1.03);ax.set_ylim(-.06,1.14);ax.set_xlabel('Mean sigmoid of saved selection logit');ax.set_ylabel('Annotated full-support rate')
    ax.text(.02,-.31,'Empty bins (n=0): '+empty,transform=ax.transAxes,fontsize=7)
axes[0].legend(loc='center left',fontsize=7,frameon=False)
save(fig,'selected_scores')
rr=read(H/'supplement/index_cost_refined64.csv')
fig,axes=plt.subplots(1,2,figsize=(7.1,2.65),layout='constrained')
for ax,ds,title in zip(axes,('hotpot','musique'),('HotpotQA · fixed 32 queries','MuSiQue · fixed 32 queries')):
    for y,m,col in zip(range(3),('Flat','GB','KM'),('#555555','#0072B2','#D55E00')):
        r=next(r for r in rr if r['tag']==ds and r['method']==m)
        ax.scatter(float(r['total_seconds']),y,color=col,marker='o',s=42)
        ax.scatter(float(r['median_seconds']),y,color=col,marker='|',s=140)
    ax.set_yticks(range(3),['Flat','Granular-ball index','K-means index']);ax.invert_yaxis();ax.set_xlim(0,.75);ax.set_title(title);ax.set_xlabel('Measured selector time (seconds)');ax.grid(axis='x',alpha=.2)
axes[0].scatter([],[],marker='o',color='black',label='Mean');axes[0].scatter([],[],marker='|',color='black',label='Median');axes[0].legend(frameon=False,fontsize=8,loc='lower right')
save(fig,'index_cost')
(H/'analysis/PLOT_BUILD.json').write_text(json.dumps({'cpu_seconds':time.process_time()-cpu,'figures':3,'new_measurements':False},indent=2),encoding='utf-8')
