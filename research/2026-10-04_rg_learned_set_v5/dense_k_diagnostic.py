"""Separate the six-block restriction from H4 proxy-score selection losses."""
from common import *
from dataset import Store,greedy,coverage
from evaluate import load_models,scorer
import numpy as np


def main():
    cpu=time.process_time();wall=time.perf_counter();store=Store();net=load_models(1729)['H4']
    prior={r['query_id']:r for r in rows(LOCAL/'selections_1729_main.jsonl') if r['method']=='H4-Flat'};out=[]
    for q in store.queries:
        if q['role']!='TUNE':continue
        c=store.case(q);S=greedy(c['ctx'],range(len(c['blocks'])),6);ids=[c['blocks'][i]['id'] for i in S]
        cov,full=coverage(store.targets[q['query_id']],ids);old=prior[q['query_id']];s,_=scorer(net,c);dense_score=s.score(S)
        out.append(dict(tag=q['tag'],dense_k6_coverage=cov,dense_k6_complete=full,h4_coverage=old['coverage'],h4_complete=old['complete'],dense_k6_blocks=len(S),dense_k6_tokens=c['ctx'].tokens(S),h4_proxy_minus_dense_k6=old['score']-dense_score,lost_full_support=full==1 and old['complete']==0,gained_full_support=full==0 and old['complete']==1))
        budget(0,time.process_time()-cpu)
    summary=[]
    for tag in ('hotpot','musique'):
        rr=[r for r in out if r['tag']==tag]
        summary.append(dict(tag=tag,queries=len(rr),**{f:float(np.mean([r[f] for r in rr])) for f in rr[0] if f not in ('tag','lost_full_support','gained_full_support')},lost_full_support=sum(r['lost_full_support'] for r in rr),gained_full_support=sum(r['gained_full_support'] for r in rr),h4_proxy_below_dense_k6=sum(r['h4_proxy_minus_dense_k6'] < -1e-8 for r in rr),scope='DESCRIPTIVE_K6_BASELINE_NO_NEW_QA'))
    table(HERE/'DENSE_K6_DIAGNOSTIC.csv',summary);charge('dense_k6_diagnostic',cpu,wall,gpu_process_seconds=0)


if __name__=='__main__':main()
