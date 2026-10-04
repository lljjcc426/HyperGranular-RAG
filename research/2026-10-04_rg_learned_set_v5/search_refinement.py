"""Paired fixed-64 CPU timing of exact leaf-threshold pruning, no new QA."""
from common import *
from dataset import Store,Context,greedy
from evaluate import load_models,scorer
from search import beam
import numpy as np
import torch


def main():
    cpu=time.process_time();wall=time.perf_counter();store=Store();net=load_models(1729)['H4'];results=[];parity=[]
    try:
        for q in store.queries:
            if not q['sensitivity']:continue
            c=store.case(q);ids=[b['id'] for b in c['blocks']];s,network=scorer(net,c);reference=None
            for kind in ('Flat','GB','KM'):
                start=time.perf_counter();ctx=Context(q['question'],c['blocks'],store.tok,1024);dense=greedy(ctx,range(len(ids)),6)
                chosen,stats,trace=beam(s,ctx,ids,dense,kind=kind,leaf_threshold=True)
                stats.update(total_seconds=time.perf_counter()-start+network,network_seconds=network,token_seconds=ctx.seconds,tokenizations=ctx.checks)
                if kind=='Flat':reference=(chosen,trace)
                else:parity.append(dict(method=kind,parents=len(trace),equal=(chosen,trace)==reference))
                results.append(dict(tag=q['tag'],method=kind,**stats))
            budget(0,time.process_time()-cpu)
        if any(not r['equal'] for r in parity):raise ValueError('LEAF_PRUNING_PARITY_MISMATCH')
    finally:
        out=[]
        for tag in ('hotpot','musique'):
            for kind in ('Flat','GB','KM'):
                rr=[r for r in results if r['tag']==tag and r['method']==kind]
                if not rr:continue
                out.append(dict(tag=tag,method=kind,queries=len(rr),**{f:float(np.mean([r[f] for r in rr])) for f in ('total_seconds','network_seconds','build_seconds','token_seconds','tokenizations','true_scores','node_visits','pruned_nodes')},median_seconds=float(np.median([r['total_seconds'] for r in rr]))))
        table(HERE/'SEARCH_COSTS_LEAF_PRUNING.csv',out)
        save(HERE/'LEAF_PRUNING_PARITY.json',dict(comparisons=len(parity),parent_states=sum(r['parents'] for r in parity),mismatches=sum(not r['equal'] for r in parity),scope='Fixed sensitivity64; seed1729;1024tokens; exact leaf threshold only; no model or QA change'))
        charge('leaf_pruning_fixed64',cpu,wall,gpu_process_seconds=0)


if __name__=='__main__':main()
