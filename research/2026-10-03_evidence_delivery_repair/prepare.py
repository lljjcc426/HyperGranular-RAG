"""Reconstruct H0, diagnose opened evidence, and freeze Gold-free pilot rankings."""
import common
from common import *
from repair import Context,all_methods,gate_reasons
from score import scorers,answer_score
from collections import Counter

def diagnose(tag,c,g,visible,old_predictions,scorer):
    groups=support_groups(tag,g,c.units if tag=='hotpot' else c.original_units)
    idindex={u:i for i,u in enumerate(c.ids)};dense={c.ids[i] for i in c.d}
    h0={c.ids[i] for i in c.h0};ins={c.ids[i] for i in c.hi}
    reasons,seedunion=gate_reasons(c);byindex={i:b for b,d in reasons.items() for i in d['indices']}
    missing={k:v for k,v in groups.items() if not(v&dense)}
    stages=['outside_universe','seed_excluded','min_new_terms','size','anchor','units_per_new_term','redundancy','score','edge_budget','q25_floor','prefix_skip','insertion_capacity','final_not_visible','delivered']
    events=[]
    for target,ids in missing.items():
        unit_status={}
        for uid in ids:
            if uid not in idindex:reason='outside_universe'
            else:
                i=idindex[uid];reason=reasons[byindex[i]]['reason']
                if reason=='selected':
                    if c.s[i]<c.cfg.q25_floor:reason='q25_floor'
                    elif i in c.prefix:reason='prefix_skip'
                    elif uid not in ins:reason='insertion_capacity'
                    elif uid not in visible:reason='final_not_visible'
                    else:reason='delivered'
            unit_status[uid]=reason
        # A paragraph can be reached through any annotated member; record furthest stage.
        reason=max(unit_status.values(),key=stages.index) if unit_status else 'outside_universe'
        events.append({'support_id':target,'reason':reason,'unit_reasons':unit_status})
    selected=[]
    for edge in c.selected:
        bid=edge['accepted_ball_ids'][0];ball=next(b for b in c.balls if b['ball_id']==bid)
        selected_i=[i for i in c.hi if i in ball['indices']]
        delivered=c.union(selected_i);claimed=set(edge['new_terms'])
        selected.append({'ball_id':bid,'units':[c.ids[i] for i in ball['indices']],
            'claimed_new_terms':sorted(claimed),'selected_terms':sorted(delivered),
            'selected_title_terms':sorted(c.union(selected_i,'title')),
            'selected_body_terms':sorted(c.union(selected_i,'body')),
            'phantom_vs_inserted':sorted(claimed-delivered),
            'phantom_vs_final':sorted(claimed-c.union(c.h0))})
    delta=answer_score(tag,old_predictions['STATIC_Q25_TOP20'],g,scorer)[1]-answer_score(tag,old_predictions['DENSE_TOP20'],g,scorer)[1]
    return {'query_id':c.query['query_id'],'dataset':tag,'annotation':'sentence' if tag=='hotpot' else 'paragraph',
        'dense_support':support_coverage(groups,dense),'h0_support':support_coverage(groups,h0),
        'visible_support':support_coverage(groups,visible),'missing_support_events':events,
        'dense_support_path':[{ 'support_id':k,'in_prefix':bool(v&{c.ids[i] for i in c.prefix}),
            'in_h0':bool(v&h0),'visible':bool(v&set(visible))} for k,v in groups.items() if v&dense],
        'seed_minus_prefix':sorted(seedunion-c.union(c.prefix)),
        'prefix_minus_seed':sorted(c.union(c.prefix)-seedunion),
        'second_ball_repeated_new_terms':sorted(set(c.selected[0]['new_terms'])&set(c.selected[1]['new_terms'])) if len(c.selected)==2 else [],
        'query_terms':sorted(c.qt),'observable_terms':sorted(c.union(range(c.n))),
        'prefix_terms':sorted(c.union(c.prefix)),'dense_terms':sorted(c.union(c.d)),
        'selected_balls':selected,'all_ball_gates':reasons,
        'selected_ball_q25_excluded':sum(c.s[i]<c.cfg.q25_floor for b in c.balls if any(b['ball_id'] in e['accepted_ball_ids'] for e in c.selected) for i in b['indices']),
        'selected_ball_prefix_skips':sum(i in c.prefix for b in c.balls if any(b['ball_id'] in e['accepted_ball_ids'] for e in c.selected) for i in b['indices']),
        'promotions':len(ins&dense),'new':len(ins-dense),'evicted':sorted(dense-h0),
        'legacy_answer_change':'gain' if delta>0 else 'harm' if delta<0 else 'same',
        'legacy_answer_f1_delta':delta}

