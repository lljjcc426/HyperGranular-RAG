"""Check manuscript aggregates and retained old-manuscript identities only.

Does not read prediction rows, Gold maps, restricted data, or execute evaluators.
"""
from pathlib import Path
import csv
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SHARED = HERE / 'shared'
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

record = read(SHARED/'evidence_check.json')
sources = {k: read(REPO/'results'/v) for k,v in record['sources'].items()}
dataset_files = {
    'H': 'stage4h_cbe_hotpot1000_musique1500_v1_dataset_summaries.json',
    'I': 'stage4i_sdc_hotpot1000_musique1500_v1_dataset_summaries.json',
    'A': 'stage5a_bnh_confirmation_dataset_summaries.json',
}
datasets = {k: read(REPO/'results'/v) for k,v in dataset_files.items()}
checks = []
metrics = {'f1':'answer_f1','em':'answer_em','cr20':'retrieval_cr20','er20':'retrieval_er20'}
def mean(stage, method, metric):
    rows = [v['methods'][method][metric] for k,v in datasets[stage].items() if not k.startswith('_')]
    assert len(rows) == 2
    return sum(rows)/2
def compare(label, published, value):
    assert abs(float(published)-value) <= 0.00000501, (label,published,value)
    checks.append({'field':label,'display':published,'aggregate_value':value})

with (SHARED/'table1_core.csv').open(encoding='utf-8-sig',newline='') as f:
    compact = list(csv.DictReader(f))
for row,stage in zip(compact,['E','F','H']):
    for arm in ['dense','full']:
        method = 'DENSE_TOP20' if arm=='dense' else ('STATIC_Q25_FULL' if stage=='H' else 'STATIC_Q25_TOP20')
        for suffix,metric in metrics.items():
            value = mean(stage,method,metric) if stage=='H' else sources[stage]['methods'][method][metric]
            compare(f'{stage}/{arm}/{metric}',row[f'{arm}_{suffix}'],value)
with (SHARED/'table6_core.csv').open(encoding='utf-8-sig',newline='') as f:
    strong = list(csv.DictReader(f))
arms = [('H','STRONG_DENSE_TOP20'),('H','STATIC_Q25_FULL'),
        ('I','BGE_TOP20'),('I','BGE_HGRAG_PROTECTED_TOP20'),
        ('A','BGE_TOP20'),('A','BGE_NATIVE_HGRAG_PROTECTED_TOP20')]
for row,(stage,method) in zip(strong,arms):
    for suffix,metric in metrics.items():
        compare(f'{stage}/{method}/{metric}',row[f'equal_weight_{suffix}'],mean(stage,method,metric))

bib=(SHARED/'references.bib').read_text(encoding='utf-8')
bibkeys=set(re.findall(r'@\w+\{([^,]+),',bib))
citation_checks={}
for version in ['conference','journal']:
    source=(HERE/version/'main.tex').read_text(encoding='utf-8')
    keys={key.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',source) for key in group.split(',')}
    assert keys <= bibkeys, keys-bibkeys
    citation_checks[version]={'unique_citations':len(keys),'missing_keys':sorted(keys-bibkeys)}

old=[]
for entry in record['old_manuscript_identity']:
    raw=(REPO/entry['path']).read_bytes()
    unchanged=len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256']
    assert unchanged, entry['path']
    old.append({'path':entry['path'],'unchanged_from_writing_start':unchanged})
result={'scope':'existing aggregate transcription and citation-key checks; not independent metric recomputation',
        'absolute_metric_cells_checked':len(checks),'checks':checks,
        'dataset_sources':dataset_files,'citation_keys':citation_checks,'old_manuscripts':old}
(SHARED/'manuscript_consistency.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','dataset_sources')}))
