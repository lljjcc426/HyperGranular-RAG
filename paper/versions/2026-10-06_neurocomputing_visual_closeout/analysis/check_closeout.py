"""Narrow editorial checks: unchanged evidence, references, build, and packaging."""
import json
import re
import zipfile
from pathlib import Path
import pymupdf as fitz

H = Path(__file__).resolve().parents[1]
OLD = H.parent/'2026-10-06_neurocomputing_final_polish'
main = (H/'manuscript/main.tex').read_text(encoding='utf-8')
start = main.index('Figure~\\ref{fig:design}')
end = main.index('\\subsection{Evidence units and feasible decisions}', start)
assert main[:start] + main[end:] == (OLD/'manuscript/main.tex').read_text(encoding='utf-8')
unchanged = [
    'data_roles_table.tex', 'qa_table.tex', 'paired_table.tex',
    'decomposition.tex', 'reference_table.tex', 'cost_table.tex',
    'joint_transitions.pdf', 'selected_scores.pdf', 'index_cost.pdf',
    'references.bib', 'additions.bib', 'nc_references.bib',
]
for name in unchanged:
    assert (H/'manuscript'/name).read_bytes() == (OLD/'manuscript'/name).read_bytes(), name
for name in ['Reproducibility_Supplement.zip', 'Highlights.txt', 'Highlights.docx']:
    assert (H/name).read_bytes() == (OLD/name).read_bytes(), name
authored = H/'submission_local/authored'
assert (authored/'main.tex').read_text(encoding='utf-8') == '\\def\\WithAuthors{1}\n'+main
for name in ['author_frontmatter.tex', 'author_credit.tex']:
    assert (authored/name).read_bytes() == (OLD/'submission_local'/name).read_bytes()

builds = {}
for name, path in [('main', H/'manuscript'), ('authored', authored), ('clean', H/'build/clean_source')]:
    log = (path/'main.log').read_text(encoding='utf-8', errors='replace')
    assert not re.search(r'Overfull|undefined|Float too large|multiply defined', log, re.I), name
    aux = (path/'main.aux').read_text(encoding='utf-8')
    figures = re.findall(r'\\newlabel\{(fig:[^}]+)\}\{\{(\d+)\}', aux)
    assert figures == [('fig:design', '1'), ('fig:scores', '2'), ('fig:joint', '3'), ('fig:cost', '4')]
    tables = re.findall(r'\\newlabel\{(tab:[^}]+)\}\{\{(\d+)\}', aux)
    assert [n for _, n in tables] == list('123456')
    doc = fitz.open(path/'main.pdf')
    assert len(doc) == 25
    assert all(doc.extract_font(f[0])[3] for p in doc for f in p.get_fonts())
    runs = json.loads((H/'build'/f'{name}_build.json').read_text())
    assert all(r['exit'] == 0 for r in runs)
    builds[name] = dict(pages=len(doc), figure_labels=figures, table_labels=tables,
                       embedded_fonts=True, passes=runs)

def pdf_text(path):
    with fitz.open(path) as d:
        return [p.get_text() for p in d]

assert pdf_text(H/'manuscript/main.pdf') == pdf_text(H/'build/clean_source/main.pdf')
assert (H/'Manuscript_Neurocomputing_VisualCloseout.pdf').read_bytes() == (H/'manuscript/main.pdf').read_bytes()
assert (H/'submission_local/Manuscript_Neurocomputing_WithAuthors_VisualCloseout.pdf').read_bytes() == (authored/'main.pdf').read_bytes()
with zipfile.ZipFile(H/'Neurocomputing_VisualCloseout_Source.zip') as z:
    names = z.namelist()
    assert len(names) == 18 and all('/' not in n for n in names)
    assert not any('author' in n for n in names)
    assert all(z.read(n) == (H/'manuscript'/n).read_bytes() for n in names)

report = dict(status='PASS', scope='Editorial regression only; no rescoring or statistical testing',
              unchanged_body_except_overview_insertion=True, unchanged_assets=unchanged,
              numerical_supplement_byte_identical=True, author_materials_unchanged=True,
              clean_extract_text_matches=True, public_source_members=names, builds=builds,
              model_calls=0, new_experiments=0, gpu_seconds=0, paid_cost=0)
(H/'analysis/CLOSEOUT_CHECK.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('PASS: unchanged evidence and text, 4 figures / 6 tables, both 25-page PDFs, clean source build.')
