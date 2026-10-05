"""Reconstruct reported numeric summaries, not predictions. Python stdlib only."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


def write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path(__file__).with_name('qa_records.csv'))
    parser.add_argument('--out', type=Path, default=Path('reconstructed'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with args.input.open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    grouped = defaultdict(list)
    for row in rows:
        row['seed'] = int(row['seed'])
        for key in ('full','coverage','f1','em','input_tokens','blocks'):
            row[key] = float(row[key])
        grouped[row['seed'],row['method']].append(row)
    mmr = mean(r['f1'] for r in grouped[1729,'MMR'])
    summary, datasets, own_static, counts = [], [], [], []
    for (seed,method), rr in sorted(grouped.items()):
        assert len(rr) == 128 and len({r['query'] for r in rr}) == 128
        tags = {tag:[r for r in rr if r['dataset']==tag] for tag in ('hotpot','musique')}
        assert all(len(values)==64 for values in tags.values())
        score = mean(mean(r['f1'] for r in values) for values in tags.values())
        summary.append(dict(seed=seed,method=method,n=128,full_count=sum(int(r['full']) for r in rr),
                            full=mean(r['full'] for r in rr),f1=score,delta_f1_mmr=score-mmr,
                            em=mean(r['em'] for r in rr),input_tokens=mean(r['input_tokens'] for r in rr)))
        for tag, values in tags.items():
            datasets.append(dict(seed=seed,method=method,dataset=tag,n=len(values),
                                 full=mean(r['full'] for r in values),f1=mean(r['f1'] for r in values),
                                 coverage=mean(r['coverage'] for r in values),em=mean(r['em'] for r in values),
                                 input_tokens=mean(r['input_tokens'] for r in values),blocks=mean(r['blocks'] for r in values)))
        if method.endswith(' aligned'):
            static = grouped[seed,'Static '+method.split()[0]]
            own_static.append(dict(seed=seed,model=method.split()[0],static_f1=mean(r['f1'] for r in static),
                                   aligned_f1=score,delta_f1=score-mean(r['f1'] for r in static)))
    for seed in (1729,2026):
        a = {r['query']:r for r in grouped[seed,'Static H4']}
        b = {r['query']:r for r in grouped[seed,'H4 aligned']}
        assert a.keys() == b.keys()
        def direction(x):
            return 'gain' if x>1e-12 else 'loss' if x< -1e-12 else 'same'
        for support in ('gain','same','loss'):
            for answer in ('gain','same','loss'):
                counts.append(dict(seed=seed,support_change=support,f1_change=answer,
                                   queries=sum(direction(b[q]['full']-a[q]['full'])==support and
                                               direction(b[q]['f1']-a[q]['f1'])==answer for q in a)))
    for name, data in [('same_panel_qa',summary),('dataset_qa',datasets),('own_static',own_static),('paired_counts',counts)]:
        write(args.out/(name+'.csv'),data)
    print(f'Reconstructed {len(rows)} numeric method-question records on 128 questions; no inference or rescoring.')


if __name__ == '__main__':
    main()
