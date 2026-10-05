"""One merged search-state pool; direct training of the deployed set logit."""
from support import *
from dataset import Store,Context,coverage,greedy,mmr
from model import Selector
from evaluate import scorer
from search import beam
from train import Batches,objective
import numpy as np
import torch
import torch.nn.functional as F

def load(kind,seed=1729,path=None):
    ck=torch.load(path or V5/'local'/f'{kind}_{seed}.pt',map_location='cpu',weights_only=False)
    net=Selector(kind,**ck['normal']);net.load_state_dict(ck['state']);return net.eval(),ck

def boundaries(store):
    path=LOCAL/'boundaries.json'
    if path.exists():return read(path)
    panel=[q for q in store.queries if q['panel']];excluded={q['group'] for q in panel}
    mine=[];dev=[]
    for tag in ('hotpot','musique'):
        mine+=stratified([q for q in store.queries if q['tag']==tag and q['role']=='FIT'],256,'rg-v6-mine')
        dev+=stratified([q for q in store.queries if q['tag']==tag and q['role']=='TUNE' and q['group'] not in excluded],64,'rg-v6-select')
    result={k:[q['query_id'] for q in qq] for k,qq in [('mine',mine),('dev',dev),('qa',panel)]}
    assert not(set(result['mine'])&set(result['dev']) or set(result['dev'])&set(result['qa']))
    save(path,result)
    table(HERE/'DATA_BOUNDARIES.csv',[dict(boundary=k,tag=t,stratum=s,queries=sum(q['query_id'] in ids and q['tag']==t and q['stratum']==s for q in store.queries)) for k,ids in result.items() for t in ('hotpot','musique') for s in sorted({q['stratum'] for q in store.queries if q['tag']==t})])
    return result

def select(net,c):
    net.float().cpu().eval();sc,_=scorer(net,c);ids=[b['id'] for b in c['blocks']]
    dense=greedy(c['ctx'],range(len(ids)),6)
    s,stats,trace=beam(sc,c['ctx'],ids,dense,kind='Flat')
    return s,sc,trace,stats

def preferences(records,parents,finals):
    index={tuple(r['indices']):i for i,r in enumerate(records)}
    u=[.5*(r['full']+r['cov']) for r in records]
    frontier=set();final=set()
    for children in parents:
        ii=[index[s] for s in children if s in index]
        frontier.update((i,j) for i in ii for j in ii if u[i]>u[j])
    # Same-depth pairs are a fallback only where parent-specific pairs are absent.
    if not frontier:
        frontier.update((i,j) for i,a in enumerate(records) for j,b in enumerate(records) if len(a['indices'])==len(b['indices']) and u[i]>u[j])
    ii=[index[s] for s in finals if s in index]
    for i in ii:
        for j in ii:
            if u[i]>u[j] and len(records[i]['indices'])==len(records[j]['indices']):final.add((i,j))
    near={(i,j) for i,j in final if .8<=records[i]['tokens']/max(1,records[j]['tokens'])<=1.25}
    return sorted(near or final),sorted(frontier)

def mine(store,bd,round_no,seed=1729):
    path=LOCAL/f'mined_{seed}_{round_no}.json'
    if path.exists():return read(path)
    cpu=time.process_time();wall=time.perf_counter();qmap={q['query_id']:q for q in store.queries}
    models={k:load(k,seed,None if round_no==1 else LOCAL/f'{k}_{seed}_r{round_no-1}.pt')[0] for k in KINDS}
    pool={};stats=[]
    try:
        for count,qid in enumerate(bd['mine']):
            budget(cpu=time.process_time()-cpu);q=qmap[qid];c=store.case(q);ids=[b['id'] for b in c['blocks']];target=store.targets[qid]
            dense=greedy(c['ctx'],range(len(ids)),6);div=mmr(c['ctx'],c['x'],c['scores'],6)
            priority={dense:(0,0),div:(0,0)};parents=[];finals={dense,div};scores={};traces={}
            for ki,kind in enumerate(KINDS):
                selected,sc,tr,st=select(models[kind],c);finals.add(selected);priority[selected]=(0,ki+1);traces[kind]=tr
                for parent,children in tr:
                    parents.append([tuple(s) for s in children])
                    for rank,s in enumerate(children):
                        cov,full=coverage(target,[ids[i] for i in s]);over=1/(1+np.exp(-np.clip(sc.score(s),-40,40)))-.5*(cov+full)
                        value=(1 if rank==0 else 2,rank,-len(s),-float(over),ki)
                        if s not in priority or value<priority[s]:priority[s]=value
                # Exactly eight deterministic replacement attempts at most/trajectory.
                alternatives=[i for i in range(len(ids)) if i not in selected][:8]
                for j,i in enumerate(alternatives):
                    if not selected:break
                    s=tuple(sorted(set(selected)-{selected[j%len(selected)]}|{i}))
                    if c['ctx'](s):
                        finals.add(s);priority.setdefault(s,(3,j,ki))
            chosen=sorted(priority,key=lambda s:(priority[s],tuple(ids[i] for i in s)))[:64]
            records=[]
            for s in chosen:
                cov,full=coverage(target,[ids[i] for i in s]);records.append(dict(indices=list(s),cov=cov,full=full,tokens=c['ctx'].tokens(s)))
            fp,pp=preferences(records,parents,finals)
            pool[qid]=dict(block_ids=ids,subsets=records,final_pairs=fp,frontier_pairs=pp)
            stats.append(dict(tag=q['tag'],queries=1,sets=len(records),final_pairs=len(fp),frontier_pairs=len(pp),reachable_full=coverage(target,ids)[1],missing_final=int(not fp),missing_frontier=int(not pp)))
            if count%64==0:print('mine',seed,round_no,count,round(time.perf_counter()-wall,1),flush=True)
        save(path,pool)
        table(HERE/f'MINING_{seed}_R{round_no}.csv',[dict(tag=t,queries=sum(r['tag']==t for r in stats),**{k:sum(r[k] for r in stats if r['tag']==t) for k in ('sets','final_pairs','frontier_pairs','reachable_full','missing_final','missing_frontier')}) for t in ('hotpot','musique')])
        return pool
    finally:charge(f'mine_{seed}_{round_no}',cpu,wall,gpu_process_seconds=0)

