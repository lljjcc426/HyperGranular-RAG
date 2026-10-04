"""Final input/output binding, prescribed reader replay, and cost accounting."""
from common import *
from protocols import *
def finish():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    contexts=read(LOCAL/'contexts.json');cm={(r['query_id'],r['context']):r for r in contexts}
    ps=rows(LOCAL/'core.jsonl')+rows(LOCAL/'extra.jsonl');pm={(r['query_id'],r['context'],r['protocol']):r for r in ps}
    expected={(r['query_id'],r['context'],p) for r in contexts for p in PROTOCOLS}
    if set(pm)!=expected or len(ps)!=384:raise ValueError('FACTORIAL_DENOMINATOR')
    cache={r['key']:r for r in rows(LOCAL/'cache.jsonl')}
    for key,r in pm.items():
        c=cm[key[:2]];ident=identity(tok,prompt(c['question'],c['body'],r['protocol']),r['protocol'])
        if digest(ident)!=r['key'] or digest(ident['input_ids'])!=r['generation']['input_digest']:raise ValueError('OUTPUT_INPUT_IDENTITY')
        if len(ident['input_ids'])>1024 or r['body_digest']!=digest(c['body']):raise ValueError('BODY_OR_CAP')
        if r['key'] in cache and cache[r['key']]['generation']['output_ids']!=r['generation']['output_ids']:raise ValueError('CACHE_OUTPUT_CHANGED')
        answer,status=parse(r['generation']['text'],r['protocol'])
        if answer!=r['parsed_answer'] or status!=r['parse_status']:raise ValueError('FIELD_SCORING_PROTOCOL')
    reruns=rows(LOCAL/'rerun.jsonl');out=[]
    if len(reruns)!=8:raise ValueError('REPLAY_DENOMINATOR')
    for r in reruns:
        m=pm[r['query_id'],r['context'],r['protocol']]
        same_input=m['key']==r['key'];same_output=m['generation']['output_ids']==r['generation']['output_ids']
        out.append(dict(query_id=r['query_id'],context=r['context'],protocol=r['protocol'],input_identical=same_input,output_tokens_identical=same_output,cache_bypassed=not r['cache_hit']))
        if not same_input or not same_output or r['cache_hit']:raise ValueError('READER_REPLAY_MISMATCH')
    table(HERE/'RERUN_CHECK.csv',out)
    save(HERE/'FINAL_CHECK.json',dict(logical_rows=384,queries=16,contexts=8,protocols=3,all_input_identities_match=True,
        common_body_per_context=True,all_inputs_at_most_1024=True,prescribed_uncached_replays=8,output_token_identity=True,
        limitations='Source coordinates were checked by tests.py before inference. This check does not certify semantic evidence sufficiency or independent confirmation.'))
    charge('final_binding_check',cpu,wall)
    calls=rows(LOCAL/'calls.jsonl');cost=rows(HERE/'cost.jsonl');physical=[]
    for stage in sorted({r['stage'] for r in calls}):
        rs=[r for r in calls if r['stage']==stage]
        physical.append(dict(stage=stage,actual_calls=len(rs),input_tokens=sum(r['input_tokens'] for r in rs),output_tokens=sum(r['output_tokens'] for r in rs),generation_seconds=sum(r['seconds'] for r in rs)))
    table(HERE/'ACTUAL_CALL_COSTS.csv',physical)
    before=read(V3/'RESOURCE_SUMMARY.json');gpu=sum(r.get('gpu_process_seconds',0) for r in cost);cpusec=sum(r['cpu_seconds'] for r in cost)
    save(HERE/'RESOURCE_AND_IDENTITY.json',dict(spec_id='HGRAG-CONTEXT-READER-V4-20261004',reference_commit='93e27c82333d83ee276113ad586cfe26d50ad062',
        main_reader_implementation_commit='76b2495',model='Qwen2.5-3B-Instruct',revision='aa8e72537993ba99e69dfaafa59ed015b17504d1',
        precision='float16',adapter=False,greedy=True,input_cap=1024,p0_max_new_tokens=32,p1_p2_max_new_tokens=128,
        actual_calls=len(calls),d0_calls=sum('D0' in r['stage'] for r in calls),main_calls=sum(any(s in r['stage'] for s in ('core','extra')) for r in calls),
        rerun_calls=sum('rerun' in r['stage'] for r in calls),logical_main_rows=384,main_reused_rows=sum(r['cache_hit'] for r in ps),
        input_tokens=sum(r['input_tokens'] for r in calls),output_tokens=sum(r['output_tokens'] for r in calls),
        gpu_process_seconds=gpu,cpu_process_seconds_measured=cpusec,peak_gpu_allocated_bytes=max(r.get('peak_gpu_bytes',0) for r in cost),
        directory_bytes_snapshot=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()),
        cumulative_gpu_process_seconds=before['cumulative_gpu_process_seconds_measured']+gpu,
        cumulative_cpu_process_seconds_lower_bound=before['cumulative_cpu_process_seconds_lower_bound']+cpusec,
        unknown_cpu='Historical unmeasured work, unit tests, shell, scoring and short read-only analyses; not imputed as zero.',
        new_search_calls=0,new_extraction_verification_calls=0,new_embeddings=0,training=0,model_downloads=0,paid=0,
        versions=before['versions'],accounting='GPU process wall includes model loading and process CPU. Logical cached model time is not physical new work or deployment latency.'))
    print('384 logical outputs bound; 8 uncached replays identical;',len(calls),'actual calls; GPU process seconds',gpu)
if __name__=='__main__':finish()
