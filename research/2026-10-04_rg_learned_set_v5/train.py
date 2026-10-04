from common import *
from dataset import Store
from model import Selector
import numpy as np
import torch
import torch.nn.functional as F

class Batches:
    def __init__(self,store):
        self.store=store;self.ss=read(LOCAL/'subsets.json');self.qmap={q['query_id']:q for q in store.queries};self.pool={}
        for qid,s in self.ss.items():
            tag=self.qmap[qid]['tag'];ii=[store.index[tag][b] for b in s['block_ids']]
            self.pool[qid]=(np.asarray(store.xx[tag][ii]),np.array([store.lengths[tag][i] for i in ii],dtype='float32'),np.array([float(b in store.targets[qid]['coverage']) for b in s['block_ids']],dtype='float32'))
    def batch(self,qids,rng):
        Q=[];X=[];L=[];M=[];Y=[];P=[];pairs=[]
        for qid in qids:
            s=self.ss[qid];xx,ll,pp=self.pool[qid];ix=[]
            if s['pairs']:
                i,j=s['pairs'][int(rng.integers(len(s['pairs'])))];pairs.append((len(Q),len(Q)+1));ix=[i,j]
            ix+=rng.choice(len(s['subsets']),8-len(ix),replace=len(s['subsets'])<8).tolist()
            for i in ix:
                row=s['subsets'][i];jj=row['indices'];n=len(jj);pad=jj+[0]*(6-n)
                Q.append(self.store.qx[qid]);X.append(xx[pad]);L.append(ll[pad]);M.append([1.]*n+[0.]*(6-n));Y.append([row['full'],row['cov']]);P.append(pp[pad])
        ts=[torch.as_tensor(np.asarray(a),device='cuda',dtype=torch.float32) for a in (Q,X,L,M,Y,P)]
        return ts,pairs

def objective(net,ts,pairs):
    q,x,l,m,y,p=ts;d=net.factors(q,x,l);pred,terms=net.score(d,m,True)
    loss=F.binary_cross_entropy_with_logits(pred[:,0],y[:,0])+.5*F.mse_loss(pred[:,1].sigmoid(),y[:,1])
    point=(F.binary_cross_entropy_with_logits(d['a'][...,0],p,reduction='none')*m).sum()/m.sum().clamp_min(1)
    loss=loss+.25*point
    ranking=torch.tensor(0.,device='cuda');correct=0
    if pairs:
        a,b=zip(*pairs);delta=pred[list(a),0]-pred[list(b),0];ranking=F.softplus(-delta).mean();correct=float((delta>0).sum())
    return loss+.25*ranking,correct,len(pairs),[float(t.detach().abs().mean()) for t in terms]

def main(seed=1729):
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    store=Store();data=Batches(store);normal=read(LOCAL/'normalization.json')
    fit=[q['query_id'] for q in store.queries if q['role']=='FIT'];tune=[q['query_id'] for q in store.queries if q['role']=='TUNE'];history=[];summary=[]
    try:
        for kind in ('H1','H2','H4','DeepSets'):
            path=LOCAL/f'{kind}_{seed}.pt'
            if path.exists():continue
            torch.manual_seed(seed);rng=np.random.default_rng(seed);net=Selector(kind,**normal).cuda();opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001)
            best=float('inf');stale=0
            for epoch in range(30):
                start=time.perf_counter();net.train();trainloss=[];grads=[];terms=[];order=rng.permutation(len(fit))
                for b in range(0,len(fit),8):
                    budget(time.perf_counter()-wall,time.process_time()-cpu,qa_reserve=True)
                    ts,pairs=data.batch([fit[i] for i in order[b:b+8]],rng);opt.zero_grad(set_to_none=True)
                    loss,_,_,term=objective(net,ts,pairs);loss.backward()
                    if hasattr(net,'w'):
                        grads.append(net.w.weight.grad.reshape(2,net.order-1,32,128).norm(dim=(2,3)).mean(0).detach().cpu().tolist())
                    torch.nn.utils.clip_grad_norm_(net.parameters(),1);opt.step();trainloss.append(float(loss.detach()));terms.append(term)
                net.eval();vl=[];right=0;count=0;vrng=np.random.default_rng(909)
                with torch.inference_mode():
                    for b in range(0,len(tune),8):
                        ts,pairs=data.batch(tune[b:b+8],vrng);loss,c,n,_=objective(net,ts,pairs);vl.append(float(loss));right+=c;count+=n
                value=float(np.mean(vl));rank=right/max(1,count)
                row=dict(seed=seed,model=kind,epoch=epoch+1,train_loss=float(np.mean(trainloss)),tune_loss=value,tune_pair_accuracy=rank,pair_queries=count,parameters=sum(p.numel() for p in net.parameters()),seconds=time.perf_counter()-start,
                    term_abs=json.dumps(np.mean(terms,axis=0).tolist()),order_weight_grad=json.dumps(np.mean(grads,axis=0).tolist() if grads else []))
                history.append(row);append(LOCAL/'training_history.jsonl',row);print(json.dumps(row),flush=True)
                # Loss primary; ranking only resolves numerical ties, not QA.
                if value<best-1e-5:
                    best=value;stale=0;torch.save(dict(kind=kind,seed=seed,normal=normal,state=net.cpu().state_dict(),epoch=epoch+1,validation=row),LOCAL/f'{kind}_{seed}.best.pt');net.cuda()
                else:stale+=1
                if stale>=5:break
            os.replace(LOCAL/f'{kind}_{seed}.best.pt',path)
            ck=torch.load(path,map_location='cpu',weights_only=False);summary.append(ck['validation']);del net,opt;torch.cuda.empty_cache()
    finally:
        charge(f'train_seed_{seed}',cpu,wall,gpu_process_seconds=time.perf_counter()-wall,peak_gpu_bytes=torch.cuda.max_memory_allocated())
        allhist=rows(LOCAL/'training_history.jsonl') if (LOCAL/'training_history.jsonl').exists() else []
        table(HERE/'TRAINING_CURVES.csv',allhist)
        table(HERE/f'TRAINING_CHECKPOINTS_{seed}.csv',summary)

if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 1729)
