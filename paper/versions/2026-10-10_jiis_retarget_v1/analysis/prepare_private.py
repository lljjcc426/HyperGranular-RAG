"""Use confirmed local metadata; never embed author identities in public code."""
from pathlib import Path
import re, shutil, zipfile, json, html
H=Path(__file__).resolve().parents[1]
OLD=H.parent/'2026-10-06_neurocomputing_visual_micro_polish'
P=H/'submission_local'; A=P/'source'; A.mkdir(exist_ok=True)
fm=(OLD/'submission_local/author_frontmatter.tex').read_text(encoding='utf-8')
names=re.findall(r'\\author\[aff\]\{([^\\}]+)',fm)
emails=re.findall(r'\\ead\{([^}]+)\}',fm)
with zipfile.ZipFile(OLD/'submission_local/Title_Page.docx') as z:
    title_text=html.unescape(re.sub('<[^>]+>',' ',z.read('word/document.xml').decode()))
orcids=re.findall(r'\d{4}-\d{4}-\d{4}-\d{4}',title_text)
assert len(names)==len(emails)==len(orcids)==4
aff=re.search(r'organization=\{([^}]+)\}',fm)[1]
authors=[]
for i,(n,e,o) in enumerate(zip(names,emails,orcids)):
    first,last=n.rsplit(' ',1)
    star='*' if i==0 else ''
    authors.append('\\author'+star+'[1]{\\fnm{'+first+'} \\sur{'+last+'}\\textsuperscript{\\href{https://orcid.org/'+o+'}{iD}}}\\email{'+e+'}')
authors.append('\\affil[1]{\\orgname{'+aff+'}, \\orgaddress{\\country{China}}}')
credit=(OLD/'submission_local/author_credit.tex').read_text(encoding='utf-8')
credit=credit.replace(r'\section*{CRediT authorship contribution statement}',r'\subsection*{Author contributions}')
files=['sn-jnl.cls','sn-basic.bst','references.bib','additions.bib','nc_references.bib','jiis_references.bib']+[f'Fig{i}.pdf' for i in range(1,6)]
for f in files: shutil.copyfile(H/'manuscript'/f,A/f)
t=(H/'manuscript/main.tex').read_text(encoding='utf-8').replace('% AUTHOR_BLOCK','\n'.join(authors)).replace('% CREDIT_BLOCK',credit)
(A/'main.tex').write_text(t,encoding='utf-8')
(P/'confirmed_metadata.json').write_text(json.dumps({'authors':names,'emails':emails,'orcids':orcids,'affiliation':aff},indent=2),encoding='utf-8')
print('Private Springer title and contribution blocks staged from confirmed local sources.')
