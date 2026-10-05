"""Read completed numeric records only; no scorer, inference or training imports."""
from pathlib import Path
import csv
import json
import time
import shutil
from collections import defaultdict
from statistics import mean

HERE = Path(__file__).resolve().parent
V6 = HERE.parent
V5 = V6.parent / '2026-10-04_rg_learned_set_v5'


def rows(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def table(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def main():
    wall, cpu = time.perf_counter(), time.process_time()
    current = rows(V6 / 'local/qa.jsonl')
    old = rows(V5 / 'local/qa.jsonl')
    queries = json.loads((V5 / 'local/queries.json').read_text(encoding='utf-8'))
    bounds = json.loads((V6 / 'local/boundaries.json').read_text(encoding='utf-8'))
    qa_ids = set(bounds['qa'])
    selected = [r for r in current if r['query_id'] in qa_ids]
    for r in old:
        if (r['query_id'] in qa_ids and r['setting'] == 'opened'
                and r['budget'] == 1024 and r['seed'] in (1729, 2026)
                and r['method'] in ('H1', 'H2', 'H4-Flat', 'DeepSets')):
            selected.append({**r, 'method': 'Static ' + r['method'].replace('-Flat', '')})
    aliases = {'v5-H4': 'Static H4', 'H4-replay': 'H4 replay'}
    numeric = {}
    id_map = {qid: f'q{i+1:03d}' for i, qid in enumerate(sorted(qa_ids))}
    for r in selected:
        method = aliases.get(r['method'], r['method']).replace('-aligned', ' aligned')
        rec = dict(query=id_map[r['query_id']], dataset=r['tag'], seed=r['seed'], method=method,
                   full=r['complete'], coverage=r['coverage'], f1=r['f1'], em=r['em'],
                   input_tokens=r['tokens'], blocks=r['blocks'])
        key = (rec['seed'], method, rec['query'])
        if key in numeric:
            assert numeric[key] == rec, ('Repeated result differs', key)
        numeric[key] = rec
    records = sorted(numeric.values(), key=lambda r: (r['seed'], r['method'], r['query']))
    table(HERE / 'anonymous_supplement/qa_records.csv', records)
    grouped = defaultdict(list)
    for r in records:
        grouped[r['seed'], r['method']].append(r)
    summary = []
    mmr = mean(r['f1'] for r in grouped[1729, 'MMR'])
    for (seed, method), rr in sorted(grouped.items()):
        assert len(rr) == 128 and {r['query'] for r in rr} == set(id_map.values())
        assert all(sum(r['dataset'] == tag for r in rr) == 64 for tag in ('hotpot', 'musique'))
        summary.append(dict(seed=seed, method=method, n=len(rr), full_count=sum(int(r['full']) for r in rr),
                            full=mean(r['full'] for r in rr), f1=mean(r['f1'] for r in rr),
                            delta_f1_mmr=mean(r['f1'] for r in rr)-mmr,
                            em=mean(r['em'] for r in rr), input_tokens=mean(r['input_tokens'] for r in rr)))
    table(HERE / 'SAME_PANEL_QA.csv', summary)
    by_key = {(r['seed'], r['method']): r for r in summary}
    assert by_key[1729, 'Static H4']['full_count'] == 55
    assert by_key[1729, 'H4 aligned']['full_count'] == 57
    paired = []
    for seed in (1729, 2026):
        a = {r['query']: r for r in grouped[seed, 'Static H4']}
        b = {r['query']: r for r in grouped[seed, 'H4 aligned']}
        assert len(a) == 128 and a.keys() == b.keys()
        for support in ('gain', 'same', 'loss'):
            for answer in ('gain', 'same', 'loss'):
                def direction(x):
                    return 'gain' if x > 1e-12 else 'loss' if x < -1e-12 else 'same'
                count = sum(direction(b[q]['full']-a[q]['full']) == support
                            and direction(b[q]['f1']-a[q]['f1']) == answer for q in a)
                paired.append(dict(seed=seed, support_change=support, f1_change=answer, queries=count))
    table(HERE / 'H4_PAIRED_COUNTS.csv', paired)
    roles = {role: {q['query_id'] for q in queries if q['role'] == role} for role in ('FIT', 'TUNE', 'DEV')}
    roles.update(MINE=set(bounds['mine']), DEV_SELECT=set(bounds['dev']), QA=qa_ids)
    assert roles['MINE'] <= roles['FIT']
    assert roles['DEV_SELECT'] <= roles['TUNE'] and roles['QA'] <= roles['TUNE']
    assert not roles['DEV_SELECT'] & roles['QA']
    role_rows = []
    for role, ids in roles.items():
        qq = [q for q in queries if q['query_id'] in ids]
        role_rows.append(dict(role=role, queries=len(qq), groups=len({q['group'] for q in qq}),
                              hotpot=sum(q['tag']=='hotpot' for q in qq), musique=sum(q['tag']=='musique' for q in qq)))
    table(HERE / 'DATA_ROLES.csv', role_rows)
    overlaps = [dict(left=a, right=b, queries=len(roles[a]&roles[b])) for i,a in enumerate(roles) for b in list(roles)[i+1:]]
    table(HERE / 'ROLE_OVERLAP.csv', overlaps)
    for source, target in [
        (HERE/'DATA_ROLES.csv','data_roles.csv'),
        (HERE/'ROLE_OVERLAP.csv','role_overlap.csv'),
        (V5/'TRAINING_AND_SELECTION_RESULTS.csv','static_selection.csv'),
        (V5/'SEARCH_COSTS_LEAF_PRUNING.csv','index_cost.csv'),
        (V6/'SEARCH_ALIGNED_RESULTS.csv','checkpoint_selection.csv')]:
        shutil.copyfile(source,HERE/'anonymous_supplement'/target)
    order = ['Dense', 'MMR', 'Static H4', 'H4 replay', 'H1 aligned', 'H2 aligned', 'DeepSets aligned', 'H4 aligned']
    tex = [r'\begin{table}[t]\centering\small',
           r'\caption{Same QA panel (64 questions per dataset), seed 1729. Full is annotated support completeness, with counts out of 128. F1 is dataset-equal canonical answer F1; $\Delta$F1 is relative to MMR. Dense/MMR share the token ceiling but may use more than six blocks.}',
           r'\label{tab:qa}', r'\begin{tabular}{lrrr}\toprule',
           r'Method & Full (count) & F1 & $\Delta$F1\\\midrule']
    for method in order:
        r = by_key[1729, method]
        tex.append(f"{method} & {r['full']:.4f} ({r['full_count']}) & {r['f1']:.4f} & {r['delta_f1_mmr']:+.4f}"+r'\\')
    tex += [r'\bottomrule\end{tabular}\end{table}']
    (V6/'manuscripts/shared/qa_table.tex').write_text('\n'.join(tex)+'\n', encoding='utf-8')
    report = dict(task='V6-SUBMISSION-EDITORIAL-ONLY-20261005',
                  source='Completed per-query v5/v6 QA records; no prediction rescoring',
                  verified_same_panel_h4_counts=[55,57], questions=128,
                  full_record_count=len(records), model_calls=0, training_calls=0, paid=0,
                  wall_seconds=time.perf_counter()-wall, cpu_seconds=time.process_time()-cpu)
    (HERE/'DERIVATION_STATUS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    print('H4 primary:', by_key[1729,'Static H4'], by_key[1729,'H4 aligned'])
    print('H4 secondary:', by_key[2026,'Static H4'], by_key[2026,'H4 aligned'])


if __name__ == '__main__':
    main()
