"""Isolated pilot I/O. No historical writes, no locked inputs."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
from pathlib import Path
import json, time, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LOCAL=HERE/'local'
OLD=HERE.parent/'2026-10-03_evidence_delivery_repair'
DATA=ROOT.parent/'超粒球RAG_数据'
MODEL=DATA/'models'/'rg_refinement_Qwen2.5-3B-Instruct'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def rows(p):
    with Path(p).open(encoding='utf-8') as f: return [json.loads(s) for s in f if s.strip()]
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def append(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(x,ensure_ascii=False)+'\n')
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def charge(stage,cpu,wall,**extra):
    append(HERE/'COST_LEDGER.jsonl',dict(stage=stage,cpu_seconds=time.process_time()-cpu,
        wall_seconds=time.perf_counter()-wall,**extra))
