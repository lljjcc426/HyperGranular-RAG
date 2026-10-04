from common import *
import numpy as np
from transformers import AutoTokenizer

class Context:
    def __init__(self,question,blocks,tok,limit=1024):
        self.question=question;self.blocks=blocks;self.tok=tok;self.limit=limit;self.cache={};self.seconds=0.;self.checks=0
    def user(self,S):return P.prompt(self.question,P.body([(self.blocks[i]['title'],self.blocks[i]['text']) for i in sorted(S)]),'P2')
    def tokens(self,S):
        key=tuple(sorted(S))
        if key not in self.cache:
            t=time.perf_counter();self.cache[key]=len(P.ids(self.tok,self.user(key)));self.seconds+=time.perf_counter()-t;self.checks+=1
        return self.cache[key]
    def __call__(self,S):return self.tokens(S)<=self.limit

def greedy(ctx,order,k=None):
    selected=[]
    for i in order:
        if ctx(selected+[int(i)]):selected.append(int(i))
        if k and len(selected)>=k:break
    return tuple(sorted(selected))

def mmr(ctx,x,scores,k=None):
    selected=[];remaining=list(range(len(x)));sim=x@x.T
    while remaining:
        values=.7*scores[remaining]-(.3*np.max(sim[np.ix_(remaining,selected)],axis=1) if selected else 0)
        j=int(np.argmax(values));i=remaining.pop(j)
        if ctx(selected+[i]):selected.append(i)
        if k and len(selected)>=k:break
    return tuple(sorted(selected))

def coverage(target,ids):
    hit=set()
    for i in set(ids):hit.update(target['coverage'].get(i,[]))
    cov=len(hit)/target['total'];return cov,float(len(hit)==target['total'])

class Store:
    def __init__(self):
        self.corpus=read(LOCAL/'corpus.json');self.queries=read(LOCAL/'queries.json');self.targets=read(LOCAL/'targets.json');self.retr=read(LOCAL/'retrieved.json')
        self.xx={t:np.load(LOCAL/f'{t}_blocks.npy',mmap_mode='r') for t in self.corpus}
        self.qx={};self.index={t:{b['id']:i for i,b in enumerate(c)} for t,c in self.corpus.items()}
        for t in self.corpus:
            qq=[q for q in self.queries if q['tag']==t];x=np.load(LOCAL/f'{t}_queries.npy')
            self.qx.update({q['query_id']:x[j] for j,q in enumerate(qq)})
        self.tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
        self.lengths=read(LOCAL/'lengths.json') if (LOCAL/'lengths.json').exists() else {t:[len(self.tok.encode(b['title']+'\n'+b['text'],add_special_tokens=False)) for b in c] for t,c in self.corpus.items()}
        if not (LOCAL/'lengths.json').exists():save(LOCAL/'lengths.json',self.lengths)
    def case(self,q,training=False,closed=False,limit=1024):
        tag=q['tag'];qid=q['query_id'];xx=self.xx[tag];qx=self.qx[qid]
        ii=[self.index[tag][i] for i in q['closed']] if closed else list(self.retr[qid])
        if closed:ii=sorted(set(ii),key=lambda i:(-float(xx[i]@qx),self.corpus[tag][i]['id']))
        injected=0
        if training and q['role']=='FIT':
            missing=[self.index[tag][b] for b in self.targets[qid]['coverage'] if self.index[tag][b] not in ii]
            if missing:
                hard=[int(i) for i in np.argsort(-(xx@qx),kind='stable') if int(i) not in ii and int(i) not in missing][:len(missing)]
                ii+=missing+hard;injected=len(missing)
        blocks=[self.corpus[tag][i] for i in ii];x=np.asarray(xx[ii]);length=np.array([self.lengths[tag][i] for i in ii],dtype='float32')
        return dict(q=q,qx=qx,x=x,blocks=blocks,length=length,scores=x@qx,ctx=Context(q['question'],blocks,self.tok,limit),injected=injected)

