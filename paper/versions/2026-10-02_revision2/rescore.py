"""Append-only historical prediction review. No model or retrieval imports."""
from __future__ import annotations
import ast
import collections
import csv
import hashlib
import json
import re
import string
import urllib.request
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / 'scoring'
H = 'hotpotqa_train_distractor_v1_1'
M = 'musique_ans_v1_0_train'
CONFIGS = dict(zip(['4E','4F','4G','4H','4I','5A'], [
 'stage4e_e2e_official_train1000_v1','stage4f_xdr_official','stage4g_gtr_official',
 'stage4h_cbe_official','stage4i_sdc_official','stage5a_bnh_official']))
IDENTITIES = {}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def rows(path, expected=None):
    p=Path(path); b=p.read_bytes()
    identity={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest().upper()}
    if expected:
        assert identity == {k:expected[k] for k in identity}, f'Identity mismatch: {p.name}'
    IDENTITIES[str(p)] = {**identity,'frozen_binding_verified':bool(expected)}
    return [json.loads(line) for line in b.splitlines() if line.strip()]

def save(name,obj):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def table(name,data):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

def official():
    specs={
      'hotpot':('hotpotqa/hotpot','3635853403a8735609ee997664e1528f4480762a','hotpot_evaluate_v1.py','D35FC91A6DB21D791DBDDA11DAF3856E9359F5701D54E3EEFBA20D88FECC02C0'),
      'musique':('StonyBrookNLP/musique','922ac98f19a201998dbdae6d7f2887a5258dbdeb','metrics/answer.py','10368F619B4D5EF5D83748C05A96C0AFD332A14AB5C010740C98D58DFAEFE974')}
    modules={}; provenance={}
    cache=REPO/'temp/revision2_official_sources';cache.mkdir(exist_ok=True)
    for key,(repo,rev,file,sha) in specs.items():
        url=f'https://raw.githubusercontent.com/{repo}/{rev}/{file}'
        path=cache/f'{key}.py'
        b=path.read_bytes() if path.exists() else urllib.request.urlopen(url).read()
        assert hashlib.sha256(b).hexdigest().upper()==sha
        if not path.exists():path.write_bytes(b)
        # Execute only the reviewed, pure metric functions; no CLI/import side effects.
        tree=ast.parse(b.decode());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
        env={'re':re,'string':string,'Counter':collections.Counter,'collections':collections}
        exec(compile(tree,url,'exec'),env)
        modules[key]=env;provenance[key]={'url':url,'commit':rev,'sha256':sha,'bytes':len(b)}
    save('OFFICIAL_SCORER_SOURCES.json',provenance)
    return modules

def norm(s):
    return ' '.join(re.sub(r'\b(a|an|the)\b',' ',''.join(c for c in s.lower() if c not in string.punctuation)).split())

def legacy(pred,answers,stage,dataset):
    p=norm(pred);pt=p.split();em=[];f1=[]
    for answer in answers:
        a=norm(answer);at=a.split();em.append(float(p==a))
        special=(stage in ('4E','4G') and dataset==H and p!=a and (p in ('yes','no','noanswer') or a in ('yes','no','noanswer')))
        overlap=sum((collections.Counter(pt)&collections.Counter(at)).values())
        if special:f=0.
        elif not pt or not at:f=0. if stage=='4E' else float(pt==at)
        elif not overlap:f=0.
        else:
            precision=overlap/len(pt);recall=overlap/len(at);f=2*precision*recall/(precision+recall)
        f1.append(f)
    return max(em),max(f1)

def canonical(pred,answers,dataset,officials):
    if dataset==H:
        assert len(answers)==1, 'Hotpot single-answer contract'
        o=officials['hotpot'];return float(o['exact_match_score'](pred,answers[0])),float(o['f1_score'](pred,answers[0])[0])
    o=officials['musique']
    return float(max(o['compute_exact'](a,pred) for a in answers)),float(max(o['compute_f1'](a,pred) for a in answers))

def check_close(a,b,label):
    assert abs(a-b)<1e-12, (label,a,b)

