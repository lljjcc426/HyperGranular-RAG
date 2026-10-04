"""Deterministic descriptive case selection after all outputs; no predictor write."""
from common import *
def run():
    qs=list(csv.DictReader((HERE/'FACTORIAL_RESULTS.csv').open(encoding='utf-8')))
    scores={(r['query_id'],r['context'],r['protocol']):float(r['f1']) for r in qs if r['status']=='COMPLETE'}
    sample=selected();reasons={}
    def add(q,reason):reasons.setdefault(q,[]).append(reason)
    for tag in ('hotpot','musique'):add(next(c['query_id'] for c in sample if c['tag']==tag),'first_v3_hash_'+tag)
    add('musique_ans_v1_0_train::2hop__430640_80728','v3_program_complete_chain')
    for a,pa,b,pb in [('A_G','P2','D','P2'),('R','P2','D','P2'),('D','P2','D','P1')]:
        for sign,label in [(1,'gain'),(-1,'harm')]:
            eligible=[c['query_id'] for c in sample if sign*(scores[c['query_id'],a,pa]-scores[c['query_id'],b,pb])>1e-12]
            if eligible:add(eligible[0],f'first_sample_order_{label}_{a}_{pa}_minus_{b}_{pb}')
    cs=read(LOCAL/'contexts.json');ps=rows(LOCAL/'core.jsonl');out=[]
    for c in sample:
        q=c['query_id']
        if q not in reasons:continue
        rr=dict(query_id=q,question=c['query']['question'],reasons=reasons[q],contexts=[r for r in cs if r['query_id']==q and r['context'] in ('D','A_G','L_G','R')],
            outputs=[dict(context=r['context'],protocol=r['protocol'],raw=r['generation']['text'],parsed=r['parsed_answer'],f1=scores[q,r['context'],r['protocol']]) for r in ps if r['query_id']==q])
        out.append(rr)
        print(json.dumps({k:v for k,v in rr.items() if k!='contexts'},ensure_ascii=False))
    save(LOCAL/'review_cases.json',out)
if __name__=='__main__':run()