def direct_pair_loss(logit,y,pairs):
    if not pairs:return logit.sum()*0
    a,b=zip(*pairs);a=list(a);b=list(b);u=y.mean(-1)
    return F.softplus(.2*(u[a]-u[b])-(logit[a]-logit[b])).mean()

class Mixed:
    def __init__(self,store,pool):
        self.store=store;self.static=Batches(store);self.pool=pool;self.qmap=self.static.qmap;self.arr={}
        for qid,s in pool.items():
            tag=self.qmap[qid]['tag'];idx=[store.index[tag][i] for i in s['block_ids']]
            self.arr[qid]=(np.asarray(store.xx[tag][idx]),np.array([store.lengths[tag][i] for i in idx],dtype='float32'),np.array([float(i in store.targets[qid]['coverage']) for i in s['block_ids']],dtype='float32'))
    def query(self,qid,rng):
        data=[[],[],[],[],[],[]];basepairs=[];final=[];front=[]
        def add(source,i):
            ss=self.static.ss[qid] if source=='static' else self.pool[qid];xx,ll,pp=self.static.pool[qid] if source=='static' else self.arr[qid]
            row=ss['subsets'][int(i)];idx=row['indices'];n=len(idx);pad=idx+[0]*(6-n);start=len(data[0])
            for dst,v in zip(data,(self.store.qx[qid],xx[pad],ll[pad],[1.]*n+[0.]*(6-n),[row['full'],row['cov']],pp[pad])):dst.append(v)
            return start
        ss=self.static.ss[qid]
        if ss['pairs']:
            a,b=ss['pairs'][int(rng.integers(len(ss['pairs'])))];basepairs.append((add('static',a),add('static',b)))
        for _ in range(4-len(data[0])):add('static',rng.integers(len(ss['subsets'])))
        ms=self.pool[qid]
        # Four mined base observations and up to one pair of each category.
        for _ in range(4):add('mined',rng.integers(len(ms['subsets'])))
        for key,dst in [('final_pairs',final),('frontier_pairs',front)]:
            if ms[key]:
                a,b=ms[key][int(rng.integers(len(ms[key])))];dst.append((add('mined',a),add('mined',b)))
        tensors=[torch.as_tensor(np.asarray(x),dtype=torch.float32,device='cuda') for x in data]
        return tensors,basepairs,final,front

def dev_evaluate(store,bd,net,static,model,epoch,seed,round_no):
    cpu=time.process_time();wall=time.perf_counter();net.cpu().float().eval();out=[];qmap=static.qmap
    with torch.inference_mode():
        for qid in bd['dev']:
            q=qmap[qid];c=store.case(q);ids=[b['id'] for b in c['blocks']];target=store.targets[qid]
            s,sc,tr,st=select(net,c);cov,full=coverage(target,[ids[i] for i in s])
            dense=greedy(c['ctx'],range(len(ids)),6);div=mmr(c['ctx'],c['x'],c['scores'],6)
            out.append(dict(query_id=qid,tag=q['tag'],model=model,seed=seed,round=round_no,epoch=epoch,coverage=cov,complete=full,output=float(1/(1+np.exp(-np.clip(sc.score(s),-40,40)))),dense_full=coverage(target,[ids[i] for i in dense])[1],mmr_full=coverage(target,[ids[i] for i in div])[1],reachable_full=coverage(target,ids)[1],tokens=c['ctx'].tokens(s)))
    net.float().cuda();vrng=np.random.default_rng(909);loss=[]
    with torch.inference_mode():
        for i in range(0,len(bd['dev']),8):
            ts,pairs=static.batch(bd['dev'][i:i+8],vrng);loss.append(float(objective(net,ts,pairs)[0]))
    means=lambda k:float(np.mean([np.mean([r[k] for r in out if r['tag']==t]) for t in ('hotpot','musique')]))
    result=dict(model=model,seed=seed,round=round_no,epoch=epoch,complete=means('complete'),coverage=means('coverage'),original_loss=float(np.mean(loss)))
    append(LOCAL/'dev_metrics.jsonl',dict(summary=result,rows=out));print('DEV',json.dumps(result),flush=True)
    return result

