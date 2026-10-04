from common import *
from dataset import Store,Context,greedy,mmr,coverage
from model import Selector
from search import HScore,beam
import numpy as np
import torch

class GeneralScore:
    def __init__(self,net,d):self.net=net;self.d=d;self.n=len(d['h']);self.cache={}
    def values(self,sets):
        if not sets:return np.array([])
        n=torch.tensor([len(s) for s in sets]);h=torch.stack([self.d['h'][list(s)].sum(0)/6 for s in sets]);a=torch.stack([self.d['a'][list(s),0].sum()/6 for s in sets]);q=self.d['q'].expand(len(sets),-1)
        with torch.inference_mode():y=a+self.d['b'][0,n]+self.net.rho(torch.cat([h,q],-1))[:,0]
        return y.numpy()
    def score(self,S):
        S=tuple(sorted(S))
        if S not in self.cache:self.cache[S]=float(self.values([S])[0])
        return self.cache[S]
    def expansion_scores(self,S):
        sets=[tuple(sorted((*S,i))) for i in range(self.n) if i not in S];v=self.values(sets);out=np.full(self.n,-np.inf)
        for s,x in zip(sets,v):self.cache[s]=float(x)
        for i in range(self.n):
            if i not in S:out[i]=self.cache[tuple(sorted((*S,i))) ]
        return out

def scorer(net,c):
    start=time.perf_counter()
    with torch.inference_mode():d=net.factors(torch.tensor(c['qx']),torch.tensor(c['x']),torch.tensor(c['length']))
    if net.order:
        s=HScore(d['a'][:,0].numpy(),d['v'].numpy(),d['w'][0].numpy() if net.order>1 else np.zeros((0,32)),d['b'][0].numpy(),net.order)
    else:
        # Float64 scoring of the same learned factors for tie consistency.
        d={k:v.double() for k,v in d.items()};s=GeneralScore(net.double(),d)
    return s,time.perf_counter()-start

def load_models(seed):
    models={}
    for kind in ('H1','H2','H4','DeepSets'):
        ck=torch.load(LOCAL/f'{kind}_{seed}.pt',map_location='cpu',weights_only=False);net=Selector(kind,**ck['normal']);net.load_state_dict(ck['state']);net.eval();models[kind]=net
    return models

