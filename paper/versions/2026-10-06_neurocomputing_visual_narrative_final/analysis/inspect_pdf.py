"""Render every page and record basic PDF facts; visual review is separate."""
import json, re, sys, time
from pathlib import Path
import fitz
from PIL import Image, ImageOps, ImageDraw
H=Path(__file__).resolve().parents[1];p=Path(sys.argv[1]) if len(sys.argv)>1 else H/'manuscript/main.pdf'
label=sys.argv[2] if len(sys.argv)>2 else 'manuscript';out=H/'build'/label;out.mkdir(exist_ok=True)
cpu=time.process_time();doc=fitz.open(p);info=[]
for i,page in enumerate(doc):
    page.get_pixmap(dpi=120).save(out/f'page_{i+1:02}.png')
    txt=page.get_text();(out/f'page_{i+1:02}.txt').write_text(txt,encoding='utf-8')
    fonts=page.get_fonts(full=True)
    info.append(dict(page=i+1,text_characters=len(txt),first_line=txt.splitlines()[0] if txt else '',fonts=[x[3] for x in fonts],font_types=sorted(set(x[2] for x in fonts))))
for i in range(0,len(doc),4):
    ims=[]
    for j in range(i,min(i+4,len(doc))):
        im=Image.open(out/f'page_{j+1:02}.png').convert('RGB');im.thumbnail((700,990))
        canvas=Image.new('RGB',(720,1030),'#ddd');canvas.paste(im,((720-im.width)//2,30));ImageDraw.Draw(canvas).text((15,8),f'Page {j+1}',fill='black');ims.append(canvas)
    grid=Image.new('RGB',(1440,2060),'white')
    for k,im in enumerate(ims):grid.paste(im,((k%2)*720,(k//2)*1030))
    grid.save(out/f'overview_{i+1:02}.png')
(out/'PAGE_FACTS.json').write_text(json.dumps(dict(pages=len(doc),cpu_seconds=time.process_time()-cpu,details=info),indent=2),encoding='utf-8')
print(json.dumps(dict(pages=len(doc),facts=info),ensure_ascii=False))
