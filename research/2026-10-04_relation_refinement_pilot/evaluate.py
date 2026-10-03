"""Append-only D1 evaluation from actual new predictions, never old F1."""
from io_utils import *
import csv,collections
def table(name,records):
    with (HERE/name).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def main():
    cpu=time.process_time();wall=time.perf_counter()
    assert read(HERE/'CALIBRATION_DECISION.json')['run_d1']
    sys.path.insert(0,str(OLD));from score import scorers,answer_score
    modules=scorers();records=rows(LOCAL/'d1_main.jsonl');assert len(records)==64*8*2
    keys={(r['query_id'],r['method'],r['budget']) for r in records};assert len(keys)==len(records)
    rerun=rows(LOCAL/'d1_rerun.jsonl');assert len(rerun)==4*7
    lookup={(r['query_id'],r['method'],r['budget']):r for r in records}
    for r in rerun:
        m=lookup[r['query_id'],r['method'],r['budget']]
        for field in ('slots','states','context'):
            assert r[field]==m[field],(r['query_id'],r['method'],field)
        assert r['answer']['input_digest']==m['answer']['input_digest']
        assert r['answer']['output_ids']==m['answer']['output_ids']
        assert [a['window'] for a in r['trace']]==[a['window'] for a in m['trace']]
        assert not any(a['cache_hit'] for a in r['trace']) and not r['reader_cache_hit']
    gold={}
    for tag,file in [('hotpot','stage4e_e2e_official_train1000_v1_gold_targets.jsonl'),('musique','stage4f_xdr_musique_train3000_v1_gold_targets.jsonl')]:
        want={r['query_id'] for r in records if r['tag']==tag}
        for g in rows(DATA/'processed'/file):
            if g['query_id'] in want:gold[g['query_id']]=g
    scored=[]
    for r in records:
        em,f1=answer_score(r['tag'],r['answer']['text'],gold[r['query_id']],modules)
        scored.append(dict(query_id=r['query_id'],tag=r['tag'],stratum=r['stratum'],method=r['method'],budget=r['budget'],em=em,f1=f1,
            input_tokens=r['context']['input_tokens'],visible_bundle=int(r['context']['complete_bundle_visible']),
            probes=r['logical_probes'],binary_pairs=r['logical_binary_pairs']))
    save(LOCAL/'scored.json',scored);groups=collections.defaultdict(list)
    for r in scored:groups[r['tag'],r['stratum'],r['method'],r['budget']].append(r)
    aggregate=[]
    for (tag,s,m,b),rs in sorted(groups.items()):
        aggregate.append(dict(dataset=tag,stratum=s,method=m,budget=b,n=len(rs),
            **{k:sum(r[k] for r in rs)/len(rs) for k in ('em','f1','input_tokens','visible_bundle','probes','binary_pairs')}))
    table('RESULTS.csv',aggregate);comparisons=[]
    for tag,s in sorted({(r['tag'],r['stratum']) for r in scored}):
        for b in (16,32):
            a={r['query_id']:r for r in scored if r['tag']==tag and r['stratum']==s and r['budget']==b and r['method']=='GB-feedback'}
            for control in ('GB-uniform','GB-fixed','KM-feedback','Flat-binding','Dense-window'):
                other={r['query_id']:r for r in scored if r['tag']==tag and r['stratum']==s and r['budget']==b and r['method']==control}
                assert a.keys()==other.keys();d=[a[q]['f1']-other[q]['f1'] for q in sorted(a)]
                comparisons.append(dict(dataset=tag,stratum=s,budget=b,comparison='GB-feedback - '+control,n=len(d),
                    delta_f1=sum(d)/len(d),gain=sum(v>0 for v in d),same=sum(v==0 for v in d),harm=sum(v<0 for v in d)))
    table('PAIRED_COMPARISONS.csv',comparisons)
    save(HERE/'D1_VERIFICATION.json',dict(rows=len(scored),uncached_rerun_rows=len(rerun),status='DESCRIPTIVE_DEVELOPMENT_ONLY',
        statistics='paired raw changes; no confirmatory test or equivalence inference'))
    charge('D1_evaluate',cpu,wall,gpu_process_seconds=0)
if __name__=='__main__':main()