def main(seed=1729,mode='main'):
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);store=Store();models=load_models(seed)
    queries=[q for q in store.queries if q['role']=='TUNE' and (mode=='main' and seed==1729 or (q['panel'] if mode=='main' else q['sensitivity']))]
    limits=(512,2048) if mode=='sensitivity' else (1024,);closed=mode=='closed';outfile=LOCAL/f'selections_{seed}_{mode}.jsonl'
    previous=rows(outfile) if outfile.exists() else [];done={(r['query_id'],r['budget'],r['method']) for r in previous};costs=[];parity=[];allrows=previous
    try:
        for j,q in enumerate(queries):
            for limit in limits:
                c=store.case(q,closed=closed,limit=limit);ids=[b['id'] for b in c['blocks']];t=store.targets[q['query_id']];reach=coverage(t,ids)
                def record(method,S,stats=None,value=None):
                    cov,full=coverage(t,[ids[i] for i in S]);r=dict(query_id=q['query_id'],tag=q['tag'],stratum=q['stratum'],panel=q['panel'],sensitivity=q['sensitivity'],seed=seed,setting='closed' if closed else 'opened',budget=limit,method=method,selected=[ids[i] for i in S],coverage=cov,complete=full,reachable_cov=reach[0],reachable_full=reach[1],blocks=len(S),tokens=c['ctx'].tokens(S),score=value)
                    append(outfile,r);allrows.append(r)
                    if stats:costs.append(dict(query_hash=digest(q['query_id']),tag=q['tag'],seed=seed,mode=mode,budget=limit,method=method,**stats))
                for method in ('Dense','MMR') if not closed else ('Dense',):
                    if (q['query_id'],limit,method) in done:continue
                    c['ctx']=Context(q['question'],c['blocks'],store.tok,limit);st=time.perf_counter();S=greedy(c['ctx'],range(len(ids))) if method=='Dense' else mmr(c['ctx'],c['x'],c['scores'])
                    record(method,S,dict(total_seconds=time.perf_counter()-st,token_seconds=c['ctx'].seconds,tokenizations=c['ctx'].checks))
                for kind,net in models.items():
                    if closed and kind not in ('H1','H4'):continue
                    methods=['H4-Flat','H4-GB','H4-KM','H4-Representative'] if kind=='H4' else [kind]
                    if all((q['query_id'],limit,m) in done for m in methods):continue
                    if kind=='DeepSets':net.float()
                    s,network_seconds=scorer(net,c);reference=None
                    for method in methods:
                        if (q['query_id'],limit,method) in done:continue
                        selection_start=time.perf_counter();c['ctx']=Context(q['question'],c['blocks'],store.tok,limit);ctx=c['ctx'];dense=greedy(ctx,range(len(ids)),6)
                        # Dense-K construction belongs to every selector cost.
                        dense_seconds=ctx.seconds;idxkind=method.split('-')[-1] if kind=='H4' else 'Flat'
                        S,stats,trace=beam(s,ctx,ids,dense,kind=idxkind);stats.update(network_seconds=network_seconds,dense_token_seconds=dense_seconds,token_seconds=ctx.seconds,tokenizations=ctx.checks)
                        stats['total_seconds']=time.perf_counter()-selection_start+network_seconds
                        if method=='H4-Flat':reference=(S,trace)
                        if method in ('H4-GB','H4-KM') and reference:
                            equal=S==reference[0] and trace==reference[1];parity.append(dict(query_hash=digest(q['query_id']),method=method,budget=limit,parents=len(trace),equal=equal))
                            if not equal:
                                save(LOCAL/'parity_difference.json',dict(query_id=q['query_id'],method=method,reference=reference,actual=(S,trace)));S=reference[0];stats['fallback_flat']=1
                            else:stats['fallback_flat']=0
                        record(method,S,stats,s.score(S))
                    if kind=='H1' and not closed:
                        c['ctx']=Context(q['question'],c['blocks'],store.tok,limit)
                        S=greedy(c['ctx'],np.argsort(-s.a,kind='stable'),6);record('H1-sort',S,value=s.score(S))
                budget(0,time.process_time()-cpu)
            if j%20==0:print('selection',seed,mode,j,len(queries),round(time.perf_counter()-wall,1),flush=True)
    finally:
        append(LOCAL/'selection_cost_batches.jsonl',dict(seed=seed,mode=mode,rows=costs,parity=parity))
        summarize();charge(f'selection_{seed}_{mode}',cpu,wall,gpu_process_seconds=0)

def summarize():
    data=[r for p in LOCAL.glob('selections_*.jsonl') for r in rows(p)];summary=[]
    keys=sorted(set((r['seed'],r['setting'],r['budget'],r['method'],r['tag']) for r in data))
    for key in keys:
        rr=[r for r in data if (r['seed'],r['setting'],r['budget'],r['method'],r['tag'])==key]
        summary.append(dict(zip(('seed','setting','budget','method','tag'),key),queries=len(rr),**{k:float(np.mean([r[k] for r in rr])) for k in ('coverage','complete','reachable_cov','reachable_full','blocks','tokens')}))
    table(HERE/'TRAINING_AND_SELECTION_RESULTS.csv',summary)
    costs=[r for b in rows(LOCAL/'selection_cost_batches.jsonl') for r in b['rows']] if (LOCAL/'selection_cost_batches.jsonl').exists() else []
    cc=[]
    for key in sorted(set((r['seed'],r['mode'],r['budget'],r['method'],r['tag']) for r in costs)):
        rr=[r for r in costs if (r['seed'],r['mode'],r['budget'],r['method'],r['tag'])==key]
        cc.append(dict(zip(('seed','mode','budget','method','tag'),key),queries=len(rr),**{k:float(np.mean([r.get(k,0) for r in rr])) for k in ('network_seconds','build_seconds','total_seconds','token_seconds','true_scores','tokenizations','node_visits','pruned_nodes','fallback_flat')}))
    table(HERE/'SEARCH_COSTS.csv',cc)
    pp=[r for b in rows(LOCAL/'selection_cost_batches.jsonl') for r in b['parity']] if (LOCAL/'selection_cost_batches.jsonl').exists() else []
    save(HERE/'NATURAL_PARITY.json',dict(comparisons=len(pp),parent_states=sum(r['parents'] for r in pp),mismatches=sum(not r['equal'] for r in pp)))

if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 1729,sys.argv[2] if len(sys.argv)>2 else 'main')
