"""Four exposed D0 source checks of new extraction -> verification -> delivery.

Uses v2 model-produced plans, and the existing annotation-selected diagnostic
window. This is a controlled source diagnostic, never a natural method score.
"""
from common import *
from runtime import LM
from frontend import scope,extract_task
from delivery import Delivery

def run():
    packets=read(V1/'local/d0_packets.json');old=rows(V2/'local/v27_C.jsonl');dest=LOCAL/'d0_through_v35.jsonl'
    done={r['index'] for r in rows(dest)} if dest.exists() else set();lm=LM(quantized=True,adapter=V2/'adapters/v27')
    try:
        for i in (1,4,16,26):
            if i in done:continue
            p=packets[i];r=next(r for r in old if r['index']==i);slots=r['slots'];constraints,g=scope(lm,p['question'],slots,'B_D0_scope')
            chosen=next(w for w in r['windows'] if w['condition']=='ANNOTATED_SUPPORT')['window']
            # Stored windows may be an ID or the original dataclass mapping.
            wid=chosen['id'] if isinstance(chosen,dict) else chosen
            ws=[engine.Window(**w) for w in p['windows']];w=next(w for w in ws if w.id==wid)
            catalog=sorted({(z.title,z.source) for z in ws});results=[]
            for s in slots:
                if not any(not s[k].startswith('?') for k in ('head','tail')):continue
                results.append(extract_task(lm,p['question'],slots,constraints,s,{},w,catalog,'B_D0_task'))
            fs=[f for z in results for f in z['facts']]
            d=Delivery(p['question'],ws,lm.ids);context=d.partial([dict(binding={},facts=fs)],slots,constraints)
            append(dest,dict(index=i,dataset=p['tag'],question=p['question'],slots=slots,constraints=constraints,scope_generation=g,
                results=results,context=context,diagnostic='annotation_window_model_plan_not_natural_score'))
            print('D0',i,len(fs),len(context['new_spans']),flush=True)
    finally:lm.close('B_D0_through')
if __name__=='__main__':run()
