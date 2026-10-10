"""Bounded editorial checks and packaging; no scientific scoring."""
from pathlib import Path
import re, json, shutil, zipfile, subprocess
import fitz
from PIL import Image, ImageOps, ImageDraw
H=Path(__file__).resolve().parents[1]
OLD=H.parent/'2026-10-06_neurocomputing_visual_micro_polish'
M=H/'manuscript'; P=H/'submission_local'; B=H/'build'
# Caption punctuation only; scientific text remains unchanged.
t=(M/'main.tex').read_text(encoding='utf-8')
t=re.sub(r'(\\caption\{[^\n]*?)\.\}(\\label)',r'\1}\2',t)
(M/'main.tex').write_text(t,encoding='utf-8')
subprocess.run([__import__('sys').executable,str(H/'analysis/prepare_private.py')],check=True)
for folder,name in [(M,'neutral'),(P/'source','authored')]:
 subprocess.run([__import__('sys').executable,str(H/'analysis/build.py'),str(folder),name],check=True)
out={}
for folder,name in [(M,'neutral'),(P/'source','authored')]:
 doc=fitz.open(folder/'main.pdf'); out[name]={'pages':len(doc)}
 text='\n'.join(p.get_text() for p in doc)
 out[name]['unresolved_question_marks']='??' in text
 out[name]['overfull_boxes']=(folder/'main.log').read_text(errors='replace').count('Overfull \\')
 assert len(doc)<=25 and '??' not in text
 target=H/'Manuscript_JIIS_Neutral.pdf' if name=='neutral' else P/'Manuscript_JIIS_WithAuthors.pdf'
 shutil.copyfile(folder/'main.pdf',target)
 for i,page in enumerate(doc):
  pix=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  pix.save(str(B/f'{name}_{i+1:02d}.png'))
 for start in range(0,len(doc),4):
  canvas=Image.new('RGB',(1224,1644),'#cccccc')
  for j in range(min(4,len(doc)-start)):
   im=Image.open(B/f'{name}_{start+j+1:02d}.png'); im.thumbnail((602,812))
   canvas.paste(im,((j%2)*612,(j//2)*822))
  canvas.save(B/f'{name}_contact_{start+1:02d}.png')
abstract=re.search(r'\\abstract\{(.*?)\}\s*\\keywords',t,re.S)[1]
out['abstract_word_count']=len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b",re.sub(r'\\[A-Za-z]+','',abstract)))
out['figures']=len(re.findall(r'\\begin\{figure\}',t));out['tables']=len(re.findall(r'\\begin\{table\}',t))
old=(OLD/'manuscript/main.tex')
if not old.exists(): old=OLD/'main.tex'
if not old.exists():
 matches=list(OLD.rglob('main.tex')); old=next(x for x in matches if 'submission_local' not in str(x))
base=old.read_text(encoding='utf-8')
out['old_source']=str(old.relative_to(OLD))
out['display_equations_unchanged']=re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',base,re.S)==re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',t,re.S)
out['five_figure_bytes_unchanged']=all((M/f'Fig{i}.pdf').read_bytes()==(OLD/'figures'/f).read_bytes() for i,f in enumerate(['motivating_examples.pdf','study_design.pdf','selected_scores.pdf','joint_transitions.pdf','index_cost.pdf'],1))
files=['main.tex','main.bbl','sn-jnl.cls','sn-basic.bst','references.bib','additions.bib','nc_references.bib','jiis_references.bib']+[f'Fig{i}.pdf' for i in range(1,6)]
with zipfile.ZipFile(P/'JIIS_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(P/'source'/f,f)
clean=B/'independent_source';clean.mkdir(exist_ok=True)
with zipfile.ZipFile(P/'JIIS_LaTeX_Source.zip') as z:
 assert all('/' not in n for n in z.namelist()); z.extractall(clean)
subprocess.run([__import__('sys').executable,str(H/'analysis/build.py'),str(clean),'independent'],check=True)
a=fitz.open(clean/'main.pdf'); b=fitz.open(P/'source/main.pdf')
out['independent_source_same_page_text']=len(a)==len(b) and all(x.get_text()==y.get_text() for x,y in zip(a,b))
S=B/'supplement'
for private in [False,True]:
 dest=P/'Online_Resource_2.zip' if private else H/'Online_Resource_2_Neutral.zip'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for f in S.rglob('*'):
   if f.is_file() and '__pycache__' not in str(f):z.write(f,f.relative_to(S).as_posix())
  meta=(P/'Online_Resource_2_Metadata.md').read_text() if private else '# JIIS numerical resource\n\nNeutral public copy; author metadata is supplied in the private submission archive.\n'
  z.writestr('JIIS_README.md',meta+'\nRun python reconstruct.py. Saved-score reconstruction only; no answer rescoring or additional tests. README.md retains the original numerical-package scope.\n')
si=B/'independent_numerical';si.mkdir(exist_ok=True)
with zipfile.ZipFile(P/'Online_Resource_2.zip') as z:z.extractall(si)
result=subprocess.run([__import__('sys').executable,'reconstruct.py'],cwd=si,capture_output=True,text=True)
out['numerical_reconstruction_returncode']=result.returncode
out['numerical_reconstruction_output']=result.stdout
out['derived_csv_unchanged']=all(f.read_bytes()==(S/'derived'/f.name).read_bytes() for f in (si/'derived').glob('*.csv'))
for name,path in [('si_private',P/'Online_Resource_1.pdf'),('si_neutral',H/'Online_Resource_1_Neutral.pdf')]:
 doc=fitz.open(path);out[name+'_pages']=len(doc)
 for i,page in enumerate(doc):page.get_pixmap(matrix=fitz.Matrix(1,1)).save(str(B/f'{name}_{i+1:02d}.png'))
(B/'editorial_checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
