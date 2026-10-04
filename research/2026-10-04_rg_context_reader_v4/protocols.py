"""Shared source body, explicit protocol parsing, complete generation identity."""
from common import *
SYSTEM='You are a careful evidence assistant.'
LEGACY='Answer the question using only the evidence. Return a short answer, or UNKNOWN if insufficient.'
ANSWER_INSTRUCTION='''Use only the supplied evidence to answer the question.
Return exactly one JSON object with one field, "answer".
The value must be the shortest complete answer to the question: a name,
a place, a date, a number, yes/no, or another short answer as appropriate.
Preserve any qualifiers needed to make the answer correct.
Do not include an explanation, citations, or a restatement of the question.
If the evidence is insufficient, use "UNKNOWN" as the value.'''
SCHEMA={'type':'object','properties':{'answer':{'type':'string'}},'required':['answer'],'additionalProperties':False}
PROTOCOLS=('P0','P1','P2')
def prompt(question,body,protocol):return (ANSWER_INSTRUCTION if protocol=='P2' else LEGACY)+'\nQuestion: '+question+'\nEvidence:\n'+body
def body(items):return '\n'.join(f'[{j+1}] Title: {title}\n{text}' for j,(title,text) in enumerate(items))
def ids(tok,user):
    t=tok.apply_chat_template([{'role':'system','content':SYSTEM},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
    return tok.encode(t,add_special_tokens=False)
def identity(tok,user,protocol):
    import importlib.metadata as md
    return dict(model_revision='aa8e72537993ba99e69dfaafa59ed015b17504d1',precision='float16',adapter=False,
        tokenizer_revision='aa8e72537993ba99e69dfaafa59ed015b17504d1',chat_template=tok.chat_template,
        input_ids=ids(tok,user),generation=dict(do_sample=False,num_beams=1,max_new_tokens=32 if protocol=='P0' else 128,
        eos_token_id=tok.eos_token_id,pad_token_id=tok.eos_token_id,use_cache=True),schema=SCHEMA if protocol=='P2' else None,
        constraint_version=md.version('lm-format-enforcer') if protocol=='P2' else None,
        transformers=md.version('transformers'),torch=md.version('torch'),
        inference_kernel=hashlib.sha256((V2/'runtime.py').read_bytes()).hexdigest(),schema_input_mode='generated_suffix_only')
def parse(text,protocol):
    if protocol!='P2':return text,'RAW_TEXT'
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('DUPLICATE_FIELD')
            d[k]=v
        return d
    try:
        obj=json.loads(text,object_pairs_hook=unique)
        if type(obj)!=dict or set(obj)!= {'answer'} or type(obj['answer'])!=str:raise ValueError('SCHEMA')
        return obj['answer'],'VALID_ANSWER_FIELD'
    except (ValueError,TypeError):return '','PROTOCOL_FAILURE'
