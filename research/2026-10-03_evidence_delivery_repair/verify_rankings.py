"""Independent small-set reference for R1/R2 on every pilot query, no Gold."""
from common import *
from repair import Context,METHODS
import itertools,math,subprocess

def verify(c,rr):
    # Reference uses unit-ID sets and recomputes empirical ranks, not r1/r2/phi/place.
    d=[c.ids[i] for i in c.d];prefix=d[:c.p];imap={s:i for i,s in enumerate(c.ids)}
    def phi(s,l):
        ix=sorted(imap[u] for u in s)
        ranks=[sum(v<=c.s[i] for v in c.s)/c.n for i in ix]
        terms=set().union(*(c.t[i] for i in ix))
        return l*math.fsum(ranks)/len(d)+(1-l)*len(terms)/max(1,len(c.qt))
    def ordered(ins):return sorted(ins,key=lambda u:c.key(imap[u]))
    def placed(ins,removed=()):return list(dict.fromkeys(prefix+ordered(ins)+[u for u in d if u not in removed]))[:len(d)]
    for m,r in rr.items():
        ids=r['ranking'];assert len(ids)==min(40 if m=='Dense40' else 20,c.n)
        assert len(ids)==len(set(ids)) and set(ids)<=set(c.ids)
        assert ids[:c.p]==prefix
        assert all(c.s[imap[u]]>=c.cfg.q25_floor and u not in prefix for u in r['inserted'])
        assert r['inserted']==ordered(r['inserted'])
    for l in (.85,.70):
        r=rr[f'R1_{l:.2f}'];ins=[];cand=[c.ids[i] for i in c.candidates]
        for _ in range(min(c.b,len(cand))):
            base=phi(set(placed(ins)),l)
            chosen=min((u for u in cand if u not in ins),key=lambda u:(-(phi(set(placed(ins+[u])),l)-base),*c.key(imap[u])))
            ins.append(chosen)
        assert r['inserted']==ordered(ins) and r['ranking']==placed(ins)
        for family in ('R2','Flat-R2','KMeans-R2'):
            target=rr[f'{family}_{l:.2f}'];ins=target['inserted'];a=len(set(ins)-set(d));base=placed(ins);old=set(d)-set(base)
            candidates=sorted(set(d)-set(prefix)-set(ins));options=[]
            for removed in itertools.combinations(candidates,a):
                s=(set(d)-set(removed))|set(ins);options.append((phi(s,l),removed))
            maximum=max(v for v,r in options)
            best=min((r for v,r in options if v==maximum),key=lambda r:(set(r)!=old,r))
            assert target['ranking']==placed(ins,best),(family,l,'reference eviction differs')
            if family=='R2':assert target['inserted']==rr[f'R1_{l:.2f}']['inserted']
    return True

def main():
    cpu=time.process_time();wall=time.perf_counter()
    result=subprocess.run([sys.executable,str(HERE/'tests.py')],capture_output=True,text=True)
    with (HERE/'TEST_OUTPUT.txt').open('x',encoding='utf-8') as h:h.write(result.stdout+result.stderr)
    assert result.returncode==0
    rr={}
    for r in rows(HERE/'pilot_rankings.jsonl'):rr.setdefault(r['query_id'],{})[r['method']]=r
    count=0
    for tag in CONFIGS:
        cfg,p,units,queries,x,q,spans,_=dataset(tag,verify=False)
        for j,row in enumerate(queries):
            if row['query_id'] not in rr:continue
            a,b=spans[row['query_id']];c=Context(row,units[a:b],x[a:b],q[j]);verify(c,rr[row['query_id']]);count+=1
    assert count==400
    save(HERE/'RANKING_VERIFICATION.json',{'status':'PASS','queries':count,'arms':13,'reference':'ID-set greedy and independent exhaustive eviction','gold_read':False,'synthetic_tests':6})
    charge('verify_rankings',cpu,wall,gpu_process_seconds=0)
    print('400 query reference checks PASS; 6 synthetic tests PASS',flush=True)
if __name__=='__main__':main()
