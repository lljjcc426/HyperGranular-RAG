"""Five-arm exposed-development comparison. No label import in this runner."""
from common import *
from frontend import scope,extract_task,legacy,task_identity
from runtime import LM,Encoder
from delivery import Delivery
from search import search
import numpy as np,argparse

METHODS=('Dense-window','Flat-binding','GB-uniform','GB-feedback','KM-feedback')
IDENTITY=dict(version='RG-evidence-delivery-v3.0/v35',model='aa8e72537993ba99e69dfaafa59ed015b17504d1',
    adapter='v2/adapters/v27',precision='NF4-double-bfloat16',verifier='base-only',decoding='greedy1',
    tokenizer='same-model-snapshot',schema='v3-tristate-scoped',window='v2-sentence-neighbours',
    code={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('frontend.py','state.py','search.py','delivery.py','runtime.py','source_rules.py')})

def load_inputs(c):
    folder=old_case(c);ix=read(folder/'index.json');ws=[engine.Window(**w) for w in ix['windows']]
    with np.load(folder/'vectors.npz') as z:x=z['x'];q=z['q']
    old=read(folder/'main.json');parsed=next(r['parse'] for r in old if r['parse'] is not None)
    return ix,ws,x,q,parsed,old

def execute(budget_point,rerun=False):
    sample=selected()
    if rerun:sample=[next(c for c in sample if c['tag']==tag) for tag in ('hotpot','musique')]
    lm=LM(quantized=True,adapter=V2/'adapters/v27');enc=Encoder('cpu')
    try:
        for c in sample:
            folder=LOCAL/'natural'/c['sampling_hash'];folder.mkdir(parents=True,exist_ok=True)
            dest=folder/(f'rerun_{budget_point}.json' if rerun else f'main_{budget_point}.json')
            if dest.exists():continue
            ix,ws,x,q,parsed,old=load_inputs(c);question=c['query']['question'];slots=parsed['slots']
            d=Delivery(question,ws,lm.ids,{w.id:float(x[i]@q) for i,w in enumerate(ws)})
            planpath=folder/'plan.json'
            if planpath.exists():plan=read(planpath)
            else:
                constraints,g=scope(lm,question,slots,'C_scope')
                plan=dict(slots=slots,constraints=constraints,scope_generation=g,parse=parsed,parse_reuse='V2_EXACT_SAME_PARSER_ADAPTER_MODEL',identity=IDENTITY)
                save(planpath,plan)
            if plan['identity']!=IDENTITY:raise RuntimeError('C_FRONTEND_VERSION_CHANGED')
            constraints=plan['constraints'];cachepath=folder/'tasks.jsonl'
            stored={r['key']:r for r in rows(cachepath)} if cachepath.exists() else {}
            ep=folder/'conditional.jsonl';emb={r['text']:r for r in rows(ep)} if ep.exists() else {}
            def embed(text):
                if rerun or text not in emb:
                    t=time.perf_counter();v=enc.encode([text],True)[0]
                    r=dict(text=text,vector=v.tolist(),seconds=time.perf_counter()-t)
                    if not rerun:append(ep,r)
                    emb[text]=r
                return np.array(emb[text]['vector'])
            def request(key,slot,binding,cs,w):
                hit=key in stored and not rerun
                if hit:r=stored[key]['result']
                else:
                    r=extract_task(lm,question,slots,constraints,slot,binding,w,ix['catalog'],'C_v35_task'+('_rerun' if rerun else ''))
                    if not rerun:
                        item=dict(key=key,result=r);append(cachepath,item);stored[key]=item
                return r,hit
            records=[]
            for method in (('GB-feedback','KM-feedback') if rerun else METHODS):
                if method=='Dense-window' or not slots:
                    result=dict(states=[],trace=[],splits=[],facts=[],conditional_texts=[],seconds=0.,group_repairs=0)
                else:result=search(method,question,slots,constraints,ws,x,q,embed,request,IDENTITY,d,budget_point)
                context=d.partial(result['states'],slots,constraints) if method!='Dense-window' else d.record(d.dense,'Dense',fallback=True)
                rs=dict(query_id=c['query_id'],tag=c['tag'],stratum=c['stratum'],method=method+'-v3',budget=budget_point,
                    context=context,result=result,slots=slots if method!='Dense-window' else [],constraints=constraints if method!='Dense-window' else [],
                    parse=parsed if method!='Dense-window' else None,scope=plan['scope_generation'] if method!='Dense-window' else None,
                    conditional_seconds=sum(emb[t]['seconds'] for t in result['conditional_texts']),index_seconds=ix['seconds'],identity=IDENTITY)
                if budget_point==16 and not rerun and (folder/'main_8.json').exists():
                    previous=next(r for r in read(folder/'main_8.json') if r['method']==rs['method'])
                    if [t['task'] for t in previous['result']['trace']]!=[t['task'] for t in result['trace'][:8]]:raise RuntimeError('TASK_PREFIX_CHANGED')
                records.append(rs);print(c['tag'],c['query_id'],method,budget_point,len(result['trace']),len(result['facts']),len(context.get('new_spans',[])),flush=True)
            save(dest,records)
    finally:lm.close('C_frontend_'+('rerun' if rerun else str(budget_point)))

def readers(budget_point,rerun=False):
    sample=selected()
    if rerun:sample=[next(c for c in sample if c['tag']==tag) for tag in ('hotpot','musique')]
    cache={}
    for c in sample:
        for r in read(old_case(c)/'main.json'):cache[r['context']['prompt']]=r['answer']
    for p in (LOCAL/'natural').glob('*/answers_*.json'):
        for r in read(p):cache[r['context']['prompt']]=r['answer']
    lm=None
    try:
        for c in sample:
            folder=LOCAL/'natural'/c['sampling_hash'];src=folder/(f'rerun_{budget_point}.json' if rerun else f'main_{budget_point}.json')
            dest=folder/(f'answers_rerun_{budget_point}.json' if rerun else f'answers_{budget_point}.json')
            if dest.exists() or not src.exists():continue
            records=read(src)
            for r in records:
                prompt=r['context']['prompt'];hit=prompt in cache and not rerun
                if hit:r['answer']=cache[prompt]
                else:
                    if lm is None:lm=LM()
                    r['answer']=lm.generate(prompt,'You are a careful evidence assistant.',32,'C_reader'+('_rerun' if rerun else ''))
                    cache[prompt]=r['answer']
                r['reader_cache_hit']=hit
                # Prompt text + same chat template implies same tokens; verify
                # actual input identity for reused predictions, not just a label.
                if lm is not None and digest(lm.ids(prompt))!=r['answer']['input_digest']:raise RuntimeError('READER_INPUT_IDENTITY')
            save(dest,records);print('C_reader',c['query_id'],budget_point,'rerun',rerun,flush=True)
    finally:
        if lm is not None:lm.close('C_reader_'+('rerun' if rerun else str(budget_point)))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['run','read','rerun','read-rerun']);ap.add_argument('--budget',type=int,choices=[8,16],default=8);a=ap.parse_args()
    if a.action.startswith('read'):readers(a.budget,a.action=='read-rerun')
    else:execute(a.budget,a.action=='rerun')
