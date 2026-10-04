from common import *
from review_measure import table
from importlib.metadata import version,distribution
import collections

def main():
    costs=rows(HERE/'cost.jsonl');calls=rows(LOCAL/'calls.jsonl');groups=collections.defaultdict(list)
    for c in calls:groups[c['stage']].append(c)
    summary=[]
    for stage,rs in sorted(groups.items()):
        summary.append(dict(stage=stage,actual_calls=len(rs),input_tokens=sum(r.get('input_tokens',0) for r in rs),
            output_tokens=sum(r.get('output_tokens',0) for r in rs),recorded_inference_seconds=sum(r['seconds'] for r in rs)))
    table(HERE/'ACTUAL_CALL_COSTS.csv',summary)
    deps=['lm-format-enforcer','pydantic','pydantic-core','interegular','annotated-types','typing-inspection','peft','bitsandbytes']
    depfiles=set()
    for name in deps:
        d=distribution(name)
        for file in d.files or []:
            p=Path(d.locate_file(file))
            if p.is_file():depfiles.add(p)
    dependency_bytes=sum(p.stat().st_size for p in depfiles)
    directory_bytes=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    gpu=sum(c.get('gpu_process_seconds',0) for c in costs);cpu=sum(c['cpu_seconds'] for c in costs)
    result=dict(round_gpu_process_seconds=gpu,round_cpu_process_seconds_measured=cpu,
        prior_gpu_process_seconds=1343.813,prior_cpu_seconds_lower_bound=1395.453,
        cumulative_gpu_process_seconds_measured=1343.813+gpu,
        cumulative_cpu_seconds_lower_bound=1395.453+cpu,
        unknown_cpu='Historical unmeasured time and shell/package-install overhead are unknown, not zero.',
        run_directory_bytes=directory_bytes,new_dependency_installed_bytes=dependency_bytes,
        measured_new_disk_bytes=directory_bytes+dependency_bytes,
        caps=dict(round_gpu_seconds=21600,round_cpu_seconds=14400,round_disk_bytes=2000000000,paid=0),
        actual_model_calls=len(calls),model_call_count_scope='Logged inference requests only; training is counted separately and its process cost is included in the same resource totals.',
        adapter_optimizer_steps=read(HERE/'TRAIN_RESULT.json')['steps'],adapter_epochs=read(HERE/'TRAIN_RESULT.json')['epochs'],
        paid=0,versions={n:version(n) for n in deps+['torch','transformers','numpy','accelerate']},
        peak_gpu_allocated_bytes=max(c.get('peak_gpu_bytes',0) for c in costs),
        accounting='GPU process wall time includes loading and CPU work inside those processes; not pure kernel time. Logical method costs are separate from cached actual calls.')
    save(HERE/'RESOURCE_SUMMARY.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
