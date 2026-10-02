"""Local document compilation and page rendering; no experiment code."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

ROOT=Path(__file__).resolve().parent
TEX=Path.home()/'AppData/Local/Programs/MiKTeX/miktex/bin/x64'

def build(name):
    folder=ROOT/name
    builddir=folder/'build'
    builddir.mkdir(exist_ok=True)
    commands=[
        [str(TEX/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],
        [str(TEX/'bibtex.exe'),'build/main'],
        [str(TEX/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],
        [str(TEX/'pdflatex.exe'),'-interaction=nonstopmode','-halt-on-error','-output-directory=build','main.tex'],
    ]
    # Added tables shift float/page references in both manuscripts.
    commands.append(commands[-1])
    for i,cmd in enumerate(commands,1):
        env=dict(os.environ)
        env['BSTINPUTS']=str(ROOT/'shared')+os.pathsep
        env['BIBINPUTS']=str(ROOT/'shared')+os.pathsep
        result=subprocess.run(cmd,cwd=folder,capture_output=True,env=env)
        (builddir/f'command_{i}.log').write_bytes(result.stdout+b'\n'+result.stderr)
        print(name,'command',i,'exit',result.returncode,flush=True)
        if result.returncode:
            print(result.stdout.decode('utf-8',errors='replace')[-5000:])
            raise SystemExit(result.returncode)
    output=folder/f'HyperGranular-RAG_{name.capitalize()}.pdf'
    shutil.copyfile(builddir/'main.pdf',output)
    doc=fitz.open(output)
    review=folder/'page_review'
    review.mkdir(exist_ok=True)
    pages=[]
    for i,p in enumerate(doc):
        p.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(review/f'page_{i+1:02}.png')
        pages.append({'page':i+1,'width':p.rect.width,'height':p.rect.height,'text_characters':len(p.get_text()),'visual_review':'PENDING'})
    (builddir/'extracted_text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n'+p.get_text(sort=True) for i,p in enumerate(doc)),encoding='utf-8')
    for first in range(0,len(doc),6):
        sheet=Image.new('RGB',(1200,1700),'#e7e9ec')
        draw=ImageDraw.Draw(sheet)
        for j in range(first,min(first+6,len(doc))):
            im=Image.open(review/f'page_{j+1:02}.png')
            im.thumbnail((390,795))
            x=((j-first)%3)*400+(400-im.width)//2
            y=((j-first)//3)*850+30
            sheet.paste(im,(x,y))
            draw.text((x,y-20),f'{name} page {j+1}',fill='black')
        sheet.save(review/f'contact_{first+1:02}.png')
    result={'document':name,'pdf':str(output),'pages':len(doc),'compiler':'MiKTeX pdfTeX 4.23 (25.12)','commands_exited_zero':len(commands),'page_checks':pages}
    (folder/'BUILD_STATUS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'document':name,'pages':len(doc),'pdf':str(output)}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('versions',nargs='+',choices=['conference','journal'])
    for version in parser.parse_args().versions:build(version)
