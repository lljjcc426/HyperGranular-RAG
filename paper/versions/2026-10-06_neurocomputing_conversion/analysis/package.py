"""Allowlisted public archives; never include author materials or raw source data."""
import json, shutil, subprocess, zipfile
from pathlib import Path
H=Path(__file__).resolve().parents[1]
for name in ('elsarticle.cls','elsarticle-num.bst'):
    source=subprocess.check_output(['kpsewhich',name],text=True).strip()
    shutil.copyfile(source,H/'manuscript'/name)
shutil.copyfile(H/'manuscript/main.pdf',H/'Manuscript_Neurocomputing_Review.pdf')
sources=['main.tex','references.bib','additions.bib','nc_references.bib','main.bbl','elsarticle.cls','elsarticle-num.bst','qa_table.tex','paired_table.tex','decomposition.tex','reference_table.tex','joint_transitions.pdf','selected_scores.pdf','index_cost.pdf']
with zipfile.ZipFile(H/'Neurocomputing_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for n in sources:z.write(H/'manuscript'/n,n)
with zipfile.ZipFile(H/'Reproducibility_Supplement.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((H/'supplement').rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(H/'supplement').as_posix())
reports={}
for name,folder in [('Neurocomputing_Source.zip','clean_source'),('Reproducibility_Supplement.zip','clean_supplement')]:
    out=H/'build'/folder;out.mkdir(exist_ok=True)
    with zipfile.ZipFile(H/name) as z:
        assert all(not n.startswith(('/','../')) and not any(x in n.lower() for x in ('private','submission_local','.git','font','weight')) for n in z.namelist())
        z.extractall(out);reports[name]=z.namelist()
(H/'analysis/ARCHIVE_CONTENTS.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps({n:len(v) for n,v in reports.items()}))
