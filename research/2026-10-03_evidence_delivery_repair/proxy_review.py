"""Align proxy and answer references; append-only correction, no algorithm rerun."""
from common import *
from repair import Context
from collections import Counter

def main():
    cpu=time.process_time();wall=time.perf_counter()
    rm={(r['query_id'],r['method']):r for r in rows(HERE/'pilot_rankings.jsonl')}
    qs={(r['query_id'],r['method']):r for r in rows(LOCAL/'query_scores.jsonl')}
    counts={};records=[]
    for tag in CONFIGS:
        cfg,p,units,queries,x,q,spans,_=dataset(tag,verify=False)
        cc={f'{family}_{l:.2f}':Counter() for family in ('R1','R2') for l in (.85,.70)}
        for j,query in enumerate(queries):
            qid=query['query_id']
            if (qid,'H0') not in rm:continue
            a,b=spans[qid];c=Context(query,units[a:b],x[a:b],q[j]);imap={u:i for i,u in enumerate(c.ids)}
            for l in (.85,.70):
                for family,base in [('R1','H0'),('R2',f'R1_{l:.2f}')]:
                    m=f'{family}_{l:.2f}';target=rm[qid,m];ref=rm[qid,base]
                    ph=c.phi([imap[u] for u in target['ranking']],l)-c.phi([imap[u] for u in ref['ranking']],l)
                    fd=qs[qid,m]['f1']-qs[qid,base]['f1']
                    label=('proxy_gain' if ph>0 else 'proxy_harm' if ph<0 else 'proxy_same')+'|'+('answer_gain' if fd>0 else 'answer_harm' if fd<0 else 'answer_same')
                    cc[m][label]+=1;cc[m]['changed_ranking']+=target['ranking']!=ref['ranking']
                    cc[m]['changed_members']+=set(target['ranking'])!=set(ref['ranking'])
                    records.append({'query_id':qid,'tag':tag,'method':m,'reference':base,'proxy_delta':ph,'answer_f1_delta':fd})
        counts[tag]={m:dict(c) for m,c in cc.items()}
    with (LOCAL/'aligned_proxy_query_details.jsonl').open('x',encoding='utf-8') as h:
        for r in records:line(h,r)
    save(HERE/'PROXY_REFERENCE_CORRECTION.json',{'status':'ALIGNED_PROXY_AND_ANSWER_REFERENCES',
        'supersedes':'Only proxy_answer_cross_tabs in ANALYSIS_DETAILS.json; all answer scores/CIs unchanged',
        'reason':'R1 step deltas sum relative to Dense20; original cross table paired them with answer delta relative to H0. Recompute Phi(R1)-Phi(H0) from fixed rankings.',
        'counts':counts})
    charge('proxy_review',cpu,wall,gpu_process_seconds=0);print(json.dumps(counts))
if __name__=='__main__':main()
