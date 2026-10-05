"""Bounded schema inspection; no scientific modules or model loading."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
for version in ('2026-10-04_rg_learned_set_v5','2026-10-05_rg_search_aligned_closeout_v6'):
    base=ROOT/'research'/version/'local'
    for name in ('selections_1729_main.jsonl','selection_cost_batches.jsonl','dev_metrics.jsonl','training.jsonl','training_history.jsonl'):
        p=base/name
        if p.exists():
            with p.open(encoding='utf-8') as f:r=json.loads(next(f))
            print(version,name,json.dumps(r)[:3500])
base=ROOT/'research/2026-10-04_rg_learned_set_v5/local'
for name in ('queries.json','corpus.json','targets.json'):
    obj=json.loads((base/name).read_text(encoding='utf-8'))
    if isinstance(obj,list):print(name,'list',len(obj),list(obj[0]))
    else:
        k=next(iter(obj));v=obj[k]
        print(name,'dict',len(obj),'first value type',type(v).__name__,'shape',list(v[0]) if isinstance(v,list) else list(v))
