"""Append-only summaries from completed records; no inference, no locked inputs."""
from io_utils import *
import csv
from collections import Counter, defaultdict
from statistics import mean, median

def table(name, data):
    with (HERE/name).open('x', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

def run():
    synth=list(csv.DictReader((HERE/'SYNTHETIC_RESULTS_v2.csv').open(encoding='utf-8')))
    assert len(synth)==224
    summary=[]
    for method in dict.fromkeys(r['method'] for r in synth):
        for red,mix in [('ALL','ALL')]+[(str(a),str(b)) for a in (0,1) for b in (0,1)]:
            rs=[r for r in synth if r['method']==method and (red=='ALL' or (r['redundancy'],r['mixing'])==(red,mix))]
            found=[int(r['first_complete_probe']) for r in rs if r['first_complete_probe']]
            summary.append(dict(domain='EXACT_WITNESS_SYNTHETIC',method=method,redundancy=red,mixing=mix,n=len(rs),
                complete8=sum(int(r['complete8']) for r in rs),complete16=sum(int(r['complete16']) for r in rs),
                complete32=sum(int(r['complete32']) for r in rs),false_joins=sum(int(r['false_joins']) for r in rs),
                mean_capped_first_probe=mean(int(r['first_complete_probe']) if r['first_complete_probe'] else 33 for r in rs),
                median_first_probe_found_only=median(found) if found else None,
                mean_splits=mean(int(r['splits']) for r in rs),
                mean_search_seconds=mean(float(r['seconds']) for r in rs),
                mean_split_seconds=mean(float(r['split_seconds']) for r in rs),answer_f1=None))
    table('RESULTS.csv',summary)
    paired=[]
    for other in ('GB-uniform','GB-fixed','KM-feedback','Flat-binding'):
        for budget in (8,16,32):
            key=lambda r:(r['redundancy'],r['mixing'],r['seed'])
            a={key(r):int(r['complete'+str(budget)]) for r in synth if r['method']=='GB-feedback'}
            b={key(r):int(r['complete'+str(budget)]) for r in synth if r['method']==other}
            ds=[a[k]-b[k] for k in a]
            paired.append(dict(domain='EXACT_WITNESS_SYNTHETIC',method='GB-feedback',control=other,budget=budget,n=32,
                gain=sum(d>0 for d in ds),same=sum(d==0 for d in ds),harm=sum(d<0 for d in ds),
                delta_complete=mean(ds),delta_answer_f1=None))
    table('PAIRED_COMPARISONS.csv',paired)
    # Natural method comparison was gated, not evaluated as zero.
    table('D1_STATUS.csv',[dict(method=m,n_planned=64,n_completed=0,status='NOT_RUN_D0_CAPABILITY_GATE',em=None,f1=None)
        for m in ('Dense-window','Flat-binding','GB-fixed','GB-uniform','GB-feedback','KM-fixed','KM-uniform','KM-feedback')])
    query=[]
    for prefix,model in [('', '1.5b_attempted_fallback'),('3b_','3b_preferred')]:
        for r in rows(LOCAL/(prefix+'d0_reader.jsonl')):
            query.append(dict(model=model,index=r['index'],role=r['role'],dataset=r['tag'],condition=r['condition'],
                em=r['em'],f1=r['f1'],input_tokens=r['input_tokens'],output_tokens=r['output_tokens'],
                support_all_visible=r['supplied_support_all_visible'],seconds=r['seconds']))
    assert len(query)==128
    table('D0_QUERY_METRICS.csv',query)
    calls=rows(LOCAL/'calls.jsonl');groups=defaultdict(list)
    for r in calls:groups[(r.get('model','1.5b'),r['stage'],r['kind'])].append(r)
    costs=[]
    for (model,stage,kind),rs in sorted(groups.items()):
        costs.append(dict(model=model,stage=stage,kind=kind,actual_calls=len(rs),
            input_tokens=sum(r['input_tokens'] for r in rs),output_tokens=sum(r.get('output_tokens',0) for r in rs),
            call_seconds=sum(r['seconds'] for r in rs)))
    table('CALL_COSTS.csv',costs)
    ledger=rows(HERE/'COST_LEDGER.jsonl');prior=read(HERE/'RUN_CARD.json')['prior_measured']
    size=lambda path:sum(p.stat().st_size for p in path.rglob('*') if p.is_file())
    gpu=sum(r.get('gpu_process_seconds',0) for r in ledger);cpu=sum(r['cpu_seconds'] for r in ledger)
    disk=dict(model_directory_bytes=size(DOWNLOAD_MODEL),pilot_directory_bytes=size(HERE))
    xet=Path(os.environ['USERPROFILE'])/'.cache/huggingface/xet'
    disk['xet_cache_current_bytes_upper_bound']=size(xet) if xet.exists() else 0
    # Directory metadata only after downloader exit. Conservatively count all Xet bytes,
    # including pre-existing cache if present; no cache file contents are opened.
    disk['new_bytes_conservative_snapshot']=sum(disk.values())
    save(HERE/'RESOURCE_SUMMARY.json',dict(gpu_process_seconds=gpu,ledger_cpu_seconds=cpu,
        stopped_downloader_observed_cpu_seconds=31.53125,
        cpu_measurement_limit='Ledger plus observed stopped process; initial tokenizer/download and shell/document CPU not fully metered. Not an exact total.',
        cumulative_measured_gpu_seconds=gpu+prior['gpu_process_seconds'],
        cumulative_measured_cpu_lower_bound=cpu+31.53125+prior['cpu_seconds'],
        prior_document_cpu=None,actual_generate_calls=sum(r['kind']=='generate' for r in calls),
        actual_binary_pairs=sum(r['kind']=='binary' for r in calls),
        max_gpu_allocated_bytes=max(r.get('peak_allocated_bytes',0) for r in ledger),paid=0,
        d1_calls=0,cache_hit_speedup_claim=False,**disk))
    print(json.dumps(read(HERE/'RESOURCE_SUMMARY.json')),flush=True)

if __name__=='__main__':run()
