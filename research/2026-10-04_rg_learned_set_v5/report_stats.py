"""Descriptive aggregates of completed v5 rows; no scoring or model calls."""
from common import *
import numpy as np


def main():
    selected=[r for p in LOCAL.glob('selections_*.jsonl') for r in rows(p)]
    qa=rows(LOCAL/'qa.jsonl') if (LOCAL/'qa.jsonl').exists() else []
    out=[]
    for source,data in (('selection',selected),('qa',qa)):
        keys=sorted({(r['seed'],r['setting'],r['budget'],r['method'],r['tag']) for r in data})
        for key in keys:
            rr=[r for r in data if (r['seed'],r['setting'],r['budget'],r['method'],r['tag'])==key]
            groups=[('ALL',rr),('TOP128_COMPLETE',[r for r in rr if r['reachable_full']]),('TOP128_INCOMPLETE',[r for r in rr if not r['reachable_full']])]
            groups += [(s,[r for r in rr if r['stratum']==s]) for s in sorted({r['stratum'] for r in rr})]
            for name,ss in groups:
                if not ss:continue
                fields=('coverage','complete','blocks','tokens','score') if source=='selection' else ('coverage','complete','em','f1','blocks','tokens')
                out.append(dict(source=source,**dict(zip(('seed','setting','budget','method','tag'),key)),subgroup=name,queries=len(ss),**{f:float(np.mean([r[f] for r in ss if r.get(f) is not None])) if any(r.get(f) is not None for r in ss) else None for f in fields}))
    table(HERE/'STRATIFIED_RESULTS.csv',out)
    out=[]
    learned=[r for r in selected if r.get('score') is not None]
    for key in sorted({(r['seed'],r['setting'],r['budget'],r['method'],r['tag']) for r in learned}):
        rr=[r for r in learned if (r['seed'],r['setting'],r['budget'],r['method'],r['tag'])==key]
        logits=np.array([r['score'] for r in rr]);probs=np.exp(-np.logaddexp(0,-logits));targets=np.array([r['complete'] for r in rr])
        out.append(dict(zip(('seed','setting','budget','method','tag'),key),queries=len(rr),mean_predicted_full=float(probs.mean()),observed_annotation_full=float(targets.mean()),brier=float(np.mean((probs-targets)**2)),scope='SELECTED_SETS_DEVELOPMENT_DESCRIPTIVE'))
    table(HERE/'CALIBRATION_ON_SELECTED.csv',out)
    rep=[]
    for tag in ('hotpot','musique'):
        rr=[r for r in selected if r['seed']==1729 and r['setting']=='opened' and r['budget']==1024 and r['tag']==tag]
        by={(r['query_id'],r['method']):r for r in rr}
        ids=sorted({r['query_id'] for r in rr if r['method']=='H4-Representative'} & {r['query_id'] for r in rr if r['method']=='H4-Flat'})
        if not ids:continue
        pairs=[(by[q,'H4-Representative'],by[q,'H4-Flat']) for q in ids]
        rep.append(dict(tag=tag,queries=len(ids),same_selected_set=sum(a['selected']==b['selected'] for a,b in pairs),**{'representative_minus_flat_'+f:float(np.mean([a[f]-b[f] for a,b in pairs])) for f in ('score','coverage','complete','blocks','tokens')},evidence='APPROXIMATION_DIAGNOSTIC_NO_QA'))
    table(HERE/'REPRESENTATIVE_DIAGNOSTIC.csv',rep)
    batches=rows(LOCAL/'selection_cost_batches.jsonl') if (LOCAL/'selection_cost_batches.jsonl').exists() else []
    costs=[r for b in batches for r in b['rows']];out=[]
    for key in sorted({(r['seed'],r['mode'],r['budget'],r['method'],r['tag']) for r in costs}):
        rr=[r for r in costs if (r['seed'],r['mode'],r['budget'],r['method'],r['tag'])==key]
        values=np.array([r['total_seconds'] for r in rr])
        out.append(dict(zip(('seed','mode','budget','method','tag'),key),queries=len(rr),median_seconds=float(np.median(values)),p95_seconds=float(np.quantile(values,.95)),token_fraction_of_total=sum(r.get('token_seconds',0) for r in rr)/sum(values)))
    table(HERE/'SEARCH_DISTRIBUTIONS.csv',out)
    primary_cost={(r['query_hash'],r['method']):r for r in costs if r['seed']==1729 and r['mode']=='main' and r['budget']==1024}
    out=[]
    for tag in ('hotpot','musique'):
        for method in sorted({r['method'] for r in qa}):
            rr=[r for r in qa if r['seed']==1729 and r['setting']=='opened' and r['budget']==1024 and r['tag']==tag and r['method']==method]
            if not rr:continue
            cc=[primary_cost[digest(r['query_id']),method] for r in rr]
            selection=float(np.mean([r['total_seconds'] for r in cc]));generation=float(np.mean([r['reader_seconds'] for r in rr]))
            out.append(dict(tag=tag,method=method,queries=len(rr),f1=float(np.mean([r['f1'] for r in rr])),selection_seconds=selection,observed_prompt_generation_seconds=generation,component_sum_seconds=selection+generation,scope='MATCHED_PRIMARY128_COMPONENT_SUM_NOT_INDEPENDENT_END_TO_END_RERUN; SHARED_ENCODING_RETRIEVAL_SEPARATE'))
    table(HERE/'QUALITY_COST_MAIN128.csv',out)
    out=[]
    for key in sorted({(r['seed'],r['setting'],r['budget'],r['method'],r['tag']) for r in qa}):
        rr=[r for r in qa if (r['seed'],r['setting'],r['budget'],r['method'],r['tag'])==key]
        out.append(dict(zip(('seed','setting','budget','method','tag'),key),queries=len(rr),protocol_failure=sum(r['status']!='VALID_ANSWER_FIELD' for r in rr),unknown=sum(r['unknown'] for r in rr),zero_f1=sum(r['f1']==0 for r in rr),exact_with_incomplete_known_support=sum(r['em']==1 and not r['complete'] for r in rr),nonexact_with_complete_known_support=sum(r['em']<1 and bool(r['complete']) for r in rr)))
    table(HERE/'QA_ERROR_SUMMARY.csv',out)
    # The main table has128 queries, sensitivity/closed64. Compare only the
    # same fixed64 here; never attribute a change of query composition to budget.
    matched=[r for r in qa if r['seed']==1729 and r['sensitivity'] and r['method'] not in ('H4-GB','H4-KM')]
    out=[]
    for key in sorted({(r['setting'],r['budget'],r['method'],r['tag']) for r in matched}):
        rr=[r for r in matched if (r['setting'],r['budget'],r['method'],r['tag'])==key]
        out.append(dict(zip(('setting','budget','method','tag'),key),queries=len(rr),**{f:float(np.mean([r[f] for r in rr])) for f in ('em','f1','coverage','complete','blocks','tokens')},scope='FIXED_HASH64_MATCHED_PANEL'))
    table(HERE/'MATCHED64_QA.csv',out)
    primary=[r for r in qa if r['setting']=='opened' and r['budget']==1024 and r['method'] not in ('H4-GB','H4-KM')]
    out=[]
    for method in sorted({r['method'] for r in primary}):
        for tag in ('hotpot','musique','equal_weight_datasets'):
            vals=[]
            for seed in sorted({r['seed'] for r in primary}):
                rr=[r for r in primary if r['method']==method and r['seed']==seed and (tag=='equal_weight_datasets' or r['tag']==tag)]
                if len(rr)!=(128 if tag=='equal_weight_datasets' else 64):continue
                vals.append(float(np.mean([r['f1'] for r in rr])))
            if vals:out.append(dict(method=method,tag=tag,seeds=len(vals),mean_f1=float(np.mean(vals)),seed_sd=float(np.std(vals,ddof=1)) if len(vals)>1 else None,min_f1=min(vals),max_f1=max(vals),scope='SAME_FIXED_PANEL_TRAINING_SEED_VARIATION_NOT_CI'))
    table(HERE/'QA_SEED_STABILITY.csv',out)


if __name__=='__main__':main()
