"""Actual process and request accounting; do not call while a GPU run is open."""
from common import *
import importlib.metadata
def report():
    costs=rows(HERE/'cost.jsonl');calls=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else []
    enc=rows(LOCAL/'encoding.jsonl') if (LOCAL/'encoding.jsonl').exists() else []
    grouped=[]
    for stage in sorted({r['stage'] for r in calls}):
        rs=[r for r in calls if r['stage']==stage]
        grouped.append(dict(stage=stage,actual_calls=len(rs),input_tokens=sum(r['input_tokens'] for r in rs),output_tokens=sum(r['output_tokens'] for r in rs),generation_seconds=sum(r['seconds'] for r in rs)))
    table(HERE/'ACTUAL_CALL_COSTS.csv',grouped)
    gpu=sum(r.get('gpu_process_seconds',0) for r in costs);cpu=sum(r['cpu_seconds'] for r in costs)
    total_bytes=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    prior=read(V2/'RESOURCE_SUMMARY.json')
    result=dict(round_gpu_process_seconds=gpu,round_cpu_process_seconds_measured=cpu,new_directory_bytes=total_bytes,
        cumulative_gpu_process_seconds_measured=prior['cumulative_gpu_process_seconds_measured']+gpu,
        cumulative_cpu_process_seconds_lower_bound=prior['cumulative_cpu_seconds_lower_bound']+cpu,
        unknown_cpu='Historical unmeasured CPU, shell work, two failed A constructions, unit tests and short analysis commands were not process-timed; not zero.',
        actual_frontend_calls=sum('reader' not in r['stage'] for r in calls),actual_reader_calls=sum('reader' in r['stage'] for r in calls),
        actual_input_tokens=sum(r['input_tokens'] for r in calls),actual_output_tokens=sum(r['output_tokens'] for r in calls),
        actual_encoding_strings=sum(r['strings'] for r in enc),actual_encoding_input_tokens=sum(r['input_tokens'] for r in enc),actual_encoding_seconds=sum(r['seconds'] for r in enc),
        peak_gpu_allocated_bytes=max((r.get('peak_gpu_bytes',0) for r in costs),default=0),training_steps=0,new_models=0,paid=0,
        caps=dict(gpu_process_seconds=10800,cpu_process_seconds=10800,disk_bytes=1000000000,frontend_calls=2500,reader_calls=768),
        versions={name:importlib.metadata.version(name) for name in ['torch','transformers','numpy','peft','bitsandbytes','lm-format-enforcer','accelerate']},
        accounting='Process wall includes loading and CPU work inside GPU processes. Encoding seconds are already included in process time; do not add twice. Historical cached parse/index/reader costs are charged logically per method but not new physical work.')
    save(HERE/'RESOURCE_SUMMARY.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':report()
