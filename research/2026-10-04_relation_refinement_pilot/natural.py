"""Fixed D1 driver. Explicit D0 decision file is required; no automatic tuning."""
from io_utils import *
from core import *
from models import LM,Encoder,PARSE,EXTRACT,json_object
from windows import make_windows
from dataclasses import asdict

def index():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter()
    gate=read(HERE/'CALIBRATION_DECISION.json');assert gate['run_d1'] is True
    model_path=DOWNLOAD_MODEL if os.environ.get('RG_MODEL')=='3b' else MODEL
    tok=AutoTokenizer.from_pretrained(model_path,local_files_only=True);enc=Encoder('cuda')
    try:
        for c in read(LOCAL/'inputs.json'):
            if c['role']!='D1':continue
            query_start=time.perf_counter()
            ws=make_windows(c['units'],tok);x=enc.encode([w.text for w in ws]);q=enc.encode([c['query']['question']],True)[0]
            scores=x@q;order=sorted(range(len(ws)),key=lambda i:(-float(scores[i]),ws[i].id))[:64]
            name=c['sampling_hash']
            save(LOCAL/(name+'_windows.json'),[asdict(ws[i]) for i in order])
            np.savez(LOCAL/(name+'_vectors.npz'),x=x[order],q=q)
            append(LOCAL/'index_summary.jsonl',dict(query_id=c['query_id'],all_windows=len(ws),retained=len(order),truncated=sum(w.truncated for w in ws),
                window_and_index_seconds=time.perf_counter()-query_start))
    finally:charge('D1_index',cpu,wall,gpu_process_seconds=time.perf_counter()-wall)

def execute(rerun=False):
    gate=read(HERE/'CALIBRATION_DECISION.json');assert gate['run_d1'] is True
    threshold=gate['threshold'];lm=LM();cases=sorted((c for c in read(LOCAL/'inputs.json') if c['role']=='D1'),key=lambda c:c['sampling_hash'])
    if rerun:cases=cases[:4]
    filename='d1_rerun.jsonl' if rerun else 'd1_main.jsonl'
    assert not (LOCAL/filename).exists(),'append-only run must not be repeated'
    try:
        for case in cases:
            question=case['query']['question'];name=case['sampling_hash']
            ws=[Window(**w) for w in read(LOCAL/(name+'_windows.json'))]
            with np.load(LOCAL/(name+'_vectors.npz')) as z:x=z['x'];q=z['q']
            catalog=tuple({(w.title,w.source) for w in ws});embed_cache={};probe_cost={};answer_cache={}
            parse_record=None;slots=[]
            if not rerun:
                context=render(question,ws,[],1,lm.ids)
                answer=lm.generate(context['prompt'],'You are a careful evidence assistant.',32,'D1_dense')
                answer_cache[context['prompt']]=answer
                for budget in (16,32):append(LOCAL/filename,dict(query_id=case['query_id'],method='Dense-window',budget=budget,
                    tag=case['tag'],stratum=case['stratum'],context=context,answer=answer,parse_status='NOT_USED',logical_probes=0,
                    logical_binary_pairs=0,conditional_queries=0,logical_parse_calls=0,splits=0,reader_cache_hit=budget==32))
            for method in METHODS[1:]:
                if parse_record is None or rerun:
                    parse_record=lm.generate(question,PARSE,224,'D1_parse_rerun' if rerun else 'D1_parse')
                    slots=parse_contract(question,json_object(parse_record['text']))
                def embed(text):
                    if text not in embed_cache or rerun:
                        # On-demand CPU encoder: no second GPU-resident model; loading is charged.
                        t=time.perf_counter();enc=Encoder('cpu');v=enc.encode([text],True)[0];del enc
                        embed_cache[text]=(v,time.perf_counter()-t)
                    return embed_cache[text][0]
                def callback(w):
                    r=lm.generate(json.dumps(dict(question=question,slots=slots,body=w.text)),EXTRACT,320,'D1_extract_rerun' if rerun else 'D1_extract')
                    fs=[];pairs=[]
                    for raw in json_object(r['text']).get('facts',[])[:3]:
                        f=witnessed(raw,w,slots,catalog,.5)
                        if f is None:continue
                        s=next(s for s in slots if s['id']==f.slot)
                        b=lm.binary(w.text,f.head+' -- '+s['relation']+' --> '+f.tail+'; conditions: '+f.conditions,'D1_verify')
                        pairs.append(b);fs.append(witnessed(raw,w,slots,catalog,b['score']))
                    probe_cost[w.id]=dict(generation=r,binary=pairs)
                    return fs
                if method==METHODS[1] or rerun:probe=LazyProbe(callback)
                if slots:
                    result=search(method,question,slots,ws,x,q,embed,probe,threshold,rerun,16 if rerun else 32)
                else:result=dict(snapshots={},trace=[],splits=[],seconds=0)
                for budget in ((16,) if rerun else (16,32)):
                    available=[b for b in result['snapshots'] if b<=budget]
                    snap=result['snapshots'][max(available)] if available else dict(states=[],probe_count=0,complete=False,leaf_count=0)
                    states=snap['states'];context=render(question,ws,states,len(slots) or 1,lm.ids)
                    hit=context['prompt'] in answer_cache and not rerun
                    if hit:answer=answer_cache[context['prompt']]
                    else:
                        answer=lm.generate(context['prompt'],'You are a careful evidence assistant.',32,'D1_reader_rerun' if rerun else 'D1_reader')
                        if not rerun:answer_cache[context['prompt']]=answer
                    trace=result['trace'][:budget];cost=[probe_cost[a['window']] for a in trace]
                    record=dict(query_id=case['query_id'],tag=case['tag'],stratum=case['stratum'],method=method,budget=budget,
                        parse_status='OK' if slots else 'PARSE_FAIL',parse=parse_record,slots=slots,context=context,answer=answer,
                        logical_probes=len(trace),logical_binary_pairs=sum(len(z['binary']) for z in cost),logical_parse_calls=1,
                        logical_probe_seconds=sum(z['generation']['seconds']+sum(b['seconds'] for b in z['binary']) for z in cost),
                        reader_cache_hit=hit,probe_cache_hits=sum(a['cache_hit'] for a in trace),trace=trace,
                        splits=[s for s in result['splits'] if s['step']<=budget],complete=snap['complete'],
                        states=[dict(binding=b,facts=[asdict(f) for f in fs]) for b,fs in states],
                        conditional_queries=snap.get('conditional_strings',0),leaf_count=snap['leaf_count'],
                        logical_conditional_seconds=sum(embed_cache[t][1] for t in snap.get('conditional_texts',[])),
                        renderer_fit={str(b):render(question,ws,states,len(slots) or 1,lm.ids,b)['complete_bundle_visible'] for b in (512,2048)})
                    append(LOCAL/filename,record)
            print('D1',case['query_id'],'rerun',rerun,flush=True)
    finally:lm.close('D1_rerun' if rerun else 'D1_main')
if __name__=='__main__':
    if sys.argv[1]=='index':index()
    else:execute(sys.argv[1]=='rerun')
