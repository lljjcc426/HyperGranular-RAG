"""Canonical scoring after source inputs are saved; opened historical Gold only."""
from common import *
import statistics,itertools
score=load_module('rg_v3_canonical_score',OLD/'score.py')
def means(xs,k):return statistics.mean(r[k] for r in xs) if xs else 0.
def gold():
    names={'hotpot':'stage4e_e2e_official_train1000_v1_gold_targets.jsonl','musique':'stage4f_xdr_musique_train3000_v1_gold_targets.jsonl'}
    return {tag:{r['query_id']:r for r in rows(DATA/'processed'/name)} for tag,name in names.items()}
def replay():
    modules=score.scorers();gg=gold();rs=read(LOCAL/'replay_inputs.json');extra=rows(LOCAL/'replay_answers.jsonl') if (LOCAL/'replay_answers.jsonl').exists() else []
    cache={r['key']:r['answer'] for r in extra};qs=[]
    dense={r['query_id']:r for r in rs if r['kind']=='Dense'}
    for r in rs:
        answer=r.get('answer') or cache[digest(r['context']['prompt'])]
        em,f1=score.answer_score(r['tag'],answer['text'],gg[r['tag']][r['query_id']],modules)
        de,df=score.answer_score(r['tag'],dense[r['query_id']]['answer']['text'],gg[r['tag']][r['query_id']],modules)
        c=r['context'];qs.append(dict(query_id=r['query_id'],dataset=r['tag'],method=r['method'],kind=r['kind'],em=em,f1=f1,dense_delta=f1-df,
            changed=int(c['prompt']!=dense[r['query_id']]['context']['prompt']),new_sentences=len(c.get('new_spans',[])),displaced_sentences=len(c.get('displaced_spans',[])),
            input_tokens=c['input_tokens'],package_relations=len(c.get('package_relations',[])),count_match_infeasible=int(c.get('status')=='COUNT_MATCH_INFEASIBLE')))
    out=[]
    for method,kind in sorted({(r['method'],r['kind']) for r in qs}):
        for dataset in ('hotpot','musique','ALL64'):
            xs=[r for r in qs if (r['method'],r['kind'])==(method,kind) and (dataset=='ALL64' or r['dataset']==dataset)]
            out.append(dict(method=method,delivery=kind,dataset=dataset,n=len(xs),em=means(xs,'em'),f1=means(xs,'f1'),delta_dense_f1=means(xs,'dense_delta'),
                prompt_changed=sum(r['changed'] for r in xs),gain=sum(r['dense_delta']>0 for r in xs),same=sum(r['dense_delta']==0 for r in xs),harm=sum(r['dense_delta']<0 for r in xs),
                new_sentences=sum(r['new_sentences'] for r in xs),displaced_sentences=sum(r['displaced_sentences'] for r in xs),mean_input_tokens=means(xs,'input_tokens'),
                package_relations=sum(r['package_relations'] for r in xs),count_match_infeasible=sum(r['count_match_infeasible'] for r in xs)))
    table(HERE/'REPLAY_RESULTS.csv',out);save(LOCAL/'replay_scored.json',qs)
    print('A',len(qs),'records scored')

