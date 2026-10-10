"""Journal-style panel lettering only; no data/geometry change."""
from pathlib import Path
import subprocess,shutil
H=Path(__file__).resolve().parents[1];O=H.parent/'2026-10-06_neurocomputing_visual_micro_polish/figures'
F=H/'figure_sources';F.mkdir(exist_ok=True)
for i,name in enumerate(['motivating_examples','study_design'],1):
 t=(O/f'{name}.tex').read_text(encoding='utf-8')
 for a,b in [('A','a'),('B','b'),('C','c')]:t=t.replace('{'+a+'\\quad','{'+b+'\\quad')
 (F/f'Fig{i}.tex').write_text(t,encoding='utf-8')
 p=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(H/'build'),str(F/f'Fig{i}.tex')],capture_output=True)
 (H/'build'/f'figure{i}_compile.log').write_bytes(p.stdout)
 assert p.returncode==0
 shutil.copyfile(H/'build'/f'Fig{i}.pdf',H/'manuscript'/f'Fig{i}.pdf')
