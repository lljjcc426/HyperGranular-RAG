from io_utils import *
import numpy as np

PARSE='''Decompose ONLY the given question into 1-4 directed relation slots. Do not answer it. Constants must be exact substrings of the question. Unknown entities must be variables beginning ?. Reuse a variable only for the same entity. Include all conditions in relation phrases. Output only JSON: {"slots":[{"id":"r1","head":"question literal or ?v","relation":"relation phrase","tail":"?answer"}],"answer_var":"?answer","ambiguous":false}. No reasoning text.'''
PARSE='''Convert the question into a small JSON object. Do not answer the question. Output a FLAT list of 1 to 4 relation objects, not a list inside a list. An unknown person/place/date is a variable like ?person, ?place or ?answer. Do not invent names or dates. Every constant must be copied exactly from the question. Reuse variables only for the same entity. Preserve qualifiers in relation text.
Example question: Where was the writer of Night River born?
Example output: {"slots":[{"id":"r1","head":"Night River","relation":"written by","tail":"?person"},{"id":"r2","head":"?person","relation":"born in","tail":"?answer"}],"answer_var":"?answer","ambiguous":false}
Now output only the JSON for the user's question. No explanation.'''
EXTRACT='''Read only this window, not outside knowledge or the title. Return up to 3 facts matching the directed question slots. Both head and tail must be exact body substrings. quote must be an exact body substring supporting this direction and all relevant conditions. A question slot does not make a fact true. Do not guess unresolved names or dates. If unsupported return no fact. Output JSON only: {"facts":[{"slot_id":"r1","head":"exact span","tail":"exact span","quote":"exact quote","polarity":"positive","conditions":"qualifiers or empty","explicit":true}]}. No reasoning text.'''
EXTRACT+=''' Example BODY: Ada wrote Green Sky. For a slot asking who wrote Green Sky, a valid fact is {"slot_id":"r1","head":"Green Sky","tail":"Ada","quote":"Ada wrote Green Sky.","polarity":"positive","conditions":"","explicit":true}. Output actual names/spans, never ?variables or relation text in head/tail. Use {"facts":[]} when the body does not resolve the slot.'''
VERIFY='''Does the BODY explicitly support the whole directed CLAIM, including its entity binding, direction, negation and qualifiers? Use only BODY. Missing information or a different entity means no. Answer exactly yes or no.'''

def json_object(text):
    try:return json.loads(text[text.index('{'):text.rindex('}')+1])
    except (ValueError,TypeError):return {}

class LM:
    def __init__(self):
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM
        self.torch=torch;self.cpu=time.process_time();self.wall=time.perf_counter()
        torch.set_num_threads(1);torch.manual_seed(1729);torch.use_deterministic_algorithms(True)
        model_path=DOWNLOAD_MODEL if os.environ.get('RG_MODEL')=='3b' else MODEL
        self.tokenizer=AutoTokenizer.from_pretrained(model_path,local_files_only=True)
        self.model=AutoModelForCausalLM.from_pretrained(model_path,local_files_only=True,dtype=torch.float16).eval().to('cuda')
        self.model_tag='3b' if os.environ.get('RG_MODEL')=='3b' else '1.5b'
        torch.cuda.reset_peak_memory_stats();self.calls=0;self.pairs=0
        logs=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else []
        self.prior_calls=sum(z['kind']=='generate' for z in logs);self.prior_pairs=sum(z['kind']=='binary' for z in logs)
        self.prior_cost=rows(HERE/'COST_LEDGER.jsonl') if (HERE/'COST_LEDGER.jsonl').exists() else []
        self.yes=self.tokenizer.encode('yes',add_special_tokens=False);self.no=self.tokenizer.encode('no',add_special_tokens=False)
        assert len(self.yes)==len(self.no)==1
    def ids(self,user,system='You are a careful evidence assistant.'):
        text=self.tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
        return self.tokenizer.encode(text,add_special_tokens=False)
    def check(self):
        if self.prior_calls+self.calls>=6500 or self.prior_pairs+self.pairs>=16000:
            raise RuntimeError('CALL_CAP_AT_REQUEST_BOUNDARY')
        completed=self.prior_cost
        gpu=sum(z.get('gpu_process_seconds',0) for z in completed)+time.perf_counter()-self.wall
        cpu=sum(z['cpu_seconds'] for z in completed)+time.process_time()-self.cpu
        if gpu>=21600 or cpu>=14400:raise RuntimeError('RESOURCE_CAP_AT_REQUEST_BOUNDARY')
    def generate(self,user,system,max_tokens,stage):
        self.check();torch=self.torch;ids=self.ids(user,system);x=torch.tensor([ids],device='cuda');start=time.perf_counter()
        with torch.inference_mode():
            output=self.model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,num_beams=1,
                max_new_tokens=max_tokens,pad_token_id=self.tokenizer.eos_token_id,use_cache=True)
        torch.cuda.synchronize();tokens=output[0,len(ids):].tolist();seconds=time.perf_counter()-start;self.calls+=1
        result=dict(text=self.tokenizer.decode(tokens,skip_special_tokens=True).strip(),input_tokens=len(ids),output_tokens=len(tokens),seconds=seconds,
                    input_digest=digest(ids),output_ids=tokens)
        append(LOCAL/'calls.jsonl',dict(kind='generate',model=self.model_tag,stage=stage,**result));return result
    def binary(self,body,claim,stage):
        self.check();torch=self.torch;ids=self.ids('BODY:\n'+body+'\nCLAIM:\n'+claim,VERIFY);x=torch.tensor([ids],device='cuda');start=time.perf_counter()
        with torch.inference_mode(): logits=self.model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits[0,-1,[self.no[0],self.yes[0]]].float()
        score=float(logits.softmax(0)[1]);torch.cuda.synchronize();seconds=time.perf_counter()-start;self.pairs+=1
        result=dict(score=score,seconds=seconds,input_tokens=len(ids),input_digest=digest(ids))
        append(LOCAL/'calls.jsonl',dict(kind='binary',model=self.model_tag,stage=stage,**result))
        if not np.isfinite(score):raise RuntimeError('NONFINITE_BINARY_LOGITS_RUNTIME_FAILURE')
        return result
    def close(self,stage):
        peak=self.torch.cuda.max_memory_allocated();del self.model;self.torch.cuda.empty_cache()
        charge(stage,self.cpu,self.wall,gpu_process_seconds=time.perf_counter()-self.wall,
               generate_calls=self.calls,binary_pairs=self.pairs,peak_allocated_bytes=peak)

