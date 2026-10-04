"""Bounded post-fix check of emitted span order; no model calls or rescoring."""
from common import *
from delivery import Delivery
import numpy as np
def run():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    def ids(p):return tok.encode(tok.apply_chat_template([{'role':'system','content':'You are a careful evidence assistant.'},{'role':'user','content':p}],tokenize=False,add_generation_prompt=True),add_special_tokens=False)
    records=read(LOCAL/'replay_inputs.json');byid={c['query_id']:c for c in cases('D1')};done=[];mismatches=0
    for qid in byid:
        c=byid[qid];ix=read(old_case(c)/'index.json');ws=[engine.Window(**w) for w in ix['windows']]
        d=Delivery(c['query']['question'],ws,ids);old=read(old_case(c)/'main.json')
        for r in [r for r in records if r['query_id']==qid]:
            if r['kind']=='Legacy-complete-only':done.append(r);continue
            if r['kind']=='Dense':current=d.record(d.dense,'Dense')
            else:
                source=next(z for z in old if z['method']==r['method'] and z['budget']==16)
                p=d.partial(source['states'],source['slots']);current=p if r['kind']=='Partial-grounded' else d.count_dense(p)
            if current['prompt']!=r['context']['prompt']:raise ValueError('REPLAY_PROMPT_CHANGED')
            if current['input_tokens']!=r['context']['input_tokens']:raise ValueError('TOKEN_COUNT_CHANGED')
            mismatches+=current['visible_spans']!=r['context']['visible_spans']
            done.append(dict(r,context=current))
    save(LOCAL/'replay_inputs_layout_corrected.json',done)
    save(HERE/'A_REPLAY_VERIFICATION.json',dict(queries=64,records=len(records),all_prompts_unchanged=True,all_token_counts_unchanged=True,
        source_order_metadata_corrected_records=mismatches,original_local_input_preserved=True,new_model_calls=0,
        detail='A source IDs initially used first possible window rank, while exact prompts used accepted Dense-window order. Corrected metadata follows the actual emitted prompt; no answer, text membership, metric or prompt changed.'))
    charge('A_source_order_metadata_check',cpu,wall);print('A unchanged prompts; metadata corrections',mismatches)
if __name__=='__main__':run()