def train_round(store,bd,pool,round_no,seed=1729,replay=True):
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    mixed=Mixed(store,pool);kinds=list(KINDS)+(['H4-replay'] if replay else [])
    try:
        for name in kinds:
            dest=LOCAL/f'{name}_{seed}_r{round_no}.pt'
            if dest.exists():continue
            kind='H4' if name=='H4-replay' else name
            path=None if round_no==1 else LOCAL/f'{name}_{seed}_r{round_no-1}.pt'
            net,ck=load(kind,seed,path);net.cuda();torch.manual_seed(seed);opt=torch.optim.AdamW(net.parameters(),lr=3e-4,weight_decay=1e-4);best=None;updates=0
            for epoch in range(1,9):
                net.float().cuda().train();rng=np.random.default_rng(seed+1000*round_no+epoch);order=rng.permutation(bd['mine']);losses=[]
                for start in range(0,len(order),8):
                    budget(time.perf_counter()-wall,time.process_time()-cpu,reserve=True);qids=order[start:start+8];opt.zero_grad(set_to_none=True)
                    if name=='H4-replay':
                        ts,pairs=mixed.static.batch(qids,rng);loss=objective(net,ts,pairs)[0];loss.backward()
                    else:
                        parts=[]
                        for qid in qids:
                            ts,pairs,fp,pp=mixed.query(qid,rng)
                            # Base uses exactly four static + four mined sets; appended pairs only rank.
                            base=[t[:8] for t in ts];base_loss=objective(net,base,pairs)[0]
                            pred=net(*ts[:4]);value=base_loss+.5*direct_pair_loss(pred[:,0],ts[4],fp)+.5*direct_pair_loss(pred[:,0],ts[4],pp)
                            (value/len(qids)).backward();parts.append(float(value.detach()))
                        loss=torch.tensor(np.mean(parts))
                    torch.nn.utils.clip_grad_norm_(net.parameters(),1);opt.step();updates+=1;losses.append(float(loss.detach()))
                row=dict(model=name,seed=seed,round=round_no,epoch=epoch,updates=updates,loss=float(np.mean(losses)))
                append(LOCAL/'training.jsonl',row);print('TRAIN',json.dumps(row),flush=True)
                if epoch in (2,4,8):
                    result=dev_evaluate(store,bd,net,mixed.static,name,epoch,seed,round_no)
                    key=(result['complete'],result['coverage'],-result['original_loss'],-epoch)
                    checkpoint=dict(kind=kind,seed=seed,normal=ck['normal'],state={k:v.detach().cpu() for k,v in net.state_dict().items()},selection=result,updates=updates)
                    torch.save(checkpoint,LOCAL/f'{name}_{seed}_r{round_no}_e{epoch}.pt')
                    if best is None or key>best:
                        best=key;torch.save(checkpoint,LOCAL/f'{name}_{seed}_r{round_no}.best.pt')
            if name=='H4-replay':
                # The replay comparator follows the selected H4 update count,
                # not its own best epoch; both received all eight training epochs.
                chosen=torch.load(LOCAL/f'H4_{seed}_r{round_no}.pt',map_location='cpu',weights_only=False)['selection']['epoch']
                replay_ck=torch.load(LOCAL/f'{name}_{seed}_r{round_no}_e{chosen}.pt',map_location='cpu',weights_only=False)
                torch.save(replay_ck,dest)
            else:os.replace(LOCAL/f'{name}_{seed}_r{round_no}.best.pt',dest)
            save(LOCAL/f'{name}_{seed}_r{round_no}_training.json',dict(total_updates=updates,epochs=8))
            del net,opt;torch.cuda.empty_cache()
    finally:charge(f'train_{seed}_{round_no}',cpu,wall,gpu_process_seconds=time.perf_counter()-wall)

def baseline_dev(store,bd,seed=1729):
    dest=LOCAL/f'baseline_dev_{seed}.json'
    if dest.exists():return
    cpu=time.process_time();wall=time.perf_counter();static=Batches(store);out=[]
    try:
        for kind in KINDS:
            net,ck=load(kind,seed);out.append(dev_evaluate(store,bd,net,static,'v5-'+kind,0,seed,0));del net;torch.cuda.empty_cache()
        save(dest,out)
    finally:charge(f'baseline_dev_{seed}',cpu,wall,gpu_process_seconds=time.perf_counter()-wall)

def main():
    torch.set_num_threads(1);store=Store();bd=boundaries(store);action=sys.argv[1];seed=int(sys.argv[3]) if len(sys.argv)>3 else 1729;rd=int(sys.argv[2]) if len(sys.argv)>2 else 1
    if action=='mine':mine(store,bd,rd,seed)
    elif action=='train':train_round(store,bd,read(LOCAL/f'mined_{seed}_{rd}.json'),rd,seed,seed==1729)
    elif action=='baseline':baseline_dev(store,bd,seed)
if __name__=='__main__':main()
