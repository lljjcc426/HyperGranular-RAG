import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
import sys,json,time,hashlib,importlib.util
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]; V1=HERE.parent/'2026-10-04_relation_refinement_pilot'
LOCAL=HERE/'local';LOCAL.mkdir(exist_ok=True)
DATA=ROOT.parent/'超粒球RAG_数据'
MODEL=DATA/'models/rg_refinement_Qwen2.5-3B-Instruct'
BGE=DATA/'models/huggingface/hub/models--BAAI--bge-large-en-v1.5/snapshots/d4aa6901d3a41ba39fb536a557fa166f842b0e09'
OLD=HERE.parent/'2026-10-03_evidence_delivery_repair'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def append(p,r):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def save(p,r):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
engine=load_module('rg_v1_engine',V1/'core.py')
# v1 windows imports only the pure core; no old I/O is imported or written.
sys.modules['core']=engine
window_module=load_module('rg_v1_windows',V1/'windows.py')
make_windows=window_module.make_windows
def cases(role=None):
    xs=read(V1/'local/inputs.json')
    return [c for c in xs if role is None or (c['role']=='D1' if role=='D1' else c['role'].startswith('D0'))]
def charge(stage,cpu,wall,**kw):
    append(HERE/'cost.jsonl',dict(stage=stage,cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-wall,**kw))
def budget(current_wall=0,current_cpu=0):
    rs=rows(HERE/'cost.jsonl') if (HERE/'cost.jsonl').exists() else []
    if sum(r.get('gpu_process_seconds',0) for r in rs)+current_wall>=21600:raise RuntimeError('GPU_BUDGET_REACHED')
    if sum(r['cpu_seconds'] for r in rs)+current_cpu>=14400:raise RuntimeError('CPU_BUDGET_REACHED')

