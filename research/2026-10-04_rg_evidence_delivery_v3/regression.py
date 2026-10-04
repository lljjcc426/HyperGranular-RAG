"""Actual source regression; assistant development labels, not expert Gold."""
from common import *
from frontend import verify,scope
from runtime import LM
import copy

def examples():
    review=load_module('rg_v3_old_review',V2/'review_measure.py');out=[]
    local_extra={(0,'ANNOTATED_SUPPORT',0),(1,'ANNOTATED_SUPPORT',0),(5,'ANNOTATED_SUPPORT',0)}
    for r in rows(V2/'local/v23_B.jsonl'):
        for w in r['windows']:
            for j,f in enumerate(w['facts']):
                key=(r['index'],w['condition'],j);payload=copy.deepcopy(f['provenance']['payload']);payload['CLAIM']['qualifiers']=[]
                out.append(dict(id='old:'+':'.join(map(str,key)),origin='D0_existing',expected_local=int(key in review.SUPPORTED|local_extra),
                    expected_whole=int(key in review.SUPPORTED),payload=payload,constraints=[],owners={},old_key=list(key)))
    def add(name,body,h,rel,t,label,constraints=None,owners=None):
        payload=dict(CLAIM=dict(subject=h,relation=rel,object=t,qualifiers=[]),EVIDENCE=dict(title='Source',sentences=[dict(sid='s0',text=body)]),
            LOCATIONS=dict(head=dict(text=h,identity=h,identity_basis='mention'),tail=dict(text=t,identity=t,identity_basis='mention'),support_sids=['s0']))
        out.append(dict(id=name,origin='constructed',expected_local=label,payload=payload,constraints=constraints or [],owners=owners or {}))
    add('multi_first','Mara directed Lake and Hill.','Mara','directed','Lake',1)
    add('multi_second','Mara directed Lake and Hill.','Mara','directed','Hill',1)
    add('reverse','Elena\'s father was Marco.','Marco','has father','Elena',0)
    add('cooccur','Ada met Mira at the studio.','Ada','directed','Mira',0)
    add('negated','Mara did not direct Lake.','Mara','directed','Lake',0)
    add('ambiguous_name','Alex (the teacher) has a son Ben. Alex (the artist) has no children.','Alex (the artist)','has son','Ben',0)
    c=dict(id='c1',owner='?film',predicate='nationality',value_or_text='Australian',question_span='Australian',scope='entity')
    add('film_not_director_country','Mara is an Australian director. She directed Lake in 2014.','Mara','directed','Lake',1,[c],{'c1':'Lake'})
    c=dict(id='c1',owner='?film',predicate='release year',value_or_text='2014',question_span='2014',scope='entity')
    add('missing_year_local_supported','Mara directed Lake.','Mara','directed','Lake',1,[c],{'c1':'Lake'})
    add('year_supported','Lake was released in 2014 and directed by Mara.','Mara','directed','Lake',1,[c],{'c1':'Lake'})
    return out

def run():
    dest=LOCAL/'regression_v35.jsonl';done={r['id'] for r in rows(dest)} if dest.exists() else set();lm=LM(quantized=True,adapter=V2/'adapters/v27')
    try:
        for e in examples():
            if e['id'] in done:continue
            r=verify(lm,e['payload'],e['constraints'],e['owners'],'B_v35_verify')
            append(dest,dict(**e,result=r));print(e['id'],r['verdict'],flush=True)
    finally:lm.close('B_v35_regression')

def summarize():
    out=[]
    for p in sorted(LOCAL.glob('regression_v*.jsonl')):
        for r in rows(p):
            v=r['result'];out.append(dict(iteration=p.stem,id=r['id'],origin=r['origin'],expected_local=r['expected_local'],accepted=int(v['verdict']=='supported'),verdict=v['verdict'],
                condition_states=json.dumps(v['constraints'],sort_keys=True),seconds=v['generation']['seconds'],input_tokens=v['generation']['input_tokens'],output_tokens=v['generation']['output_tokens']))
    table(HERE/'FRONTEND_REGRESSION.csv',out)
    for iteration,origin in sorted({(r['iteration'],r['origin']) for r in out}):
        xs=[r for r in out if r['origin']==origin and r['iteration']==iteration];print(iteration,origin,dict(n=len(xs),TP=sum(r['accepted'] and r['expected_local'] for r in xs),FP=sum(r['accepted'] and not r['expected_local'] for r in xs),FN=sum(not r['accepted'] and r['expected_local'] for r in xs)))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='rules':
        from source_rules import apply
        dest=LOCAL/'regression_v34.jsonl'
        if dest.exists():raise FileExistsError(dest)
        for r in rows(LOCAL/'regression_v33.jsonl'):
            r['result']=apply(r['payload'],r['constraints'],r['owners'],r['result']);r['inference_reuse']='exact v33 model inputs; new deterministic source rules only';append(dest,r)
        summarize()
    elif len(sys.argv)>1 and sys.argv[1]=='summarize':summarize()
    else:run()
