from common import *
from delivery import Delivery
import numpy as np

def construct():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    def ids(p):
        text=tok.apply_chat_template([{'role':'system','content':'You are a careful evidence assistant.'},{'role':'user','content':p}],tokenize=False,add_generation_prompt=True)
        return tok.encode(text,add_special_tokens=False)
    records=[];audit=[]
    for c in sorted(cases('D1'),key=lambda c:c['sampling_hash']):
        folder=old_case(c);ix=read(folder/'index.json');ws=[engine.Window(**w) for w in ix['windows']];old=read(folder/'main.json')
        with np.load(folder/'vectors.npz') as z:base={w.id:float(z['x'][i]@z['q']) for i,w in enumerate(ws)}
        d=Delivery(c['query']['question'],ws,ids,base)
        dense=next(r for r in old if r['method']=='Dense-window' and r['budget']==16)
        if d.prompt(d.dense)!=dense['context']['prompt']:raise ValueError('DENSE_RECONSTRUCTION_DIFFERS')
        def add(method,kind,context,old_answer=None):
            r=dict(query_id=c['query_id'],tag=c['tag'],stratum=c['stratum'],method=method,kind=kind,context=context)
            exact=next((z for z in old if z['context']['prompt']==context['prompt']),None)
            if exact:
                if digest(ids(context['prompt']))!=exact['answer']['input_digest']:raise ValueError('OLD_INPUT_IDENTITY')
                r['answer']=exact['answer'];r['answer_reuse']='V2_EXACT_FP16_GREEDY32'
            records.append(r)
        add('Dense-window','Dense',d.record(d.dense,'Dense'))
        for m in ('Flat-binding','GB-feedback','KM-feedback'):
            source=next(r for r in old if r['method']==m and r['budget']==16)
            observed={t['window'] for t in source['trace']}
            if any(f['window'] not in observed or f['score']!=1 for s in source['states'] for f in s['facts']):raise ValueError('UNOBSERVED_OR_UNACCEPTED_FACT')
            add(m,'Legacy-complete-only',source['context'])
            partial=d.partial(source['states'],source['slots']);control=d.count_dense(partial)
            add(m,'Partial-grounded',partial);add(m,'Count-conditioned-Dense',control)
            audit.append(dict(query_id=c['query_id'],dataset=c['tag'],method=m,changed=partial['prompt_changed'],
                new_sentences=len(partial['new_spans']),displaced_sentences=len(partial['displaced_spans']),
                package_relations=len(partial['package_relations']),missing_slots=len(partial['missing_slots']),
                count_match=control['status'],new_window_target=partial['new_window_target'],
                partial_tokens=partial['input_tokens'],control_tokens=control['input_tokens'],reasons=json.dumps(partial['reasons'],sort_keys=True)))
    save(LOCAL/'replay_inputs.json',records);table(HERE/'REPLAY_INPUT_AUDIT.csv',audit)
    save(HERE/'C_SAMPLE_IDS.json',[dict(query_id=c['query_id'],dataset=c['tag'],stratum=c['stratum'],selection_hash=sample_key(c),sampling_hash=c['sampling_hash']) for c in selected()])
    charge('A_construct',cpu,wall)
    print(json.dumps(dict(records=len(records),changed=sum(r['changed'] for r in audit),new_unique_prompts=len({r['context']['prompt'] for r in records if 'answer' not in r}))))

def readers():
    from runtime import LM
    rs=read(LOCAL/'replay_inputs.json');dest=LOCAL/'replay_answers.jsonl'
    cache={r['key']:r['answer'] for r in rows(dest)} if dest.exists() else {}
    todo={digest(r['context']['prompt']):r['context']['prompt'] for r in rs if 'answer' not in r}
    lm=LM()
    try:
        for key,p in todo.items():
            if key in cache:continue
            a=lm.generate(p,'You are a careful evidence assistant.',32,'A_reader')
            append(dest,dict(key=key,answer=a));print('A_reader',len(cache)+1,len(todo),flush=True);cache[key]=a
    finally:lm.close('A_reader')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['construct','read']);a=ap.parse_args()
    construct() if a.action=='construct' else readers()