def natural():
    modules=score.scorers();gg=gold();qs=[]
    for p in sorted((LOCAL/'natural').glob('*/answers_[0-9]*.json')):
        for r in read(p):
            em,f1=score.answer_score(r['tag'],r['answer']['text'],gg[r['tag']][r['query_id']],modules)
            trace=r['result']['trace'];generations=[];extraction=0;verification=0
            for t in trace:
                d=t['detail'];generations.append(d['generation']);extraction+=1
                for v in d['verification']:
                    gs=v.get('generations',[v['generation']]);generations.extend(gs);verification+=len(gs)
            parse=r['parse'];scope=r['scope'];parse_g=[parse['generation']] if parse else []
            allgs=generations+parse_g+([scope] if scope else [])+[r['answer']]
            states=r['result']['states'];c=r['context']
            qs.append(dict(query_id=r['query_id'],dataset=r['tag'],method=r['method'],budget=r['budget'],em=em,f1=f1,
                parse_failed=int(r['method']!='Dense-window-v3' and not r['slots']),prompt_changed=int(c.get('prompt_changed',False)),
                new_sentences=len(c.get('new_spans',[])),fallback=int(c['fallback']),local_package=int(bool(c.get('package_relations'))),
                program_complete=int(any(s['program_complete'] for s in states)),accepted_events=len(r['result']['facts']),
                semantic_facts=len({(f['slot'],f['head_id'],f['tail_id'],f.get('polarity'),f.get('conditions')) for f in r['result']['facts']}),
                tasks=len(trace),extraction_calls=extraction,verification_calls=verification,parse_calls=int(parse is not None),scope_calls=int(scope is not None),reader_calls=1,
                logical_input_tokens=sum(g['input_tokens'] for g in allgs),logical_output_tokens=sum(g['output_tokens'] for g in allgs),
                logical_model_seconds=sum(g['seconds'] for g in allgs),conditional_seconds=r['conditional_seconds'],index_seconds=r['index_seconds'],
                conditional_queries=len(r['result']['conditional_texts']),actual_search_transaction_seconds=r['result']['seconds'],splits=len(r['result']['splits']),
                task_cache_hits=sum(t['cache_hit'] for t in trace),reader_cache_hit=int(r['reader_cache_hit']),reader_input_tokens=r['context']['input_tokens']))
    if not qs:return
    table(HERE/'NATURAL_QUERY_OUTCOMES.csv',qs);out=[]
    for method,b in sorted({(r['method'],r['budget']) for r in qs}):
        for dataset in ('hotpot','musique','EQUAL_WEIGHT_16'):
            xs=[r for r in qs if (r['method'],r['budget'])==(method,b) and (dataset=='EQUAL_WEIGHT_16' or r['dataset']==dataset)]
            item=dict(method=method,budget=b,dataset=dataset,n=len(xs),em=means(xs,'em'),f1=means(xs,'f1'))
            for k in ('parse_failed','prompt_changed','new_sentences','fallback','local_package','program_complete','accepted_events','semantic_facts','tasks','extraction_calls','verification_calls','parse_calls','scope_calls','reader_calls','logical_input_tokens','logical_output_tokens','logical_model_seconds','conditional_seconds','index_seconds','conditional_queries','splits','task_cache_hits','reader_cache_hit'):
                item[k]=sum(r[k] for r in xs)
            item['mean_reader_input_tokens']=means(xs,'reader_input_tokens');out.append(item)
    table(HERE/'NATURAL_RESULTS.csv',out)
    pairs=[]
    for b in sorted({r['budget'] for r in qs}):
        for comparator in ('Dense-window-v3','Flat-binding-v3','GB-uniform-v3','KM-feedback-v3'):
            for dataset in ('hotpot','musique','EQUAL_WEIGHT_16'):
                target={r['query_id']:r for r in qs if r['method']=='GB-feedback-v3' and r['budget']==b and (dataset=='EQUAL_WEIGHT_16' or r['dataset']==dataset)}
                control={r['query_id']:r for r in qs if r['method']==comparator and r['budget']==b and r['query_id'] in target}
                if set(target)!=set(control):raise ValueError('PAIRED_DENOMINATOR_INCOMPLETE')
                ds=[r['f1']-control[q]['f1'] for q,r in target.items()]
                pairs.append(dict(dataset=dataset,budget=b,comparison='GB-feedback-v3 minus '+comparator,n=len(ds),delta_f1=statistics.mean(ds),gain=sum(d>0 for d in ds),same=sum(d==0 for d in ds),harm=sum(d<0 for d in ds)))
    table(HERE/'NATURAL_PAIRED.csv',pairs)
    print('C',len(qs),'records scored')

def reruns():
    out=[]
    for p in (LOCAL/'natural').glob('*/answers_rerun_8.json'):
        main={r['method']:r for r in read(p.parent/'answers_8.json')}
        for r in read(p):
            m=main[r['method']]
            def fingerprints(z):
                gs=[]
                for t in z['result']['trace']:
                    gs.append(t['detail']['generation'])
                    for v in t['detail']['verification']:gs.extend(v.get('generations',[v['generation']]))
                return [(g['input_digest'],g['output_ids']) for g in gs]
            out.append(dict(query_id=r['query_id'],method=r['method'],tasks_equal=[t['task'] for t in r['result']['trace']]==[t['task'] for t in m['result']['trace']],
                model_inputs_outputs_equal=fingerprints(r)==fingerprints(m),prompt_equal=r['context']['prompt']==m['context']['prompt'],reader_output_equal=r['answer']['output_ids']==m['answer']['output_ids']))
    if out:table(HERE/'RERUN_CHECK.csv',out)
if __name__=='__main__':
    import sys
    {'replay':replay,'natural':natural,'rerun':reruns}[sys.argv[1]]()