def subsets(case,target):
    ids=[b['id'] for b in case['blocks']];ctx=case['ctx'];scores=case['scores'];length=case['length'];n=len(ids)
    positives=[i for i,b in enumerate(ids) if b in target['coverage']];negatives=[i for i,b in enumerate(ids) if b not in target['coverage']]
    found={};match_fail=0
    def add(S):
        S=tuple(sorted(set(S)))
        if len(S)<=6 and ctx(S):found[S]=coverage(target,[ids[i] for i in S])
    add(());add(positives)
    for i in positives+negatives[:6]:add([i])
    for i in positives:
        partial=[j for j in positives if j!=i];add(partial)
        matched=[j for j in negatives if .5<=length[j]/max(length[i],1)<=2 and abs(scores[j]-scores[i])<=.1]
        if not matched:match_fail+=1
        for j in sorted(matched,key=lambda j:(abs(length[j]-length[i])/max(1,length[i])+abs(scores[j]-scores[i]),ids[j]))[:3]:add(partial+[j])
    for j in negatives[:6]:add(positives+[j])
    dense=greedy(ctx,range(n),6);add(dense);add(mmr(ctx,case['x'],scores,6))
    for k in range(1,7):add(dense[:k])
    rng=np.random.default_rng(int(digest(['subsets',case['q']['group']])[:8],16))
    for _ in range(160):
        k=int(rng.integers(1,7));S=rng.choice(n,min(k,n),replace=False).tolist()
        # Half random subsets begin with a real partial support set; no answer features.
        if positives and rng.random()<.5:S=list(dict.fromkeys(rng.choice(positives,min(len(positives),k),replace=False).tolist()+S))[:k]
        add(S)
        if len(found)>=64:break
    result=[dict(indices=list(s),cov=c,full=f) for s,(c,f) in found.items()][:64]
    pairs=[(i,j) for i,a in enumerate(result) for j,b in enumerate(result) if a['full']==1 and b['full']==0 and len(a['indices'])==len(b['indices'])]
    return dict(subsets=result,pairs=pairs,matching_failures=match_fail,positive_blocks=len(positives),injected=case['injected'])

def prepare_subsets():
    cpu=time.process_time();wall=time.perf_counter();store=Store();out={};stats=[];scalars=[]
    for j,q in enumerate(store.queries):
        if q['role']=='DEV':continue
        c=store.case(q,training=q['role']=='FIT');t=store.targets[q['query_id']];s=subsets(c,t)
        s['block_ids']=[b['id'] for b in c['blocks']];out[q['query_id']]=s
        if q['role']=='FIT':scalars.append(np.stack([c['scores'],np.log1p(c['length'])],-1))
        cov,full=coverage(t,[store.corpus[q['tag']][i]['id'] for i in store.retr[q['query_id']]])
        stats.append(dict(tag=q['tag'],role=q['role'],stratum=q['stratum'],reachable_cov=cov,reachable_full=full,nsets=len(s['subsets']),pairs=len(s['pairs']),match_fail=s['matching_failures'],injected=s['injected']))
        if j%400==0:print('subsets',j,flush=True)
        budget(0,time.process_time()-cpu)
    scalars=np.concatenate(scalars);save(LOCAL/'subsets.json',out);save(LOCAL/'normalization.json',dict(mean=scalars.mean(0).tolist(),std=np.maximum(scalars.std(0),1e-6).tolist()))
    summary=[]
    for tag in ('hotpot','musique'):
        for role in ('FIT','TUNE'):
            rs=[r for r in stats if r['tag']==tag and r['role']==role]
            summary.append(dict(tag=tag,role=role,queries=len(rs),**{k:float(np.mean([r[k] for r in rs])) for k in ('reachable_cov','reachable_full','nsets','pairs','match_fail','injected')}))
    table(HERE/'DATA_DIAGNOSTICS.csv',summary);charge('subsets',cpu,wall,gpu_process_seconds=0)

if __name__=='__main__':prepare_subsets()
