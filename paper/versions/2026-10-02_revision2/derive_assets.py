"""Figures from the completed canonical reanalysis; no experiments or resampling."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
OUT=HERE/'shared'
rows=list(csv.DictReader((HERE/'scoring/PAIRED_COMPARISONS.csv').open(encoding='utf-8')))
effects=json.loads((HERE.parent/'2026-10-02_dual_manuscripts/shared/effects.json').read_text())
mapping={'Hotpot':('4E','q25_minus_dense'),'Musique':('4F','q25_minus_dense'),'Gemma':('4G','q25_minus_dense'),
 'Joint':('4H','DENSE_TOP20'),'Facet':('4H','Q25_NO_FACET_HYPEREDGE'),'Protection':('4H','Q25_NO_PROTECTION'),
 'Strong':('4H','STRONG_DENSE_TOP20'),'Bm':('4H','BM25_TOP20'),'Hybrid':('4H','DENSE_BM25_HYBRID_TOP20')}
for prefix,stage in [('Sidecar','4I'),('Native','5A')]:
    for suffix,comparison in [('', 'protected_minus_bge'),('Facet','protected_minus_no_facet'),('Place','protected_minus_unprotected'),('Unprotected','unprotected_minus_bge')]:
        mapping[prefix+suffix]=(stage,comparison)
for e in effects:
    stage,comparison=mapping[e['key']]
    matches=[r for r in rows if r['stage']==stage and r['comparison']==comparison and r['metric']=='f1' and (stage in ('4E','4F') or r['dataset']=='equal_weight')]
    assert len(matches)==1
    row=matches[0]
    for field,col in [('point','delta'),('lower','lower'),('upper','upper')]:
        value=float(row['canonical_'+col]);assert abs(value-e[field])<1e-12;e[field]=value
    e['historical_source']=e.pop('source')
    e['source']='scoring/PAIRED_COMPARISONS.csv';e['stage']=stage;e['comparison']=comparison;e['scorer']='dataset-canonical'
(OUT/'effects.json').write_text(json.dumps(effects,indent=2)+'\n',encoding='utf-8')
macros=[]
for e in effects:
    macros.extend([rf'\newcommand{{\eff{e["key"]}}}{{{e["point"]:+.5f}}}',rf'\newcommand{{\ci{e["key"]}}}{{[{e["lower"]:.5f},\,{e["upper"]:.5f}]}}'])
(OUT/'numbers.tex').write_text('\n'.join(macros)+'\n',encoding='utf-8')
bykey={e['key']:e for e in effects}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'axes.linewidth':.7})
def forest(keys,name,size):
    fig,ax=plt.subplots(figsize=size)
    for y,k in enumerate(keys):
        e=bykey[k];color='#0072B2' if e['lower']>0 else '#D55E00' if e['upper']<0 else '#656B73'
        ax.plot([100*e['lower'],100*e['upper']],[y,y],color=color,lw=1.7)
        ax.plot(100*e['point'],y,'o',color=color,mfc=color if e['lower']>0 or e['upper']<0 else 'white',ms=5)
        ax.text(3,y,f"{100*e['point']:+.2f} [{100*e['lower']:.2f}, {100*e['upper']:.2f}]",va='center',fontsize=8)
    ax.axvline(0,color='#444444',lw=.7,ls='--');ax.invert_yaxis()
    ax.set_yticks(range(len(keys)),[bykey[k]['label'] for k in keys])
    ax.set_xlim(-6,7.4);ax.set_xticks([-6,-4,-2,0,2])
    ax.set_xlabel('Canonical answer F1 difference (pp); reconstructed 95% percentile interval',loc='left',fontsize=8)
    ax.grid(axis='x',alpha=.16);ax.tick_params(axis='y',length=0)
    fig.tight_layout();fig.savefig(OUT/name,bbox_inches='tight');plt.close(fig)
forest(['Hotpot','Musique','Joint','Strong','Sidecar','Native','Gemma'],'effects.pdf',(8,3.55))
forest(['Facet','Protection','SidecarFacet','SidecarPlace','NativeFacet','NativePlace'],'components.pdf',(8,3.2))
print('17 canonical effect rows matched; two forests and shared number macros written.')
