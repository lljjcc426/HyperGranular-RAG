"""Actual QA on the unchanged exposed panel; cache identity is the v5 P2 identity."""
from support import *
from aligned import Store,Context,load,select,boundaries
from dataset import coverage
import numpy as np
import torch

def chosen(kind,seed):
    paths=list(LOCAL.glob(f'{kind}_{seed}_r[12].pt'))
    if not paths:raise ValueError('NO_COMPLETE_TRAINING_ROUND')
    def key(p):
        c=torch.load(p,map_location='cpu',weights_only=False);r=c['selection']
        return (r['complete'],r['coverage'],-r['original_loss'],-r['round'],-r['epoch'])
    return max(paths,key=key)

def select_panel(seed=1729):
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);store=Store();bd=boundaries(store);qmap={q['query_id']:q for q in store.queries};dest=LOCAL/f'qa_selection_{seed}.jsonl'
    done={(r['query_id'],r['method']) for r in rows(dest)} if dest.exists() else set()
    modelpaths={k:chosen(k,seed) for k in KINDS}
    if seed==1729:
        hp=modelpaths['H4'];modelpaths['H4-replay']=LOCAL/hp.name.replace('H4_','H4-replay_')
    models={k:load('H4' if k=='H4-replay' else k,seed,p)[0] for k,p in modelpaths.items()}
    save(LOCAL/f'qa_checkpoints_{seed}.json',{k:p.name for k,p in modelpaths.items()})
    try:
        for j,qid in enumerate(bd['qa']):
            budget(cpu=time.process_time()-cpu);q=qmap[qid]
            for kind,net in models.items():
                method=kind if kind=='H4-replay' else kind+'-aligned'
                if (qid,method) in done:continue
                start=time.perf_counter();c=store.case(q);s,sc,tr,stats=select(net,c);ids=[c['blocks'][i]['id'] for i in s];cov,full=coverage(store.targets[qid],ids)
                row=dict(query_id=qid,tag=q['tag'],stratum=q['stratum'],seed=seed,method=method,budget=1024,selected=ids,coverage=cov,complete=full,blocks=len(s),tokens=c['ctx'].tokens(s),selection_seconds=time.perf_counter()-start,checkpoint=modelpaths[kind].name)
                append(dest,row)
            if j%32==0:print('qa_selection',seed,j,flush=True)
    finally:charge(f'qa_selection_{seed}',cpu,wall,gpu_process_seconds=0)

def run(seed=1729):
    store=Store();qmap={q['query_id']:q for q in store.queries};src=rows(LOCAL/f'qa_selection_{seed}.jsonl');dest=LOCAL/'qa.jsonl'
    oldqa=rows(V5/'local/qa.jsonl')
    for r in oldqa:
        if r['seed']==1729 and r['setting']=='opened' and r['budget']==1024 and r['method'] in ('Dense','MMR','H4-Flat'):
            src.append({**r,'seed':seed,'method':{'Dense':'Dense','MMR':'MMR','H4-Flat':'v5-H4'}[r['method']]}) if seed==1729 else None
    done={(r['query_id'],r['seed'],r['method']) for r in rows(dest)} if dest.exists() else set()
    cache={r['key']:r for r in rows(V5/'local/reader_cache.jsonl')}
    cp=LOCAL/'reader_cache.jsonl'
    if cp.exists():cache.update({r['key']:r for r in rows(cp)})
    runtime=load_module('v6_reader_runtime',V2/'runtime.py')
    runtime.LOCAL=LOCAL;runtime.budget=budget;runtime.charge=charge
    score=load_module('v6_score',HERE.parent/'2026-10-03_evidence_delivery_repair/score.py');scorers=score.scorers();lm=None
    calls=len(rows(LOCAL/'calls.jsonl')) if (LOCAL/'calls.jsonl').exists() else 0
    try:
        for r in src:
            key0=(r['query_id'],seed,r['method'])
            if key0 in done:continue
            q=qmap[r['query_id']];bb=[store.corpus[r['tag']][store.index[r['tag']][i]] for i in r['selected']]
            user=Context(q['question'],bb,store.tok).user(range(len(bb)));ident=P.identity(store.tok,user,'P2');key=digest(ident);hit=key in cache
            if hit:
                if ident!=cache[key]['identity']:raise ValueError('CACHE_IDENTITY_MISMATCH')
                g=cache[key]['generation']
            else:
                if calls>=1192:raise RuntimeError('READER_CAP')
                if lm is None:lm=runtime.LM(False,None)
                g=lm.generate(user,P.SYSTEM,128,'v6_reader',P.SCHEMA);calls+=1
                assert len(ident['input_ids'])<=1024 and g['input_digest']==digest(ident['input_ids'])
                cache[key]=dict(key=key,identity=ident,generation=g,origin='v6');append(cp,cache[key])
            answer,status=P.parse(g['text'],'P2');em,f1=score.answer_score(q['tag'],answer,store.targets[q['query_id']]['gold'],scorers)
            row={**r,'key':key,'prediction':answer,'status':status,'em':em,'f1':f1,'cache_hit':hit,'input_tokens':g['input_tokens'],'output_tokens':g['output_tokens'],'reader_seconds':g['seconds'],'unknown':answer.casefold()=='unknown','eos':g['ended_eos'],'hit_limit':g['output_tokens']>=128 and not g['ended_eos']}
            append(dest,row);done.add(key0)
            if len(done)%64==0:print('qa',len(done),'actual_new',calls,flush=True)
    finally:
        if lm is not None:lm.close(f'qa_{seed}')
        summarize()

