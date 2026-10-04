"""v4 local I/O; all imported historical runtimes receive this LOCAL/HERE."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
import sys,json,time,hashlib,importlib.util,csv
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
V1=HERE.parent/'2026-10-04_relation_refinement_pilot';V2=HERE.parent/'2026-10-04_rg_active_development_v2';V3=HERE.parent/'2026-10-04_rg_evidence_delivery_v3'
LOCAL=HERE/'local';LOCAL.mkdir(exist_ok=True)
DATA=ROOT.parent/'超粒球RAG_数据';MODEL=DATA/'models/rg_refinement_Qwen2.5-3B-Instruct'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]
def append(p,r):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def save(p,r):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with Path(p).open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
def table(p,rs):
    with Path(p).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
engine=load_module('rg_v4_core_dependency',V1/'core.py');sys.modules['core']=engine
make_windows=load_module('rg_v4_windows_dependency',V1/'windows.py').make_windows
def cases():return read(V1/'local/inputs.json')
def selected():
    byid={c['query_id']:c for c in cases()}
    return [byid[s['query_id']] for s in read(V3/'C_SAMPLE_IDS.json')]
def d0_selected():
    cc=cases();return [c for tag in ('hotpot','musique') for c in sorted((c for c in cc if c['tag']==tag and c['role'].startswith('D0')),key=lambda c:c['sampling_hash'])[:4]]
def old_case(c):return V2/'local/d1'/c['sampling_hash']
def charge(stage,cpu,wall,**kw):append(HERE/'cost.jsonl',dict(stage=stage,cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-wall,**kw))
def budget(current_wall=0,current_cpu=0):
    rs=rows(HERE/'cost.jsonl') if (HERE/'cost.jsonl').exists() else []
    if sum(r.get('gpu_process_seconds',0) for r in rs)+current_wall>=7200:raise RuntimeError('GPU_BUDGET_REACHED')
    if sum(r['cpu_seconds'] for r in rs)+current_cpu>=7200:raise RuntimeError('CPU_BUDGET_REACHED')
    if sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())>=512000000:raise RuntimeError('DISK_BUDGET_REACHED')
