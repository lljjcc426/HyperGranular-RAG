"""Small real FIT capability check before full training, no reader reward."""
from train import *

def main():
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    store=Store();data=Batches(store);normal=read(LOCAL/'normalization.json')
    qs=[q['query_id'] for tag in ('hotpot','musique') for q in sorted([q for q in store.queries if q['role']=='FIT' and q['tag']==tag],key=lambda q:q['group'])[:8]]
    batches=[data.batch(qs[i:i+8],np.random.default_rng(1729)) for i in (0,8)];results=[]
    try:
        for kind in ('H1','H2','H4','DeepSets'):
            torch.manual_seed(1729);net=Selector(kind,**normal).cuda();opt=torch.optim.AdamW(net.parameters(),lr=.001,weight_decay=.0001)
            for step in range(101):
                ts,pairs=batches[step%2];opt.zero_grad(set_to_none=True);loss,c,n,terms=objective(net,ts,pairs)
                if not torch.isfinite(loss):raise ValueError('NONFINITE_CALIBRATION')
                loss.backward();grad=[]
                if hasattr(net,'w'):grad=net.w.weight.grad.reshape(2,net.order-1,32,128).norm(dim=(2,3)).mean(0).detach().cpu().tolist()
                if step in (0,20,100):results.append(dict(model=kind,step=step,fit_queries=16,loss=float(loss.detach()),pair_accuracy=c/max(n,1),pairs=n,terms=json.dumps(terms),grad=json.dumps(grad)))
                torch.nn.utils.clip_grad_norm_(net.parameters(),1);opt.step()
            del net,opt;torch.cuda.empty_cache()
    finally:
        table(HERE/'FIT_CAPABILITY.csv',results);charge('real_fit_capability',cpu,wall,gpu_process_seconds=time.perf_counter()-wall)
    print(json.dumps(results),flush=True)

if __name__=='__main__':main()
