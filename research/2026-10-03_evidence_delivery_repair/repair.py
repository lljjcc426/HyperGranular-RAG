"""Gold-free static-q25 delivery repairs. No target/answer input or I/O."""
from pathlib import Path
import sys
import itertools
import math
import time
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import stage4f_xdr_retrieval as old

LAMBDAS=(.85,.70)
METHODS=['Dense20','Dense40','H0']+[f'{m}_{l:.2f}' for m in ['R1','R2','Flat-R2','KMeans-R2','Matched-MMR'] for l in LAMBDAS]

class Context:
    def __init__(self,query,units,x,q):
        # Explicitly retain only blind fields; labels cannot be consumed downstream.
        self.query={'question':query['question'],'query_id':query['query_id']}
        self.units=[{k:u[k] for k in ('unit_id','title','text')} for u in units]
        self.x=x; self.q=q; self.n=len(units); self.k=min(20,self.n)
        self.p=min(10,self.k); self.b=min(4,self.k-self.p)
        self.ids=[u['unit_id'] for u in units]
        self.s=[old.dot(q,z) for z in x]
        self.order=sorted(range(self.n),key=self.key)
        self.d=self.order[:self.k]; self.prefix=self.d[:self.p]
        self.r=np.searchsorted(np.sort(self.s),self.s,side='right')/self.n
        self.qt=old.content_tokens(query['question'])
        self.title=[old.content_tokens(u['title']) & self.qt for u in units]
        self.body=[old.content_tokens(u['text']) & self.qt for u in units]
        self.t=[a|b for a,b in zip(self.title,self.body)]
        self.cfg=old.RetrievalConfig()
        self.balls=old.build_balls(query['query_id'],list(range(self.n)),x,self.cfg)
        self.selected,self.candidates=proposals(self,self.balls)
        self.hi=self.candidates[:self.b]
        self.h0=self.place(self.hi)

    def key(self,i):return (-self.s[i],self.ids[i])
    def union(self,indices,kind=None):
        terms=self.t if kind is None else getattr(self,kind)
        return set().union(*(terms[i] for i in indices)) if indices else set()
    def phi(self,indices,lam):
        return lam*math.fsum(float(self.r[i]) for i in sorted(set(indices)))/self.k+(1-lam)*len(self.union(indices))/max(1,len(self.qt))
    def place(self,inserted,removed=()):
        seq=self.prefix+sorted(inserted,key=self.key)+[i for i in self.d if i not in removed]
        return list(dict.fromkeys(seq))[:self.k]

def proposals(c,balls):
    old.enrich_balls_goldfree(balls,c.units)
    edges,_=old.select_facet_edges_goldfree(c.query,c.q,balls,c.cfg)
    selected={i for e in edges for i in e['accepted_ball_ids']}
    candidates=sorted([i for b in balls if b['ball_id'] in selected for i in b['indices']
                       if c.s[i]>=c.cfg.q25_floor and i not in c.prefix],key=c.key)
    return edges,candidates

def r1(c,candidates,lam):
    ins=[];steps=[]
    for _ in range(min(c.b,len(candidates))):
        current=c.phi(c.place(ins),lam)
        choices=[(c.phi(c.place(ins+[i]),lam)-current,i) for i in candidates if i not in ins]
        gain,i=min(choices,key=lambda z:(-z[0],*c.key(z[1])))
        ins.append(i);steps.append({'unit_id':c.ids[i],'proxy_delta':gain})
    ins=sorted(ins,key=c.key)
    return c.place(ins),ins,steps

def r2(c,ranking,ins,lam):
    a=len(set(ins)-set(c.d));original=set(c.d)-set(ranking)
    if not a:return list(ranking),{'combinations':1,'removed':[],'proxy_gain':0.}
    options=sorted(set(c.d)-set(c.prefix)-set(ins),key=lambda i:c.ids[i])
    choices=[]
    for removed in itertools.combinations(options,a):
        candidate=c.place(ins,removed)
        choices.append((c.phi(candidate,lam),removed,candidate))
    best=max(z[0] for z in choices)
    tied=[z for z in choices if z[0]==best]
    picked=min(tied,key=lambda z:(set(z[1])!=original,tuple(c.ids[i] for i in z[1])))
    return picked[2],{'combinations':len(choices),'removed':[c.ids[i] for i in picked[1]],
                      'proxy_gain':picked[0]-c.phi(ranking,lam)}

