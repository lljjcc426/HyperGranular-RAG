"""Build original TikZ vectors with installed Arial; do not bundle fonts."""
import json
import shutil
import subprocess
import time
from pathlib import Path
import pymupdf as fitz

H = Path(__file__).resolve().parents[1]
rows = []
for name in ['motivating_examples', 'study_design']:
    start = time.perf_counter()
    p = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                        '-output-directory='+str(H/'build'), name+'.tex'],
                       cwd=H/'figures', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (H/'build'/f'{name}_compile.log').write_bytes(p.stdout)
    if p.returncode:
        raise RuntimeError(p.stdout.decode(errors='replace')[-4000:])
    for target in ['figures', 'manuscript']:
        shutil.copyfile(H/'build'/f'{name}.pdf', H/target/f'{name}.pdf')
    shutil.copyfile(H/'figures'/f'{name}.tex', H/'manuscript'/f'{name}.tex')
    with fitz.open(H/'figures'/f'{name}.pdf') as doc:
        assert len(doc) == 1
        embedded = all(doc.extract_font(f[0])[3] for f in doc[0].get_fonts())
        assert embedded
        doc[0].get_pixmap(dpi=200).save(H/'figures'/f'{name}.png')
        rows.append(dict(name=name, wall_seconds=time.perf_counter()-start,
                         embedded_fonts=embedded, box=list(doc[0].rect)))
(H/'analysis/DIAGRAM_BUILD.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
print('Two original diagram PDFs built with embedded fonts.')
