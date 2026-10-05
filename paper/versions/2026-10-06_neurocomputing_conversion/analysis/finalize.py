"""Check the delivered archives and record build scope; no model or scoring work."""
import json
import subprocess
import zipfile
from pathlib import Path
import fitz

H = Path(__file__).resolve().parents[1]
ROOT = H.parents[2]
def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

main = fitz.open(H/'Manuscript_Neurocomputing_Review.pdf')
clean = fitz.open(H/'build/clean_source/main.pdf')
assert len(main) == len(clean) == 23
assert [p.get_text() for p in main] == [p.get_text() for p in clean]
fonts = {f[0] for p in main for f in p.get_fonts()}
assert all(main.extract_font(x)[3] for x in fonts)
tables = sorted((H/'supplement/derived').glob('*.csv'))
assert all(p.read_bytes() == (H/'build/clean_supplement/derived'/p.name).read_bytes() for p in tables)
builds = {n:read(H/'build'/f'{n}_build.json') for n in ('main','clean')}
assert all(x['exit'] == 0 for b in builds.values() for x in b)
log = (H/'manuscript/main.log').read_text(encoding='utf-8',errors='replace')
assert 'Overfull' not in log and 'undefined citations' not in log
meta = read(ROOT/'temp/nc_conversion_20261006_input/private/AUTHOR_METADATA_PRIVATE.json')
needles = []
for a in meta['authors']:
    needles += [a['given_name']+' '+a['family_name'],a['email'],a['orcid']]
public = subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',str(H.relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
hits=[]
for name in public:
    p=ROOT/name
    texts=[]
    if p.suffix in ('.zip','.docx'):
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.endswith(('.xml','.tex','.bib','.md','.csv','.json','.py')):
                    texts.append(z.read(n).decode('utf-8',errors='replace'))
    elif p.suffix == '.pdf':
        with fitz.open(p) as d:texts=[page.get_text() for page in d]
    else:texts=[p.read_text(encoding='utf-8',errors='replace')]
    if any(s.casefold() in t.casefold() for s in needles for t in texts):hits.append(name)
assert not hits, hits
reports = [H/'analysis/PREPARATION_CHECK.json',H/'analysis/PLOT_BUILD.json',H/'supplement/derived/CHECK.json',H/'build/clean_supplement/derived/CHECK.json']
reports += list((H/'build').glob('*/PAGE_FACTS.json'))
cpu = sum(read(p).get('cpu_seconds',0) for p in reports) + sum(x['cpu_seconds'] for b in builds.values() for x in b)
paths=[H,ROOT/'temp/nc_conversion_runtime',ROOT/'temp/nc_conversion_20261006_input',ROOT/'temp/nc_lo_profile']
disk={p.relative_to(ROOT).as_posix():sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) for p in paths}
report={'status':'DELIVERY_CHECKS_PASSED','pages':len(main),'clean_archive_pdf_text_matches':True,'fonts_embedded':len(fonts),'reconstructed_csvs_byte_equal':[p.name for p in tables],'build_commands':builds,'public_author_metadata_hits':hits,'public_paths_checked':len(public),'gpu_seconds':0,'new_model_calls':0,'answer_rescoring':0,'paid_cost':0,'retained_instrumented_cpu_seconds_lower_bound':cpu,'cpu_scope_note':'Preparation, last plot/build/render passes and two numerical reconstructions only. Shell, Node/LibreOffice, installation and earlier corrected builds were not all instrumented; total CPU is not claimed exact.','task_disk_bytes_by_directory':disk,'task_disk_bytes_total':sum(disk.values())}
(H/'analysis/DELIVERY_CHECK.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
