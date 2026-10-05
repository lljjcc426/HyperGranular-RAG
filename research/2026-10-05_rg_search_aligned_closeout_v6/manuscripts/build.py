"""Compile new manuscripts and render every page; never replaces an old PDF."""
from pathlib import Path
import os,subprocess,shutil,json,time,sys,ctypes
import pymupdf as fitz
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
TEX=Path.home()/'AppData/Local/Programs/MiKTeX/miktex/bin/x64'
def build(name):
    folder=HERE/name;bd=folder/'build';bd.mkdir(exist_ok=True);cpu=time.process_time();wall=time.perf_counter()
    env=dict(os.environ);env['BSTINPUTS']=str(HERE/'shared')+os.pathsep;env['BIBINPUTS']=str(HERE/'shared')+os.pathsep
    commands=[[str(TEX/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],[str(TEX/'bibtex.exe'),'build/main']]
    commands += [commands[0]]*3
    child_cpu=0.0
    for i,cmd in enumerate(commands):
        p=subprocess.Popen(cmd,cwd=folder,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout,stderr=p.communicate()
        stamps=[ctypes.c_ulonglong() for _ in range(4)]
        ok=ctypes.windll.kernel32.GetProcessTimes(ctypes.c_void_p(int(p._handle)),*[ctypes.byref(t) for t in stamps])
        if not ok:raise OSError('Cannot measure compiler CPU time')
        child_cpu+=(stamps[2].value+stamps[3].value)/1e7
        (bd/f'command_{i+1}.log').write_bytes(stdout+b'\n'+stderr)
        print(name,'compile',i+1,'exit',p.returncode,flush=True)
        if p.returncode:
            with (HERE.parent/'cost.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps(dict(stage='build_failed_'+name,cpu_seconds=time.process_time()-cpu+child_cpu,wall_seconds=time.perf_counter()-wall,gpu_process_seconds=0))+'\n')
            print(stdout.decode('utf-8','replace')[-4000:]);raise RuntimeError('LATEX_BUILD_FAILED')
    out=folder/f'HyperGranular-RAG_{name.capitalize()}_V6.pdf';shutil.copyfile(bd/'main.pdf',out)
    doc=fitz.open(out);review=bd/'pages';review.mkdir(exist_ok=True);rs=[]
    for i,p in enumerate(doc):
        p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(review/f'page_{i+1:02}.png')
        rs.append(dict(page=i+1,characters=len(p.get_text()),visual_status='PENDING'))
    for first in range(0,len(doc),4):
        sheet=Image.new('RGB',(1300,1800),'#e7e9ec');draw=ImageDraw.Draw(sheet)
        for j in range(first,min(first+4,len(doc))):
            im=Image.open(review/f'page_{j+1:02}.png');im.thumbnail((630,850));x=(j-first)%2*650+(650-im.width)//2;y=(j-first)//2*900+30
            sheet.paste(im,(x,y));draw.text((x,y-20),f'{name} page {j+1}',fill='black')
        sheet.save(review/f'contact_{first+1:02}.png')
    text='\n\n'.join(f'PAGE {i+1}\n'+p.get_text(sort=True) for i,p in enumerate(doc));(bd/'text.txt').write_text(text,encoding='utf-8')
    result=dict(document=name,pages=len(doc),commands=len(commands),page_checks=rs,wall_seconds=time.perf_counter()-wall,python_cpu_seconds=time.process_time()-cpu,child_cpu_seconds=child_cpu)
    with (HERE.parent/'cost.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(stage='build_'+name,cpu_seconds=result['python_cpu_seconds']+child_cpu,wall_seconds=result['wall_seconds'],gpu_process_seconds=0))+'\n')
    (folder/'BUILD_STATUS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':
    for name in sys.argv[1:] or ['conference','journal']:build(name)
