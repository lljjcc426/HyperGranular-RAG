"""Descriptive context and cost tables; no model or new statistical test."""
from common import *
import statistics
def run():
    contexts=read(LOCAL/'contexts.json');out=[]
    for name in ('D','A_G','L_G','R','A_F','L_F','A_K','L_K'):
        rs=[r for r in contexts if r['context']==name];ts=[r['body_tokens'] for r in rs]
        active=[r for r in rs if not r['fallback']];gaps=[r['budget_gap'] for r in active if 'budget_gap' in r]
        out.append(dict(context=name,n=len(rs),fallback=sum(r['fallback'] for r in rs),package=sum(r['status']=='AUTOMATIC_PACKAGE' for r in rs),
            body_min=min(ts),body_median=statistics.median(ts),body_max=max(ts),body_mean=statistics.mean(ts),
            active_n=len(active),active_body_mean=statistics.mean(r['body_tokens'] for r in active),
            budget_gap_mean=statistics.mean(gaps) if gaps else '',budget_gap_max=max(gaps) if gaps else '',
            reference_complete=sum(r.get('reference_complete',False) for r in rs),reference_outside_top64=sum(r.get('reference_outside_top64',False) for r in rs),
            reference_capped=sum(r['status']=='REFERENCE_CAPPED' for r in rs),shared_cap=sum(r['shared_cap_adjustment'] for r in rs)))
    table(HERE/'CONTEXT_SUMMARY.csv',out)
    s=list(csv.DictReader((HERE/'SUMMARY.csv').open(encoding='utf-8')));cost=[]
    for r in s:
        if r['protocol']!='P2' or r['dataset']!='EQUAL_WEIGHT_16':continue
        reader=float(r['logical_reader_seconds']);search=float(r['historical_search_model_seconds'])
        cost.append(dict(context=r['context'],n=16,protocol='P2',logical_reader_seconds=reader,historical_search_model_seconds=search,
            accounted_model_seconds=reader+search,historical_search_calls=int(r['historical_search_calls']),
            annotation_cost='NOT_MEASURED' if r['context']=='R' else 'NOT_APPLICABLE',
            limitation='Model-time accounting, not measured end-to-end deployment latency. L uses A-derived length.'))
    table(HERE/'COST_COMPARISON.csv',cost)
    cm={(r['query_id'],r['context']):r for r in contexts}
    matches={name:sum(cm[c['query_id'],'A_G']['body']==cm[c['query_id'],name]['body'] for c in selected()) for name in ('A_F','A_K')}
    print(json.dumps(dict(contexts=out,body_identity_to_G=matches),ensure_ascii=False))
if __name__=='__main__':run()
