"""Post-training developer checks; never changes the inference candidate pool."""
from common import *
from dataset import Store,coverage,Context
from model import Selector
import numpy as np
import torch

def run(seed=1729):
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);store=Store();ss=read(LOCAL/'subsets.json');out=[]
    for kind in ('H1','H2','H4','DeepSets'):
        ck=torch.load(LOCAL/f'{kind}_{seed}.pt',map_location='cpu',weights_only=False);net=Selector(kind,**ck['normal']);net.load_state_dict(ck['state']);net.eval();per=[]
        with torch.inference_mode():
            for q in store.queries:
                if q['role']!='TUNE':continue
                s=ss[q['query_id']];tag=q['tag'];ii=[store.index[tag][b] for b in s['block_ids']];xx=np.asarray(store.xx[tag][ii]);ll=np.array([store.lengths[tag][i] for i in ii]);sets=s['subsets'];X=[];M=[];L=[]
                for r in sets:
                    n=len(r['indices']);ix=r['indices']+[0]*(6-n);X.append(xx[ix]);L.append(ll[ix]);M.append([1.]*n+[0.]*(6-n))
                Q=np.repeat(store.qx[q['query_id']][None],len(sets),axis=0)
                args=[torch.tensor(np.asarray(a),dtype=torch.float32) for a in (Q,X,L,M)];pred,terms=net(*args,terms=True);p=pred.numpy();pairs=s['pairs'];dif=[p[a,0]-p[b,0] for a,b in pairs]
                per.append(dict(tag=tag,stratum=q['stratum'],sets=len(sets),pairs=len(pairs),pair_correct=sum(d>0 for d in dif),pair_ties=sum(d==0 for d in dif),full_bce=float(torch.nn.functional.binary_cross_entropy_with_logits(pred[:,0],torch.tensor([r['full'] for r in sets]))),cov_mse=float(np.mean((torch.sigmoid(pred[:,1]).numpy()-[r['cov'] for r in sets])**2)),terms=[float(t[:,0].abs().mean()) for t in terms],positive_sets=sum(r['full'] for r in sets)))
        for tag in ('hotpot','musique'):
            for stratum in ('ALL',)+tuple(sorted({r['stratum'] for r in per if r['tag']==tag})):
                rr=[r for r in per if r['tag']==tag and (stratum=='ALL' or r['stratum']==stratum)];pairs=sum(r['pairs'] for r in rr)
                out.append(dict(seed=seed,model=kind,tag=tag,stratum=stratum,queries=len(rr),sets=sum(r['sets'] for r in rr),positive_sets=sum(r['positive_sets'] for r in rr),same_size_pairs=pairs,pair_accuracy=sum(r['pair_correct'] for r in rr)/pairs if pairs else None,pair_ties=sum(r['pair_ties'] for r in rr),full_bce=float(np.mean([r['full_bce'] for r in rr])),cov_mse=float(np.mean([r['cov_mse'] for r in rr])),term_abs=json.dumps(np.mean([r['terms'] for r in rr],axis=0).tolist())))
    table(HERE/f'SET_DIAGNOSTICS_{seed}.csv',out)
    # Verify all group roles, panel exclusion and source offsets once on actual inputs.
    groups={}
    for q in store.queries:groups.setdefault(q['group'],set()).add(q['role'])
    assert all(len(v)==1 for v in groups.values());assert all(q['role']=='TUNE' for q in store.queries if q['panel'])
    old={r['query_id'] for r in read(V1/'local/inputs.json')};assert not old&{q['query_id'] for q in store.queries if q['panel']}
    q=next(q for q in store.queries if q['panel']);a=store.case(q);oldtarget=store.targets[q['query_id']];store.targets[q['query_id']]={'total':1,'coverage':{},'gold':{'answer':'MUTATED'}};b=store.case(q);store.targets[q['query_id']]=oldtarget
    assert [x['id'] for x in a['blocks']]==[x['id'] for x in b['blocks']] and np.array_equal(a['x'],b['x'])
    for tag in store.corpus:
        src=read(LOCAL/f'{tag}_sources.json')
        for block in store.corpus[tag]:
            for source in src[block['id']]:
                assert all(0<=s['start']<s['end']<=len(block['text']) for s in source['sentences'])
    # Exact token length identity and cache protocol separation are checked without LM calls.
    c=a['ctx'];S=(0,);assert c.tokens(S)==len(P.ids(store.tok,c.user(S)))
    u=c.user(S);i=P.identity(store.tok,u,'P2');j=P.identity(store.tok,u,'P1');assert digest(i)!=digest(j)
    save(HERE/'DATA_INTERFACE_CHECKS.json',dict(groups=len(groups),panel=128,old_dev_excluded=True,group_roles_disjoint=True,gold_mutation_inference_unchanged=True,all_source_offsets_in_range=True,actual_token_and_protocol_cache_identity=True))
    charge(f'diagnostics_{seed}',cpu,wall,gpu_process_seconds=0)

if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 1729)
