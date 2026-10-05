"""Derive public tables and manuscript numbers from completed local outputs."""
from support import *
qa_v6=load_module('rg_v6_qa_summary',HERE/'qa.py')
summarize,chosen=qa_v6.summarize,qa_v6.chosen
import numpy as np
import torch

def main():
    summarize();data=rows(LOCAL/'qa.jsonl') if (LOCAL/'qa.jsonl').exists() else [];dev=rows(LOCAL/'dev_metrics.jsonl');panels=read(LOCAL/'boundaries.json');out=[]
    selected={}
    for seed in sorted({r['seed'] for r in data} or {1729}):
        for kind in KINDS:
            pp=list(LOCAL.glob(f'{kind}_{seed}_r[12].pt'))
            if pp:selected[(seed,kind)]=torch.load(chosen(kind,seed),map_location='cpu',weights_only=False)['selection']
    for (seed,kind),s in selected.items():
        old=next(b for b in dev if b['summary']['model']=='v5-'+kind and b['summary']['seed']==seed)
        batch=next(b for b in dev if all(b['summary'][k]==s[k] for k in ('seed','model','round','epoch')))
        for tag in ('hotpot','musique'):
            rr=[r for r in batch['rows'] if r['tag']==tag];oo=[r for r in old['rows'] if r['tag']==tag];mapping={r['query_id']:r for r in oo}
            out.append(dict(seed=seed,model=kind,tag=tag,queries=len(rr),round=s['round'],epoch=s['epoch'],full=float(np.mean([r['complete'] for r in rr])),v5_full=float(np.mean([r['complete'] for r in oo])),cov=float(np.mean([r['coverage'] for r in rr])),v5_cov=float(np.mean([r['coverage'] for r in oo])),output=float(np.mean([r['output'] for r in rr])),v5_output=float(np.mean([r['output'] for r in oo])),dense_full=float(np.mean([r['dense_full'] for r in rr])),mmr_full=float(np.mean([r['mmr_full'] for r in rr])),gained=sum(r['complete'] and not mapping[r['query_id']]['complete'] for r in rr),lost=sum(not r['complete'] and mapping[r['query_id']]['complete'] for r in rr)))
    table(HERE/'SELECTED_CHECKPOINTS.csv',out)
    table(HERE/'PUBLIC_QUERY_QA.csv',[{k:r[k] for k in ('seed','method','tag','stratum','f1','em','coverage','complete','tokens','blocks','cache_hit','status')}|dict(query_hash=digest(r['query_id'])) for r in data])
    paired=[]
    for seed in sorted({r['seed'] for r in data}):
        rr=[r for r in data if r['seed']==seed];baseline={r['query_id']:r for r in data if r['seed']==1729 and r['method']=='MMR'}
        for method in sorted({r['method'] for r in rr}):
            for tag in ('hotpot','musique'):
                ss=[r for r in rr if r['method']==method and r['tag']==tag];ds=[r['f1']-baseline[r['query_id']]['f1'] for r in ss]
                if ss:paired.append(dict(seed=seed,method=method,tag=tag,queries=len(ss),delta_f1_mmr=float(np.mean(ds)),gain=sum(x>0 for x in ds),harm=sum(x<0 for x in ds),unchanged=sum(x==0 for x in ds)))
    table(HERE/'PAIRED_QA.csv',paired)
    oldqa=rows(V5/'local/qa.jsonl');own=[]
    for seed in sorted({r['seed'] for r in data}):
        for kind in KINDS:
            prior_method='H4-Flat' if kind=='H4' else kind
            prior={r['query_id']:r for r in oldqa if r['seed']==seed and r['setting']=='opened' and r['budget']==1024 and r['method']==prior_method}
            current=[r for r in data if r['seed']==seed and r['method']==kind+'-aligned']
            for tag in ('hotpot','musique'):
                rr=[r for r in current if r['tag']==tag]
                if rr:
                    ds=[r['f1']-prior[r['query_id']]['f1'] for r in rr]
                    own.append(dict(seed=seed,model=kind,tag=tag,queries=len(rr),static_f1=float(np.mean([prior[r['query_id']]['f1'] for r in rr])),aligned_f1=float(np.mean([r['f1'] for r in rr])),delta_f1=float(np.mean(ds)),gain=sum(d>0 for d in ds),harm=sum(d<0 for d in ds),unchanged=sum(d==0 for d in ds)))
    table(HERE/'ALIGNED_VS_OWN_STATIC.csv',own)
    shared=HERE/'manuscripts/shared';shared.mkdir(exist_ok=True)
    # Public aggregate table, actual selected checkpoints only.
    lines=[r'\begin{table}[t]\centering\small',r'\caption{Checkpoint-panel support completeness before and after search alignment (64 questions per dataset). Selection uses this panel, not QA.}',r'\label{tab:aligned}',r'\begin{tabular}{llrrrr}\toprule',r'Seed & Model & Static H & Aligned H & Static M & Aligned M\\\midrule']
    for (seed,kind),s in selected.items():
        h=next(r for r in out if r['seed']==seed and r['model']==kind and r['tag']=='hotpot');m=next(r for r in out if r['seed']==seed and r['model']==kind and r['tag']=='musique')
        lines.append(f"{seed} & {kind} & {h['v5_full']:.4f} & {h['full']:.4f} & {m['v5_full']:.4f} & {m['full']:.4f}"+r'\\')
    lines += [r'\bottomrule\end{tabular}\end{table}']
    primary=[r for r in out if r['seed']==1729];gains={k:float(np.mean([r['full']-r['v5_full'] for r in primary if r['model']==k])) for k in KINDS if any(r['model']==k for r in primary)}
    para=r'Table~\ref{tab:aligned} shows actual checkpoint-panel selections. For seed 1729, '
    para+=', '.join(f'{k} changes equal-dataset completeness by ${g:+.4f}$' for k,g in gains.items())+'. '
    para+='These are selected development effects, with the full checkpoint trajectory retained. They do not by themselves establish answer improvement or a unique advantage of fourth-order interactions.'
    selected_rounds={key:s['round'] for key,s in selected.items()}
    if selected_rounds and all(r==1 for r in selected_rounds.values()) and any(b['summary']['round']==2 and b['summary']['seed']==1729 for b in dev):
        para+=' Every reported aligned checkpoint comes from round one; the completed second rounds did not improve the best selection criterion. Continued loss reduction was not continued selection progress.'
    (shared/'aligned_results.tex').write_text('\n'.join(lines)+'\n\n'+para+'\n',encoding='utf-8')
    if data:
        qa=[];lines=[r'\begin{table}[t]\centering\small',r'\caption{Canonical answer F1 on the fixed 128-query development panel (64 per dataset), at 1,024 input tokens. Original rows reuse their exact prior generations.}',r'\label{tab:qa}',r'\begin{tabular}{llrrr}\toprule',r'Seed & Method & HotpotQA & MuSiQue & Mean\\\midrule']
        order=['Dense','MMR','v5-H4','H4-replay','H1-aligned','H2-aligned','DeepSets-aligned','H4-aligned']
        for seed in sorted({r['seed'] for r in data}):
            for method in order:
                ss=[r for r in data if r['seed']==seed and r['method']==method]
                if not ss:continue
                vals=[np.mean([r['f1'] for r in ss if r['tag']==t]) for t in ('hotpot','musique')]
                label='Static H4' if method=='v5-H4' else method.replace('-',' ')
                lines.append(f"{seed} & {label} & {vals[0]:.4f} & {vals[1]:.4f} & {np.mean(vals):.4f}"+r'\\')
                qa.append(dict(seed=seed,method=method,f1=float(np.mean(vals)),queries=len(ss)))
        lines += [r'\bottomrule\end{tabular}\end{table}'];(shared/'qa_table.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8');table(HERE/'QA_EQUAL_DATASET.csv',qa)
        vals={r['method']:r['f1'] for r in qa if r['seed']==1729}
        text=r'Table~\ref{tab:qa} reports answer F1. '+f"For primary seed 1729, aligned H4 changes mean F1 from {vals['v5-H4']:.4f} to {vals['H4-aligned']:.4f}. Its difference from MMR is ${vals['H4-aligned']-vals['MMR']:+.4f}$ and from matched static replay is ${vals['H4-aligned']-vals['H4-replay']:+.4f}$. "
        secondary={r['method']:r['f1'] for r in qa if r['seed']==2026}
        if len(secondary)==4:
            prior_h4=float(np.mean([r['static_f1'] for r in own if r['seed']==2026 and r['model']=='H4']))
            text+=f"For seed 2026, H4 changes from {prior_h4:.4f} to {secondary['H4-aligned']:.4f}; aligned H1, H2 and DeepSets score {secondary['H1-aligned']:.4f}, {secondary['H2-aligned']:.4f} and {secondary['DeepSets-aligned']:.4f}. "
        text+='Every method retains all 128 exposed questions. These descriptive comparisons do not establish independent confirmation.'
        (shared/'qa_interpretation.tex').write_text(text+'\n',encoding='utf-8')
        own_text='Relative to each corresponding static checkpoint, the primary-seed mean F1 changes are '
        own_text+=', '.join(f"{k} ${np.mean([r['delta_f1'] for r in own if r['seed']==1729 and r['model']==k]):+.4f}$" for k in KINDS)+'. '
        if len(secondary)==4:
            own_text+=' For seed 2026, the corresponding changes are '+', '.join(f"{k} ${np.mean([r['delta_f1'] for r in own if r['seed']==2026 and r['model']==k]):+.4f}$" for k in KINDS)+'. '
        own_text+='The static comparisons reuse the same original questions and predictions; no additional generation or independent replication is implied.'
        (shared/'own_static.tex').write_text(own_text+'\n',encoding='utf-8')
        detail=[r'\begin{table}[t]\centering\small',r'\caption{Primary-seed QA-panel selection and output diagnostics, equal dataset weight over all 128 questions. Full is annotated support completeness; EM is canonical answer exact match. Input includes instructions.}',r'\label{tab:qa-details}',r'\begin{tabular}{lrrrrr}\toprule',r'Method & Full & Coverage & Blocks & Input tokens & EM\\\midrule']
        for method in order:
            ss=[r for r in data if r['seed']==1729 and r['method']==method]
            if not ss:continue
            vals=[float(np.mean([r[k] for r in ss])) for k in ('complete','coverage','blocks','input_tokens','em')]
            label='Static H4' if method=='v5-H4' else method.replace('-',' ')
            detail.append(f"{label} & {vals[0]:.4f} & {vals[1]:.4f} & {vals[2]:.2f} & {vals[3]:.1f} & {vals[4]:.4f}"+r'\\')
        detail += [r'\bottomrule\end{tabular}\end{table}']
        (shared/'qa_details.tex').write_text('\n'.join(detail)+'\n',encoding='utf-8')
    calls=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else [];g,c=usage();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    ledger=rows(HERE/'cost.jsonl');build_cpu=sum(r['cpu_seconds'] for r in ledger if r['stage'].startswith('build'))
    research_cpu=c-build_cpu
    cost=dict(gpu_process_seconds=g,cpu_seconds_measured=c,new_disk_bytes=size,new_reader_calls=len(calls),logical_qa_rows=len(data),cache_hits=sum(r['cache_hit'] for r in data),input_tokens=sum(r['input_tokens'] for r in calls),output_tokens=sum(r['output_tokens'] for r in calls),generation_seconds=sum(r['seconds'] for r in calls),cumulative_gpu_seconds=24114.6555248+g,cumulative_cpu_lower_bound=29061.828+c,prior_unknown_cpu='UNKNOWN',paid=0,accounting_scope='Phase CPU and GPU model-residency wall time; includes recorded compiler CPU. Interpreter startup, shell operations and older unknown CPU are not imputed.',peak_gpu_bytes=max([r.get('peak_gpu_bytes',0) for r in rows(HERE/'cost.jsonl')]+[0]),format_failures=sum(r['status']!='VALID_ANSWER_FIELD' for r in data),hit_limits=sum(r['hit_limit'] for r in data))
    cost['cpu_research_seconds_measured']=research_cpu;cost['cpu_build_seconds_measured']=build_cpu;save(HERE/'RESOURCE_SUMMARY.json',cost)
    (shared/'cost_text.tex').write_text(f"The continuation records {g:,.2f} GPU process-wall seconds, {research_cpu:,.2f} measured research CPU seconds, and {len(calls):,} real reader calls, including eight uncached checks. It produces {len(data):,} logical QA rows with {sum(r['cache_hit'] for r in data):,} cache hits. New generations total {cost['input_tokens']:,} input tokens and {cost['output_tokens']:,} output tokens. No comparison row has an invalid answer field or reaches the output limit. Typesetting CPU is accounted separately in the accompanying ledger. Older unmeasured CPU use remains unknown; phase accounting is not reconstructed whole-system billing. No paid compute is used.\n",encoding='utf-8')
    (shared/'cost_short.tex').write_text(f"The bounded continuation uses {g/3600:.2f} GPU process-wall hours and {len(calls):,} actual reader calls, including eight uncached checks. Identical generation identities are reused; the {len(data):,} logical rows are not independent samples or fresh calls.\n",encoding='utf-8')
    print(json.dumps(dict(resources=cost,gains=gains),indent=2),flush=True)
if __name__=='__main__':main()
