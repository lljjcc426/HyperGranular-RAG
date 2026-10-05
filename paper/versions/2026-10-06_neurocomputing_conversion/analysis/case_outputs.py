"""Expose only the 16 preselected existing answers after text-first review."""
import json
from pathlib import Path
H=Path(__file__).resolve().parents[1]
cases=json.loads((H/'private/CASE_SELECTION.json').read_text(encoding='utf-8'))
obs=json.loads((H/'private/observations.json').read_text(encoding='utf-8'))
ix={(r['query'],r['seed'],r['model'],r['phase']):r for r in obs}
rows=[]
for c in cases:
    a=ix[c['query'],c['seed'],'H4','static']; b=ix[c['query'],c['seed'],'H4','aligned']
    rows.append(dict(case=c['case'],query=c['query'],seed=c['seed'],support=f"{int(a['full'])}{int(b['full'])}",static_answer=a['prediction'],aligned_answer=b['prediction'],static_f1=a['f1'],aligned_f1=b['f1'],static_em=a['em'],aligned_em=b['em'],static_tokens=a['input_tokens'],aligned_tokens=b['input_tokens'],static_blocks=a['blocks'],aligned_blocks=b['blocks'],static_eos=a['eos'],aligned_eos=b['eos'],static_limit=a['hit_limit'],aligned_limit=b['hit_limit']))
(H/'private/CASE_OUTPUTS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
