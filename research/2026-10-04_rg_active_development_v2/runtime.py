from common import *
import numpy as np

class LM:
    def __init__(self):
        import torch,transformers
        from transformers import AutoTokenizer,AutoModelForCausalLM
        # LMFE 0.11.3 imports this type from its pre-v5 location. Process-local
        # compatibility alias only: no package files or existing environment upgrade.
        import transformers.tokenization_utils as tu
        from transformers.tokenization_utils_base import PreTrainedTokenizerBase
        tu.PreTrainedTokenizerBase=PreTrainedTokenizerBase
        from lmformatenforcer.integrations.transformers import build_token_enforcer_tokenizer_data
        self.cpu=time.process_time();self.wall=time.perf_counter();self.torch=torch
        torch.set_num_threads(1);torch.manual_seed(1729);torch.use_deterministic_algorithms(True)
        self.tokenizer=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
        self.model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,dtype=torch.float16).eval().to('cuda')
        torch.cuda.reset_peak_memory_stats();self.token_data=build_token_enforcer_tokenizer_data(self.tokenizer)
        self.yes=self.tokenizer.encode('yes',add_special_tokens=False)[0];self.no=self.tokenizer.encode('no',add_special_tokens=False)[0]
    def ids(self,user,system='You are a careful evidence assistant.'):
        text=self.tokenizer.apply_chat_template([{'role':'system','content':system},{'role':'user','content':user}],tokenize=False,add_generation_prompt=True)
        return self.tokenizer.encode(text,add_special_tokens=False)
    def check(self):budget(time.perf_counter()-self.wall,time.process_time()-self.cpu)
    def generate(self,user,system,max_tokens,stage,schema=None):
        self.check();torch=self.torch;ids=self.ids(user,system);x=torch.tensor([ids],device='cuda');start=time.perf_counter();kwargs={};mask_calls=0
        if schema:
            from lmformatenforcer import JsonSchemaParser
            from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
            fn=build_transformers_prefix_allowed_tokens_fn(self.token_data,JsonSchemaParser(schema))
            def allowed(batch,sent):
                nonlocal mask_calls
                mask_calls+=1
                return fn(batch,sent[len(ids):])
            kwargs['prefix_allowed_tokens_fn']=allowed
        with torch.inference_mode():
            out=self.model.generate(input_ids=x,attention_mask=torch.ones_like(x),do_sample=False,num_beams=1,max_new_tokens=max_tokens,
                eos_token_id=self.tokenizer.eos_token_id,pad_token_id=self.tokenizer.eos_token_id,use_cache=True,**kwargs)
        torch.cuda.synchronize();tokens=out[0,len(ids):].tolist();text=self.tokenizer.decode(tokens,skip_special_tokens=True).strip()
        raw=None;error=None
        if schema:
            try:raw=json.loads(text)
            except ValueError:error='JSON_OR_LENGTH_FAILURE'
        r=dict(text=text,raw=raw,json_error=error,input_tokens=len(ids),output_tokens=len(tokens),output_ids=tokens,
            ended_eos=bool(tokens and tokens[-1]==self.tokenizer.eos_token_id),mask_calls=mask_calls,seconds=time.perf_counter()-start,
            input_digest=digest(ids),schema_digest=digest(schema),stage=stage)
        append(LOCAL/'calls.jsonl',dict(kind='generate',**r));return r
    def verify(self,payload,stage):
        from schemas import VERIFY_PROMPT
        self.check();torch=self.torch;ids=self.ids(json.dumps(payload,ensure_ascii=False,sort_keys=True),VERIFY_PROMPT)
        x=torch.tensor([ids],device='cuda');start=time.perf_counter()
        with torch.inference_mode():logits=self.model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).logits[0,-1,[self.no,self.yes]].float()
        score=float(logits.softmax(0)[1]);torch.cuda.synchronize()
        if not np.isfinite(score):raise RuntimeError('NONFINITE_VERIFY')
        r=dict(score=score,input_tokens=len(ids),seconds=time.perf_counter()-start,input_digest=digest(ids))
        append(LOCAL/'calls.jsonl',dict(kind='binary',stage=stage,**r));return r
    def close(self,stage):
        peak=self.torch.cuda.max_memory_allocated();del self.model;self.torch.cuda.empty_cache()
        charge(stage,self.cpu,self.wall,gpu_process_seconds=time.perf_counter()-self.wall,peak_gpu_bytes=peak)

class Encoder:
    def __init__(self,device='cpu'):
        import torch
        from transformers import AutoTokenizer,AutoModel
        self.torch=torch;torch.set_num_threads(1);self.device=device
        self.tokenizer=AutoTokenizer.from_pretrained(BGE,local_files_only=True)
        self.model=AutoModel.from_pretrained(BGE,local_files_only=True).eval().to(device)
    def encode(self,texts,query=False):
        if query:texts=['Represent this sentence for searching relevant passages: '+t for t in texts]
        out=[];start=time.perf_counter();tokens=0
        for i in range(0,len(texts),8):
            b=self.tokenizer(texts[i:i+8],padding=True,truncation=True,max_length=512,return_tensors='pt').to(self.device)
            tokens+=int(b['attention_mask'].sum())
            with self.torch.inference_mode():x=self.model(**b).last_hidden_state[:,0]
            out.append(self.torch.nn.functional.normalize(x,p=2,dim=1).cpu().numpy())
        append(LOCAL/'encoding.jsonl',dict(strings=len(texts),query=query,seconds=time.perf_counter()-start,input_tokens=tokens,device=self.device))
        return np.concatenate(out)

