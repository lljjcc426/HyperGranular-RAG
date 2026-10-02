"""Record completed page inspection and derive rates from existing audit counts.

Run only after the agent has visually inspected every final rendered page.
This script does not itself perform or claim an automatic visual inspection.
"""
import csv
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
NOTES={
'conference':[
 'Title, abstract, motivation; numerical and placement claims legible.',
 'Contributions, related work, equations 1-2; line numbers stable after extra pass.',
 'Static score, insertion and data design; formula and text fit columns.',
 'Workflow figure/caption, scoring lineage and inference boundaries readable.',
 'Main table, strong baseline and transfer results; no clipped interval text.',
 'Canonical forest, fixed-content placement and limits; graph labels readable.',
 'Component forest, conclusion, disclosure and references; no overlap.',
 'Remaining references, native definition and geometric appendix; formulas fit.',
 'Reproduction appendix and final pagination; no unresolved cross references.'
],
'journal':[
 'Title, abstract, keywords and introduction readable.',
 'Research questions and contribution boundaries coherent; no layout defects.',
 'Related work and problem definition; citations and equation 1 readable.',
 'Historical split predicate and static score equations fit.',
 'Workflow figure and native variant details readable.',
 'Native score, compactness propositions and proofs; mathematical symbols clear.',
 'Static coverage counterexample and background greedy bound; no new guarantee claimed.',
 'Dataset table and baseline/generator design fit page.',
 'Legacy/canonical scorer lineage, 17 corrections and equal-weight estimator readable.',
 'Canonical absolute-score table, uncertainty and verification scope readable.',
 'Component forest and compact/strong comparison; all labels and intervals legible.',
 'Strong-backbone table, native/transfer intervals and placement-set derivation fit.',
 'Main forest, actual token distribution table and visible-evidence verification clear.',
 'Evidence-turnover table and mechanism figure; supporting-unit granularity labeled.',
 'Qualitative case table, cases and cost complexity readable.',
 'Recorded cost table and discussion; process/transaction distinction explicit.',
 'Placement interpretation, future controls and limitations; no clipping.',
 'Conclusion, responsibility statement and bibliography start readable.',
 'References and evidence appendix; long commit identifier fits.',
 'Scorer provenance, terminology table and extension counterexample; no overflow.',
 'Path-dependence appendix and reproduction details; final page complete.'
]}
for name,notes in NOTES.items():
    p=HERE/name/'BUILD_STATUS.json';status=json.loads(p.read_text())
    assert len(notes)==status['pages']
    log=(HERE/name/'build/main.log').read_text(errors='replace')
    assert not re.search(r'Overfull|undefined|Warning:',log),name
    for page,note in zip(status['page_checks'],notes):
        page['visual_review']='REVIEWED';page['note']=note
    status['review_method']='Agent inspected each final page PNG, not text-only or contact-sheet-only review.'
    p.write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')

path=HERE/'scoring/BUDGET_UTILIZATION_SUMMARY.csv'
with path.open(encoding='utf-8',newline='') as f:data=list(csv.DictReader(f))
for row in data:
    for count,rate in [('at_cap_count','at_cap_rate'),('drop_unit_count','drop_unit_rate'),('partial_truncation_count','partial_truncation_rate')]:
        row[rate]=int(row[count])/int(row['n'])
with path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)

bib=(HERE/'shared/references.bib').read_text(encoding='utf-8')
keys=set(re.findall(r'@\w+\s*\{([^,]+),',bib))
checks={}
for name in NOTES:
    source=(HERE/name/'main.tex').read_text(encoding='utf-8')
    citations={k.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',source) for k in group.split(',')}
    assert citations<=keys,(name,citations-keys)
    assert '\\input{../shared/numbers.tex}' in source
    checks[name]={'citation_keys_resolved':len(citations),'shared_canonical_number_macros':True,'final_pages':len(NOTES[name]),'final_log_warnings':0}
(HERE/'MANUSCRIPT_CONSISTENCY.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,indent=2))
