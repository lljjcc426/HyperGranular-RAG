"""Bounded public bibliographic metadata check; not a literature or experiment run."""
import concurrent.futures,json,re,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parents[1]
t=(H/'manuscript/main.tex').read_text(encoding='utf-8')
keys=set(k for s in re.findall(r'\\cite\w*\{([^}]+)\}',t) for k in s.split(','))
entries={}
for p in (H/'manuscript').glob('*.bib'):
    text=p.read_text(encoding='utf-8')
    for m in re.finditer(r'@\w+\{([^,]+),',text):
        start=m.end(); depth=1; i=start
        while i<len(text) and depth:
            if text[i]=='{': depth+=1
            elif text[i]=='}': depth-=1
            i+=1
        if m[1] in keys: entries[m[1]]=text[start:i-1]
def field(e,f):
    m=re.search(r'\b'+f+r'\s*=\s*\{',e,re.I)
    if not m:return ''
    start=m.end();i=start;d=1
    while i<len(e) and d:
        if e[i]=='{':d+=1
        elif e[i]=='}':d-=1
        i+=1
    return e[start:i-1]
def fetch(item):
    k,e=item;doi=field(e,'doi');url=field(e,'url')
    row={'key':k,'manuscript_title':field(e,'title'),'manuscript_authors':field(e,'author'),'manuscript_year':field(e,'year'),'doi':doi,'url':url}
    if not doi:
        row['status']='PRIMARY_URL_AND_PRIOR_REGISTER_REVIEW'; return row
    try:
        req=urllib.request.Request('https://api.crossref.org/works/'+doi,headers={'User-Agent':'HGRAG-JIIS-bibliographic-check/1.0'})
        with urllib.request.urlopen(req,timeout=25) as r:m=json.load(r)['message']
        row.update(status='CROSSREF_METADATA_RETRIEVED',registered_title=m.get('title'),registered_authors=[a.get('given','')+' '+a.get('family','') for a in m.get('author',[])],published=m.get('published'),published_online=m.get('published-online'),published_print=m.get('published-print'),volume=m.get('volume'),pages=m.get('page'))
    except Exception as ex:row.update(status='LOOKUP_UNAVAILABLE',detail=str(ex))
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,sorted(entries.items())))
(H/'analysis/REFERENCE_METADATA.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for r in rows:print(r['key'],r['status'],r.get('registered_title',''),r.get('registered_authors',''))
