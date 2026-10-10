"""Mechanical journal naming/declaration formatting; no result computation."""
from pathlib import Path
import shutil
H=Path(__file__).resolve().parents[1]
p=H/'manuscript/main.tex'
t=p.read_text(encoding='utf-8')
t=t.replace('while MMR remains competitive.', 'while maximal marginal relevance remains competitive.')
t=t.replace(r'\section*{Funding}',r'\section*{Statements and Declarations}'+'\n'+r'\subsection*{Funding}')
for s in ['Declaration of generative AI and AI-assisted technologies in the manuscript preparation process','Declaration of competing interests','Data availability','Ethics and consent']:
    t=t.replace('\\section*{'+s+'}', '\\subsection*{'+s+'}')
for i,n in enumerate(['motivating_examples','study_design','selected_scores','joint_transitions','index_cost'],1):
    shutil.copyfile(H/'manuscript'/f'{n}.pdf',H/'manuscript'/f'Fig{i}.pdf')
    t=t.replace('{'+n+'.pdf}', '{Fig'+str(i)+'.pdf}')
p.write_text(t,encoding='utf-8')
print('Journal names applied; table bodies and values untouched.')
