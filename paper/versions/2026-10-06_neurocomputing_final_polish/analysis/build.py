"""Local LaTeX build with real process timing and retained logs."""
import ctypes, json, subprocess, sys, time, shutil
from pathlib import Path
H=Path(__file__).resolve().parents[1]
target=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else H/'manuscript'
label=sys.argv[2] if len(sys.argv)>2 else 'main'
report=[]
for cmd in (['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['bibtex','main'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex'],['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']):
    start=time.perf_counter();p=subprocess.Popen(cmd,cwd=target,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out=p.communicate()[0]; times=[ctypes.c_ulonglong() for _ in range(4)]
    ok=ctypes.windll.kernel32.GetProcessTimes(ctypes.c_void_p(int(p._handle)),*[ctypes.byref(t) for t in times])
    report.append(dict(command=cmd,exit=p.returncode,wall_seconds=time.perf_counter()-start,cpu_seconds=(times[2].value+times[3].value)/1e7 if ok else None))
    (H/'build'/f'{label}_{len(report)}.log').write_bytes(out)
    if p.returncode:
        print(out.decode('utf-8',errors='replace')[-6000:]);break
(H/'build'/f'{label}_build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report));sys.exit(report[-1]['exit'])