class Encoder:
    def __init__(self,device='cpu'):
        import torch
        from transformers import AutoModel,AutoTokenizer
        self.torch=torch;torch.set_num_threads(1);self.device=device
        self.path=DATA/'models/huggingface/hub/models--BAAI--bge-large-en-v1.5/snapshots/d4aa6901d3a41ba39fb536a557fa166f842b0e09'
        self.tokenizer=AutoTokenizer.from_pretrained(self.path,local_files_only=True)
        self.model=AutoModel.from_pretrained(self.path,local_files_only=True).eval().to(device)
    def encode(self,texts,query=False):
        if query:texts=['Represent this sentence for searching relevant passages: '+t for t in texts]
        out=[];start=time.perf_counter();tokens=0
        for i in range(0,len(texts),8):
            batch=self.tokenizer(texts[i:i+8],padding=True,truncation=True,max_length=512,return_tensors='pt').to(self.device)
            tokens+=int(batch['attention_mask'].sum())
            with self.torch.inference_mode():x=self.model(**batch).last_hidden_state[:,0]
            out.append(self.torch.nn.functional.normalize(x,p=2,dim=1).cpu().numpy())
        append(LOCAL/'embedding_cost.jsonl',dict(query=query,strings=len(texts),tokens=tokens,seconds=time.perf_counter()-start,device=self.device))
        return np.concatenate(out)

def measure():
    lm=LM();timings=[]
    try:
        for j in ((0,2,5,7) if lm.model_tag=='3b' else range(8)):
            body=f'Alba{j} wrote Book{j}. Book{j} was published in City{j}. City{j} is in Country{j}.'
            body+=' This archive also describes unrelated editions and their printing schedules.'*(j*3)
            slots=[dict(id='r1',head=f'Alba{j}',relation='wrote',tail='?book'),dict(id='r2',head='?book',relation='published in',tail='?city')]
            r=lm.generate(json.dumps(dict(question=f'Where was the book by Alba{j} published?',slots=slots,body=body)),EXTRACT,320,'synthetic_extract')
            if lm.model_tag=='3b' and j==0:
                repeat=lm.generate(json.dumps(dict(question=f'Where was the book by Alba{j} published?',slots=slots,body=body)),EXTRACT,320,'synthetic_uncached_repeat')
                assert r['input_digest']==repeat['input_digest'] and r['output_ids']==repeat['output_ids'],'synthetic model nondeterminism'
            v=lm.binary(body,f'Alba{j} wrote Book{j}.','synthetic_binary')
            timings.append(dict(kind='extract',**{k:r[k] for k in ('seconds','input_tokens','output_tokens')},binary_seconds=v['seconds']))
        for j in range(2 if lm.model_tag=='3b' else 4):
            r=lm.generate(f'Who founded the company that published Book{j}?',PARSE,224,'synthetic_parse');timings.append(dict(kind='parse',seconds=r['seconds'],output_tokens=r['output_tokens']))
            r=lm.generate(f'Question: Where is City{j}? Evidence: City{j} is in Country{j}. Return a short answer.', 'Use only evidence.',32,'synthetic_reader');timings.append(dict(kind='reader',seconds=r['seconds'],output_tokens=r['output_tokens']))
        # Upper request envelope, typical-call timing; not a runtime guarantee.
        ext=max(t['seconds'] for t in timings if t['kind']=='extract')
        par=max(t['seconds'] for t in timings if t['kind']=='parse')
        ans=max(t['seconds'] for t in timings if t['kind']=='reader')
        binary=max(t.get('binary_seconds',0) for t in timings)
        projection=4544*ext+96*par+1056*ans+13800*binary
        filename='3b_RESOURCE_CALIBRATION.json' if lm.model_tag=='3b' else 'RESOURCE_CALIBRATION_v2.json'
        save(HERE/filename,dict(model=lm.model_tag,timings=timings,projection_seconds=projection,
            projection_type='maximum observed synthetic cost times conservative request envelope, excluding indexing/loading; not guarantee',
            full_plan_within_six_hours_before_overhead=projection<21600,peak_gpu_bytes=lm.torch.cuda.max_memory_allocated()))
        print('RESOURCE_PROJECTION',projection,flush=True)
    finally:lm.close('synthetic_model_calibration')
if __name__=='__main__':measure()
