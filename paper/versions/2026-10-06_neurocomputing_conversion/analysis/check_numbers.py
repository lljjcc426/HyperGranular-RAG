"""Check published endpoint identities against saved paired observations once."""
import csv, json, re
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def read(name):
    with (H/'supplement'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rr=read('derived/QA_SUMMARY.csv');ix={(r['seed'],r['model'],r['phase']):r for r in rr}
checks=[]
for seed,a,b,fa,fb in [('1729',55,57,.4181066176470588,.3765887605042017),('2026',53,57,.43038340336134456,.38309917717086833)]:
    s=ix[seed,'H4','static'];t=ix[seed,'H4','aligned']
    assert int(s['full_count'])==a and int(t['full_count'])==b
    assert abs(float(s['f1'])-fa)<1e-12 and abs(float(t['f1'])-fb)<1e-12
    cells=[r for r in read('derived/PAIRED_TRANSITIONS.csv') if r['dataset']=='equal64+64' and r['seed']==seed and r['model']=='H4']
    assert sum(int(r['n']) for r in cells)==128
    d=[r for r in read('derived/ENDPOINT_DECOMPOSITION.csv') if r['dataset']=='equal64+64' and r['seed']==seed and r['model']=='H4']
    assert abs(sum(float(r['contribution_to_panel_mean']) for r in d)-(fb-fa))<1e-12
    checks.append(dict(seed=seed,counts=[a,b],f1=[fa,fb],joint_total=128,decomposition_matches=True))
main=(H/'manuscript/main.tex').read_text(encoding='utf-8')
abstract=main.split('\\begin{abstract}')[1].split('\\end{abstract}')[0]
words=len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract))
result=dict(status='PASSED',h4_saved_endpoint_checks=checks,abstract_word_count=words,keyword_count=6,new_inference=0,new_scoring=0)
(H/'analysis/NUMERIC_CHECK.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
