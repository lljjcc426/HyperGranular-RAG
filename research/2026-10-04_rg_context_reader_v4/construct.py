"""Build all contexts on CPU before any v4 reader result exists."""
from common import *
from protocols import *
from contexts import Builder
from reference import support_maps,reference
import numpy as np
CORE=('D','A_G','L_G','R');EXTRA=('A_F','L_F','A_K','L_K')
def construct():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    gg=support_maps();records=[];audit=[]
    for c in selected():
        ix=read(old_case(c)/'index.json');ws=[engine.Window(**w) for w in ix['windows']]
        with np.load(old_case(c)/'vectors.npz') as z:base={w.id:float(z['x'][i]@z['q']) for i,w in enumerate(ws)}
        b=Builder(c['query']['question'],ws,tok,base)
        old=read(V3/'local/natural'/c['sampling_hash']/'answers_16.json')
        dense=next(r for r in old if r['method']=='Dense-window-v3')
        if b.d.dense_prompt!=dense['context']['prompt']:raise ValueError('OLD_DENSE_NOT_RECONSTRUCTED')
        out={'D':b.dense_record()}
        for letter,name in [('G','GB-feedback-v3'),('F','Flat-binding-v3'),('K','KM-feedback-v3')]:
            src=next(r for r in old if r['method']==name)
            out['A_'+letter]=b.automatic(src);out['L_'+letter]=b.length_control(out['A_'+letter])
        # R receives labels only after ALL automatic contexts have been built.
        out['R']=reference(c,b,gg[c['tag']].get(c['query_id'],[]))
        for context in CORE+EXTRA:
            v=out[context];spans=[tuple(k) for k in v['visible_spans']]
            record=dict(query_id=c['query_id'],tag=c['tag'],sampling_hash=c['sampling_hash'],context=context,
                question=c['query']['question'],data_role='EXPOSED_DEVELOPMENT',**v,
                source_items=[dict(id=k[0],start=k[1],end=k[2],title=b.d.units[k][0],text=b.d.units[k][1]) for k in spans])
            for p in PROTOCOLS:
                user=prompt(record['question'],record['body'],p)
                if len(ids(tok,user))!=v['input_tokens'][p] or v['input_tokens'][p]>1024:raise ValueError('INPUT_CAP')
            records.append(record)
            audit.append(dict(query_id=c['query_id'],dataset=c['tag'],context=context,status=v['status'],fallback=v['fallback'],
                shared_cap_adjustment=v['shared_cap_adjustment'],source_change=v['source_change'],order_only=v['order_only'],
                retained=v['retained'],removed=v['removed'],added=v['added'],body_tokens=v['body_tokens'],
                p0_input=v['input_tokens']['P0'],p1_input=v['input_tokens']['P1'],p2_input=v['input_tokens']['P2'],
                protocol_body_identical=True,package_relations=len(v.get('package_relations',[])),
                budget_tokens=v.get('budget_tokens',''),budget_gap=v.get('budget_gap',''),
                budget_relative_gap=v['budget_gap']/v['budget_tokens'] if v.get('budget_tokens',0) else '',
                reference_complete=v.get('reference_complete',''),reference_outside_top64=v.get('reference_outside_top64',''),
                full_reference_body_tokens=v.get('full_reference_body_tokens',''),missing_reference_count=len(v.get('missing_reference_ids',[])),
                source_span_count=len(v['visible_spans']),source_identity=digest(v['visible_spans'])))
    save(LOCAL/'contexts.json',records);table(HERE/'CONTEXT_AUDIT.csv',audit)
    # Fixed D0 sources: existing diagnostic windows in stored order, no new retrieval.
    packets={p['query_id']:p for p in read(V1/'local/d0_packets.json')};dev=[]
    for c in d0_selected():
        packet=packets[c['query_id']];ws=[engine.Window(**w) for w in packet['windows']]
        b=Builder(c['query']['question'],ws,tok,{w.id:-i for i,w in enumerate(ws)})
        dev.append(dict(query_id=c['query_id'],tag=c['tag'],question=c['query']['question'],sampling_hash=c['sampling_hash'],**b.dense_record()))
    save(LOCAL/'d0_contexts.json',dev)
    save(HERE/'SAMPLE_IDS.json',dict(main=[dict(query_id=c['query_id'],dataset=c['tag'],sampling_hash=c['sampling_hash']) for c in selected()],
        d0=[dict(query_id=c['query_id'],dataset=c['tag'],sampling_hash=c['sampling_hash']) for c in d0_selected()]))
    charge('construct',cpu,wall)
    print('contexts',len(records),'A packages',sum(r['status']=='AUTOMATIC_PACKAGE' for r in records),'shared D cap',sum(r['context']=='D' and r['shared_cap_adjustment'] for r in records),'R complete',sum(r.get('reference_complete',False) for r in records))
if __name__=='__main__':construct()
