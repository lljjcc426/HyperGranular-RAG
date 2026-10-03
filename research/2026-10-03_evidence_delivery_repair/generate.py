"""Fixed 13-arm pilot; real rendered IDs, bounded calls, uncached rerun."""
from common import *
from repair import METHODS
import importlib.metadata,subprocess,platform

def main():
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter()
    environment=load(ROOT/'results/stage4e_e2e_environment_manifest.json')
    f._set_determinism(environment)
    cfg=config('hotpot');snapshot=Path(cfg['paths']['generator_snapshot'])
    f.validate_snapshot(snapshot,cfg['models']['generator'],'generator')
    save(HERE/'GENERATION_BINDING.json',{'environment':environment,'model':cfg['models']['generator'],
        'implementation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        'source_files':{p.name:identity(p) for p in HERE.glob('*.py')},
        'prior_experiment_gpu_seconds':0,'prior_document_cpu_seconds':None,
        'prior_cpu_unknown_not_imputed':True,'maximum_calls':5464})
    tokenizer=AutoTokenizer.from_pretrained(snapshot,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(snapshot,local_files_only=True,dtype=torch.float16)
    model.eval().to('cuda');torch.cuda.reset_peak_memory_stats();calls=0
    prior_cpu=sum(z['cpu_seconds'] for z in rows(HERE/'RESOURCE_LEDGER.jsonl'))
    def call(ids):
        nonlocal calls
        if calls>=5464 or time.perf_counter()-wall>=43200 or prior_cpu+time.process_time()-cpu>=86400:
            raise RuntimeError('RESOURCE_CAP_REACHED_AT_CALL_BOUNDARY')
        if calls%100==0 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())>9_900_000_000:
            raise RuntimeError('DISK_CAP_REACHED_AT_CALL_BOUNDARY')
        tensor=torch.tensor([ids],dtype=torch.long,device='cuda');mask=torch.ones_like(tensor)
        torch.cuda.synchronize();started=time.perf_counter()
        with torch.no_grad():
            output=model.generate(input_ids=tensor,attention_mask=mask,pad_token_id=tokenizer.eos_token_id,**f.GENERATOR_KWARGS)
        torch.cuda.synchronize();elapsed=time.perf_counter()-started;calls+=1
        tokens=output[0,len(ids):].cpu().tolist()
        return {'prediction':tokenizer.decode(tokens,skip_special_tokens=True).strip(),'output_ids':tokens,'generation_seconds':elapsed,'call_id':calls}
    try:
        synthetic=f.build_prompt(tokenizer,'Which color is named?',[
            {'unit_id':str(i),'title':'Synthetic evidence','text':'The named color is blue. '*80} for i in range(20)])
        first=call(synthetic['input_ids']);second=call(synthetic['input_ids'])
        assert first['output_ids']==second['output_ids'],'synthetic determinism mismatch'
        cost={'synthetic_calls':2,'input_tokens':len(synthetic['input_ids']),
            'seconds':[first['generation_seconds'],second['generation_seconds']],
            'conservative_call_projection_seconds':max(first['generation_seconds'],second['generation_seconds'])*5462,
            'projection_is_not_guarantee':True}
        save(HERE/'RESOURCE_CALIBRATION.json',cost);print('CALIBRATION',json.dumps(cost),flush=True)
        if cost['conservative_call_projection_seconds']+time.perf_counter()-wall>43200:
            raise RuntimeError('FIXED_PLAN_NOT_FEASIBLE_BEFORE_REAL_ANSWERS')
        inputs=rows(LOCAL/'pilot_inputs.jsonl');rankings={(r['query_id'],r['method']):r for r in rows(HERE/'pilot_rankings.jsonl')}
        archives={tag:{(z['query_id'],z['method']):z for z in rows(config(tag)['paths']['prompt_audit_main'])} for tag in CONFIGS}
        cache={};main_records={};logical=0;hits=0;reruns=0
        with (LOCAL/'predictions_main.jsonl').open('x',encoding='utf-8') as pred, (LOCAL/'prompt_audit.jsonl').open('x',encoding='utf-8') as audit:
            for case in inputs:
                query=case['query'];umap={u['unit_id']:u for u in case['units']}
                for method in METHODS:
                    ranking=rankings[query['query_id'],method]['ranking'];render_start=time.perf_counter()
                    prompt=f.build_prompt(tokenizer,query['question'],[umap[i] for i in ranking])
                    if method in ('Dense20','H0'):
                        oldmethod='DENSE_TOP20' if method=='Dense20' else 'STATIC_Q25_TOP20'
                        historical=archives[case['tag']][query['query_id'],oldmethod]
                        assert all(prompt[k]==historical[k] for k in ('prompt_sha256','evidence_unit_ids','input_token_count','rank1_truncated'))
                    render_seconds=time.perf_counter()-render_start
                    digest=hashlib.sha256(json.dumps(prompt['input_ids'],separators=(',',':')).encode()).hexdigest()
                    reused=digest in cache
                    if reused:result=dict(cache[digest]);hits+=1
                    else:result=call(prompt['input_ids']);cache[digest]=dict(result)
                    record={'query_id':query['query_id'],'dataset':query['dataset'],'tag':case['tag'],'method':method,
                        **result,'cache_hit':reused,'actual_generation_seconds':0. if reused else result['generation_seconds'],
                        'input_ids_sha256':digest}
                    line(pred,record);main_records[query['query_id'],method]=record;logical+=1
                    line(audit,{'query_id':query['query_id'],'tag':case['tag'],'method':method,**prompt,
                        'input_ids_sha256':digest,'render_seconds':render_seconds,
                        'visible_units':[{'unit_id':i,'title':umap[i]['title'],'text':umap[i]['text'],
                                          'fully_visible':not prompt['rank1_truncated']} for i in prompt['evidence_unit_ids']],
                        'serialized_visible_prompt':tokenizer.decode(prompt['input_ids'],skip_special_tokens=False),
                        'omitted_ids':[i for i in ranking if i not in prompt['evidence_unit_ids']]})
                pred.flush();audit.flush()
                if logical%650==0:print('MAIN',logical,'actual_calls',calls,flush=True)
        with (LOCAL/'predictions_rerun.jsonl').open('x',encoding='utf-8') as rerun:
            for case in inputs:
                if not case['rerun']:continue
                query=case['query'];umap={u['unit_id']:u for u in case['units']}
                for method in METHODS:
                    prompt=f.build_prompt(tokenizer,query['question'],[umap[i] for i in rankings[query['query_id'],method]['ranking']])
                    digest=hashlib.sha256(json.dumps(prompt['input_ids'],separators=(',',':')).encode()).hexdigest()
                    result=call(prompt['input_ids']);previous=main_records[query['query_id'],method]
                    assert digest==previous['input_ids_sha256'] and result['output_ids']==previous['output_ids'] and result['prediction']==previous['prediction'],(query['query_id'],method,'rerun differs')
                    line(rerun,{'query_id':query['query_id'],'tag':case['tag'],'method':method,**result,'input_ids_sha256':digest,'matched':True});reruns+=1
                rerun.flush()
        assert logical==5200 and reruns==260
        save(HERE/'GENERATION_SUMMARY.json',{'status':'COMPLETE_INPUT_AND_OUTPUT_RERUN_MATCH',
            'logical_main_predictions':logical,'main_cache_hits':hits,'main_actual_calls':logical-hits,
            'uncached_rerun_calls':reruns,'synthetic_calls':2,'total_actual_calls':calls,
            'peak_gpu_memory_bytes':torch.cuda.max_memory_allocated(),
            'gpu_process_wall_seconds':time.perf_counter()-wall,'failed_calls':0})
    finally:
        charge('generate',cpu,wall,gpu_process_seconds=time.perf_counter()-wall,actual_calls=calls)
    print('GENERATION_COMPLETE',calls,flush=True)
if __name__=='__main__':main()
