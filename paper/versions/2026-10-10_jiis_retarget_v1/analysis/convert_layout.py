"""One-time, content-preserving Springer layout baseline; no scientific execution."""
from pathlib import Path
import re
H=Path(__file__).resolve().parents[1]
OLD=H.parent/'2026-10-06_neurocomputing_visual_micro_polish'
p=(OLD/'manuscript/main.tex').read_text(encoding='utf-8')
title=re.search(r'\\title\{(.*?)\}',p).group(1)
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',p,re.S).group(1).strip()
keywords=re.search(r'\\begin\{keyword\}(.*?)\\end\{keyword\}',p,re.S).group(1).replace(r'\sep',',').strip()
body=p.split(r'\end{frontmatter}',1)[1]
body=body.replace(r'\bibliographystyle{elsarticle-num}', '')
body=body.replace(r'\ifdefined\WithAuthors'+'\n'+r'\input{author_credit.tex}'+'\n'+r'\fi','')
body=re.sub(r'\\input\{([^}]+)\}',lambda m:(OLD/'manuscript'/m[1]).read_text(encoding='utf-8'),body)
header=r'''\documentclass[pdflatex,sn-basic,Numbered]{sn-jnl}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,booktabs,array,graphicx,microtype}
\usepackage{placeins,flafter}
\newcommand{\cov}{\operatorname{cov}}
\newcommand{\full}{\operatorname{full}}
\begin{document}
'''
text=header+'\\title{'+title+'}\n% AUTHOR_BLOCK\n\\abstract{'+abstract+'}\n\\keywords{'+keywords+'}\n\\maketitle\n'+body
(H/'manuscript/main.tex').write_text(text,encoding='utf-8')
(H/'build/layout_baseline.tex').write_text(text,encoding='utf-8')
print('Baseline converted to one self-contained main.tex; body and tables preserved.')
