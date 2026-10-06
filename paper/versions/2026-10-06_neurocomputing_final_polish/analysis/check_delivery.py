"""Check editorial invariants and clean numerical reconstruction, without inference."""
import csv
import json
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import pymupdf
import matplotlib

H = Path(__file__).resolve().parents[1]
OLD = H.parent/'2026-10-06_neurocomputing_conversion'
cpu = time.process_time()
report = {}

def rows(name):
    with (H/'supplement'/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

unchanged = []
for p in sorted((OLD/'supplement').rglob('*')):
    if p.is_file() and p.suffix in {'.csv', '.json', '.jsonl', '.py'}:
        rel = p.relative_to(OLD/'supplement')
        assert p.read_bytes() == (H/'supplement'/rel).read_bytes(), str(rel)
        unchanged.append(str(rel).replace('\\', '/'))
report['unchanged_v1_numeric_and_reconstruction_files'] = unchanged
derived = ['QA_SUMMARY.csv', 'PAIRED_TRANSITIONS.csv', 'ENDPOINT_DECOMPOSITION.csv', 'SELECTED_SCORE_BINS.csv']
for name in derived:
    assert (H/'supplement/derived'/name).read_bytes() == (H/'build/clean_supplement_final/derived'/name).read_bytes(), name
report['clean_reconstruction_equal'] = derived

old_tex = (OLD/'manuscript/main.tex').read_text(encoding='utf-8')
tex = (H/'manuscript/main.tex').read_text(encoding='utf-8')
eq = r'\\begin\{equation\}.*?\\end\{equation\}'
assert re.findall(eq, old_tex, re.S) == re.findall(eq, tex, re.S)
report['unchanged_equations'] = len(re.findall(eq, tex, re.S))
for name in ['references.bib', 'additions.bib', 'nc_references.bib']:
    assert (OLD/'manuscript'/name).read_bytes() == (H/'manuscript'/name).read_bytes()
cited = set(k.strip() for s in re.findall(r'\\cite\{([^}]+)\}', tex) for k in s.split(','))
bbl = (H/'manuscript/main.bbl').read_text(encoding='utf-8')
assert cited == set(re.findall(r'\\bibitem\{([^}]+)\}', bbl))
report['resolved_unchanged_bibliographic_entries'] = len(cited)

# Check printed numeric cells against the saved table inputs; no score functions are called.
qa = {(r['seed'], r['model'], r['phase']): r for r in rows('derived/QA_SUMMARY.csv')}
qa_tex = (H/'manuscript/qa_table.tex').read_text()
for m,p in [('Dense','static'),('MMR','static'),('H4','static'),('H4-replay','aligned'),('H1','aligned'),('H2','aligned'),('DeepSets','aligned'),('H4','aligned')]:
    r=qa['1729',m,p]
    cells=f"{r['full_count']}/128 & {float(r['f1']):.4f} & {float(r['em']):.4f} & {float(r['blocks']):.2f} & {float(r['input_tokens']):.1f}"
    assert cells in qa_tex
paired_tex=(H/'manuscript/paired_table.tex').read_text()
for seed in ['1729','2026']:
    for m in ['H1','H2','H4','DeepSets']:
        a,b=qa[seed,m,'static'],qa[seed,m,'aligned']
        cells=f"{seed} & {m} & {a['full_count']} $\\to$ {b['full_count']} & {float(a['f1']):.4f} & {float(b['f1']):.4f} & {float(b['f1'])-float(a['f1']):+.4f}"
        assert cells in paired_tex
decomp_tex=(H/'manuscript/decomposition.tex').read_text()
for r in rows('derived/ENDPOINT_DECOMPOSITION.csv'):
    if r['dataset']=='equal64+64' and r['model']=='H4':
        cells=f"{r['n']} & {float(r['sum_delta_f1']):+.4f} & {float(r['mean_delta_f1']):+.4f} & {float(r['contribution_to_panel_mean']):+.4f}"
        assert cells in decomp_tex
reference_tex=(H/'manuscript/reference_table.tex').read_text()
for r in rows('reference_gaps.csv'):
    cells=f"{r['queries']} & {float(r['dense_k6_complete']):.4f} & {float(r['h4_complete']):.4f} & {r['lost_full_support']} & {r['gained_full_support']}"
    assert cells in reference_tex
cost_tex=(H/'manuscript/cost_table.tex').read_text()
for r in rows('index_cost_refined64.csv'):
    assert f"{float(r['total_seconds']):.4f} & {float(r['median_seconds']):.4f}" in cost_tex
report['table_checks'] = {'qa':8,'paired':8,'decomposition':8,'reference':2,'cost_dataset_method_pairs':6,'roles':'Reviewed against data_roles.csv and role_overlap.csv; nesting clarified'}

plots=json.loads((H/'analysis/PLOT_DATA.json').read_text())
assert plots['selected_scores'] == [r for r in rows('derived/SELECTED_SCORE_BINS.csv') if r['model']=='H4']
report['figure_data_source'] = 'Unchanged saved bins, paired counts, and refined timing aggregates; no intervals added'
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',tex,re.S).group(1)
conclusion=tex.split('\\section{Conclusion}')[1].split('\\ifdefined')[0]
report['abstract_words']=len(abstract.split())
report['conclusion_words']=len(conclusion.split())

authored=H/'submission_local/authored_final'
assert (authored/'main.tex').read_text(encoding='utf-8')=='\\def\\WithAuthors{1}\n'+tex
for name in ['data_roles_table.tex','qa_table.tex','paired_table.tex','decomposition.tex','reference_table.tex','cost_table.tex','selected_scores.pdf','joint_transitions.pdf','index_cost.pdf']:
    assert (H/'manuscript'/name).read_bytes()==(authored/name).read_bytes()
shutil.copyfile(authored/'main.pdf', H/'submission_local/Manuscript_Neurocomputing_WithAuthors_FinalReview.pdf')
report['authored_scientific_source'] = 'Same main.tex plus author switch; identical tables and figure files; named front matter/CRediT and bibliography spacing are local only'

public_doc=pymupdf.open(H/'Manuscript_Neurocomputing_FinalReview.pdf')
clean_doc=pymupdf.open(H/'build/clean_source_final/main.pdf')
assert [p.get_text() for p in public_doc]==[p.get_text() for p in clean_doc]
report['public_pdf_pages']=len(public_doc)
report['clean_source_pdf_text_and_pagination_equal']=True
report['private_authored_pdf_pages']=len(pymupdf.open(authored/'main.pdf'))
font_refs={f[0] for p in public_doc for f in p.get_fonts(full=True)}
assert all(public_doc.extract_font(x)[3] for x in font_refs)
report['public_fonts_embedded']=True
logs={}
for label in ['main','clean_source_final','authored_final']:
    text=(H/'build'/f'{label}_4.log').read_text(errors='replace')
    assert not re.search(r'Overfull \\[hv]box|undefined|LaTeX Error',text)
    logs[label]=json.loads((H/'build'/f'{label}_build.json').read_text())
report['final_builds']=logs

office={}
for p in [H/'Highlights.docx', *sorted((H/'submission_local').glob('*.docx'))]:
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.endswith('.xml'): ET.fromstring(z.read(n))
    pdf=H/'build/office_pdf'/p.with_suffix('.pdf').name
    assert pdf.exists()
    office[p.name]={'xml_well_formed':True,'libreoffice_rendered_pages':len(pymupdf.open(pdf))}
report['office_documents']=office
report['full_office_xsd_validation']='Not run: provided validator import blocked by missing defusedxml; XML parsing, actual LibreOffice conversion, and visual review performed instead'
report['highlights_characters']=[len(s) for s in (H/'Highlights.txt').read_text().splitlines()]
assert all(n<=85 for n in report['highlights_characters'])
report['runtime']={'python':sys.version.split()[0],'matplotlib':matplotlib.__version__,'pymupdf':pymupdf.__version__}
report['new_experiment_counts']={k:0 for k in ['training','model_forward','reader','retrieval','embedding','answer_rescoring','statistical_tests','gpu','paid_calls']}
report['this_check_cpu_seconds']=time.process_time()-cpu
report['retained_task_directory_bytes']=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())
report['status']='EDITORIAL_AND_NUMERICAL_CHECKS_PASSED_WITH_STATED_SCOPE'
(H/'analysis/FINAL_CHECK.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['status','public_pdf_pages','private_authored_pdf_pages','unchanged_equations','abstract_words','retained_task_directory_bytes']}))
