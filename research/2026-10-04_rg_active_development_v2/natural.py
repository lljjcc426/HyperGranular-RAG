"""v2 fixed D1 comparison. No reference-plan or Gold import in execution."""
from common import *
from frontend import parse,extract,render,Fact
from runtime import LM,Encoder
from dataclasses import asdict
import numpy as np
import argparse

def index():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter()
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);enc=Encoder('cuda')
    try:
        for c in sorted(cases('D1'),key=lambda c:c['sampling_hash']):
            folder=LOCAL/'d1'/c['sampling_hash'];folder.mkdir(parents=True,exist_ok=True)
            if (folder/'index.json').exists():continue
            start=time.perf_counter();ws=make_windows(c['units'],tok)
            x=enc.encode([w.text for w in ws]);q=enc.encode([c['query']['question']],True)[0]
            order=sorted(range(len(ws)),key=lambda i:(-float(x[i]@q),ws[i].id))[:64]
            np.savez(folder/'vectors.npz',x=x[order],q=q)
            save(folder/'index.json',dict(query_id=c['query_id'],all_windows=len(ws),retained=len(order),
                windows=[asdict(ws[i]) for i in order],catalog=sorted({(w.title,w.source) for w in ws}),
                seconds=time.perf_counter()-start,truncated=sum(w.truncated for w in ws)))
            budget(time.perf_counter()-wall,time.process_time()-cpu)
            print('index',c['query_id'],len(order),flush=True)
    finally:charge('D1_index',cpu,wall,gpu_process_seconds=time.perf_counter()-wall)

def detail_cost(d):
    gs=d['generation'] if isinstance(d['generation'],list) else [d['generation']]
    vs=d['verification']
    return dict(extraction_calls=len(gs),verification_calls=sum(v.get('model_calls',1) for v in vs),
        seconds=sum(r['seconds'] for r in gs+vs),input_tokens=sum(r['input_tokens'] for r in gs+vs),
        output_tokens=sum(r.get('output_tokens',0) for r in gs+vs))

