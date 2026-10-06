"""Compile the original TikZ overview and render a preview; no data computation."""
import json
from pathlib import Path
import shutil
import subprocess
import time
import pymupdf

H=Path(__file__).resolve().parents[1]
start=time.perf_counter()
p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                  '-output-directory='+str(H/'build'),'study_design.tex'],
                 cwd=H/'figures',capture_output=True)
(H/'build/overview_compile.log').write_bytes(p.stdout+p.stderr)
if p.returncode:
    raise RuntimeError(p.stdout.decode(errors='replace')[-2000:])
for target in [H/'figures/study_design.pdf',H/'manuscript/study_design.pdf']:
    shutil.copyfile(H/'build/study_design.pdf',target)
shutil.copyfile(H/'figures/study_design.tex',H/'manuscript/study_design.tex')
with pymupdf.open(H/'figures/study_design.pdf') as doc:
    assert len(doc)==1
    doc[0].get_pixmap(dpi=200).save(H/'figures/study_design.png')
    fonts={x[0] for x in doc[0].get_fonts(full=True)}
    embedded=all(bool(doc.extract_font(x)[3]) for x in fonts)
    assert embedded
    dimensions=list(doc[0].rect)
(H/'analysis/OVERVIEW_BUILD.json').write_text(json.dumps({
    'status':'COMPILED','wall_seconds':time.perf_counter()-start,
    'pdf_box_points':dimensions,'all_fonts_embedded':embedded,
    'new_measurements':False,'model_calls':0},indent=2),encoding='utf-8')
print('Overview compiled; fonts embedded; PDF, TikZ, and PNG delivered.')
