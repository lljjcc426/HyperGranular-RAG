"""Independent joins/official metric aggregates and real-call provenance."""
from common import *
from repair import METHODS
from score import scorers,answer_score
import csv

def main():
    cpu=time.process_time();wall=time.perf_counter();ps=rows(LOCAL/'predictions_main.jsonl');rs=rows(LOCAL/'predictions_rerun.jsonl')
    bindings=load(HERE/'DATA_ROLES.json')
    for tag in CONFIGS:
        frozen=load(config(tag)['paths']['telemetry_main'])['embedding_cache']
        assert all(bindings[tag]['embedding_cache'][k]==frozen[k] for k in ('bytes','sha256'))
    pm={(z['query_id'],z['method']):z for z in ps};assert len(ps)==len(pm)==5200
    inputs=rows(LOCAL/'pilot_inputs.jsonl');expected={(z['query']['query_id'],m) for z in inputs for m in METHODS}
    assert set(pm)==expected
    assert {(z['query_id'],z['method']) for z in rs}=={(z['query']['query_id'],m) for z in inputs if z['rerun'] for m in METHODS}
    for r in rs:
        p=pm[r['query_id'],r['method']]
        assert all(p[k]==r[k] for k in ('prediction','output_ids','input_ids_sha256'))
    cache={};actual=[]
    for p in ps:
        if not p['cache_hit']:
            assert p['input_ids_sha256'] not in cache
            cache[p['input_ids_sha256']]=p;actual.append(p['call_id'])
        else:
            source=cache[p['input_ids_sha256']]
            assert all(source[k]==p[k] for k in ('prediction','output_ids','call_id'))
    actual += [r['call_id'] for r in rs]
    assert sorted(actual)==list(range(3,3+len(actual)))
    modules=scorers();numbers={}
    with (HERE/'PILOT_RESULTS.csv').open(encoding='utf-8') as h:reported={(r['dataset'],r['method']):r for r in csv.DictReader(h)}
    for tag in CONFIGS:
        gold={g['query_id']:g for g in rows(config(tag)['paths']['gold'])}
        for m in METHODS:
            selected=[p for p in ps if p['tag']==tag and p['method']==m];assert len(selected)==200
            v=[answer_score(tag,p['prediction'],gold[p['query_id']],modules) for p in selected]
            numbers[tag,m]=[sum(a[i] for a in v)/200 for i in range(2)]
            for i,name in enumerate(('answer_em','answer_f1')):assert abs(numbers[tag,m][i]-float(reported[tag,m][name]))<1e-12
    for m in METHODS:
        for i,name in enumerate(('answer_em','answer_f1')):
            assert abs(sum(numbers[t,m][i] for t in CONFIGS)/2-float(reported['equal_dataset_mean',m][name]))<1e-12
    result={'status':'PASS','prediction_records':5200,'independent_rerun_calls':260,
        'actual_main_and_rerun_calls':len(actual),'synthetic_calls':2,
        'verified':'complete method/query grid; uncached rerun equality; cache source call IDs; official metric aggregates',
        'scope_limit':'No independent reimplementation of official scorer; no confirmatory validity claim'}
    save(HERE/'FINAL_VERIFICATION.json',result);charge('verify_results',cpu,wall,gpu_process_seconds=0);print(json.dumps(result))
if __name__=='__main__':main()
