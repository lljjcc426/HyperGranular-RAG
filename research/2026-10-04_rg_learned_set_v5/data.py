"""Opened Stage4E/F paragraph union. Labels are a separate local target map."""
from common import *
import collections
import numpy as np

def prepare():
    cpu=time.process_time();wall=time.perf_counter()
    old={r['query_id'] for r in read(V1/'local/inputs.json')}
    corpus={};queries=[];targets={};bindings={}
    for tag,config,meta in [('hotpot','stage4e_e2e_official_train1000_v1','stage4e_e2e_official_train1000_v1_descriptive_metadata.jsonl'),('musique','stage4f_xdr_official','stage4f_xdr_musique_train3000_v1_sealed_metadata.jsonl')]:
        cfg=read(ROOT/'configs'/f'{config}.json');paths={k:Path(v.replace('E:\\科研\\','E:\\SCIENCE\\')) for k,v in cfg['paths'].items()}
        blind=rows(paths['blind']);gold={g['query_id']:g for g in rows(paths['gold'])};metadata={g['query_id']:g for g in rows(DATA/'processed'/meta)}
        bindings[tag]={k:dict(path=str(paths[k]),bytes=paths[k].stat().st_size,previous_binding=cfg['inputs'].get(k)) for k in ('blind','gold')}
        blocks={};sources={}
        for q in blind:
            qid=q['query_id'];g=gold[qid];parts=[]
            if tag=='hotpot':
                for c in q['context']:
                    parts.append((c['context_index'],c['title'],[(f"{qid}::c{c['context_index']}::s{j}",' '.join(s.split())) for j,s in enumerate(c['sentences']) if s.strip()]))
            else:
                byp=collections.defaultdict(list)
                for u in q['candidate_units']:byp[u['paragraph_index']].append(u)
                for pi,us in sorted(byp.items()):parts.append((pi,us[0]['title'],[(u['unit_id'],u['text']) for u in sorted(us,key=lambda u:u['sentence_index'])]))
            closed=[];coverage={};total=len(g['supporting_facts']) if tag=='hotpot' else len(set(g['supporting_paragraph_indices']))
            sf={x['unit_id']:j for j,x in enumerate(g.get('supporting_facts',[]))}
            sp={pi:j for j,pi in enumerate(sorted(set(g.get('supporting_paragraph_indices',[]))))}
            for pi,title,sent in parts:
                text=' '.join(s for _,s in sent);bid=digest([tag,norm(title),norm(text)])
                if bid not in blocks:blocks[bid]=dict(id=bid,title=title,text=text)
                offset=0;mapping=[]
                for uid,s in sent:mapping.append(dict(unit_id=uid,start=offset,end=offset+len(s)));offset+=len(s)+1
                sources.setdefault(bid,[]).append(dict(query_id=qid,paragraph=pi,sentences=mapping))
                closed.append(bid)
                hit={sf[uid] for uid,_ in sent if uid in sf} if tag=='hotpot' else ({sp[pi]} if pi in sp else set())
                if hit:coverage.setdefault(bid,set()).update(hit)
            stratum=metadata[qid]['type'] if tag=='hotpot' else ('2hop' if metadata[qid]['hop_count']==2 else '3_4hop')
            queries.append(dict(query_id=qid,sample_id=q['sample_id'],tag=tag,question=q['question'],stratum=stratum,closed=list(dict.fromkeys(closed))))
            targets[qid]=dict(total=total,coverage={k:sorted(v) for k,v in coverage.items()},gold=g)
        corpus[tag]=[blocks[k] for k in sorted(blocks)]
        save(LOCAL/f'{tag}_sources.json',sources)
    # Union exact normalized questions and identical source IDs, not shared documents.
    parent=list(range(len(queries)))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    seen={}
    for i,q in enumerate(queries):
        for k in ((q['tag'],'text',norm(q['question'])),(q['tag'],'source',q['sample_id'])):
            if k in seen:parent[root(i)]=root(seen[k])
            else:seen[k]=i
    groups=collections.defaultdict(list)
    for i in range(len(queries)):groups[root(i)].append(i)
    for members in groups.values():
        key=min(queries[i]['tag']+'\0'+norm(queries[i]['question']) for i in members)
        h=hashlib.sha256(('rg-learned-set-v5-split\0'+key).encode()).hexdigest()
        role='DEV' if any(queries[i]['query_id'] in old for i in members) else ('TUNE' if int(h[:8],16)%5==0 else 'FIT')
        for i in members:queries[i].update(group=h,role=role,panel=False,sensitivity=False)
    for tag,plan in [('hotpot',[('bridge',48),('comparison',16)]),('musique',[('2hop',32),('3_4hop',32)])]:
        pool=sorted([q for q in queries if q['tag']==tag and q['role']=='TUNE'],key=lambda q:digest(['v5-panel',q['group']]))
        selected=[]
        for s,n in plan:selected.extend([q for q in pool if q['stratum']==s][:n])
        selected += [q for q in pool if q not in selected][:64-len(selected)]
        assert len(selected)==64
        for q in selected:q['panel']=True
        for q in sorted(selected,key=lambda q:digest(['v5-sensitivity',q['group']]))[:32]:q['sensitivity']=True
    overlap={}
    for tag in corpus:
        a={b for q in queries if q['tag']==tag and q['role']=='FIT' for b in q['closed']};b={b for q in queries if q['tag']==tag and q['role']=='TUNE' for b in q['closed']}
        overlap[tag]=dict(fit_documents=len(a),tune_documents=len(b),shared=len(a&b))
    save(LOCAL/'corpus.json',corpus);save(LOCAL/'queries.json',queries);save(LOCAL/'targets.json',targets)
    save(HERE/'DATA_AND_MODELS.json',dict(spec='HGRAG-LEARNED-SET-V5-20261004',status='EXPOSED_DEVELOPMENT',inputs=bindings,
        counts=dict(collections.Counter(q['tag']+'/'+q['role']+'/'+q['stratum'] for q in queries)),panel=dict(collections.Counter(q['tag']+'/'+q['stratum'] for q in queries if q['panel'])),
        corpus={t:len(c) for t,c in corpus.items()},document_overlap=overlap,subquestion_overlap='Native blind inputs do not retain decomposition IDs; not reconstructed from locked/raw material; no unseen-composition claim.',
        encoder=dict(path=str(BGE),revision=BGE.name,max_tokens=512,pooling='CLS/L2',precision='float32'),reader=dict(path=str(MODEL),revision='aa8e72537993ba99e69dfaafa59ed015b17504d1',precision='float16',adapter=False,protocol='v4-P2'),
        budget=dict(gpu_seconds=18000,cpu_seconds=14400,disk_bytes=2000000000,reader_calls=3000,paid=0),initial_cumulative=dict(gpu_seconds=19764.376329,cpu_seconds_lower_bound=18520.078,prior_unmeasured_cpu='UNKNOWN')))
    charge('prepare',cpu,wall,gpu_process_seconds=0);print('prepared',len(queries),{t:len(c) for t,c in corpus.items()},flush=True)

