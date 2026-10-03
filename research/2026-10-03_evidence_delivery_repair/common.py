"""Scoped input loading and append-only outputs for opened Stage4E/F only."""
import os
for k,v in {'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','CUBLAS_WORKSPACE_CONFIG':':4096:8','TOKENIZERS_PARALLELISM':'false'}.items():os.environ[k]=v
from pathlib import Path
import json,hashlib,sys,time
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LOCAL=HERE/'local'
sys.path.insert(0,str(ROOT/'scripts'))
import stage4e_e2e_goldfree_runner as e
import stage4f_xdr_retrieve_generate as f
CONFIGS={'hotpot':'stage4e_e2e_official_train1000_v1','musique':'stage4f_xdr_official'}

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
    with Path(p).open(encoding='utf-8') as h:return [json.loads(s) for s in h if s.strip()]
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as h:json.dump(x,h,ensure_ascii=False,indent=2);h.write('\n')
def line(h,x):h.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def identity(p):
    p=Path(p)
    with p.open('rb') as h:d=hashlib.file_digest(h,'sha256').hexdigest().upper()
    return {'path':str(p),'bytes':p.stat().st_size,'sha256':d}
def config(tag):return load(ROOT/'configs'/f'{CONFIGS[tag]}.json')
def key(q,prefix='evidence-delivery-repair-v1'):
    return hashlib.sha256((prefix+'\0'+q['dataset']+'\0'+q['query_id']).encode()).hexdigest()
def dataset(tag,verify=True):
    c=config(tag);p={k:Path(v.replace('E:\\科研\\','E:\\SCIENCE\\')) for k,v in c['paths'].items()}
    binding={}
    for name in ['blind','embedding_cache','rankings','prompt_audit_main','predictions_main','gold']:
        ident=identity(p[name]) if verify else {'path':str(p[name])}
        if verify and name in c['inputs']:
            for a in ('bytes','sha256'):assert ident[a]==c['inputs'][name][a],(tag,name,a)
        binding[name]={**ident,'stage':'Stage4E' if tag=='hotpot' else 'Stage4F',
                       'role':'HISTORICALLY_EXPOSED_EXPLORATORY','opened':True,
                       'use':'evaluation/diagnostic only' if name=='gold' else 'reconstruction/generation/diagnostic'}
    blind=rows(p['blind']);units,queries=(e if tag=='hotpot' else f).build_units_queries(blind)
    with np.load(p['embedding_cache'],allow_pickle=False) as cache:
        assert cache['unit_ids'].tolist()==[u['unit_id'] for u in units]
        assert cache['query_ids'].tolist()==[q['query_id'] for q in queries]
        x=cache['unit_embeddings'].copy();q=cache['query_embeddings'].copy()
        metadata=json.loads(str(cache['metadata_json'].item()))
        assert metadata['encoder_revision']=='1110a243fdf4706b3f48f1d95db1a4f5529b4d41'
    assert np.isfinite(x).all() and np.isfinite(q).all()
    spans={};offset=0
    for row in queries:
        n=row['num_candidate_units'];spans[row['query_id']]=(offset,offset+n);offset+=n
    assert offset==len(units)
    return c,p,units,queries,x,q,spans,binding

def support_groups(tag,g,units):
    if tag=='hotpot':
        return {a['unit_id']:{a['unit_id']} for a in g['supporting_facts']}
    return {str(p):{u['unit_id'] for u in units if u['paragraph_index']==p}
            for p in g['supporting_paragraph_indices']}
def support_coverage(groups,ids):
    hits=sum(bool(v&set(ids)) for v in groups.values())
    return {'hits':hits,'total':len(groups),'er':hits/len(groups),'cr':int(hits==len(groups))}

def charge(name,started_cpu,started_wall,**extra):
    with (HERE/'RESOURCE_LEDGER.jsonl').open('a',encoding='utf-8') as h:
        line(h,{'process':name,'cpu_seconds':time.process_time()-started_cpu,
                'wall_seconds':time.perf_counter()-started_wall,**extra})
