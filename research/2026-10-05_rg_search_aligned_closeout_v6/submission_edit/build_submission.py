"""Prepare flat editable manuscripts, compile, render, and package without model execution."""
from pathlib import Path
import argparse
import ctypes
import json
import os
import re
import shutil
import subprocess
import time
import zipfile
import pymupdf as fitz
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
PAPERS = HERE.parent/'manuscripts'


def used_sources(name, destination):
    destination.mkdir(exist_ok=True)
    main = (PAPERS/name/'main.tex').read_text(encoding='utf-8')
    files = {'main.tex': main.replace('../shared/','')}
    for filename in re.findall(r'\\input\{\.\./shared/([^}]+)\}', main):
        files[filename] = (PAPERS/'shared'/filename).read_text(encoding='utf-8')
    citations = set()
    for text in files.values():
        for group in re.findall(r'\\cite\w*\{([^}]+)\}', text):
            citations.update(group.split(','))
    for filename in ('references.bib','additions.bib'):
        bib = (PAPERS/'shared'/filename).read_text(encoding='utf-8')
        entries = re.split(r'(?m)(?=^@)',bib)
        chosen = []
        for entry in entries:
            match = re.match(r'@\w+\{([^,]+),',entry)
            if match and match[1] in citations:
                chosen.append(entry.strip())
        files[filename] = '\n\n'.join(chosen)+'\n'
    for filename,text in files.items():
        (destination/filename).write_text(text,encoding='utf-8')
    support = ['llncs.cls'] if name=='conference' else ['sn-jnl.cls','cuted.sty']
    for filename in support:
        shutil.copyfile(PAPERS/name/filename,destination/filename)
    bst = 'splncs04.bst' if name=='conference' else 'sn-mathphys-num.bst'
    shutil.copyfile(PAPERS/'shared'/bst,destination/bst)
    return citations


def compile_one(name, texbin=None):
    start,cpu = time.perf_counter(),time.process_time()
    dest = HERE/('anonymous_conference' if name=='conference' else 'submission_bundle')
    citations = used_sources(name,dest)
    build = HERE/'build'/name
    build.mkdir(parents=True,exist_ok=True)
    if texbin:
        binary = lambda exe: str(Path(texbin)/(exe+'.exe' if os.name=='nt' else exe))
    else:
        def binary(exe):
            found = shutil.which(exe)
            if found:return found
            return str(Path.home()/'AppData/Local/Programs/MiKTeX/miktex/bin/x64'/(exe+'.exe'))
    env = dict(os.environ)
    for key in ('BIBINPUTS','BSTINPUTS','TEXINPUTS'):
        env[key] = str(dest)+os.pathsep
    latex = [binary('pdflatex'),'-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}','main.tex']
    commands = [latex,[binary('bibtex'),str(build/'main')],latex,latex]
    child_cpu=0.0
    for i,command in enumerate(commands):
        proc=subprocess.Popen(command,cwd=dest,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout,stderr=proc.communicate()
        if os.name=='nt':
            stamps=[ctypes.c_ulonglong() for _ in range(4)]
            ok=ctypes.windll.kernel32.GetProcessTimes(ctypes.c_void_p(int(proc._handle)),*[ctypes.byref(x) for x in stamps])
            if ok:child_cpu+=(stamps[2].value+stamps[3].value)/1e7
        (build/f'command_{i+1}.log').write_bytes(stdout+b'\n'+stderr)
        if proc.returncode:
            print(stdout.decode('utf-8','replace')[-5000:])
            raise RuntimeError(f'{name} command {i+1} failed: {proc.returncode}')
    pdfname = 'Set_Selection_Conference_V6_Submission_Edit.pdf' if name=='conference' else 'Evidence_Selection_Journal_V6_Submission_Edit.pdf'
    shutil.copyfile(build/'main.pdf',dest/pdfname)
    # Include the generated editable bibliography for submission-system compatibility.
    shutil.copyfile(build/'main.bbl',dest/'main.bbl')
    doc=fitz.open(dest/pdfname)
    pages=build/'pages';pages.mkdir(exist_ok=True)
    page_records=[]
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(pages/f'page_{i+1:02}.png')
        text=page.get_text(sort=True)
        page_records.append(dict(page=i+1,characters=len(text),visual_check='PENDING'))
    (build/'text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+p.get_text(sort=True) for i,p in enumerate(doc)),encoding='utf-8')
    for first in range(0,len(doc),4):
        sheet=Image.new('RGB',(1400,1900),'#e7e9ec');draw=ImageDraw.Draw(sheet)
        for i in range(first,min(first+4,len(doc))):
            im=Image.open(pages/f'page_{i+1:02}.png');im.thumbnail((680,900))
            x=(i-first)%2*700+(700-im.width)//2;y=(i-first)//2*950+30
            sheet.paste(im,(x,y));draw.text((x,y-20),f'{name} page {i+1}',fill='black')
        sheet.save(pages/f'contact_{first+1:02}.png')
    log=(build/'main.log').read_text(encoding='utf-8',errors='replace')
    warnings=[line for line in log.splitlines() if any(t in line for t in ('Overfull','undefined','Missing character','Warning:'))]
    bib=(build/'main.bbl').read_text(encoding='utf-8')
    result=dict(document=name,status='COMPILED_VISUAL_REVIEW_PENDING',pdf=f'{dest.name}/{pdfname}',
                pages=len(doc),citations=len(citations),bibliography_items=len(re.findall(r'\\bibitem',bib)),
                commands_succeeded=len(commands),flat_bundle=True,warnings=warnings,page_checks=page_records,
                pdf_metadata=doc.metadata,wall_seconds=time.perf_counter()-start,
                python_cpu_seconds=time.process_time()-cpu,compiler_cpu_seconds=child_cpu,
                new_model_calls=0,training_calls=0,paid=0)
    (HERE/f'BUILD_{name.upper()}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (HERE/'EDITORIAL_COST.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(stage='build_'+name,wall_seconds=result['wall_seconds'],
                               python_cpu_seconds=result['python_cpu_seconds'],
                               compiler_cpu_seconds=child_cpu,new_model_calls=0,paid=0))+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('page_checks','pdf_metadata')},indent=2),flush=True)


def package():
    for folder,name in [('anonymous_conference','Conference_Anonymous_Source.zip'),
                        ('submission_bundle','JIIS_Submission_Bundle.zip'),
                        ('anonymous_supplement','Anonymous_Numerical_Supplement.zip')]:
        with zipfile.ZipFile(HERE/name,'w',zipfile.ZIP_DEFLATED) as z:
            for path in sorted((HERE/folder).iterdir()):
                if path.is_file():z.write(path,arcname=path.name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('targets',nargs='*',choices=['conference','journal','package'])
    parser.add_argument('--tex-bin')
    args=parser.parse_args()
    for name in args.targets or ['conference','journal']:
        if name=='package':package()
        else:compile_one(name,args.tex_bin)
