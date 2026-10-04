"""Same-cardinality, exact/near actual-token-length set discrimination."""
from common import *
from dataset import Store
from model import Selector
import numpy as np
import torch

def main(seed=1729):
    cpu=0.;wall=time.perf_counter();torch.set_num_threads(1);store=Store();ss=read(LOCAL/'subsets.json');models={};stats={}
    for kind in ('H1','H2','H4','DeepSets'):
        ck=torch.load(LOCAL/f'{kind}_{seed}.pt',map_location='cpu',weights_only=False);net=Selector(kind,**ck['normal']);net.load_state_dict(ck['state']);models[kind]=net.eval()
    for q in store.queries:
        if q['role']!='TUNE':continue
        c=store.case(q);s=ss[q['query_id']];sets=s['subsets'];lens=[c['ctx'].tokens(r['indices']) for r in sets]
        pairs={'exact_tokens':[(a,b) for a,b in s['pairs'] if lens[a]==lens[b]],'within_5_percent':[(a,b) for a,b in s['pairs'] if abs(lens[a]-lens[b])<=.05*max(lens[a],lens[b])]}
        X=[];L=[];M=[]
        for r in sets:
            n=len(r['indices']);ix=r['indices']+[0]*(6-n);X.append(c['x'][ix]);L.append(c['length'][ix]);M.append([1.]*n+[0.]*(6-n))
        Q=np.repeat(c['qx'][None],len(sets),axis=0);args=[torch.tensor(np.asarray(a),dtype=torch.float32) for a in (Q,X,L,M)]
        for kind,net in models.items():
            with torch.inference_mode():pred=net(*args)[:,0].numpy()
            for scope,pp in pairs.items():
                r=stats.setdefault((q['tag'],kind,scope),dict(queries_with_pairs=0,pairs=0,correct=0,ties=0,query_accuracy_sum=0.))
                correct=sum(pred[a]>pred[b] for a,b in pp);r['queries_with_pairs']+=bool(pp);r['pairs']+=len(pp);r['correct']+=int(correct);r['ties']+=sum(int(pred[a]==pred[b]) for a,b in pp)
                if pp:r['query_accuracy_sum']+=correct/len(pp)
        budget(0,time.process_time())
    out=[]
    for (tag,model,scope),r in stats.items():out.append(dict(seed=seed,tag=tag,model=model,condition=scope,**r,pair_accuracy=r['correct']/r['pairs'] if r['pairs'] else None,query_macro_accuracy=r['query_accuracy_sum']/r['queries_with_pairs'] if r['queries_with_pairs'] else None))
    table(HERE/f'LENGTH_CONTROL_{seed}.csv',out);charge(f'length_control_{seed}',cpu,wall,gpu_process_seconds=0)
if __name__=='__main__':main()