def main():
    cpu=time.process_time();wall=time.perf_counter();LOCAL.mkdir(exist_ok=True)
    modules=scorers();bindings={};sample=[];summaries={};all_rankings=[]
    with (LOCAL/'loss_queries.jsonl').open('x',encoding='utf-8') as loss, (LOCAL/'pilot_inputs.jsonl').open('x',encoding='utf-8') as pilot:
        for tag in CONFIGS:
            cfg,p,units,queries,x,qx,spans,binding=dataset(tag);bindings[tag]=binding
            golden=rows(p['gold']);assert [z['query_id'] for z in golden]==[q['query_id'] for q in queries]
            gm={g['query_id']:g for g in golden};archive={r['query_id']:r for r in rows(p['rankings'])}
            audits={(r['query_id'],r['method']):r for r in rows(p['prompt_audit_main'])}
            pred={(r['query_id'],r['method']):r['prediction'] for r in rows(p['predictions_main'])}
            chosen=sorted(queries,key=key)[:200];chosenids={z['query_id'] for z in chosen}
            rerun={z['query_id'] for z in sorted(chosen,key=lambda z:key(z,'evidence-delivery-repair-rerun-v1'))[:10]}
            sample.extend({'dataset':z['dataset'],'tag':tag,'query_id':z['query_id'],'sampling_hash':key(z),'rerun':z['query_id'] in rerun} for z in chosen)
            totals=Counter();cross=Counter();missing=Counter()
            for j,query in enumerate(queries):
                start,end=spans[query['query_id']];us=units[start:end];t=time.perf_counter();c=Context(query,us,x[start:end],qx[j]);base_time=time.perf_counter()-t;c.original_units=us
                a=archive[query['query_id']]
                assert [c.ids[i] for i in c.d]==a['dense_top20_unit_ids'],query['query_id']
                assert [c.ids[i] for i in c.h0]==a['static_q25_top20_unit_ids'],query['query_id']
                assert [c.ids[i] for i in c.hi]==a['q25_inserted_unit_ids'],query['query_id']
                vis=audits[query['query_id'],'STATIC_Q25_TOP20']['evidence_unit_ids']
                diagnostic=diagnose(tag,c,gm[query['query_id']],vis,{m:pred[query['query_id'],m] for m in ['DENSE_TOP20','STATIC_Q25_TOP20']},modules);line(loss,diagnostic)
                totals['queries']+=1;totals['h0_archive_matches']+=1;totals['support_targets']+=diagnostic['dense_support']['total']
                totals['dense_support_hits']+=diagnostic['dense_support']['hits'];totals['h0_support_hits']+=diagnostic['h0_support']['hits']
                totals['visible_support_hits']+=diagnostic['visible_support']['hits']
                for ev in diagnostic['missing_support_events']:missing[ev['reason']]+=1;cross[ev['reason']+'|'+diagnostic['legacy_answer_change']]+=1
                for name in ['promotions','new','selected_ball_q25_excluded','selected_ball_prefix_skips']:totals[name]+=diagnostic[name]
                totals['evicted_units']+=len(diagnostic['evicted']);totals['dense_support_lost_targets']+=sum(not z['in_h0'] for z in diagnostic['dense_support_path'])
                totals['selected_balls']+=len(diagnostic['selected_balls']);totals['balls_with_phantom_inserted']+=sum(bool(z['phantom_vs_inserted']) for z in diagnostic['selected_balls'])
                totals['balls_with_phantom_final']+=sum(bool(z['phantom_vs_final']) for z in diagnostic['selected_balls'])
                totals['second_ball_repeats']+=bool(diagnostic['second_ball_repeated_new_terms'])
                totals['seed_prefix_union_differs']+=bool(diagnostic['seed_minus_prefix'] or diagnostic['prefix_minus_seed'])
                for name,ids in [('prefix',c.prefix),('dense',c.d),('universe',range(c.n))]:totals[name+'_all_query_terms']+=c.union(ids)==c.qt
                totals['dense_observable_saturated']+=c.union(c.d)==c.union(range(c.n))
                totals['h0_prompt_omitted_units']+=len(c.h0)-len(vis)
                if query['query_id'] in chosenids:
                    methods,km=all_methods(c)
                    for m,row in methods.items():
                        row['shared_h0_reconstruction_seconds']=base_time
                        if m=='H0':row['selection_seconds']=base_time
                        line_record={'query_id':query['query_id'],'dataset':query['dataset'],'tag':tag,'method':m,**row}
                        all_rankings.append(line_record)
                    line(pilot,{'query':query,'units':us,'tag':tag,'rerun':query['query_id'] in rerun,
                        'gb_sizes':[b['size'] for b in c.balls],'kmeans':km})
                if (j+1)%500==0:print(tag,j+1,'reconstructed',flush=True)
            summaries[tag]={'counts':dict(totals),'missing_support_first_loss':dict(missing),'loss_by_old_answer_change':dict(cross)}
    save(HERE/'DATA_ROLES.json',bindings);save(HERE/'sample_ids.json',sample)
    with (HERE/'pilot_rankings.jsonl').open('x',encoding='utf-8') as h:
        for row in all_rankings:line(h,row)
    save(HERE/'LOSS_SUMMARY.json',summaries)
    save(HERE/'PREPARATION.json',{'status':'H0_4000_MATCHED_PILOT_RANKINGS_FROZEN','samples':len(sample),'logical_rankings':len(all_rankings),'sample_identity':identity(HERE/'sample_ids.json'),'ranking_identity':identity(HERE/'pilot_rankings.jsonl')})
    charge('prepare',cpu,wall,gpu_process_seconds=0)
    print(json.dumps(summaries),flush=True)
if __name__=='__main__':main()
