"""Tail-blind object recovery check; no Gold or proposed tail in its input."""
from common import *
from runtime import LM
from schemas import obj,STR
from frontend import normalized

PROMPT='''Using only the original evidence, locate the object of the requested directed relation for the supplied subject. Return one object {status, sid, text}. status is supported only when the relation and ALL required conditions are supported. text must be an exact short substring of a supplied sentence; sid is its sentence ID. For missing information return status unresolved, sid "", text "". Do not return the subject or a related organization merely because it occurs. Do not use outside knowledge. Example: Subject Ada; relation has father; evidence s0 "Ada's father is Marco." => {"status":"supported","sid":"s0","text":"Marco"}. Example: Subject Ada; relation born on; evidence s0 "Ada teaches in Paris." => {"status":"unresolved","sid":"","text":""}.'''
SCHEMA=obj(dict(status=dict(type='string',enum=['supported','unresolved']),sid=dict(type='string'),text=dict(type='string')))

def check(lm,payload,stage):
    c=payload['CLAIM'];e=payload['EVIDENCE']
    user=json.dumps(dict(subject=c['subject'],relation=c['relation'],required_conditions=c['qualifiers'],evidence=e),ensure_ascii=False)
    g=lm.generate(user,PROMPT,96,stage,SCHEMA);r=g['raw'];matched=False
    if isinstance(r,dict) and r['status']=='supported' and r['text']:
        s=next((s for s in e['sentences'] if s['sid']==r['sid']),None)
        matched=bool(s and r['text'] in s['text'] and normalized(r['text'])==normalized(payload['LOCATIONS']['tail']['text']))
    return dict(matched=matched,generation=g)

if __name__=='__main__':
    from verification import serialize
    from schemas import VERIFY_PROMPT
    lm=LM(quantized=True)
    try:
        for r in rows(LOCAL/'v23_B.jsonl'):
            for w in r['windows']:
                for j,f in enumerate(w['facts']):
                    payload=f['provenance']['payload']
                    direct=lm.generate(serialize(payload),VERIFY_PROMPT,8,'v28_plain')
                    v=check(lm,payload,'v28_object')
                    append(LOCAL/'v28_object.jsonl',dict(index=r['index'],condition=w['condition'],j=j,old_score=f['score'],direct=direct,
                        accepted=v['matched'] and direct['text'].strip().lower()=='yes',**v))
                    print(r['index'],j,v['matched'],v['generation']['raw'],flush=True)
    finally:lm.close('v28_object_regression')
