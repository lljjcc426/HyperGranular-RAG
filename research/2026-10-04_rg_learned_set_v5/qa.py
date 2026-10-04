"""Common unadapted FP16 reader; only exact generation identities reuse outputs."""
from common import *
from dataset import Store,Context
import numpy as np
runtime=load_module('v5_original_fp16_runtime',V2/'runtime.py')
scoring=load_module('v5_canonical_score',HERE.parent/'2026-10-03_evidence_delivery_repair/score.py')

def run(seed=1729,mode='main'):
    store=Store();qmap={q['query_id']:q for q in store.queries};scorers=scoring.scorers()
    source=rows(LOCAL/f'selections_{seed}_{mode}.jsonl')
    allowed={'Dense','MMR','H1','H2','DeepSets','H4-Flat','H4-GB','H4-KM'}
    source=[r for r in source if r['panel'] and r['method'] in allowed]
    dest=LOCAL/'qa.jsonl';done={(r['query_id'],r['seed'],r['setting'],r['budget'],r['method']) for r in rows(dest)} if dest.exists() else set()
    cp=LOCAL/'reader_cache.jsonl';cache={r['key']:r for r in rows(cp)} if cp.exists() else {}
    # v4 uses exactly this unchanged runtime and P2 identity. No raw text-only hits.
    if (V4/'local/cache.jsonl').exists():
        for r in rows(V4/'local/cache.jsonl'):
            if r['identity'].get('schema')==P.SCHEMA:cache.setdefault(r['key'],r)
    calls=len(rows(LOCAL/'calls.jsonl')) if (LOCAL/'calls.jsonl').exists() else 0
    lm=None
    try:
        for r in source:
            logical=(r['query_id'],r['seed'],r['setting'],r['budget'],r['method'])
            if logical in done:continue
            q=qmap[r['query_id']];bb=[store.corpus[r['tag']][store.index[r['tag']][i]] for i in r['selected']]
            ctx=Context(q['question'],bb,store.tok,r['budget']);user=ctx.user(tuple(range(len(bb))));ident=P.identity(store.tok,user,'P2');key=digest(ident)
            assert len(ident['input_ids'])<=r['budget']
            hit=key in cache
            if hit:
                stored=cache[key]
                if stored['identity']!=ident:raise ValueError('CACHE_IDENTITY_MISMATCH')
                g=stored['generation']
            else:
                if calls>=2992:raise RuntimeError('READER_CAP_RESERVED_RERUN')
                if lm is None:lm=runtime.LM(quantized=False,adapter=None)
                g=lm.generate(user,P.SYSTEM,128,'v5_reader',P.SCHEMA);calls+=1
                assert g['input_digest']==digest(ident['input_ids'])
                stored=dict(key=key,identity=ident,generation=g,origin='v5');append(cp,stored);cache[key]=stored
            answer,status=P.parse(g['text'],'P2');em,f1=scoring.answer_score(q['tag'],answer,store.targets[q['query_id']]['gold'],scorers)
            out={**r,'selected':r['selected'],'key':key,'prediction':answer,'status':status,'em':em,'f1':f1,'cache_hit':hit,'input_tokens':g['input_tokens'],'output_tokens':g['output_tokens'],'reader_seconds':g['seconds'],'unknown':answer.casefold()=='unknown','eos':g['ended_eos'],'hit_limit':g['output_tokens']>=128 and not g['ended_eos']}
            append(dest,out);done.add(logical)
            if len(done)%64==0:print('QA',len(done),'new_calls',calls,flush=True)
    finally:
        if lm is not None:lm.close(f'qa_{seed}_{mode}')
        summarize()

def summarize():
    if not (LOCAL/'qa.jsonl').exists():return
    data=rows(LOCAL/'qa.jsonl');out=[]
    for key in sorted(set((r['seed'],r['setting'],r['budget'],r['method'],r['tag']) for r in data)):
        rr=[r for r in data if (r['seed'],r['setting'],r['budget'],r['method'],r['tag'])==key]
        out.append(dict(zip(('seed','setting','budget','method','tag'),key),queries=len(rr),**{k:float(np.mean([r[k] for r in rr])) for k in ('em','f1','coverage','complete','blocks','tokens','reader_seconds','input_tokens','output_tokens','unknown','hit_limit','eos')},protocol_failures=sum(r['status']!='VALID_ANSWER_FIELD' for r in rr),cache_hits=sum(r['cache_hit'] for r in rr)))
    table(HERE/'QA_RESULTS.csv',out)

def rerun():
    data=rows(LOCAL/'qa.jsonl');cache={r['key']:r for r in rows(LOCAL/'reader_cache.jsonl')};selected=[]
    for tag in ('hotpot','musique'):
        rr=sorted([r for r in data if r['seed']==1729 and r['setting']=='opened' and r['budget']==1024 and r['tag']==tag and r['method'] in ('Dense','H4-Flat')],key=lambda r:digest([r['query_id'],r['method']]))[:4];selected+=rr
    store=Store();qmap={q['query_id']:q for q in store.queries};lm=runtime.LM(False,None);results=[]
    try:
        for r in selected:
            bb=[store.corpus[r['tag']][store.index[r['tag']][i]] for i in r['selected']];user=Context(qmap[r['query_id']]['question'],bb,store.tok,r['budget']).user(range(len(bb)))
            g=lm.generate(user,P.SYSTEM,128,'v5_reader_rerun',P.SCHEMA);old=cache[r['key']]['generation']
            results.append(dict(query_hash=digest(r['query_id']),method=r['method'],same_output_ids=g['output_ids']==old['output_ids'],same_input=g['input_digest']==old['input_digest']))
    finally:lm.close('qa_uncached_rerun');save(HERE/'READER_RERUN.json',results)

if __name__=='__main__':rerun() if sys.argv[1]=='rerun' else run(int(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else 'main')