def encode():
    import torch
    from transformers import AutoTokenizer,AutoModel
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);torch.manual_seed(1729)
    tok=AutoTokenizer.from_pretrained(BGE,local_files_only=True);model=AutoModel.from_pretrained(BGE,local_files_only=True).eval().to('cuda')
    corpus=read(LOCAL/'corpus.json');queries=read(LOCAL/'queries.json');log=[]
    try:
        for tag in corpus:
            qq=[q for q in queries if q['tag']==tag]
            for kind,texts in [('blocks',[b['title']+'\n'+b['text'] for b in corpus[tag]]),('queries',['Represent this sentence for searching relevant passages: '+q['question'] for q in qq])]:
                path=LOCAL/f'{tag}_{kind}.npy'
                if path.exists():continue
                out=np.lib.format.open_memmap(LOCAL/f'{tag}_{kind}.pending.npy',mode='w+',dtype='float32',shape=(len(texts),1024));truncated=0;tokens=0;start=time.perf_counter()
                for i in range(0,len(texts),8):
                    budget(time.perf_counter()-wall,time.process_time()-cpu,qa_reserve=True)
                    batch=tok(texts[i:i+8],padding=True,truncation=True,max_length=512,return_tensors='pt').to('cuda')
                    lens=batch['attention_mask'].sum(1);tokens+=int(lens.sum());truncated+=int((lens==512).sum())
                    with torch.inference_mode():x=torch.nn.functional.normalize(model(**batch).last_hidden_state[:,0],dim=1)
                    out[i:i+len(x)]=x.cpu().numpy()
                    if i%800==0:out.flush();print(tag,kind,i,len(texts),round(time.perf_counter()-start,1),flush=True)
                out.flush();del out;os.replace(LOCAL/f'{tag}_{kind}.pending.npy',path)
                log.append(dict(tag=tag,kind=kind,strings=len(texts),tokens=tokens,at_encoder_limit=truncated,seconds=time.perf_counter()-start))
        save(HERE/'ENCODING_COST.json',log)
    finally:
        torch.cuda.synchronize();charge('encode',cpu,wall,gpu_process_seconds=time.perf_counter()-wall,peak_gpu_bytes=torch.cuda.max_memory_allocated())
    # Vectorized exact first-stage retrieval; deterministic ties by corpus hash order.
    start=time.perf_counter();cpu=time.process_time();retrieved={}
    for tag in corpus:
        xx=np.load(LOCAL/f'{tag}_blocks.npy');qx=np.load(LOCAL/f'{tag}_queries.npy');qq=[q for q in queries if q['tag']==tag]
        for j,q in enumerate(qq):
            scores=xx@qx[j];ii=np.argsort(-scores,kind='stable')[:128]
            retrieved[q['query_id']]=ii.tolist()
    save(LOCAL/'retrieved.json',retrieved);print('retrieval_seconds',time.perf_counter()-start,flush=True)
    charge('first_stage_retrieval',cpu,start,gpu_process_seconds=0)

if __name__=='__main__':prepare() if sys.argv[1]=='prepare' else encode()
