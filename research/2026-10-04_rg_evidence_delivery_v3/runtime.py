from common import *
_runtime=load_module('rg_v3_runtime_dependency',V2/'runtime.py')
Encoder=_runtime.Encoder
class LM(_runtime.LM):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        calls=rows(LOCAL/'calls.jsonl') if (LOCAL/'calls.jsonl').exists() else []
        self.reader_count=sum('reader' in r['stage'] for r in calls)
        self.front_count=len(calls)-self.reader_count
    def generate(self,user,system,max_tokens,stage,schema=None):
        reader='reader' in stage
        if (self.reader_count>=768 if reader else self.front_count>=2500):raise RuntimeError('MODEL_CALL_BUDGET_REACHED')
        r=super().generate(user,system,max_tokens,stage,schema)
        self.reader_count+=int(reader);self.front_count+=int(not reader)
        return r
