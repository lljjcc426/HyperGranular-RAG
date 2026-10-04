"""Query-conditioned HOFM and same-input DeepSets control, not new algebra."""
import math
import torch
from torch import nn
K=6;R=32

def elementary(v,order):
    e=[torch.ones_like(v[...,0,:])]+[torch.zeros_like(v[...,0,:]) for _ in range(order)]
    for i in range(v.shape[-2]):
        for h in range(order,0,-1):e[h]=e[h]+v[...,i,:]*e[h-1]
    return e

class Selector(nn.Module):
    def __init__(self,kind,mean,std):
        super().__init__();self.kind=kind;self.order=int(kind[1:]) if kind.startswith('H') else 0
        self.register_buffer('mean',torch.tensor(mean,dtype=torch.float32));self.register_buffer('std',torch.tensor(std,dtype=torch.float32))
        self.input=nn.Sequential(nn.Linear(4098,128),nn.GELU(),nn.LayerNorm(128))
        self.query=nn.Sequential(nn.Linear(1024,128),nn.GELU())
        self.a=nn.Linear(128,2);self.card=nn.Linear(128,2*7)
        if self.order:
            self.v=nn.Sequential(nn.Linear(128,R),nn.LayerNorm(R),nn.Tanh())
            if self.order>1:
                self.w=nn.Linear(128,2*(self.order-1)*R);nn.init.zeros_(self.w.weight);nn.init.ones_(self.w.bias)
        else:self.rho=nn.Sequential(nn.Linear(256,192),nn.GELU(),nn.Linear(192,2))

    def factors(self,q,x,length):
        # q [...,1024], x [...,N,1024], no query IDs, labels or rank features.
        qq=q.unsqueeze(-2).expand_as(x);cos=(qq*x).sum(-1)
        scalar=(torch.stack([cos,torch.log1p(length)],-1)-self.mean)/self.std
        h=self.input(torch.cat([qq,x,qq*x,abs(qq-x),scalar],-1));qh=self.query(q)
        d={'a':self.a(h),'b':self.card(qh).reshape(*qh.shape[:-1],2,7),'h':h,'q':qh}
        if self.order:
            d['v']=self.v(h)
            if self.order>1:d['w']=self.w(qh).reshape(*qh.shape[:-1],2,self.order-1,R)
        return d

    def score(self,d,mask,terms=False):
        n=mask.sum(-1).long();a=(d['a']*mask.unsqueeze(-1)).sum(-2)/K
        b=d['b'].gather(-1,n[...,None,None].expand(*n.shape,2,1)).squeeze(-1)
        ts=[a,b]
        if self.order:
            e=elementary(d['v']*mask.unsqueeze(-1),self.order)
            for h in range(2,self.order+1):ts.append((d['w'][...,h-2,:]*e[h].unsqueeze(-2)).sum(-1)/(R*math.comb(K,h)))
            out=sum(ts)
        else:
            pooled=(d['h']*mask.unsqueeze(-1)).sum(-2)/K
            out=a+b+self.rho(torch.cat([pooled,d['q']],-1));ts.append(out-a-b)
        return (out,ts) if terms else out

    def forward(self,q,x,length,mask,terms=False):return self.score(self.factors(q,x,length),mask,terms)
