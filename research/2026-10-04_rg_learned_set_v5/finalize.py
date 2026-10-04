"""Aggregate public outputs without publishing Gold-derived source identities."""
from common import *
import numpy as np
import platform,importlib.metadata as md

def main():
    ledger=rows(HERE/'cost.jsonl');calls=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else [];qa=rows(LOCAL/'qa.jsonl') if (LOCAL/'qa.jsonl').exists() else []
    g,c=usage();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    resource=dict(gpu_process_seconds=g,cpu_seconds_measured=c,new_disk_bytes=size,paid=0,new_reader_calls=len(calls),qa_logical_rows=len(qa),cache_hits=sum(r['cache_hit'] for r in qa),reader_input_tokens=sum(r['input_tokens'] for r in calls),reader_output_tokens=sum(r['output_tokens'] for r in calls),generation_seconds=sum(r['seconds'] for r in calls),cumulative_gpu_seconds=19764.376329+g,cumulative_cpu_seconds_lower_bound=18520.078+c,prior_unmeasured_cpu='UNKNOWN',caps_respected=g<=18000 and c<=14400 and size<=2000000000 and len(calls)<=3000)
    resource.update(accounting_scope='Measured phase CPU and GPU model-residency wall time; interpreter imports, shell operations and older unmeasured CPU are not reconstructed.',cumulative_cpu_complete=False,cumulative_gpu_cap_respected=resource['cumulative_gpu_seconds']<=43200,cumulative_cpu_lower_bound_below_cap=resource['cumulative_cpu_seconds_lower_bound']<=86400,reader_json_errors=sum(bool(r.get('json_error')) for r in calls),reader_hit_limits=sum(r['output_tokens']>=128 and not r['ended_eos'] for r in calls),peak_gpu_bytes=max((r.get('peak_gpu_bytes',0) for r in ledger),default=0))
    save(HERE/'RESOURCE_SUMMARY.json',resource)
    save(HERE/'RUNTIME.json',dict(python=platform.python_version(),packages={p:md.version(p) for p in ('torch','transformers','numpy','lm-format-enforcer','tokenizers')},thread_settings={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','CUBLAS_WORKSPACE_CONFIG')},models='existing frozen BGE FP32; unadapted Qwen2.5-3B FP16; no relation frontend'))
    contrasts=[]
    comparisons=[('H1','Dense'),('H2','H1'),('H4-Flat','H1'),('H4-Flat','H2'),('H4-Flat','DeepSets'),('H4-Flat','Dense'),('H4-Flat','MMR')]
    for seed,setting,limit in sorted(set((r['seed'],r['setting'],r['budget']) for r in qa)):
        for tag in ('hotpot','musique'):
            sub=[r for r in qa if (r['seed'],r['setting'],r['budget'],r['tag'])==(seed,setting,limit,tag)]
            by={(r['query_id'],r['method']):r for r in sub}
            for a,b in comparisons:
                ids=sorted({r['query_id'] for r in sub if r['method']==a}&{r['query_id'] for r in sub if r['method']==b})
                if not ids:continue
                delta=np.array([by[q,a]['f1']-by[q,b]['f1'] for q in ids]);contrasts.append(dict(seed=seed,setting=setting,budget=limit,tag=tag,comparison=a+' minus '+b,queries=len(ids),delta_f1=float(delta.mean()),delta_em=float(np.mean([by[q,a]['em']-by[q,b]['em'] for q in ids])),improved=int((delta>0).sum()),worsened=int((delta<0).sum()),unchanged=int((delta==0).sum()),evidence='EXPOSED_DEVELOPMENT_NO_CONFIRMATORY_TEST'))
    table(HERE/'QA_CONTRASTS.csv',contrasts)
    print(json.dumps(resource),flush=True)

if __name__=='__main__':main()
