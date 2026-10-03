"""Descriptive opened-development evaluation. No selection or generation calls."""
from common import *
from repair import METHODS,old
from score import scorers,answer_score
from collections import Counter,defaultdict
import csv

def table(name,data):
    with (HERE/name).open('x',encoding='utf-8',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
def ci(x):return np.quantile(x,[.025,.975]).tolist()
def components(cases):
    parent=list(range(len(cases)));owner={}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,c in enumerate(cases):
        for title in {u['title'] for u in c['units']}:
            if title in owner:parent[find(i)]=find(owner[title])
            else:owner[title]=i
    sizes=Counter(find(i) for i in range(len(cases)))
    return {'components':len(sizes),'largest':max(sizes.values()),'sizes':sorted(sizes.values(),reverse=True)}

def main():
    cpu=time.process_time();wall=time.perf_counter();summary=load(HERE/'GENERATION_SUMMARY.json')
    assert summary['status']=='COMPLETE_INPUT_AND_OUTPUT_RERUN_MATCH'
    official=scorers();inputs=rows(LOCAL/'pilot_inputs.jsonl');pred=rows(LOCAL/'predictions_main.jsonl')
    audit=rows(LOCAL/'prompt_audit.jsonl');ranks=rows(HERE/'pilot_rankings.jsonl')
    pm={(r['query_id'],r['method']):r for r in pred};am={(r['query_id'],r['method']):r for r in audit};rm={(r['query_id'],r['method']):r for r in ranks}
    assert len(pm)==len(am)==len(rm)==5200
    absolute=[];allvalues={};draws={};queryscores=[];details={};rng=np.random.default_rng(20261003)
    for tag in CONFIGS:
        golden={g['query_id']:g for g in rows(config(tag)['paths']['gold'])}
        cases=sorted((z for z in inputs if z['tag']==tag),key=lambda z:key(z['query']))
        assert len(cases)==200
        values=np.empty((200,len(METHODS),2));ds={};groups_by_query={}
        for j,m in enumerate(METHODS):
            acc=defaultdict(list)
            for i,case in enumerate(cases):
                q=case['query']['query_id'];g=golden[q];p=pm[q,m];a=am[q,m];r=rm[q,m]
                values[i,j]=answer_score(tag,p['prediction'],g,official)
                groups=support_groups(tag,g,case['units']);groups_by_query[q]=groups
                support=support_coverage(groups,r['ranking']);visible=support_coverage(groups,a['evidence_unit_ids'])
                queryscores.append({'tag':tag,'query_id':q,'method':m,'em':values[i,j,0],'f1':values[i,j,1],
                    'support_er':support['er'],'support_cr':support['cr'],'visible_er':visible['er'],
                    'tokens':a['input_token_count'],'visible_entries':len(a['evidence_unit_ids'])})
                fields={'support_er':support['er'],'support_cr':support['cr'],'visible_er':visible['er'],
                    'tokens':a['input_token_count'],'visible_entries':len(a['evidence_unit_ids']),
                    'omitted_entries':len(a['omitted_ids']),'partial_truncation':a['rank1_truncated'],
                    'new_entries':r['new_count'],'promotions':r['promotion_count'],'evictions':len(r['removed']),
                    'selection_seconds':r['selection_seconds'],'proposals':r['proposal_count'],
                    'generation_call_seconds':p['generation_seconds'],'actual_generation_seconds':p['actual_generation_seconds'],
                    'cache_hit':p['cache_hit'],'changed_from_h0':r['ranking']!=rm[q,'H0']['ranking'],
                    'changed_members_from_h0':set(r['ranking'])!=set(rm[q,'H0']['ranking']),
                    'facet_count':r['facet_count']}
                for name,v in fields.items():acc[name].append(v)
            ds[m]={k:float(np.mean(v)) for k,v in acc.items()}
            ds[m].update(tokens_p50=float(np.median(acc['tokens'])),tokens_p95=float(np.quantile(acc['tokens'],.95)),tokens_max=max(acc['tokens']))
        allvalues[tag]=values
        indices=rng.integers(0,200,size=(10000,200))
        boot=np.empty((10000,len(METHODS),2))
        for j in range(len(METHODS)):
            for t in range(2):boot[:,j,t]=values[:,j,t][indices].mean(axis=1)
        draws[tag]=boot;details[tag]={'cost_and_evidence':ds,'source_document_dependence':components(cases)}
        for j,m in enumerate(METHODS):
            lo,hi=ci(boot[:,j,1]);elo,ehi=ci(boot[:,j,0])
            absolute.append({'dataset':tag,'method':m,'n_queries':200,'answer_em':values[:,j,0].mean(),'answer_f1':values[:,j,1].mean(),
                'f1_lower':lo,'f1_upper':hi,'em_lower':elo,'em_upper':ehi,**ds[m]})
    both=(draws['hotpot']+draws['musique'])/2
    for j,m in enumerate(METHODS):
        lo,hi=ci(both[:,j,1]);elo,ehi=ci(both[:,j,0])
        means=(allvalues['hotpot'][:,j].mean(axis=0)+allvalues['musique'][:,j].mean(axis=0))/2
        av={k:(details['hotpot']['cost_and_evidence'][m][k]+details['musique']['cost_and_evidence'][m][k])/2 for k in details['hotpot']['cost_and_evidence'][m]}
        # Equal-weight averages of dataset quantiles are explicitly not pooled quantiles.
        absolute.append({'dataset':'equal_dataset_mean','method':m,'n_queries':400,'answer_em':means[0],'answer_f1':means[1],
            'f1_lower':lo,'f1_upper':hi,'em_lower':elo,'em_upper':ehi,**av})
    comparisons=[('H0','Dense20'),('Dense40','Dense20')]
    for l in (.85,.70):
        comparisons += [(f'R1_{l:.2f}','H0'),(f'R2_{l:.2f}',f'R1_{l:.2f}'),(f'R2_{l:.2f}',f'Flat-R2_{l:.2f}'),
            (f'R2_{l:.2f}',f'KMeans-R2_{l:.2f}'),(f'R2_{l:.2f}','Dense20'),(f'R2_{l:.2f}',f'Matched-MMR_{l:.2f}'),
            (f'R2_{l:.2f}','H0'),(f'R2_{l:.2f}','Dense40')]
    contrasts=[]
    for a,b in comparisons:
        ai=METHODS.index(a);bi=METHODS.index(b)
        for tag in ['hotpot','musique','equal_dataset_mean']:
            if tag=='equal_dataset_mean':
                delta=np.vstack([v[:,ai]-v[:,bi] for v in allvalues.values()]);bd=both[:,ai]-both[:,bi]
            else:delta=allvalues[tag][:,ai]-allvalues[tag][:,bi];bd=draws[tag][:,ai]-draws[tag][:,bi]
            lo,hi=ci(bd[:,1]);elo,ehi=ci(bd[:,0])
            contrasts.append({'dataset':tag,'a':a,'b':b,'n_queries':len(delta),'delta_f1':delta[:,1].mean(),
                'lower_f1':lo,'upper_f1':hi,'delta_em':delta[:,0].mean(),'lower_em':elo,'upper_em':ehi,
                'gain':int(sum(delta[:,1]>0)),'same':int(sum(delta[:,1]==0)),'harm':int(sum(delta[:,1]<0))})
    table('PILOT_RESULTS.csv',absolute);table('PAIRED_CONTRASTS.csv',contrasts)
    with (LOCAL/'query_scores.jsonl').open('x',encoding='utf-8') as h:
        for r in queryscores:line(h,r)
    # Proxy-vs-answer joint outcomes; never use these to change configurations.
    proxies={};qs={(r['query_id'],r['method']):r for r in queryscores}
    for tag in CONFIGS:
        for l in (.85,.70):
            for family,base in [('R1','H0'),('R2',f'R1_{l:.2f}')]:
                events=Counter()
                for case in inputs:
                    if case['tag']!=tag:continue
                    q=case['query']['query_id'];m=f'{family}_{l:.2f}';r=rm[q,m]
                    gain=sum(x['proxy_delta'] for x in r['steps']) if family=='R1' else r['eviction']['proxy_gain']
                    fd=qs[q,m]['f1']-qs[q,base]['f1']
                    events[('proxy_gain' if gain>0 else 'proxy_same' if gain==0 else 'proxy_harm')+'|'+('answer_gain' if fd>0 else 'answer_harm' if fd<0 else 'answer_same')]+=1
                proxies[tag+'|'+family+'|'+str(l)]=dict(events)
    save(HERE/'ANALYSIS_DETAILS.json',{'datasets':details,'proxy_answer_cross_tabs':proxies,
        'bootstrap':{'iterations':10000,'seed':20261003,'paired_within_dataset':True,'shared_indices_across_methods':True,'descriptive_only':True,'p_values':False},
        'equal_dataset_quantile_columns':'Arithmetic mean of the two dataset quantiles, not pooled quantiles'})
    # Transparent success/counterexample IDs, no private raw targets in public report.
    cases_out=[]
    for tag in CONFIGS:
        for condition in ['gain','same','harm']:
            candidates=[]
            for case in inputs:
                if case['tag']!=tag:continue
                q=case['query']['query_id'];d=qs[q,'R2_0.85']['f1']-qs[q,'H0']['f1']
                label='gain' if d>0 else 'harm' if d<0 else 'same'
                if label==condition:candidates.append((key(case['query']),q,d))
            pick=min(candidates) if candidates else None
            cases_out.append({'dataset':tag,'condition':condition,'query_id':pick[1] if pick else None,'delta_f1':pick[2] if pick else None})
    save(HERE/'REPRESENTATIVE_CASE_IDS.json',cases_out)
    save(HERE/'EVALUATION_STATUS.json',{'status':'ALL_13_CONFIGS_SCORED','queries':400,'prediction_records':5200,'new_confirmation':False,'selection_after_outcomes':False})
    charge('analyze',cpu,wall,gpu_process_seconds=0)
    print(json.dumps([r for r in contrasts if r['dataset']=='equal_dataset_mean']),flush=True)
if __name__=='__main__':main()