def kmeans(c):
    k=len(c.balls);rng=np.random.default_rng(1729)
    centers=c.x[rng.choice(c.n,k,replace=False)].copy();previous=None;repairs=0
    for iteration in range(20):
        similarity=c.x@centers.T; labels=similarity.argmax(axis=1)
        sizes=np.bincount(labels,minlength=k)
        for j in range(k):
            if sizes[j]:continue
            donor=min([i for i in range(c.n) if sizes[labels[i]]>1],
                      key=lambda i:(float(similarity[i,labels[i]]),c.ids[i]))
            sizes[labels[donor]]-=1;labels[donor]=j;sizes[j]+=1;repairs+=1
        if previous is not None and np.array_equal(previous,labels):break
        previous=labels.copy()
        centers=np.stack([old.centroid(np.flatnonzero(labels==j).tolist(),c.x) for j in range(k)])
    balls=[]
    for j in range(k):
        ix=np.flatnonzero(labels==j).tolist()
        balls.append(old.describe_ball(f"{c.query['query_id']}::kmeans{j}",c.query['query_id'],ix,
                     old.centroid(ix,c.x),c.x,0,c.cfg.boundary_width))
    return balls,{'iterations':iteration+1,'empty_repairs':repairs,'sizes':[len(b['indices']) for b in balls]}

def mmr(c,candidates,lam):
    ins=[]
    for _ in range(min(c.b,len(candidates))):
        def score(i):
            sim=max((old.dot(c.x[i],c.x[j]) for j in c.prefix+ins),default=0.)
            return lam*c.r[i]-(1-lam)*sim
        ins.append(min((i for i in candidates if i not in ins),key=lambda i:(-score(i),*c.key(i))))
    ins.sort(key=c.key)
    return c.place(ins),ins

def all_methods(c):
    output={};flat=[i for i in c.order if i not in c.prefix and c.s[i]>=c.cfg.q25_floor]
    started=time.perf_counter();kb,km=kmeans(c);ke,kc=proposals(c,kb);ktime=time.perf_counter()-started
    def add(name,ranking,ins,seconds,proposals_n,**extra):
        output[name]={'ranking':[c.ids[i] for i in ranking],'inserted':[c.ids[i] for i in ins],
            'selection_seconds':seconds,'proposal_count':proposals_n,
            'new_count':len(set(ranking)-set(c.d)), 'promotion_count':len(set(ins)&set(c.d)),
            'removed':[c.ids[i] for i in c.d if i not in ranking],
            'facet_count':len(c.union(ranking)),**extra}
    add('Dense20',c.d,[],0,0);add('Dense40',c.order[:40],[],0,0);add('H0',c.h0,c.hi,0,len(c.candidates))
    for l in LAMBDAS:
        start=time.perf_counter();a,i,steps=r1(c,c.candidates,l);elapsed=time.perf_counter()-start
        add(f'R1_{l:.2f}',a,i,elapsed,len(c.candidates),steps=steps,phi=c.phi(a,l))
        start=time.perf_counter();b,meta=r2(c,a,i,l)
        add(f'R2_{l:.2f}',b,i,elapsed+time.perf_counter()-start,len(c.candidates),phi=c.phi(b,l),eviction=meta)
        for tag,cands,overhead in [('Flat-R2',flat,0),('KMeans-R2',kc,ktime)]:
            start=time.perf_counter();a,i,steps=r1(c,cands,l);b,meta=r2(c,a,i,l)
            add(f'{tag}_{l:.2f}',b,i,time.perf_counter()-start+overhead,len(cands),phi=c.phi(b,l),eviction=meta)
        start=time.perf_counter();a,i=mmr(c,flat,l)
        add(f'Matched-MMR_{l:.2f}',a,i,time.perf_counter()-start,len(flat),phi=c.phi(a,l))
    return output,km

def gate_reasons(c):
    scored=old.decision_from_balls(c.q,c.balls)['scored_balls']
    seeds=[b for _,b in scored[:2]];seed_ids={b['ball_id'] for b in seeds}
    covered=set().union(*(b['facet_terms'] for b in seeds));cfg=c.cfg
    chosen={bid for e in c.selected for bid in e['accepted_ball_ids']};result={}
    for score,b in scored:
        ft=b['facet_terms'];new=ft-covered;shared=ft&covered;size=b['size']
        sim=max((old.dot(b['center'],s['center']) for s in seeds),default=0)
        if b['ball_id'] in seed_ids:reason='seed_excluded'
        elif len(new)<cfg.min_new_terms:reason='min_new_terms'
        elif size>cfg.max_candidate_ball_size:reason='size'
        elif not(score>=cfg.min_ball_score or sim>=cfg.min_seed_similarity):reason='anchor'
        elif size/max(1,len(new))>cfg.max_units_per_new_term:reason='units_per_new_term'
        elif len(shared)/max(1,len(ft))>cfg.max_redundancy:reason='redundancy'
        else:
            s=cfg.w_new*len(new)/max(1,len(c.qt))+cfg.w_total*len(ft)/max(1,len(c.qt))+cfg.w_ball*score+cfg.w_diversity*(1-sim)-cfg.w_redundancy*len(shared)/max(1,len(ft))-cfg.w_size*size/cfg.max_candidate_ball_size
            reason='score' if s<cfg.min_facet_score else ('selected' if b['ball_id'] in chosen else 'edge_budget')
        result[b['ball_id']]={'reason':reason,'new_terms':sorted(new),'indices':b['indices']}
    return result,covered
