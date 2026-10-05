"""Prepare numeric inputs from completed v5/v6 runs. Never imports research code."""
import csv,hashlib,json,math,shutil,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
V5=ROOT/'research/2026-10-04_rg_learned_set_v5';V6=ROOT/'research/2026-10-05_rg_search_aligned_closeout_v6'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def lines(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x]
def csvout(p,rows):
    rows=list(rows);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def save(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    cpu=time.process_time();wall=time.perf_counter()
    for name in ('private','supplement','analysis','figures','manuscript','submission_local','build'):(HERE/name).mkdir(exist_ok=True)
    q5=lines(V5/'local/qa.jsonl');q6=lines(V6/'local/qa.jsonl')
    ids=sorted({r['query_id'] for r in q6});assert len(ids)==128
    anon={qid:f'q{i+1:03}' for i,qid in enumerate(ids)}
    q5=[r for r in q5 if r['query_id'] in anon and r['budget']==1024 and r['setting']=='opened' and r['method'] in ('Dense','MMR','H1','H2','H4-Flat','DeepSets') and r['seed'] in (1729,2026)]
    q6=[r for r in q6 if r['query_id'] in anon and r['seed'] in (1729,2026) and (r['method'].endswith('-aligned') or r['method']=='H4-replay')]
    records=[];local=[];keys=set()
    for phase,rows in [('static',q5),('aligned',q6)]:
        for r in rows:
            method=r['method'].replace('-Flat','').replace('-aligned','')
            key=(r['query_id'],r['seed'],method,phase);assert key not in keys;keys.add(key)
            out=dict(query=anon[r['query_id']],dataset=r['tag'],seed=r['seed'],model=method,phase=phase,budget=1024,protocol='P2',full=r['complete'],coverage=r['coverage'],em=r['em'],f1=r['f1'],blocks=r['blocks'],input_tokens=r['input_tokens'],output_tokens=r['output_tokens'],eos=int(r['eos']),hit_limit=int(r['hit_limit']),format_status=r['status'],cache_hit=int(r['cache_hit']))
            records.append(out);local.append(dict(out,query_id=r['query_id'],context_key=r['key'],selected=r['selected'],prediction=r['prediction']))
    csvout(HERE/'supplement/observations.csv',records)
    save(HERE/'private/observations.json',local)
    pairs=[];ix={(r['query_id'],r['seed'],r['model'],r['phase']):r for r in local}
    for r in local:
        if r['phase']!='aligned' or r['model']=='H4-replay':continue
        a=ix[(r['query_id'],r['seed'],r['model'],'static')]
        pairs.append(dict(query=r['query'],dataset=r['dataset'],seed=r['seed'],model=r['model'],budget=1024,protocol='P2',full_static=a['full'],full_aligned=r['full'],delta_f1=r['f1']-a['f1'],delta_coverage=r['coverage']-a['coverage'],delta_em=r['em']-a['em'],delta_blocks=r['blocks']-a['blocks'],delta_input_tokens=r['input_tokens']-a['input_tokens'],context_changed=int(a['context_key']!=r['context_key']),members_changed=int(set(a['selected'])!=set(r['selected']))))
    csvout(HERE/'supplement/paired_numeric.csv',pairs)
    back={v:k for k,v in anon.items()};csvout(HERE/'private/PAIRED_QUERY_RECORDS_LOCAL.csv',[dict(r,query_id=back[r['query']]) for r in pairs])
    # Freeze the required selection rule and chosen IDs before reading source text.
    selected=[];used=set()
    for signs in [('gain','harm'),('same',)]:
        for seed in (1729,2026):
            for dataset in ('hotpot','musique'):
                for transition in ('00','01','10','11'):
                    for sign in signs:
                        rr=[r for r in pairs if r['model']=='H4' and r['seed']==seed and r['dataset']==dataset and f"{int(r['full_static'])}{int(r['full_aligned'])}"==transition and ('gain' if r['delta_f1']>1e-12 else 'harm' if r['delta_f1'] < -1e-12 else 'same')==sign and r['query'] not in used]
                        if rr and len(selected)<16:
                            r=min(rr,key=lambda r:hashlib.sha256(('NC-case-v1|'+r['dataset']+'|'+back[r['query']]).encode()).hexdigest())
                            used.add(r['query']);selected.append(dict(r,case=f'C{len(selected)+1:02}',query_id=back[r['query']]))
    save(HERE/'private/CASE_SELECTION.json',selected)
    # Source text first; targets/answer labels are not loaded by this step.
    queries={q['query_id']:q for q in read(V5/'local/queries.json')}
    corpus=read(V5/'local/corpus.json');blocks={b['id']:b for vv in corpus.values() for b in vv}
    text=['# Fixed cases: question and actual selected source text (no answers/Gold)']
    for c in selected:
        a=ix[(c['query_id'],c['seed'],'H4','static')];b=ix[(c['query_id'],c['seed'],'H4','aligned')]
        text += [f"\n## {c['case']} | {c['query']} | {c['dataset']} | seed {c['seed']}",queries[c['query_id']]['question']]
        for group,ii in [('RETAINED',[i for i in a['selected'] if i in b['selected']]),('REMOVED',[i for i in a['selected'] if i not in b['selected']]),('ADDED',[i for i in b['selected'] if i not in a['selected']])]:
            text.append('\n### '+group)
            for i in ii:text.append(blocks[i]['title']+'\n'+blocks[i]['text'])
    (HERE/'private/CASE_TEXT_FIRST.md').write_text('\n\n'.join(text),encoding='utf-8')
    # Preserve saved model outputs only. Dense-K6 per-query logits were not retained.
    score_rows=[]
    for r in lines(V5/'local/selections_1729_main.jsonl'):
        if r['method'] not in ('H1','H2','H4-Flat','DeepSets'):continue
        score_rows.append(dict(dataset=r['tag'],seed=1729,model=r['method'].replace('-Flat',''),panel='TUNE738',score=r['score'],full=r['complete'],coverage=r['coverage'],blocks=r['blocks'],tokens=r['tokens']))
    csvout(HERE/'supplement/selected_scores.csv',score_rows)
    gaps=[]
    with (V5/'DENSE_K6_DIAGNOSTIC.csv').open() as f:
        for r in csv.DictReader(f):
            gaps.append(dict(r,model='H4',seed=1729,per_query_reference_scores='NOT_AVAILABLE',per_query_reference_sets='NOT_RETAINED_BY_DIAGNOSTIC',delta_score_distribution='NOT_AVAILABLE',score_gap_status='EXISTING_AGGREGATE_ONLY'))
    csvout(HERE/'analysis/REFERENCE_SELECTION_GAPS.csv',gaps)
    shutil.copyfile(HERE/'analysis/REFERENCE_SELECTION_GAPS.csv',HERE/'supplement/reference_gaps.csv')
    for src,dest in [('SEARCH_COSTS_LEAF_PRUNING.csv','index_cost_refined64.csv'),('TRAINING_AND_SELECTION_RESULTS.csv','static_selection.csv'),('training_history.jsonl','training_history.jsonl')]:
        p=V5/src if src!='training_history.jsonl' else V5/'local'/src
        shutil.copyfile(p,HERE/'supplement'/dest)
    for src,dest in [('SEARCH_ALIGNED_RESULTS.csv','checkpoint_selection.csv'),('RESOURCE_SUMMARY.json','cost_aligned.json')]:shutil.copyfile(V6/src,HERE/'supplement'/dest)
    shutil.copyfile(V5/'RESOURCE_SUMMARY.json',HERE/'supplement/cost_static.json')
    for name in ('data_roles.csv','role_overlap.csv','DATA_AND_REPRODUCTION.md'):shutil.copyfile(V6/'submission_edit/anonymous_supplement'/name,HERE/'supplement'/name)
    # Add raw timing rows with anonymous within-panel labels; keep old/refined boundaries distinct.
    costs=[];cm={}
    for batch in lines(V5/'local/selection_cost_batches.jsonl'):
        if batch['seed']!=1729 or batch['mode']!='main':continue
        for r in batch['rows']:
            if r['method'] not in ('H4-Flat','H4-GB','H4-KM'):continue
            qh=r['query_hash'];cm.setdefault(qh,f't{len(cm)+1:03}')
            costs.append({k:v for k,v in dict(r,query=cm[qh]).items() if k not in ('query_hash','fallback_flat')})
    csvout(HERE/'supplement/index_cost_original738.csv',costs)
    sources=[V5/'local/qa.jsonl',V6/'local/qa.jsonl',V5/'local/selections_1729_main.jsonl',V5/'DENSE_K6_DIAGNOSTIC.csv',V5/'local/selection_cost_batches.jsonl',V5/'SEARCH_COSTS_LEAF_PRUNING.csv',V5/'local/queries.json',V6/'local/boundaries.json']
    save(HERE/'SOURCE_BINDINGS.json',dict(spec_id='HGRAG-NEUROCOMPUTING-CONVERSION-20261006',base_commit='987189ce48a9eb31bc8fc1468e55bbe5bc57d6b4',analysis_role='POST_HOC_DESCRIPTIVE_ANALYSIS_OF_EXISTING_RUNS',files=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size) for p in sources],private_sources='User input package and author metadata retained locally; excluded from public artifacts',score_gap_limitation='Original diagnostic saved two aggregate rows only; no per-query Dense-K6 score/set trace. No model was loaded to reconstruct it.'))
    save(HERE/'analysis/PREPARATION_CHECK.json',dict(qa_questions=128,paired_rows=len(pairs),expected_paired_rows=1024,case_questions=len(used),saved_score_rows=len(score_rows),cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-wall,new_model_calls=0,answer_rescoring=0))
    print(json.dumps(read(HERE/'analysis/PREPARATION_CHECK.json')))
if __name__=='__main__':main()
