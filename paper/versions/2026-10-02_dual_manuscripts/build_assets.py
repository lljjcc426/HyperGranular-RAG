"""Derive manuscript-only assets from existing aggregate JSON and figure CSVs.

No evaluator, bootstrap, raw dataset, prediction, model, or experiment is run.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / 'shared'
OUT.mkdir(exist_ok=True)
CSV = REPO / 'paper/figures_stage5r/source_data'
FILES = {
 'E': 'stage4e_e2e_official_train1000_v1_evaluation_summary.json',
 'F': 'stage4f_xdr_musique_train3000_v1_evaluation_summary.json',
 'G': 'stage4g_gtr_gemma_hotpot1000_musique3000_v1_equal_weight_summary.json',
 'H': 'stage4h_cbe_hotpot1000_musique1500_v1_equal_weight_summary.json',
 'I': 'stage4i_sdc_hotpot1000_musique1500_v1_equal_weight_summary.json',
 'A': 'stage5a_bnh_confirmation_equal_weight_summary.json',
}
data = {k: json.loads((REPO/'results'/v).read_text(encoding='utf-8')) for k,v in FILES.items()}
effects=[]
def add(key,label,family,stage,value):
    effects.append(dict(key=key,label=label,family=family,source='results/'+FILES[stage],
        point=value['point'],lower=value.get('lower_95',value.get('ci95_lower')),
        upper=value.get('upper_95',value.get('ci95_upper'))))
add('Hotpot','Compact / HotpotQA','compact','E',data['E']['bootstrap']['delta_answer_f1'])
add('Musique','Compact / MuSiQue','compact','F',data['F']['bootstrap']['delta_answer_f1'])
add('Gemma','Generator transfer / Gemma','transfer','G',data['G']['bootstrap']['delta_answer_f1'])
for key,label,field in [
 ('Joint','Compact / joint','DENSE_TOP20'),
 ('Facet','Compact / Full - NoFacet','NO_FACET'),
 ('Protection','Compact / Full - NoProtection','NO_PROTECTION'),
 ('Strong','Original Full - BGE','STRONG_DENSE_TOP20'),
 ('Bm','Original Full - BM25','BM25_TOP20'),
 ('Hybrid','Original Full - hybrid','HYBRID_TOP20')]:
    # Historical arm names are located exactly; no approximate numerical match.
    candidates=[k for k,v in data['H']['comparisons'].items() if k==field or (field in ('NO_FACET','NO_PROTECTION') and field in k) or (field=='HYBRID_TOP20' and 'HYBRID' in k)]
    if len(candidates)!=1: raise ValueError((field,list(data['H']['comparisons'])))
    add(key,label,'component' if key in ('Facet','Protection') else 'backbone','H',data['H']['comparisons'][candidates[0]]['dataset_equal_weight']['delta_answer_f1'])
for stage,prefix,family in [('I','Sidecar','sidecar'),('A','Native','native')]:
    for suffix,field,lab in [('','protected_minus_bge','Protected - BGE'),('Facet','protected_minus_no_facet','Protected - NoFacet'),('Place','protected_minus_unprotected','Protected - Unprotected'),('Unprotected','unprotected_minus_bge','Unprotected - BGE')]:
        add(prefix+suffix,prefix+' / '+lab,family,stage,data[stage]['comparisons'][field]['dataset_equal_weight']['delta_answer_f1'])
bykey={e['key']:e for e in effects}
with (OUT/'effects.json').open('w',encoding='utf-8') as f: json.dump(effects,f,indent=2)
macros=[]
for e in effects:
    macros += [rf'\newcommand{{\eff{e["key"]}}}{{{e["point"]:+.5f}}}',rf'\newcommand{{\ci{e["key"]}}}{{[{e["lower"]:.5f},\,{e["upper"]:.5f}]}}']
(OUT/'numbers.tex').write_text('\n'.join(macros)+'\n',encoding='utf-8')
# Verify the pre-existing plotting CSV against the aggregate values being used.
old=list(csv.DictReader((CSV/'figure2_effect_size_forest.csv').open(encoding='utf-8-sig')))
for row in old:
    value=float(row['delta_answer_f1'])
    matches=[e for e in effects if abs(e['point']-value)<1e-14]
    assert len(matches)==1, row
    assert abs(matches[0]['lower']-float(row['ci95_lower']))<1e-14
    assert abs(matches[0]['upper']-float(row['ci95_upper']))<1e-14
record={'scope':'aggregate reuse only; no rescoring or resampling','effect_rows':len(effects),
        'existing_figure_effect_rows_matched':len(old),'sources':FILES,
        'old_manuscript_identity':[]}
for name in ['paper/latex/main.tex','paper/latex/main.pdf','paper/references/verified_references.bib']:
    raw=(REPO/name).read_bytes()
    record['old_manuscript_identity'].append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(OUT/'evidence_check.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
# Copy existing bibliography bytes into the version package; do not modify original.
shutil.copyfile(REPO/'paper/references/verified_references.bib',OUT/'references.bib')
shutil.copyfile(REPO/'paper/latex/acl_natbib.bst',OUT/'acl_natbib.bst')
shutil.copyfile(REPO/'paper/latex/vendor/acl.sty',OUT/'acl.sty')
for name in ['figure3c_evidence_displacement.csv','figure4c_insertion_distribution.csv','figure5_qualitative_cases.csv','table1_core.csv','table6_core.csv']:
    shutil.copyfile(CSV/name,OUT/name)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'axes.linewidth':0.7})
COL={'pos':'#0072B2','neg':'#D55E00','unc':'#656B73'}
def forest(keys,name,figsize):
    fig,ax=plt.subplots(figsize=figsize)
    for y,k in enumerate(keys):
        e=bykey[k]; color=COL['pos'] if e['lower']>0 else COL['neg'] if e['upper']<0 else COL['unc']
        ax.plot([100*e['lower'],100*e['upper']],[y,y],color=color,lw=1.7)
        ax.plot(100*e['point'],y,'o',color=color,mfc=color if e['lower']>0 or e['upper']<0 else 'white',ms=5)
        ax.text(3.0,y,f"{100*e['point']:+.2f} [{100*e['lower']:.2f}, {100*e['upper']:.2f}]",va='center',fontsize=8)
    ax.axvline(0,color='#444444',lw=.7,ls='--')
    ax.set_yticks(range(len(keys)),[bykey[k]['label'] for k in keys]); ax.invert_yaxis()
    ax.set_xlim(-6,7.4); ax.set_xticks([-6,-4,-2,0,2]); ax.set_xlabel('Answer F1 difference (percentage points); recorded 95% interval',loc='left',fontsize=8)
    ax.grid(axis='x',alpha=.16); ax.tick_params(axis='y',length=0)
    fig.tight_layout();fig.savefig(OUT/name,bbox_inches='tight');plt.close(fig)
forest(['Hotpot','Musique','Joint','Strong','Sidecar','Native','Gemma'],'effects.pdf',(8,3.55))
forest(['Facet','Protection','SidecarFacet','SidecarPlace','NativeFacet','NativePlace'],'components.pdf',(8,3.2))
dis=list(csv.DictReader((OUT/'figure3c_evidence_displacement.csv').open(encoding='utf-8-sig')))
fig,axs=plt.subplots(1,2,figsize=(8,2.9),gridspec_kw={'width_ratios':[1,1.12]})
labels=['Sidecar\nHotpotQA','Sidecar\nMuSiQue','Native\nHotpotQA','Native\nMuSiQue']
for i,r in enumerate(dis):
    axs[0].barh(i,float(r['added_gold_per_1000_queries']),color='#0072B2',height=.3,label='Added' if i==0 else None)
    axs[0].barh(i,-float(r['displaced_gold_per_1000_queries']),color='#D55E00',height=.3,label='Displaced' if i==0 else None)
axs[0].set_yticks(range(4),labels);axs[0].invert_yaxis();axs[0].axvline(0,color='black',lw=.6);axs[0].set_xlabel('Supporting-unit events / 1,000 queries',fontsize=8);axs[0].legend(frameon=False,fontsize=7,loc='lower left');axs[0].set_title('(a) Evidence turnover',loc='left',fontsize=10)
rows=list(csv.DictReader((OUT/'figure4c_insertion_distribution.csv').open(encoding='utf-8-sig')))
series=['Compact Full','Cross-space sidecar','BGE-native']
values=[[float(r['query_percent']) for r in rows if r['setting']==s and r['dataset']=='DATASET_EQUAL_WEIGHT'] for s in series]
im=axs[1].imshow(values,cmap='Blues',aspect='auto',vmin=0,vmax=85)
for i,row in enumerate(values):
    for j,v in enumerate(row):axs[1].text(j,i,f'{v:.1f}',ha='center',va='center',fontsize=8,color='white' if v>50 else '#14222D')
axs[1].set_yticks(range(3),['Compact','Sidecar','Native']);axs[1].set_xticks(range(5));axs[1].set_xlabel('Candidates placed per query');axs[1].set_title('(b) Query share (%)',loc='left',fontsize=10)
fig.tight_layout();fig.savefig(OUT/'mechanisms.pdf',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,2.6));ax.set_xlim(0,10);ax.set_ylim(0,3);ax.axis('off')
boxes=[(0,1.9,1.75,.78,'Closed candidates\n+ query', '#EEF2F5'),(2.1,1.9,1.85,.78,'Fixed encoder\nDense Top-20','#EEF2F5'),(4.3,1.9,2.5,.78,'Geometry-based balls\n+ seed-relative facets','#E7F2F8'),(7.15,1.9,2.8,.78,'Eligible candidate order\n(static scores; bounded)','#E7F2F8')]
for x,y,w,h,t,c in boxes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025',fc=c,ec='#62717C',lw=.8));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
for start,end in [(1.77,2.05),(3.97,4.25),(6.82,7.1)]:ax.annotate('',xy=(end,2.3),xytext=(start,2.3),arrowprops={'arrowstyle':'->','lw':1})
ax.text(.05,1.28,'Compact policy:',fontsize=9,fontweight='bold')
for x,w,t,c in [(1.75,2.4,'Dense ranks 1--10\nprotected','#C6DED1'),(4.2,1.75,'up to 4\ncandidates','#F6D79C'),(6,1.95,'Dense-order\nfill to K','$BAD')]:
    color=c if c!='$BAD' else '#D2E2EF'; ax.add_patch(FancyBboxPatch((x,.82),w,.65,boxstyle='round,pad=.025',fc=color,ec='white'));ax.text(x+w/2,1.14,t,ha='center',va='center',fontsize=9)
ax.annotate('',xy=(8.45,1.15),xytext=(8.02,1.15),arrowprops={'arrowstyle':'->'});ax.text(9.1,1.13,'Fixed prompt\n+ generator',ha='center',va='center',fontsize=9)
ax.text(5,.23,'K = min(20, candidate count)  |  Stable deduplication  |  4,096-token input cap',ha='center',fontsize=9)
fig.tight_layout();fig.savefig(OUT/'workflow.pdf',bbox_inches='tight');plt.close(fig)
print(json.dumps({'effects':len(effects),'csv_crosschecks':len(old),'output':str(OUT)}))