def execute(rerun=False):
    selection=read(HERE/'FRONTEND_SELECTION.json')
    if not selection['natural_execution_ready']:raise RuntimeError('FRONTEND_NOT_READY')
    version=selection['version'];threshold=selection['threshold']
    cc=sorted(cases('D1'),key=lambda c:c['sampling_hash'])
    if rerun:cc=[next(c for c in cc if c['tag']==tag) for tag in ('hotpot','musique')]
    adapted=bool(selection.get('adapter'))
    lm=LM(quantized=selection.get('precision')=='nf4',adapter=HERE/selection['adapter'] if adapted else None);enc=Encoder('cpu')
    try:
        for c in cc:
            folder=LOCAL/'d1'/c['sampling_hash'];outpath=folder/('frontend_rerun.json' if rerun else 'frontend_main.json')
            if outpath.exists():continue
            if not rerun:
                budget(time.perf_counter()-lm.wall+600,time.process_time()-lm.cpu+600)
            ix=read(folder/'index.json');ws=[engine.Window(**w) for w in ix['windows']];catalog=ix['catalog'];question=c['query']['question']
            with np.load(folder/'vectors.npz') as z:x=z['x'];q=z['q']
            cachepath=folder/'probes.jsonl';stored={r['window_id']:r for r in rows(cachepath)} if cachepath.exists() else {}
            if any(r['version']!=version for r in stored.values()):raise RuntimeError('CACHE_VERSION_MISMATCH')
            costs={};embeddings={};answers={};records=[]
            def embed(text):
                if text not in embeddings:
                    start=time.perf_counter();v=enc.encode([text],True)[0];embeddings[text]=(v,time.perf_counter()-start)
                return embeddings[text][0]
            def callback(w):
                if not rerun and w.id in stored:
                    item=stored[w.id];fs=[Fact(**f) for f in item['facts']];d=item['detail']
                else:
                    fs,d=extract(lm,question,slots,w,catalog,version+'_D1_extract'+('_rerun' if rerun else ''))
                    if not rerun:
                        item=dict(window_id=w.id,version=version,facts=[asdict(f) for f in fs],detail=d)
                        append(cachepath,item);stored[w.id]=item
                costs[w.id]=detail_cost(d);return fs
            parsed=parse(lm,question,version+'_D1_parse'+('_rerun' if rerun else ''));slots=parsed['slots']
            probe=engine.LazyProbe(callback)
            methods=('GB-feedback','KM-feedback') if rerun else engine.METHODS
            for method in methods:
                if slots and method!='Dense-window':
                    result=engine.search(method,question,slots,ws,x,q,embed,probe,threshold,uncached=rerun,max_probes=16 if rerun else 32)
                else:result=dict(snapshots={},trace=[],splits=[],seconds=0.)
                for b in ((16,) if rerun else (16,32)):
                    available=[k for k in result['snapshots'] if k<=b]
                    snap=result['snapshots'][max(available)] if available else dict(states=[],complete=False,conditional_texts=[],leaf_count=0,accepted_facts=0)
                    context=render(question,ws,snap['states'],len(slots) or 1,lm.ids)
                    # Reader runs later in a separate unadapted FP16 process.
                    # This avoids changing its precision or exceeding 8GB VRAM.
                    hit=False;answer=dict(status='PENDING_UNADAPTED_FP16_READER',seconds=0.)
                    trace=result['trace'][:b];used=[costs[t['window']] for t in trace]
                    r=dict(query_id=c['query_id'],tag=c['tag'],stratum=c['stratum'],method=method,budget=b,version=version,
                        parse=parsed if method!='Dense-window' else None,slots=slots if method!='Dense-window' else [],
                        context=context,answer=answer,reader_cache_hit=hit,trace=trace,
                        splits=[s for s in result['splits'] if s['step']<=b],complete=snap['complete'],accepted_facts=snap['accepted_facts'],
                        states=[dict(binding=binding,facts=[asdict(f) for f in fs]) for binding,fs in snap['states']],
                        logical_probes=len(trace),logical_parse_calls=int(method!='Dense-window'),
                        logical_parse_seconds=parsed['generation']['seconds'] if method!='Dense-window' else 0,
                        logical_index_seconds=ix['seconds'],logical_reader_seconds=answer['seconds'],
                        logical_conditional_seconds=sum(embeddings[t][1] for t in snap['conditional_texts']),
                        search_transaction_seconds=result['seconds'],search_transaction_max_probes=16 if rerun else 32,
                        conditional_queries=len(snap['conditional_texts']),leaf_count=snap['leaf_count'],
                        **{'logical_'+key:sum(z[key] for z in used) for key in ('extraction_calls','verification_calls','seconds','input_tokens','output_tokens')})
                    records.append(r)
            save(outpath,records);print('D1',c['tag'],c['query_id'],'rerun',rerun,flush=True)
    finally:lm.close('D1_rerun' if rerun else 'D1_main')

def readers(rerun=False):
    lm=LM()
    try:
        for c in sorted(cases('D1'),key=lambda c:c['sampling_hash']):
            folder=LOCAL/'d1'/c['sampling_hash'];src=folder/('frontend_rerun.json' if rerun else 'frontend_main.json');dest=folder/('rerun.json' if rerun else 'main.json')
            if not src.exists() or dest.exists():continue
            records=read(src);cache={}
            for r in records:
                prompt=r['context']['prompt'];hit=prompt in cache and not rerun
                answer=cache[prompt] if hit else lm.generate(prompt,'You are a careful evidence assistant.',32,'D1_unadapted_fp16_reader'+('_rerun' if rerun else ''))
                cache[prompt]=answer;r.update(answer=answer,reader_cache_hit=hit,logical_reader_seconds=answer['seconds'])
            save(dest,records);print('reader',c['query_id'],'rerun',rerun,flush=True)
    finally:lm.close('D1_reader_rerun' if rerun else 'D1_reader_main')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['index','run','rerun','read','read-rerun']);a=ap.parse_args()
    if a.action=='index':index()
    elif a.action.startswith('read'):readers(a.action=='read-rerun')
    else:execute(a.action=='rerun')
