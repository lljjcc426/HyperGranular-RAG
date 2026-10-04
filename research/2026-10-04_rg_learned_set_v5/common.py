"""Scoped v5 I/O and measured resource accounting."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
import sys,json,time,hashlib,importlib.util,csv
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];LOCAL=HERE/'local';LOCAL.mkdir(exist_ok=True)
DATA=ROOT.parent/'超粒球RAG_数据'
MODEL=DATA/'models/rg_refinement_Qwen2.5-3B-Instruct'
BGE=DATA/'models/huggingface/hub/models--BAAI--bge-large-en-v1.5/snapshots/d4aa6901d3a41ba39fb536a557fa166f842b0e09'
V1=HERE.parent/'2026-10-04_relation_refinement_pilot';V2=HERE.parent/'2026-10-04_rg_active_development_v2';V4=HERE.parent/'2026-10-04_rg_context_reader_v4'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]
def save(p,r):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def append(p,r):
    with Path(p).open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def table(p,rs):
    if not rs:return
    keys=list(dict.fromkeys(k for r in rs for k in r))
    with Path(p).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rs)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def charge(stage,cpu,wall,**kw):append(HERE/'cost.jsonl',dict(stage=stage,cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-wall,**kw))
def usage():
    r=rows(HERE/'cost.jsonl') if (HERE/'cost.jsonl').exists() else []
    return sum(x.get('gpu_process_seconds',0) for x in r),sum(x['cpu_seconds'] for x in r)
def budget(current_wall=0,current_cpu=0,qa_reserve=False):
    g,c=usage()
    if g+current_wall >= (12000 if qa_reserve else 18000):raise RuntimeError('GPU_BUDGET_REACHED')
    if c+current_cpu >=14400:raise RuntimeError('CPU_BUDGET_REACHED')
def norm(s):return ' '.join(s.casefold().split())
P=load_module('v5_shared_p2',V4/'protocols.py')
