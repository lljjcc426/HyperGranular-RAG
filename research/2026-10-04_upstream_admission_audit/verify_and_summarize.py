"""Read-only checks and supplementary accounting on completed diagnostic records."""
import sys
sys.dont_write_bytecode=True
import csv,json,gzip,time
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'2026-10-03_evidence_delivery_repair'

def rows(p):
    with (gzip.open(p,'rt',encoding='utf-8') if str(p).endswith('.gz') else Path(p).open(encoding='utf-8')) as f:
        for s in f:
            if s.strip():yield json.loads(s)
def save(name,obj):
    with (HERE/name).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    cpu=time.process_time();wall=time.perf_counter()
    off={'G0':set(),'G1':{'min_new_terms'},'G2':{'redundancy'},'G3':{'min_new_terms','redundancy'},
         'G4':{'min_new_terms','redundancy','units_per_new_term'},
         'G5':{'min_new_terms','redundancy','units_per_new_term','facet_score_threshold'}}
    gate=defaultdict(Counter);checks=Counter();summary=defaultdict(Counter);distinct=set();previous=defaultdict(dict)
    for z in rows(PREV/'pilot_rankings.jsonl'):
        if z['method']=='Dense20':previous[z['query_id']]=z
    for r in rows(HERE/'local/group_records.jsonl.gz'):
        k=r['dataset']+'/'+r['grouping'];v=gate[k];v['groups']+=1
        v['nonseed_groups']+=not r['is_seed']
        if not r['is_seed'] and r['new_count']==0:
            v['new_zero']+=1;v['empty_facets' if not r['facets'] else 'nonempty_facets']+=1
            assert r['redundancy']==(1 if r['facets'] else 0);checks['new_zero_redundancy_checks']+=1
            for g in r['all_failed_gates']:v['new_zero_fails_'+g]+=1
            for mask in off:
                if not(set(r['all_failed_gates'])-off[mask]):
                    v['new_zero_admitted_'+mask]+=1
                    v['new_zero_admitted_'+mask+('_nonempty' if r['facets'] else '_empty')]+=1
    losses={r['query_id']:r for r in rows(PREV/'local/loss_queries.jsonl')}
    targetstats=defaultdict(Counter)
    for r in rows(HERE/'local/support_paths.jsonl.gz'):
        if r['grouping']!='GB':continue
        targetevents={e['support_id']:e['reason'] for e in losses[r['query_id']]['missing_support_events']}
        for tid,members in r['targets'].items():
            if targetevents.get(tid)!='min_new_terms':continue
            v=targetstats[r['dataset']];v['first_new_term_targets']+=1
            ns=[m for m in members if m['ball_id'] not in r['seed_ids']]
            # ANY complete member path, never intersect failure sets across sentences.
            for mask,disabled in off.items():
                passed=[m for m in ns if not(set(m['all_failed_gates'])-disabled)]
                v[mask+'_any_same_member_all_hard_gates']+=bool(passed)
                v[mask+'_any_same_member_hard_gates_q25_nonprefix']+=any(m['q25_pass'] and not m['prefix'] for m in passed)
            for g in ('size','anchor','units_per_new_term','redundancy','facet_score_threshold'):
                v['at_least_one_member_fails_'+g]+=any(g in m['all_failed_gates'] for m in ns)
                v['all_nonseed_members_fail_'+g]+=bool(ns) and all(g in m['all_failed_gates'] for m in ns)
            if ns:
                independent=all(any(g not in m['all_failed_gates'] for m in ns) for g in ('size','anchor','units_per_new_term','redundancy','facet_score_threshold'))
                actual=any(not(set(m['all_failed_gates'])-{'min_new_terms'}) for m in ns)
                v['wrong_cross_member_conjunction_would_admit']+=independent and not actual
    variants=defaultdict(dict)
    for z in rows(HERE/'local/pilot_diagnostics.jsonl'):
        k=(z['query_id'],z['grouping'],z['mask']);assert k not in distinct;distinct.add(k)
        ids=z['id_order'];d={ids.index(u) for u in previous[z['query_id']]['ranking']}
        rule=z['rule'];ref=z['matched'];targets={t:set(ix) for t,ix in z['support_targets'].items()}
        assert len(rule['proposal'])==len(ref['proposal'])
        assert len(set(rule['proposal'])&d)==len(set(ref['proposal'])&d)
        assert set(rule['proposal'])<=set(rule['two'])<=set(rule['pre'])
        assert rule['answer_f1'] is None and ref['answer_f1'] is None
        assert rule['answer_status']==ref['answer_status']=='NOT_GENERATED'
        variants[z['query_id'],z['grouping']][z['mask']]=rule
        for kind,r,stages in [('RULE',rule,('pre','two','proposal','final')),('COUNT_MATCHED_DENSE',ref,('proposal','final'))]:
            for stage in stages:
                got={t for t,ix in targets.items() if ix&set(r[stage])}
                key=(z['dataset'],z['grouping'],z['mask'],kind,stage)
                summary[key].update({'queries':1,'hits':len(got),'targets':len(targets),'units':len(r[stage])})
                if kind=='RULE':assert got==set(z['target_hits_by_stage'][stage])
        checks['matched_composition_and_stage_checks']+=1
    equivalence=defaultdict(Counter)
    for (qid,gn),v in variants.items():
        tag=losses[qid]['dataset'];a=equivalence[tag+'/'+gn]
        for mask in off:
            a[mask+'_rank_changed_vs_g0']+=v[mask]['final']!=v['G0']['final']
            a[mask+'_members_changed_vs_g0']+=set(v[mask]['final'])!=set(v['G0']['final'])
        for lo,hi in [('G0','G2'),('G1','G3'),('G3','G4')]:
            a[hi+'_same_final_as_'+lo]+=v[hi]['final']==v[lo]['final']
    with (HERE/'MASK_AND_BREADTH_COMPARISON.csv').open(encoding='utf-8') as f:
        for z in csv.DictReader(f):
            if z['stage']=='reference':continue
            key=tuple(z[t] for t in ('dataset','grouping','mask','kind','stage'))
            for name in ('queries','hits','targets','units'):assert int(z[name])==summary[key][name]
            checks['aggregate_rows_checked']+=1
    assert len(distinct)==4800
    save('SUPPLEMENTARY_CHECKS.json',{'status':'PASS','checks':checks,'full_gb_and_pilot_kmeans_gate_interactions':gate,
        'full_first_new_term_target_paths':targetstats,'pilot_rule_changes':equivalence,
        'path_note':'Full target-path counts only evaluate independent hard-gate truth, not full-history new mask rankings or answers.',
        'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-wall})
    print(json.dumps({'checks':checks,'gate':gate,'target_paths':targetstats,'changes':equivalence,
        'cpu_seconds':time.process_time()-cpu}),flush=True)

if __name__=='__main__':main()
