"""Compare frozen numeric content and render supplementary/size checks."""
from pathlib import Path
import re,json
import fitz
from PIL import Image,ImageOps
H=Path(__file__).resolve().parents[1];B=H/'build'
old=(B/'layout_baseline.tex').read_text(encoding='utf-8');new=(H/'manuscript/main.tex').read_text(encoding='utf-8')
tabs=lambda t:re.findall(r'\\begin\{tabular\}.*?\\end\{tabular\}',t,re.S)
assert tabs(old)==tabs(new)
eq=lambda t:re.findall(r'\\begin\{equation\}.*?\\end\{equation\}',t,re.S)
assert eq(old)==eq(new)
out={'six_tabular_blocks_exactly_equal':len(tabs(new))==6,'eight_display_equations_exactly_equal':len(eq(new))==8,'keyword_count':len(re.search(r'\\keywords\{([^}]+)\}',new)[1].split(','))}
for kind in ['si_private','si_neutral']:
 ims=sorted(B.glob(kind+'_??.png'))
 canvas=Image.new('RGB',(1800,1700),'#cccccc')
 for i,f in enumerate(ims):
  im=Image.open(f);im.thumbnail((590,830));canvas.paste(im,((i%3)*600,(i//3)*850))
 canvas.save(B/f'{kind}_contact.png')
doc=fitz.open(H/'submission_local/Manuscript_JIIS_WithAuthors.pdf')
for page in [3,5,12,14,16]:
 pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(.75,.75),alpha=False)
 im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 ImageOps.grayscale(im).save(B/f'gray75_page{page}.png')
out['font_embedding']=[]
for i in range(1,6):
 d=fitz.open(H/'manuscript'/f'Fig{i}.pdf')
 out['font_embedding'].append({'figure':i,'fonts':[{'name':f[3],'embedded':bool(d.extract_font(f[0])[3])} for f in d[0].get_fonts()]})
(B/'numeric_format_checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
