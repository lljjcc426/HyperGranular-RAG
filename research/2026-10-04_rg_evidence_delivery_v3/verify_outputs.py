"""One final source/token/denominator check; no search, inference or scoring."""
from common import *
from delivery import Delivery,text_prompt
def run():
    from transformers import AutoTokenizer
    cpu=time.process_time();wall=time.perf_counter();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    def ids(p):return tok.encode(tok.apply_chat_template([{'role':'system','content':'You are a careful evidence assistant.'},{'role':'user','content':p}],tokenize=False,add_generation_prompt=True),add_special_tokens=False)
    records=0;checked_spans=0;methods={'Dense-window-v3','Flat-binding-v3','GB-uniform-v3','GB-feedback-v3','KM-feedback-v3'}
    for c in selected():
        ix=read(old_case(c)/'index.json');ws=[engine.Window(**w) for w in ix['windows']]
        unit_map={u['unit_id']:u for u in c['units']}
        for w in ws:
            for sid,text,a,b in w.sentences:
                if unit_map[sid]['text'][a:b]!=text:raise ValueError('SOURCE_COORDINATES')
        d=Delivery(c['query']['question'],ws,ids)
        for budget_point in (8,16):
            rs=read(LOCAL/'natural'/c['sampling_hash']/f'answers_{budget_point}.json')
            if {r['method'] for r in rs}!=methods or len(rs)!=5:raise ValueError('METHOD_DENOMINATOR')
            for r in rs:
                context=r['context'];ks=[tuple(k) for k in context['visible_spans']]
                p=text_prompt(c['query']['question'],[d.units[k] for k in ks])
                if p!=context['prompt'] or len(ids(p))!=context['input_tokens'] or len(ids(p))>1024:raise ValueError('ACTUAL_PROMPT_OR_TOKEN_LIMIT')
                if digest(ids(p))!=r['answer']['input_digest']:raise ValueError('READER_BINDING')
                trace=r['result']['trace'];seen={t['window'] for t in trace}
                if len({t['task'] for t in trace})!=len(trace) or len(trace)>budget_point:raise ValueError('TASK_BUDGET_OR_DUPLICATE')
                if any(f['window'] not in seen for f in r['result']['facts']):raise ValueError('UNOBSERVED_FACT')
                for w in context.get('package_windows',[]):
                    if not d.wkeys[w]<=set(ks):raise ValueError('PACKAGE_SOURCE_NOT_VISIBLE')
                checked_spans+=len(ks);records+=1
    rerun=list(csv.DictReader((HERE/'RERUN_CHECK.csv').open(encoding='utf-8')))
    if len(rerun)!=4 or any(r[k]!='True' for r in rerun for k in ('tasks_equal','model_inputs_outputs_equal','prompt_equal','reader_output_equal')):raise ValueError('RERUN_SUBSET_MISMATCH')
    save(HERE/'FINAL_VERIFICATION.json',dict(status='SOURCE_INPUT_AND_REPLAY_CHECKED',queries=16,records=records,checked_visible_spans=checked_spans,
        all_five_arms_at_8_and_16=True,source_coordinates_match_frozen_units=True,all_input_tokens_at_most_1024=True,
        reader_input_identity=True,only_requested_windows_observed=True,uncached_replays=4,
        scientific_limit='These checks do not certify relation truth, plan semantics, general determinism or independent confirmation.'))
    charge('final_source_token_check',cpu,wall);print('Verified',records,'records,',checked_spans,'visible spans, 4 uncached replays')
if __name__=='__main__':run()
