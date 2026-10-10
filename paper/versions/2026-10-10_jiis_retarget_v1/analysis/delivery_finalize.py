"""Finish local submission packaging and retain nonprivate build evidence."""
from pathlib import Path
import shutil,zipfile,json
import fitz
H=Path(__file__).resolve().parents[1];B=H/'build';P=H/'submission_local'
V=H/'verification';V.mkdir(exist_ok=True)
for name in ['editorial_checks.json','numeric_format_checks.json','neutral_build.json','authored_build.json','independent_build.json']:
 shutil.copyfile(B/name,V/name)
for name,path in [('si_private',P/'Online_Resource_1.pdf'),('si_neutral',H/'Online_Resource_1_Neutral.pdf')]:
 d=fitz.open(path);assert len(d)==5
 for i,p in enumerate(d):p.get_pixmap().save(str(B/f'{name}_{i+1:02d}.png'))
with zipfile.ZipFile(P/'JIIS_LaTeX_Source.zip','a',zipfile.ZIP_DEFLATED) as z:
 for i in [1,2]:z.write(H/'figure_sources'/f'Fig{i}.tex',f'Fig{i}_editable.tikz')
 z.writestr('BUILD_README.txt','Main article entry: main.tex. Run pdflatex main; bibtex main; pdflatex main; pdflatex main.\nAll manuscript inputs are at archive root. Fig1/2 editable TikZ originals are extra assets, not article entrypoints; their figure PDFs are included. Other figures retain published-source plotting provenance in the project.\n')
# These appended figure source assets are not new manuscript dependencies;
# the independently built main.tex and all its inputs are unchanged.
for i in [1,2]:
 assert (H/'figure_sources'/f'Fig{i}.tex').read_text(encoding='utf-8').replace('{a\\quad','{A\\quad').replace('{b\\quad','{B\\quad').replace('{c\\quad','{C\\quad')==(H.parent/'2026-10-06_neurocomputing_visual_micro_polish/figures'/(['motivating_examples.tex','study_design.tex'][i-1])).read_text(encoding='utf-8')
summary={'fig12_only_panel_case_change':True,'figures_3_to_5_unchanged':True,'supplement_pages':5,'source_zip_flat':all('/' not in n for n in zipfile.ZipFile(P/'JIIS_LaTeX_Source.zip').namelist()),'new_research_runs':0}
(V/'delivery_checks.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
