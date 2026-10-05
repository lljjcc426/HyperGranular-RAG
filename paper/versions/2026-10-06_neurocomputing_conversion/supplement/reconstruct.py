"""Reconstruct descriptive tables from saved numeric observations; Python stdlib only.
No answer scorer, bootstrap, model, source text, or network is used.
"""
import csv, json, math, time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'derived'

def read(name):
    with (HERE / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def mean(rows, key): return sum(float(r[key]) for r in rows) / len(rows)

def main():
    cpu = time.process_time(); OUT.mkdir(exist_ok=True)
    pairs = read('paired_numeric.csv'); obs = read('observations.csv')
    groups = defaultdict(list)
    for r in pairs: groups[(r['dataset'],r['seed'],r['model'])].append(r)
    for seed in ('1729','2026'):
        for model in ('H1','H2','H4','DeepSets'):
            groups[('equal64+64',seed,model)] = [r for r in pairs if r['seed']==seed and r['model']==model]
    cells=[]; decom=[]
    for (ds,seed,model), rr in sorted(groups.items()):
        assert len(rr)==(128 if ds=='equal64+64' else 64)
        sums=0
        for tr in ('00','01','10','11'):
            tt=[r for r in rr if ''.join(str(int(float(r[x]))) for x in ('full_static','full_aligned'))==tr]
            total=sum(float(r['delta_f1']) for r in tt); sums+=total
            decom.append(dict(dataset=ds,seed=seed,model=model,transition=tr,n=len(tt),N=len(rr),sum_delta_f1=total,mean_delta_f1=total/len(tt) if tt else '',contribution_to_panel_mean=total/len(rr),sum_delta_coverage=sum(float(r['delta_coverage']) for r in tt),sum_delta_em=sum(float(r['delta_em']) for r in tt),mean_delta_blocks=mean(tt,'delta_blocks') if tt else '',mean_delta_input_tokens=mean(tt,'delta_input_tokens') if tt else '',contexts_changed=sum(int(r['context_changed']) for r in tt)))
            for sign in ('gain','same','harm'):
                n=sum(('gain' if float(r['delta_f1'])>1e-12 else 'harm' if float(r['delta_f1']) < -1e-12 else 'same')==sign for r in tt)
                cells.append(dict(dataset=ds,seed=seed,model=model,transition=tr,f1_direction=sign,n=n,N=len(rr)))
        assert abs(sums-sum(float(r['delta_f1']) for r in rr))<1e-10
    write('PAIRED_TRANSITIONS.csv',cells); write('ENDPOINT_DECOMPOSITION.csv',decom)
    gg=defaultdict(list)
    for r in obs: gg[(r['seed'],r['model'],r['phase'])].append(r)
    qa=[]
    for (seed,model,phase),rr in sorted(gg.items()):
        assert len(rr)==128
        qa.append(dict(seed=seed,model=model,phase=phase,n=128,full_count=sum(int(float(r['full'])) for r in rr),**{k:mean(rr,k) for k in ('coverage','em','f1','blocks','input_tokens','output_tokens')},format_failures=sum(r['format_status']!='VALID_ANSWER_FIELD' for r in rr),output_limit_count=sum(int(r['hit_limit']) for r in rr)))
    write('QA_SUMMARY.csv',qa)
    scores=read('selected_scores.csv'); bins=[]
    for ds in ('hotpot','musique'):
        for model in ('H1','H2','H4','DeepSets'):
            rr=[r for r in scores if r['dataset']==ds and r['model']==model]
            for k in range(5):
                bb=[]
                for r in rr:
                    z=float(r['score']); p=1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
                    if min(4,int(p*5))==k: bb.append((r,p))
                bins.append(dict(dataset=ds,model=model,seed=1729,bin_left=k/5,bin_right=(k+1)/5,n=len(bb),mean_sigmoid=sum(p for _,p in bb)/len(bb) if bb else '',annotated_full_rate=sum(float(r['full']) for r,_ in bb)/len(bb) if bb else ''))
    write('SELECTED_SCORE_BINS.csv',bins)
    checks=dict(status='NUMERIC_RECONSTRUCTION_PASSED',unique_questions=len(set(r['query'] for r in pairs)),paired_rows=len(pairs),numeric_observations=len(obs),groups=len(groups),new_model_calls=0,answer_rescoring=0,new_statistical_tests=0,cpu_seconds=time.process_time()-cpu)
    assert checks['unique_questions']==128 and len(pairs)==1024
    (OUT/'CHECK.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks))

if __name__=='__main__': main()
