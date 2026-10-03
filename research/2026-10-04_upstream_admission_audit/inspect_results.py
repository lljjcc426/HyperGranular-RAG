"""Read derived aggregates or the bounded local case packet, never execute retrieval."""
import csv,json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='case_trace':
    cases=json.loads((HERE/'local/case_packets.json').read_text(encoding='utf-8'))
    allrows=[json.loads(s) for s in (HERE/'local/pilot_diagnostics.jsonl').read_text(encoding='utf-8').splitlines()]
    for idx,z in enumerate(cases):
        detail=[]
        for u in z['candidates']:
            d={'unit':u['unit_id'],'new':u['gate_record']['new_count'],'failed':u['gate_record']['all_failed_gates'],'paths':{}}
            for r in allrows:
                if r['query_id']!=z['query_id'] or r['grouping']!='GB':continue
                i=r['id_order'].index(u['unit_id']);d['paths'][r['mask']]=[s for s in ('pre','two','proposal','final') if i in r['rule'][s]]
            detail.append(d)
        print(json.dumps({'case':idx,'category':z['category'],'candidates':detail},ensure_ascii=False))
elif len(sys.argv)>1 and sys.argv[1]=='case':
    cases=json.loads((HERE/'local/case_packets.json').read_text(encoding='utf-8'))
    for idx in map(int,sys.argv[2:]):
        z=cases[idx]
        print(json.dumps({'case':idx,'dataset':z['dataset'],'category':z['category'],'hash':z['hash'],'question':z['question']},ensure_ascii=False))
        for j,u in enumerate(z['dense']):print(f'D{j+1} [{u["title"]}] {u["text"]}')
        for j,u in enumerate(z['candidates']):print(f'C{j+1} [{u["title"]}] {u["text"]}')
else:
    rows=list(csv.DictReader((HERE/'MASK_AND_BREADTH_COMPARISON.csv').open(encoding='utf-8')))
    for z in rows:
        if z['stage'] in ('final','reference'):
            print(' | '.join(z.get(k,'') for k in ('dataset','grouping','mask','kind','hits','targets','query_mean_er','added_targets_vs_g0','lost_targets_vs_g0','mean_units','targets_only_rule_vs_matched','targets_only_matched_vs_rule')))
    print((HERE/'RECONCILIATION.json').read_text(encoding='utf-8'))
