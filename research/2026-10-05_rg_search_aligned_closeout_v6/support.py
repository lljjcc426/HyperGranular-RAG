"""v6 accounting and read-only access to the v5 implementation/data."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
V5=HERE.parent/'2026-10-04_rg_learned_set_v5'
sys.path.insert(0,str(V5))
import common as old
from common import read,rows,save,append,table,digest,load_module,ROOT,MODEL,P,V2
import time,json,os
LOCAL=HERE/'local';LOCAL.mkdir(exist_ok=True)
KINDS=('H1','H2','DeepSets','H4')
def charge(stage,cpu,wall,**kw):
    append(HERE/'cost.jsonl',dict(stage=stage,cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-wall,**kw))
def usage():
    rr=rows(HERE/'cost.jsonl') if (HERE/'cost.jsonl').exists() else []
    return sum(r.get('gpu_process_seconds',0) for r in rr),sum(r['cpu_seconds'] for r in rr)
def budget(gpu=0,cpu=0,reserve=False):
    g,c=usage()
    if g+gpu>=(5400 if reserve else 7200):raise RuntimeError('V6_GPU_RESOURCE_BOUNDARY')
    if c+cpu>=10500:raise RuntimeError('V6_CPU_RESOURCE_BOUNDARY_RESERVE_BUILD')
    from datetime import datetime
    if datetime.now().date().isoformat()>'2026-10-07':raise RuntimeError('V6_MODEL_CUTOFF')
def stratified(queries,n,prefix):
    from collections import defaultdict,Counter
    groups=defaultdict(list)
    for q in queries:groups[q['group']].append(q)
    strata=Counter(q['stratum'] for q in queries);total=len(queries);n=min(n,total)
    quota={s:int(n*c/total) for s,c in strata.items()}
    for s in sorted(strata,key=lambda s:(-(n*strata[s]/total-quota[s]),s))[:n-sum(quota.values())]:quota[s]+=1
    out=[];used=set()
    for s in sorted(strata):
        have=0
        for group,qq in sorted(groups.items(),key=lambda x:digest([prefix,x[0]])):
            if group in used or not any(q['stratum']==s for q in qq):continue
            if have+len(qq)>quota[s]:continue
            out+=qq;used.add(group);have+=len(qq)
    return sorted(out,key=lambda q:digest([prefix,q['group'],q['query_id']]))