def summarize():
    data=rows(LOCAL/'qa.jsonl') if (LOCAL/'qa.jsonl').exists() else [];out=[]
    for key in sorted({(r['seed'],r['method'],r['tag']) for r in data}):
        rr=[r for r in data if (r['seed'],r['method'],r['tag'])==key]
        out.append(dict(zip(('seed','method','tag'),key),queries=len(rr),**{k:float(np.mean([r[k] for r in rr])) for k in ('f1','em','coverage','complete','tokens','blocks','input_tokens','output_tokens','reader_seconds')},cache_hits=sum(r['cache_hit'] for r in rr),format_failures=sum(r['status']!='VALID_ANSWER_FIELD' for r in rr)))
    table(HERE/'QA_RESULTS.csv',out)
    dd=rows(LOCAL/'dev_metrics.jsonl') if (LOCAL/'dev_metrics.jsonl').exists() else [];out=[]
    for batch in dd:
        for tag in ('hotpot','musique'):
            rr=[r for r in batch['rows'] if r['tag']==tag];s=batch['summary'];out.append({**s,'tag':tag,'queries':len(rr),**{k:float(np.mean([r[k] for r in rr])) for k in ('complete','coverage','output','dense_full','mmr_full','reachable_full','tokens')},'lost_dense_full':sum(r['dense_full'] and not r['complete'] for r in rr),'gained_dense_full':sum(r['complete'] and not r['dense_full'] for r in rr),'lost_mmr_full':sum(r['mmr_full'] and not r['complete'] for r in rr),'gained_mmr_full':sum(r['complete'] and not r['mmr_full'] for r in rr)})
    table(HERE/'SEARCH_ALIGNED_RESULTS.csv',out)
    if (LOCAL/'training.jsonl').exists():table(HERE/'TRAINING.csv',rows(LOCAL/'training.jsonl'))

def rerun():
    data=rows(LOCAL/'qa.jsonl');cache={r['key']:r for r in rows(LOCAL/'reader_cache.jsonl')};store=Store();qmap={q['query_id']:q for q in store.queries}
    picked=sorted([r for r in data if r['seed']==1729 and r['key'] in cache],key=lambda r:digest([r['query_id'],r['method']]))[:8]
    runtime=load_module('v6_reader_check',V2/'runtime.py');runtime.LOCAL=LOCAL;runtime.budget=budget;runtime.charge=charge;lm=runtime.LM(False,None);out=[]
    try:
        for r in picked:
            bb=[store.corpus[r['tag']][store.index[r['tag']][i]] for i in r['selected']];user=Context(qmap[r['query_id']]['question'],bb,store.tok).user(range(len(bb)))
            g=lm.generate(user,P.SYSTEM,128,'v6_uncached',P.SCHEMA);previous=cache[r['key']]['generation']
            out.append(dict(method=r['method'],tag=r['tag'],same_input=g['input_digest']==previous['input_digest'],same_output_ids=g['output_ids']==previous['output_ids']))
    finally:lm.close('uncached_reader_check');save(HERE/'READER_RERUN.json',out)

if __name__=='__main__':
    action=sys.argv[1];seed=int(sys.argv[2]) if len(sys.argv)>2 else 1729
    start_cpu=time.process_time();start_wall=time.perf_counter()
    from support import usage
    before_cpu=usage()[1]
    try:
        {'select':lambda:select_panel(seed),'run':lambda:run(seed),'summary':summarize,'rerun':rerun}[action]()
    finally:
        # LM.close accounts for model lifetime; include setup and final aggregation
        # without charging that same CPU interval twice.
        accounted=usage()[1]-before_cpu
        append(HERE/'cost.jsonl',dict(stage=f'qa_{action}_{seed}_overhead',cpu_seconds=max(0,time.process_time()-start_cpu-accounted),wall_seconds=time.perf_counter()-start_wall,gpu_process_seconds=0))