def interval(arrays,seed):
    # Each column is legacy EM/F1, canonical EM/F1. One draw shared across scorers.
    rng=np.random.default_rng(seed);samples=np.empty((10000,4))
    for i in range(10000):
        samples[i]=np.mean([a[rng.integers(0,len(a),len(a))].mean(axis=0) for a in arrays],axis=0)
    point=np.mean([a.mean(axis=0) for a in arrays],axis=0)
    bounds=np.percentile(samples,[2.5,97.5],axis=0,method='linear')
    return [{'point':float(point[j]),'lower':float(bounds[0,j]),'upper':float(bounds[1,j])} for j in range(4)]

def old_metrics(row,method,stage):
    if stage=='4E':return row['dense' if method=='DENSE_TOP20' else 'static_q25']
    if stage=='4F':return row[method.lower()]
    return row['methods'][method]

def run():
    officials=official();absolute=[];changes=[];comparisons=[];budgets=[];summary={};allarrays={}
    for stage,config_name in CONFIGS.items():
        c=load(REPO/'configs'/f'{config_name}.json')
        for prefix in (['development_','confirmation_'] if stage=='5A' else ['']):
            label=stage+('_development' if prefix=='development_' else '')
            print('SCORING',label,flush=True)
            paths=c['paths']; inputs=c['inputs']
            binding=dict(inputs)
            if stage=='4E':
                pre=load(paths['verified_pregold']);binding['predictions_main']=pre['predictions'];binding['rankings']=pre['rankings']
            elif stage in ('4F','4G'):binding.update(load(paths['verified_pregold'])['artifacts'])
            if stage=='4G':
                gold=sum([rows(inputs[d]['gold']['path'],inputs[d]['gold']) for d in (H,M)],[])
            else:gold=rows(paths[prefix+'gold'],inputs[prefix+'gold'])
            pred=rows(paths[prefix+'predictions_main'],binding.get(prefix+'predictions_main'))
            audit=rows(paths[prefix+('query_scores' if stage=='4G' else 'query_audit')])
            amap={r['query_id']:r for r in audit};gmap={r['query_id']:r for r in gold}
            pmap={(r['query_id'],r['method']):r for r in pred}
            methods=sorted({r['method'] for r in pred});datasets=[d for d in (H,M) if any(g['dataset']==d for g in gold)]
            assert len(gmap)==len(gold)==len(amap) and len(pmap)==len(pred)==len(gold)*len(methods)
            assert set(pmap)=={(q,m) for q in gmap for m in methods}
            assert [r['query_id'] for r in audit]==[r['query_id'] for r in gold], 'Original order mismatch'
            values={};affected=0
            for d in datasets:
                target=[r for r in gold if r['dataset']==d]
                values[d]={}
                for method in methods:
                    v=[];reasons=collections.Counter();alias_effect=0
                    for g in target:
                        q=g['query_id'];p=pmap[q,method];answers=g.get('answers',[g.get('answer')])
                        assert (p['dataset'],p['sample_id'])==(d,g['sample_id'])
                        le=legacy(p['prediction'],answers,stage,d);ca=canonical(p['prediction'],answers,d,officials)
                        old=old_metrics(amap[q],method,stage)
                        for metric,score in zip(('answer_em','answer_f1'),le):check_close(score,old[metric],(label,q,method,metric))
                        v.append((*le,*ca))
                        first=canonical(p['prediction'],answers[:1],d,officials)
                        alias_effect+=int(ca!=first)
                        if any(abs(x-y)>1e-14 for x,y in zip(le,ca)):
                            reason='special_yes_no_noanswer' if norm(p['prediction']) in ('yes','no','noanswer') or any(norm(a) in ('yes','no','noanswer') for a in answers) else 'empty_normalized'
                            reasons[reason]+=1;affected+=1
                            changes.append(dict(stage=label,dataset=d,query_id=q,method=method,prediction=p['prediction'],reason=reason,legacy_em=le[0],legacy_f1=le[1],canonical_em=ca[0],canonical_f1=ca[1]))
                    arr=np.array(v);values[d][method]=arr
                    absolute.append(dict(stage=label,dataset=d,method=method,n=len(v),affected=sum(reasons.values()),special_affected=reasons['special_yes_no_noanswer'],empty_affected=reasons['empty_normalized'],alias_improved_rows=alias_effect,empty_normalized_prediction_rows=sum(not norm(pmap[g['query_id'],method]['prediction']) for g in target),empty_normalized_reference_rows=sum(any(not norm(a) for a in g.get('answers',[g.get('answer')])) for g in target),multiple_reference_rows=sum(len(g.get('answers',[g.get('answer')]))>1 for g in target),legacy_em=arr[:,0].mean(),legacy_f1=arr[:,1].mean(),canonical_em=arr[:,2].mean(),canonical_f1=arr[:,3].mean()))
            # Independently check archived absolute aggregates.
            if stage in ('4E','4F'): agg=load(paths['evaluation_summary']);dsummary={datasets[0]:agg}
            elif prefix=='development_':dsummary=None;agg=load(paths['development_summary'])
            else:
                dsummary=load(paths[prefix+'dataset_summaries'])
                if 'datasets' in dsummary:dsummary=dsummary['datasets']
            for d in datasets:
                for m in methods:
                    if dsummary:
                        for j,k in enumerate(('answer_em','answer_f1')):check_close(values[d][m][:,j].mean(),dsummary[d]['methods'][m][k],(label,d,m,k,'mean'))
                    elif m!='BGE_TOP20':
                        entry=agg['config_summaries'][m.split('_')[1]]['datasets'][d]
                        for j,k in enumerate(('answer_em','answer_f1')):
                            check_close(values[d][m][:,j].mean(),entry['protected_'+k],(label,d,m,k))
                            check_close(values[d]['BGE_TOP20'][:,j].mean(),entry['baseline_'+k],(label,d,k))
            if stage in ('4E','4F','4G'):
                pairs=[('q25_minus_dense','STATIC_Q25_TOP20','DENSE_TOP20')];seed={'4E':20260720,'4F':20260723,'4G':20260724}[stage]
                oldequal=load(paths['equal_weight_summary']) if stage=='4G' else None
            elif stage=='4H':
                comps=['DENSE_TOP20','STRONG_DENSE_TOP20','Q25_NO_PROTECTION','Q25_NO_FACET_HYPEREDGE','BM25_TOP20','DENSE_BM25_HYBRID_TOP20']
                pairs=[(m,'STATIC_Q25_FULL',m) for m in comps];seed=20260725;oldequal=load(paths['equal_weight_summary'])
            elif prefix=='development_':
                pairs=[(m,m,'BGE_TOP20') for m in methods if m!='BGE_TOP20'];seed=None;oldequal=None
            else:
                stem='BGE_NATIVE_HGRAG_' if stage=='5A' else 'BGE_HGRAG_';seed=20260727 if stage=='5A' else 20260726
                pairs=[('protected_minus_bge',stem+'PROTECTED_TOP20','BGE_TOP20'),('protected_minus_unprotected',stem+'PROTECTED_TOP20',stem+'UNPROTECTED_TOP20'),('protected_minus_no_facet',stem+'PROTECTED_TOP20',stem+'NO_FACET_TOP20'),('unprotected_minus_bge',stem+'UNPROTECTED_TOP20','BGE_TOP20')]
                if stage=='4I':pairs=[pairs[0],pairs[1],pairs[3],pairs[2]]
                oldequal=load(paths[prefix+'equal_weight_summary'])
            for i,(key,left,right) in enumerate(pairs):
                delta={d:values[d][left]-values[d][right] for d in datasets}
                scopes=datasets+(['equal_weight'] if len(datasets)>1 else [])
                for d in scopes:
                    arrays=[delta[x] for x in datasets] if d=='equal_weight' else [delta[d]]
                    s=seed if stage in ('4E','4F','4G') else (None if seed is None else seed+(1000+i if d=='equal_weight' else 100*i+datasets.index(d)))
                    iv=interval(arrays,s) if s is not None else [{'point':float(np.mean([a[:,j].mean() for a in arrays])),'lower':None,'upper':None} for j in range(4)]
                    if s is not None:
                        if stage in ('4E','4F'): oldiv=agg['bootstrap']
                        elif stage=='4G':oldiv=(oldequal if d=='equal_weight' else dsummary[d])['bootstrap']
                        else:oldiv=oldequal['comparisons'][key]['dataset_equal_weight' if d=='equal_weight' else 'datasets']
                        if stage not in ('4E','4F','4G') and d!='equal_weight':oldiv=oldiv[d]
                        for j,metric in enumerate(('em','f1')):
                            oi=oldiv['delta_answer_'+metric]
                            for k,ok in [('point','point'),('lower','lower_95' if 'lower_95' in oi else 'ci95_lower'),('upper','upper_95' if 'upper_95' in oi else 'ci95_upper')]:check_close(iv[j][k],oi[ok],(label,key,d,metric,k))
                    for j,metric in enumerate(('em','f1')):
                        comparisons.append(dict(stage=label,dataset=d,comparison=key,left=left,right=right,metric=metric,seed=s,legacy_delta=iv[j]['point'],legacy_lower=iv[j]['lower'],legacy_upper=iv[j]['upper'],canonical_delta=iv[j+2]['point'],canonical_lower=iv[j+2]['lower'],canonical_upper=iv[j+2]['upper'],delta_shift=iv[j+2]['point']-iv[j]['point']))
            if stage=='4G':
                interaction={d:(values[d]['STATIC_Q25_TOP20']-values[d]['DENSE_TOP20'])-(allarrays['4E' if d==H else '4F'][d]['STATIC_Q25_TOP20']-allarrays['4E' if d==H else '4F'][d]['DENSE_TOP20']) for d in datasets}
                for d in datasets+['equal_weight']:
                    iv=interval([interaction[x] for x in datasets] if d=='equal_weight' else [interaction[d]],seed)
                    oi=(oldequal if d=='equal_weight' else dsummary[d])['generator_interaction']
                    for j,metric in enumerate(('em','f1')):
                        for k,ok in [('point','point'),('lower','lower_95'),('upper','upper_95')]:check_close(iv[j][k],oi['answer_'+metric][ok],('4G interaction',d,metric,k))
                        comparisons.append(dict(stage=label,dataset=d,comparison='generator_interaction',left='Gemma_q25_minus_dense',right='Qwen_q25_minus_dense',metric=metric,seed=seed,legacy_delta=iv[j]['point'],legacy_lower=iv[j]['lower'],legacy_upper=iv[j]['upper'],canonical_delta=iv[j+2]['point'],canonical_lower=iv[j+2]['lower'],canonical_upper=iv[j+2]['upper'],delta_shift=iv[j+2]['point']-iv[j]['point']))
            prompt=rows(paths[prefix+'prompt_audit_main'],binding.get(prefix+'prompt_audit_main'))
            if stage=='4G':rankings=sum([rows(inputs[d]['rankings']['path'],inputs[d]['rankings']) for d in datasets],[])
            else:rankings=rows(paths[prefix+'rankings'],binding.get(prefix+'rankings'))
            rmap={r['query_id']:r for r in rankings}
            for d in datasets:
                for m in methods:
                    pr=[r for r in prompt if r['dataset']==d and r['method']==m];tokens=np.array([r['input_token_count'] for r in pr]);drops=0
                    for r in pr:
                        rank=rmap[r['query_id']];ids=rank['methods'][m] if 'methods' in rank else rank['dense_top20_unit_ids' if m=='DENSE_TOP20' else 'static_q25_top20_unit_ids']
                        assert r['evidence_unit_ids']==ids[:len(r['evidence_unit_ids'])]
                        drops+=len(r['evidence_unit_ids'])<len(ids)
                    budgets.append(dict(stage=label,dataset=d,method=m,n=len(pr),token_min=int(tokens.min()),token_median=float(np.median(tokens)),token_p95=float(np.percentile(tokens,95)),token_max=int(tokens.max()),token_mean=float(tokens.mean()),at_cap_count=int(sum(tokens==4096)),drop_unit_count=drops,partial_truncation_count=sum(r['rank1_truncated'] for r in pr)))
            summary[label]={'queries':len(gold),'predictions':len(pred),'methods':len(methods),'affected_predictions':affected,'legacy_per_query_means_and_intervals':'RECONSTRUCTED','canonical_status':'COMPLETED','development_reselection':False}
            allarrays[label]=values
    table('LEGACY_VS_CANONICAL_SCORES.csv',absolute);table('PAIRED_COMPARISONS.csv',comparisons)
    if changes:table('AFFECTED_PREDICTIONS.csv',changes)
    table('BUDGET_UTILIZATION_SUMMARY.csv',budgets)
    save('INPUT_IDENTITIES.json',IDENTITIES);save('RECONSTRUCTION_STATUS.json',summary)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':run()
