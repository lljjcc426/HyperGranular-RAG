"""Canonical scoring of the fixed historically exposed D1, after predictions."""
from common import *
from review_measure import table
import collections

def main():
    cpu=time.process_time();wall=time.perf_counter();records=[];reruns=[]
    cc=cases('D1');lookup_cases={c['query_id']:c for c in cc}
    for c in cc:
        folder=LOCAL/'d1'/c['sampling_hash']
        if not (folder/'main.json').exists():raise RuntimeError(('D1_INCOMPLETE',c['query_id']))
        records.extend(read(folder/'main.json'))
        if (folder/'rerun.json').exists():reruns.extend(read(folder/'rerun.json'))
    if len(records)!=64*8*2 or len(reruns)!=4:raise RuntimeError(('RECORD_COUNTS',len(records),len(reruns)))
    main_by={(r['query_id'],r['method'],r['budget']):r for r in records}
    if len(main_by)!=len(records):raise RuntimeError('DUPLICATE_RESULTS')
    for r in reruns:
        original=main_by[r['query_id'],r['method'],r['budget']]
        for field in ('slots','states','context'):
            if original[field]!=r[field]:raise RuntimeError(('RERUN_DIFFERENCE',r['query_id'],r['method'],field))
        if original['answer']['output_ids']!=r['answer']['output_ids']:raise RuntimeError('READER_RERUN_DIFFERENCE')
        if [t['window'] for t in original['trace']]!=[t['window'] for t in r['trace']]:raise RuntimeError('TRACE_RERUN_DIFFERENCE')
        if r['reader_cache_hit'] or any(t['cache_hit'] for t in r['trace']):raise RuntimeError('RERUN_CACHE_USED')
    scorer=load_module('rg_v2_canonical_score',OLD/'score.py');modules=scorer.scorers();gold={}
    for tag,name in [('hotpot','stage4e_e2e_official_train1000_v1_gold_targets.jsonl'),('musique','stage4f_xdr_musique_train3000_v1_gold_targets.jsonl')]:
        wanted={c['query_id'] for c in cc if c['tag']==tag}
        gold.update({r['query_id']:r for r in rows(DATA/'processed'/name) if r['query_id'] in wanted})
    scored=[]
    for r in records:
        em,f1=scorer.answer_score(r['tag'],r['answer']['text'],gold[r['query_id']],modules)
        g=gold[r['query_id']];units={u['unit_id']:u for u in lookup_cases[r['query_id']]['units']}
        visible={sid for sid,a,b in r['context']['visible_spans'] if a==0 and b==len(units[sid]['text'])}
        if r['tag']=='hotpot':targets={x['unit_id'] for x in g['supporting_facts']};hits=len(targets&visible)
        else:targets=set(g['supporting_paragraph_indices']);hits=len(targets&{units[sid]['paragraph_index'] for sid in visible})
        logical=sum(r[k] for k in ('logical_parse_seconds','logical_index_seconds','logical_reader_seconds','logical_conditional_seconds','logical_seconds'))
        scored.append(dict(query_id=r['query_id'],dataset=r['tag'],stratum=r['stratum'],method=r['method'],budget=r['budget'],em=em,f1=f1,
            complete_bundle=int(r['complete']),visible_bundle=int(r['context']['complete_bundle_visible']),fallback=int(r['context']['fallback']),
            input_tokens=r['context']['input_tokens'],probes=r['logical_probes'],accepted_facts=r['accepted_facts'],splits=len(r['splits']),
            support_recall=hits/len(targets),support_complete=int(hits==len(targets)),
            logical_model_and_encoding_seconds=logical,
            logical_model_calls=r['logical_parse_calls']+r['logical_extraction_calls']+r['logical_verification_calls']+1,
            parse_usable_by_contract=int(bool(r['slots'])) if r['method']!='Dense-window' else 0))
    save(LOCAL/'scored.json',scored)
    fields=['em','f1','complete_bundle','visible_bundle','fallback','input_tokens','probes','accepted_facts','splits','support_recall','support_complete','logical_model_and_encoding_seconds','logical_model_calls','parse_usable_by_contract']
    summary=[];groups=collections.defaultdict(list)
    for r in scored:
        groups[r['dataset'],r['stratum'],r['method'],r['budget']].append(r)
        groups[r['dataset'],'ALL',r['method'],r['budget']].append(r)
    for (tag,stratum,method,budget_),rs in sorted(groups.items()):
        summary.append(dict(dataset=tag,stratum=stratum,method=method,budget=budget_,n=len(rs),status='OBSERVED_DEVELOPMENT_RESULT',**{k:sum(r[k] for r in rs)/len(rs) for k in fields}))
    for method in engine.METHODS:
        for b in (16,32):
            a=groups['hotpot','bridge',method,b];z=groups['musique','2hop',method,b]
            summary.append(dict(dataset='EQUAL_WEIGHT',stratum='hotpot_bridge_plus_musique_2hop',method=method,budget=b,n=len(a)+len(z),status='OBSERVED_DEVELOPMENT_RESULT',
                **{k:.5*(sum(r[k] for r in a)/len(a)+sum(r[k] for r in z)/len(z)) for k in fields}))
    table(HERE/'NATURAL_RESULTS.csv',summary);paired=[]
    for (tag,s,m,b),rs in sorted(groups.items()):
        if m!='GB-feedback':continue
        a={r['query_id']:r for r in rs}
        for control in ('GB-uniform','GB-fixed','KM-feedback','Flat-binding','Dense-window'):
            z={r['query_id']:r for r in groups[tag,s,control,b]}
            differences=[a[q]['f1']-z[q]['f1'] for q in sorted(a)]
            paired.append(dict(dataset=tag,stratum=s,budget=b,comparison='GB-feedback - '+control,n=len(a),delta_f1=sum(differences)/len(a),
                gains=sum(d>0 for d in differences),ties=sum(d==0 for d in differences),harms=sum(d<0 for d in differences),
                delta_visible_bundle=sum(a[q]['visible_bundle']-z[q]['visible_bundle'] for q in a)/len(a)))
    table(HERE/'NATURAL_PAIRED.csv',paired)
    save(HERE/'NATURAL_VERIFICATION.json',dict(status='DESCRIPTIVE_DEVELOPMENT_ONLY',queries=64,prediction_records=len(records),
        uncached_rerun_queries=2,uncached_rerun_records=4,rerun_scope='GB-feedback and KM-feedback at 16 probes; first sampling hash per dataset',
        states_traces_prompts_answers_equal=True,reader='unadapted Qwen2.5-3B FP16',scorers='revision2 official canonical pure functions',
        support_scope='Hotpot sentence; MuSiQue paragraph, not chain gold',cost_scope='logical model+encoding timings, plus separately logged full search transaction and actual process costs',
        interpretation='No confirmation, significance, equivalence or architecture claim.'))
    charge('D1_evaluate',cpu,wall,gpu_process_seconds=0)

if __name__=='__main__':main()
