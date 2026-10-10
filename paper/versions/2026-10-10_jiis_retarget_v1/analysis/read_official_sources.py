"""Retrieve primary publisher pages without the unavailable local proxy."""
from pathlib import Path
import requests,json
from bs4 import BeautifulSoup
H=Path(__file__).resolve().parents[1];S=H/'build/official_sources';S.mkdir(exist_ok=True)
session=requests.Session();session.trust_env=False
urls={'scope':'https://link.springer.com/journal/10844/aims-and-scope','publishing':'https://link.springer.com/journal/10844/how-to-publish-with-us','guidelines':'https://link.springer.com/journal/10844/submission-guidelines','feedback':'https://link.springer.com/article/10.1007/s10844-026-01025-y'}
rows=[]
for name,url in urls.items():
 r=session.get(url,timeout=30);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
 title=soup.title.get_text();assert 'Client Challenge' not in title
 for e in soup.select('script,style,nav,footer,header'):e.decompose()
 main=soup.find('main') or soup
 text=main.get_text('\n',strip=True)
 (S/f'{name}.txt').write_text(text,encoding='utf-8')
 rows.append({'source':name,'url':url,'title':title,'status':r.status_code,'text_characters':len(text),'retrieved_date':'2026-10-10'})
(H/'verification/OFFICIAL_SOURCE_RECORD.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
