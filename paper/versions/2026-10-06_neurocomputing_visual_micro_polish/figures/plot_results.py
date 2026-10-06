"""Redraw the three existing results; no new scores, intervals or distributions."""
import csv, json, math, shutil, time
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

H=Path(__file__).resolve().parents[1]
cpu=time.process_time()
def read(name):
    with (H/'plot_data'/Path(name).name).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))
plt.rcParams.update({'font.family':'Arial','font.size':9,'axes.titlesize':10,
    'axes.labelsize':9,'xtick.labelsize':8.5,'ytick.labelsize':8.5,
    'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,
    'axes.spines.right':False,'axes.linewidth':.7,'savefig.dpi':300})
trace={}
def save(fig,name):
    fig.savefig(H/'figures'/f'{name}.pdf')
    fig.savefig(H/'figures'/f'{name}.png',dpi=200)
    shutil.copyfile(H/'figures'/f'{name}.pdf',H/'manuscript'/f'{name}.pdf')
    plt.close(fig)

bins=read('derived/SELECTED_SCORE_BINS.csv')
fig,axes=plt.subplots(1,2,figsize=(4.77,2.6),sharey=True)
fig.subplots_adjust(left=.14,right=.98,bottom=.21,top=.86,wspace=.22)
trace['selected_scores']=[r for r in bins if r['model']=='H4']
for ax,ds,title,marker,color in zip(axes,('hotpot','musique'),('HotpotQA (n=196)','MuSiQue (n=542)'),('o','s'),('#0072B2','#B36B00')):
    rows=[r for r in bins if r['model']=='H4' and r['dataset']==ds]
    ax.plot([0,1],[0,1],ls=':',lw=.8,color='.55')
    for r in rows:
        n=int(r['n'])
        if not n:continue
        x=float(r['mean_sigmoid']);y=float(r['annotated_full_rate'])
        ax.scatter(x,y,s=12+1.8*math.sqrt(n),marker=marker,color=color,zorder=3)
        dx,dy,ha=(-5,7,'right') if x>.8 else (0,7,'center')
        if y>.9:dx,dy,ha=0,-17,'center'
        ax.annotate(f'n={n}',(x,y),xytext=(dx,dy),textcoords='offset points',ha=ha,fontsize=8.5,
                    bbox=dict(facecolor='white',edgecolor='none',pad=.5,alpha=.9))
    ax.set(xlim=(-.025,1.035),ylim=(-.055,1.08),title=title)
    ax.set_xticks([0,.5,1]);ax.set_yticks([0,.25,.5,.75,1])
axes[0].set_ylabel('Observed support completeness')
fig.text(.56,.04,'Mean sigmoid score',ha='center',fontsize=9)
save(fig,'selected_scores')

rr=read('derived/PAIRED_TRANSITIONS.csv')
fig,axes=plt.subplots(1,2,figsize=(4.77,3.2),sharey=True)
fig.subplots_adjust(left=.30,right=.985,bottom=.33,top=.86,wspace=.17)
norm=Normalize(0,60);cmap=plt.get_cmap('Blues')
trace['joint_transitions']={}
for ax,seed in zip(axes,('1729','2026')):
    z=[[int(next(r['n'] for r in rr if r['dataset']=='equal64+64' and r['model']=='H4' and r['seed']==seed and r['transition']==tr and r['f1_direction']==direction)) for direction in ('gain','same','harm')] for tr in ('00','01','10','11')]
    assert sum(map(sum,z))==128
    trace['joint_transitions'][seed]=z
    ax.imshow(z,cmap=cmap,norm=norm,aspect='auto')
    for y,row in enumerate(z):
        for x,n in enumerate(row):
            ax.text(x,y,str(n),ha='center',va='center',color='white' if n>=35 else '#111111',fontsize=10)
    ax.set_xticks(range(3),['Increase','Same','Decrease'])
    ax.set_yticks(range(4),['Incomplete →\nIncomplete','Incomplete →\nComplete','Complete →\nIncomplete','Complete →\nComplete'])
    ax.tick_params(length=0,pad=5)
    ax.set_title(f'Seed {seed} | N=128')
    ax.set_xlabel('Answer F1 change',labelpad=7)
    ax.set_xticks([-.5,.5,1.5,2.5],minor=True)
    ax.set_yticks([-.5,.5,1.5,2.5,3.5],minor=True)
    ax.grid(which='minor',color='white',linewidth=1.3)
    ax.tick_params(which='minor',length=0)
axes[0].set_ylabel('Support status (static → aligned)',labelpad=9)
cax=fig.add_axes([.44,.13,.35,.025])
cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal',ticks=[0,20,40,60])
cb.set_label('Paired question count',labelpad=2,fontsize=8.5)
save(fig,'joint_transitions')

rr=read('index_cost_refined64.csv')
trace['index_cost']=[{k:r[k] for k in ('tag','method','queries','total_seconds')} for r in rr]
fig,axes=plt.subplots(1,2,figsize=(4.77,2.35),sharex=True,sharey=True)
fig.subplots_adjust(left=.24,right=.985,bottom=.22,top=.83,wspace=.17)
for ax,ds,title in zip(axes,('hotpot','musique'),('HotpotQA (n=32)','MuSiQue (n=32)')):
    for y,m,color,marker in zip(range(3),('Flat','GB','KM'),('#444444','#0072B2','#B36B00'),('o','s','^')):
        r=next(r for r in rr if r['tag']==ds and r['method']==m)
        x=float(r['total_seconds'])
        ax.scatter(x,y,s=38,color=color,marker=marker,zorder=3)
        ax.annotate(f'{x:.4f}',(x,y),xytext=(0,9),textcoords='offset points',ha='center',fontsize=8.5)
    ax.set_yticks(range(3),['Flat','Granular-ball','K-means'])
    ax.set_ylim(2.45,-.65);ax.set_xlim(0,.76);ax.set_xticks([0,.2,.4,.6])
    ax.set_title(title);ax.grid(axis='x',color='.88',lw=.6)
    ax.tick_params(axis='y',length=0)
fig.text(.61,.025,'Mean selection time (seconds / question)',ha='center',fontsize=9)
save(fig,'index_cost')
(H/'analysis/PLOT_DATA.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
(H/'analysis/PLOT_BUILD.json').write_text(json.dumps({'figures':3,'cpu_seconds':time.process_time()-cpu,'new_measurements':False,'new_intervals':False},indent=2),encoding='utf-8')
