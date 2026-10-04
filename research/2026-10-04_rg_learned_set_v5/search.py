"""Exact conditional inner-product expansions; beam is not globally optimal."""
import math,heapq,time
import numpy as np
K=6;R=32
def es(v,H):
    e=np.zeros((H+1,v.shape[-1]),dtype=np.float64);e[0]=1
    for row in v:
        for h in range(H,0,-1):e[h]+=row*e[h-1]
    return e

class HScore:
    def __init__(self,a,v,w,b,H):
        self.a=np.asarray(a,dtype='float64');self.v=np.asarray(v,dtype='float64');self.w=np.asarray(w,dtype='float64');self.b=np.asarray(b,dtype='float64');self.H=H
        self.z=np.column_stack([self.a/K,self.v]);self.n=len(a)
    def score(self,S):
        if len(set(S))!=len(S):raise ValueError('duplicate block')
        e=es(self.v[list(S)],self.H)
        return self.b[len(S)]+self.a[list(S)].sum()/K+sum(np.dot(self.w[h-2],e[h])/(R*math.comb(K,h)) for h in range(2,self.H+1))
    def theta(self,S):
        e=es(self.v[list(S)],self.H);t=np.zeros(R)
        for h in range(2,self.H+1):t+=self.w[h-2]*e[h-1]/(R*math.comb(K,h))
        return np.r_[1.,t]
    def expansion_scores(self,S):return self.score(S)+self.b[len(S)+1]-self.b[len(S)]+self.z@self.theta(S)

class Tree:
    def __init__(self,z,kind='GB',leaf=8):
        self.z=z;self.nodes=[];self.kind=kind;self.leaf=leaf;self.root=self.build(np.arange(len(z)))
    def build(self,idx):
        x=self.z[idx];c=x.mean(0);r=float(np.max(np.linalg.norm(x-c,axis=1)));r=np.nextafter(r,np.inf)
        n=len(self.nodes);self.nodes.append(dict(idx=idx,c=c,r=r,children=[]))
        if len(idx)<=self.leaf:return n
        a=int(np.argmax(((x-c)**2).sum(1)));b=int(np.argmax(((x-x[a])**2).sum(1)));ca=x[a].copy();cb=x[b].copy()
        for _ in range(20 if self.kind=='KM' else 1):
            left=((x-ca)**2).sum(1)<=((x-cb)**2).sum(1)
            if left.all() or not left.any():left=np.arange(len(idx))<len(idx)//2;break
            if self.kind=='KM':
                na=x[left].mean(0);nb=x[~left].mean(0)
                if np.array_equal(na,ca) and np.array_equal(nb,cb):break
                ca,cb=na,nb
        self.nodes[n]['children']=[self.build(idx[left]),self.build(idx[~left])];return n
    def representatives(self):
        return [int(n['idx'][np.argmin(((self.z[n['idx']]-n['c'])**2).sum(1))]) for n in self.nodes if not n['children']]

def beam(scorer,feasible,ids,dense,kind='Flat',width=4,maxk=6):
    start=time.perf_counter();tree=Tree(scorer.z,kind) if kind in ('GB','KM','Representative') else None
    build=time.perf_counter()-start;stats=dict(build_seconds=build,node_visits=0,true_scores=0,token_checks=0,expansions=0,pruned_nodes=0)
    allowed=set(tree.representatives()) if kind=='Representative' else None
    trace=[]
    def key(S):return tuple(sorted(ids[i] for i in S))
    def add(S,i):return tuple(sorted((*S,int(i))))
    def ok(S):stats['token_checks']+=1;return feasible(S)
    def top(S):
        stats['expansions']+=1;got=[]
        if kind in ('GB','KM'):
            theta=scorer.theta(S);offset=scorer.score(S)+scorer.b[len(S)+1]-scorer.b[len(S)];tn=np.linalg.norm(theta)
            def ub(n):return offset+theta@tree.nodes[n]['c']+tn*tree.nodes[n]['r']
            heap=[(-ub(tree.root),tree.root)]
            while heap:
                neg,n=heapq.heappop(heap);stats['node_visits']+=1
                margin=1e-10*(1+abs(neg)+tn)
                if len(got)>=width and -neg < got[-1][0]-margin:stats['pruned_nodes']+=1;continue
                node=tree.nodes[n]
                if node['children']:
                    for ch in node['children']:heapq.heappush(heap,(-ub(ch),ch))
                else:
                    idx=np.array([i for i in node['idx'] if i not in S],dtype=int);values=offset+scorer.z[idx]@theta;stats['true_scores']+=len(idx)
                    for i,v in zip(idx,values):
                        ss=add(S,i)
                        if ok(ss):got.append((float(v),ss));got.sort(key=lambda p:(-p[0],key(p[1])));got=got[:width]
        else:
            vals=scorer.expansion_scores(S);stats['true_scores']+=scorer.n
            order=sorted((i for i in range(scorer.n) if i not in S and (allowed is None or i in allowed)),key=lambda i:(-vals[i],key(add(S,i))))
            for i in order:
                ss=add(S,i)
                if ok(ss):got.append((float(vals[i]),ss))
                if len(got)==width:break
        # Score by the same full function; branch search ranks identical linear sums.
        out=[ss for _,ss in got];trace.append((S,out));return out
    current=[()];visited=set()
    for depth in range(1,maxk+1):
        candidates={ss for S in current for ss in top(S)}
        if not candidates:break
        visited.update(candidates);current=sorted(candidates,key=lambda s:(-scorer.score(s),key(s)))[:width]
    if dense:visited.add(tuple(sorted(dense)))
    selected=min(visited,key=lambda s:(-scorer.score(s),feasible.tokens(s),key(s))) if visited else ()
    stats['total_seconds']=time.perf_counter()-start;stats['visited_sets']=len(visited)
    return selected,stats,trace
