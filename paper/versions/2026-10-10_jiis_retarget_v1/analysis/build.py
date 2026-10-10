"""Local LaTeX build and diagnostic record; never invokes research code."""
import json, subprocess, sys, time
from pathlib import Path
H=Path(__file__).resolve().parents[1]
folder=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else H/'manuscript'
name=sys.argv[2] if len(sys.argv)>2 else 'main'
rows=[]
for command in [['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['bibtex','main'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']]:
    start=time.perf_counter()
    p=subprocess.run(command,cwd=folder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    rows.append({'command':command,'returncode':p.returncode,'wall_seconds':time.perf_counter()-start})
    (H/'build'/f'{name}_{len(rows)}.log').write_bytes(p.stdout)
    if p.returncode:
        print(p.stdout.decode(errors='replace')[-7000:]); raise SystemExit(p.returncode)
(H/'build'/f'{name}_build.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
