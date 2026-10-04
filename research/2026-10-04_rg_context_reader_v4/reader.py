"""FP16 base reader, exact identity cache, safe per-request budget boundaries."""
from common import *
from protocols import *
runtime=load_module('rg_v4_fp16_runtime_dependency',V2/'runtime.py')
class LM(runtime.LM):
    def generate(self,*a,**kw):
        cs=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else []
        stage=kw.get('stage',a[3] if len(a)>3 else '')
        if len(cs)>=456:raise RuntimeError('READER_CALL_CAP')
        if 'D0' in stage and sum('D0' in r['stage'] for r in cs)>=64:raise RuntimeError('D0_CALL_CAP')
        if 'rerun' in stage and sum('rerun' in r['stage'] for r in cs)>=8:raise RuntimeError('RERUN_CALL_CAP')
        return super().generate(*a,**kw)
def old_cache(tok):
    cache={}
    # Pure legacy implementation is reused, same source model FP16 / adapter off.
    for c in selected():
        for r in read(V3/'local/natural'/c['sampling_hash']/'answers_16.json'):
            u=r['context']['prompt'];ident=identity(tok,u,'P0');g=r['answer']
            if digest(ident['input_ids'])!=g['input_digest']:raise ValueError('LEGACY_INPUT_IDENTITY')
            if g['schema_digest']!=digest(None):raise ValueError('LEGACY_NOT_UNCONSTRAINED')
            cache[digest(ident)]=dict(identity=ident,generation=g,origin='v3_exact_FP16_greedy32',source_query=c['query_id'])
    return cache
def run(mode):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    cache=old_cache(tok);cp=LOCAL/'cache.jsonl'
    if cp.exists():cache.update({r['key']:r for r in rows(cp)})
    dest=LOCAL/(mode+'.jsonl');done={(r['query_id'],r['context'],r['protocol']) for r in rows(dest)} if dest.exists() else set()
    if mode=='D0':contexts=[dict(r,context='D0_D') for r in read(LOCAL/'d0_contexts.json')]
    else:
        allc=read(LOCAL/'contexts.json');wanted=('D','A_G','L_G','R') if mode=='core' else ('A_F','L_F','A_K','L_K')
        contexts=[r for r in allc if r['context'] in wanted]
        if mode=='rerun':
            sample=selected();chosen={c['query_id'] for tag in ('hotpot','musique') for c in [z for z in sample if z['tag']==tag][:2]}
            contexts=[r for r in allc if r['query_id'] in chosen and r['context'] in ('D','A_G')]
    lm=None
    try:
        for c in contexts:
            for protocol in (('P2',) if mode=='rerun' else PROTOCOLS):
                logical=(c['query_id'],c['context'],protocol)
                if logical in done:continue
                user=prompt(c['question'],c['body'],protocol);ident=identity(tok,user,protocol);key=digest(ident)
                if len(ident['input_ids'])>1024:raise ValueError('INPUT_CAP')
                hit=key in cache and mode!='rerun'
                if hit:
                    stored=cache[key]
                    if stored['identity']!=ident:raise ValueError('CACHE_IDENTITY')
                    g=stored['generation'];origin=stored['origin']
                else:
                    if lm is None:lm=LM(quantized=False,adapter=None)
                    g=lm.generate(user,SYSTEM,ident['generation']['max_new_tokens'],'v4_reader_'+mode,SCHEMA if protocol=='P2' else None)
                    if g['input_digest']!=digest(ident['input_ids']):raise ValueError('EXECUTED_INPUT_IDENTITY')
                    origin='v4_'+mode
                    if mode!='rerun':
                        stored=dict(key=key,identity=ident,generation=g,origin=origin);append(cp,stored);cache[key]=stored
                answer,status=parse(g['text'],protocol)
                out=dict(query_id=c['query_id'],tag=c['tag'],context=c['context'],protocol=protocol,key=key,generation=g,
                    parsed_answer=answer,parse_status=status,cache_hit=hit,origin=origin,
                    hit_output_limit=g['output_tokens']>=ident['generation']['max_new_tokens'] and not g['ended_eos'],
                    unknown=answer.strip().casefold()=='unknown',nonempty=bool(answer.strip()),body_digest=digest(c['body']))
                append(dest,out);done.add(logical)
                print(mode,len(done),'new' if not hit else 'reuse',c['tag'],c['context'],protocol,status,flush=True)
    finally:
        if lm is not None:lm.close('reader_'+mode)
if __name__=='__main__':run(sys.argv[1])
