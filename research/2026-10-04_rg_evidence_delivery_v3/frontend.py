"""Shared v3 frontend: local propositions and scoped question constraints."""
from common import *
from delivery import norm
from dataclasses import asdict
legacy=load_module('rg_v3_legacy_frontend',V2/'frontend.py')
from schemas import obj,STR,LOCATOR,LOCATE_PROMPT
Fact=legacy.Fact
plan_contract=legacy.plan_contract

CONDITION=obj(dict(owner=STR,predicate=STR,value_or_text=STR,question_span=STR,
    scope=dict(type='string',enum=['entity','relation_instance','unresolved_scope'])))
SCOPE=obj(dict(constraints=dict(type='array',maxItems=12,items=CONDITION)))
VERDICT=obj(dict(verdict=dict(type='string',enum=['supported','refuted','unresolved']),
    support_sids=dict(type='array',items=STR,maxItems=3),
    constraints=dict(type='array',maxItems=12,items=obj(dict(id=STR,status=dict(type='string',enum=['SUPPORTED','REFUTED','UNKNOWN']),support_sids=dict(type='array',items=STR,maxItems=3))))))
SCOPE_PROMPT='''Separate question restrictions from each local relation. Do not answer. Return constraints with owner (an exact entity, variable or relation id from the plan), predicate, value_or_text, exact question_span, scope entity/relation_instance/unresolved_scope. Preserve every supplied qualifier. Include additional explicit question restrictions if present. Do not add outside facts. The nationality of a movie belongs to the movie variable, NOT its director; a release year belongs to the movie. Relation instance restrictions such as 100% ownership belong to the ownership relation id. If owner is unclear use unresolved_scope. Do not convert the requested relation itself into a restriction. Return {"constraints": [...]} only.'''
VERIFY_PROMPT='''Evaluate ONE directed local proposition and, separately, scoped question constraints using ONLY the supplied original sentences, title and mention locations. Return supported/refuted/unresolved for the local proposition, with supporting sentence ids. Multiple valid objects can coexist: another director, child, work or affiliation does NOT refute the proposed object. Do not recover a unique answer. Supported requires actual source support for subject, predicate, object, direction and identity links; names co-occurring is insufficient. Refuted requires explicit contradictory evidence; missing information is unresolved. A title may identify a body pronoun but cannot by itself prove a relation. Preserve negation, dates and relation meaning.
For EACH constraint return SUPPORTED/REFUTED/UNKNOWN with sentence ids. Evaluate it ONLY for its resolved owner. The director being Australian does not show the movie is Australian. A missing movie year leaves the year UNKNOWN, without invalidating a correct directed-by fact. Unresolved owner or scope means UNKNOWN. Do not use other windows or general knowledge. Empty support cannot establish a proposition or condition. Return only the specified JSON object.'''

LOCAL_PROMPT='''Decide if the given directed claim is supported by the source. Output the verdict followed by supporting source sentence IDs, e.g. "supported s0" or "refuted s1". For unresolved output "unresolved". Use only provided s0/s1/s2 IDs; do not explain.
supported: the source states the claim, including its subject/object roles and mention identities.
refuted: the source explicitly contradicts this claim.
unresolved: the source does not establish or contradict it.
Several valid objects are allowed. Do not demand a unique object. Do not infer a relation just from names co-occurring. Do not use outside knowledge. A title can identify a body pronoun but cannot supply an absent relation.
Source s0: Mira directed North and South. Claim: Mira directed South. Verdict: supported s0
Source s0: Elena has a father named Marco. Claim: Marco has father Elena. Verdict: unresolved
Source s0: Mira did not direct North. Claim: Mira directed North. Verdict: refuted s0
Source s0: Mira is Australian and directed North. Claim: North has nationality Australian. Verdict: unresolved'''

LOCAL_SCHEMA=obj(dict(verdict=dict(type='string',enum=['supported','refuted','unresolved']),support_sids=dict(type='array',items=STR,maxItems=3)))
LOCAL_V32='''Judge whether the supplied EVIDENCE explicitly supports CLAIM with its direction and the proposed mention-to-identity links. Use only the shown original sentences and title. Title may resolve a body pronoun but cannot by itself establish a relation. Different valid objects of a relation are allowed. Another valid object is not a contradiction. Other question relations need not be satisfied here.
supported = this exact subject, predicate and object are supported;
refuted = explicit contradiction;
unresolved = wrong role, missing evidence or uncertain identity.
Do not treat co-occurring entities as related. "X is part of Y" does not establish "X operates Y". "a novel by X, published by Y" means Y published the novel, not its author X. "X's father was Y" supports X has father Y, not Y has father X. "first participated in 2008" is not supported by "participated in 2008 after a first appearance in 1952".
Return one object with verdict and support_sids. Cite original sentence IDs for supported/refuted; use [] for unresolved. No explanations or other fields.'''

def scope_contract(question,slots,raw):
    owners={s['id'] for s in slots}|{s[k] for s in slots for k in ('head','tail')}
    out=[]
    for c in (raw or {}).get('constraints',[]):
        if not isinstance(c,dict) or not all(isinstance(c.get(k),str) for k in ('owner','predicate','value_or_text','question_span','scope')):continue
        span=c['question_span']
        if not span or norm(span) not in norm(question) or legacy.qualifier_origin(question,c['value_or_text']) is None:continue
        c=dict(c)
        if c['owner'] not in owners:c['scope']='unresolved_scope'
        out.append(c)
    for s in slots:
        for qualifier in s.get('qualifiers',[]):
            origin=legacy.qualifier_origin(question,qualifier)
            if not any(norm(qualifier)==norm(c['value_or_text']) or (origin and norm(origin['text'])==norm(c['question_span'])) for c in out):
                out.append(dict(owner=s['id'],predicate='unresolved restriction',value_or_text=qualifier,question_span=origin['text'] if origin else qualifier,scope='unresolved_scope'))
    return [dict(id='c'+str(i+1),**c) for i,c in enumerate(out)]

def scope(lm,question,slots,stage):
    restrictions=[]
    for s in slots:
        for phrase in s.get('qualifiers',[]):
            origin=legacy.qualifier_origin(question,phrase)
            restrictions.append(dict(index=len(restrictions),from_relation=s['id'],text=phrase,question_span=origin['text'] if origin else phrase))
    if not restrictions:return [],None
    owners=sorted({s['id'] for s in slots}|{s[k] for s in slots for k in ('head','tail')})
    schema=obj(dict(assignments=dict(type='array',maxItems=len(restrictions),items=obj(dict(index=dict(type='integer',enum=list(range(len(restrictions)))),
        owner=dict(type='string',enum=owners),predicate=STR,scope=dict(type='string',enum=['entity','relation_instance','unresolved_scope']))))))
    system='''Assign each supplied restriction to its owner in the question plan. Output assignments only. The program supplies restriction text and source span: do not rewrite them. Choose owner from supplied entity/variable/relation IDs. Movie nationality and release year belong to the movie variable, not its director. Percentage ownership belongs to that ownership relation instance. An answer type belongs to the variable being requested. Use unresolved_scope when the owner cannot be determined. Preserve local relation direction. Do not answer the question.'''
    with lm.base_only():r=lm.generate(json.dumps(dict(question=question,relations=slots,restrictions=restrictions),ensure_ascii=False),system,256,stage,schema)
    constraints=[]
    for restriction in restrictions:
        a=next((a for a in (r['raw'] or {}).get('assignments',[]) if a.get('index')==restriction['index']),None)
        constraints.append(dict(id='c'+str(restriction['index']+1),owner=a['owner'] if a else restriction['from_relation'],predicate=a['predicate'] if a else 'unresolved restriction',
            scope=a['scope'] if a else 'unresolved_scope',value_or_text=restriction['text'],question_span=restriction['question_span']))
    return constraints,r

def owner_value(c,slot,head,tail,binding):
    owner=c['owner']
    if c['scope']=='unresolved_scope':return None
    if c['scope']=='relation_instance':return dict(subject=head,relation=slot['relation'],object=tail) if owner==slot['id'] else None
    for side,value in [('head',head),('tail',tail)]:
        if owner==slot[side]:return value
    v=binding.get(owner)
    return display(v) if v else (owner if not owner.startswith('?') and owner in (head,tail) else None)
def display(x):return x.split('|',1)[1] if x.startswith('page:') else x.rsplit(':',1)[-1] if x.startswith('local:') else x

def verify_v30(lm,payload,constraints,owners,stage):
    request=dict(payload,CONSTRAINTS=[dict(c,resolved_owner=owners.get(c['id'])) for c in constraints])
    with lm.base_only():g=lm.generate(json.dumps(request,ensure_ascii=False,sort_keys=True),VERIFY_PROMPT,256,stage,VERDICT)
    raw=g['raw'] or {};allowed={s['sid'] for s in payload['EVIDENCE']['sentences']}
    valid=lambda ids: isinstance(ids,list) and bool(ids) and len(set(ids))==len(ids) and set(ids)<=allowed
    verdict=raw.get('verdict','unresolved')
    if verdict not in ('supported','refuted','unresolved') or (verdict!='unresolved' and not valid(raw.get('support_sids'))):verdict='unresolved'
    conditions=[]
    for c in constraints:
        r=next((z for z in raw.get('constraints',[]) if z.get('id')==c['id']),{})
        status=r.get('status','UNKNOWN')
        if c['scope']=='unresolved_scope' or owners.get(c['id']) is None or status not in ('SUPPORTED','REFUTED','UNKNOWN') or (status!='UNKNOWN' and not valid(r.get('support_sids'))):status='UNKNOWN'
        conditions.append(dict(id=c['id'],status=status,support_sids=r.get('support_sids',[]) if status!='UNKNOWN' else []))
    return dict(verdict=verdict,support_sids=raw.get('support_sids',[]),constraints=conditions,generation=g)

def verify(lm,payload,constraints,owners,stage):
    """One proposition per call; validate cited IDs and retain whole window.

    v30's combined output confused CLAIM with constraint IDs. The v31 interface
    uses a plain, three-valued judgement and evaluates each resolved restriction
    as its own proposition. Missing scope never becomes a satisfied condition.
    """
    from verification import serialize
    local=dict(payload,CLAIM=dict(payload['CLAIM'],qualifiers=[]))
    def judge(p,suffix):
        # Same serialization for regression and natural tasks; old trailing
        # yes/no instruction is replaced without changing source text.
        text=serialize(p).rsplit('\nIs this exact claim',1)[0]+'\nVerdict:'
        from schemas import VERIFY_PROMPT as DIRECT_PROMPT
        with lm.base_only():
            direct=lm.generate(serialize(p),DIRECT_PROMPT,8,stage+suffix+'_support')
            supporting=direct['text'].strip().lower()=='yes'
            generations=[direct]
            verdict='supported' if supporting else 'unresolved'
            if not supporting:
                contra=lm.generate(text,'Does the source EXPLICITLY CONTRADICT the exact directed claim? Missing evidence, another valid object, uncertain identity or missing conditions are NOT contradiction. Answer exactly yes or no.',8,stage+suffix+'_contradiction')
                generations.append(contra)
                if contra['text'].strip().lower()=='yes':verdict='refuted'
            cited=[]
            if verdict!='unresolved':
                evidence=lm.generate(text+'\nLocate the sentence IDs establishing this '+verdict+' judgement.',
                    'Return {"support_sids": ["s0"]} using only IDs of supplied sentences needed for the judgement. If no sentence establishes it return {"support_sids": []}. Do not rewrite source text.',
                    40,stage+suffix+'_source',obj(dict(support_sids=dict(type='array',items=STR,maxItems=3))))
                generations.append(evidence);cited=(evidence['raw'] or {}).get('support_sids',[])
        g=dict(direct,seconds=sum(z['seconds'] for z in generations),input_tokens=sum(z['input_tokens'] for z in generations),output_tokens=sum(z['output_tokens'] for z in generations),subcalls=generations)
        allowed={s['sid'] for s in p['EVIDENCE']['sentences']}
        if verdict not in ('supported','refuted','unresolved'):verdict='unresolved'
        if verdict!='unresolved' and (not cited or len(set(cited))!=len(cited) or not set(cited)<=allowed):verdict='unresolved'
        return verdict,g,cited if verdict!='unresolved' else []
    verdict,g,cited=judge(local,'_local');conditions=[];gs=[g]
    for c in constraints:
        owner=owners.get(c['id']);status='UNKNOWN';v='unresolved';cids=[]
        if owner is not None and c['scope']!='unresolved_scope':
            subject=json.dumps(owner,ensure_ascii=False,sort_keys=True) if isinstance(owner,dict) else owner
            p=dict(payload,CLAIM=dict(subject=subject,relation=c['predicate'],object=c['value_or_text'],qualifiers=[]))
            v,cg,cids=judge(p,'_'+c['id']);gs.append(cg)
            status={'supported':'SUPPORTED','refuted':'REFUTED','unresolved':'UNKNOWN'}[v]
        conditions.append(dict(id=c['id'],status=status,support_sids=cids))
    actual=[a for z in gs for a in z.get('subcalls',[z])]
    combined=dict(g,seconds=sum(z['seconds'] for z in gs),input_tokens=sum(z['input_tokens'] for z in gs),output_tokens=sum(z['output_tokens'] for z in gs))
    result=dict(verdict=verdict,support_sids=cited,constraints=conditions,
        generation=combined,generations=actual,evidence_basis='validated_model_sentence_ids_with_entire_supplied_window_preserved')
    from source_rules import apply
    return apply(payload,constraints,owners,result)

def task_identity(question,plan,slot,binding,constraint_states,w,identity):
    # Whole plan + owners, full current binding/status, text and model identity.
    return digest(dict(question=question,plan=plan,slot=slot,binding=sorted(binding.items()),constraint_states=constraint_states,
        window=dict(id=w.id,title=w.title,text=w.text,sentences=w.sentences),identity=identity))

def extract_task(lm,question,slots,constraints,slot,binding,w,catalog,stage):
    request_slot=dict(slot,qualifiers=[])
    for side in ('head','tail'):
        if request_slot[side] in binding:request_slot[side]=display(binding[request_slot[side]])
    prompt=json.dumps(dict(relation={k:request_slot[k] for k in ('head','relation','tail','qualifiers')},window=legacy.packet(w)),ensure_ascii=False)
    g=lm.generate(prompt,LOCATE_PROMPT,384,stage+'_extract',LOCATOR)
    fs=[];rejected=[];verification=[]
    for item in (g['raw'] or {}).get('facts',[]):
        item=dict(item);alignment=False
        # Align literal mentions to the explicitly bound endpoint, then verify
        # the resulting directed proposition. This never asserts the relation.
        for side,other in [('head','tail'),('tail','head')]:
            required=request_slot[side]
            name=lambda m:norm(m.get('identity') or m['text'])
            if not required.startswith('?') and request_slot[other].startswith('?') and name(item[other])==norm(required) and name(item[side])!=norm(required):
                item['head'],item['tail']=item['tail'],item['head'];alignment=True
        raw=dict(slot=0,head=dict(item['head'],occurrence=0),tail=dict(item['tail'],occurrence=0),support_sids=item['support_sids'],status='supported')
        try:f,payload=legacy.recover(raw,w,[request_slot],catalog)
        except (ValueError,KeyError,TypeError) as e:rejected.append(str(e));continue
        owners={c['id']:owner_value(c,slot,f.head,f.tail,binding) for c in constraints}
        v=verify(lm,payload,constraints,owners,stage+'_verify');verification.append(dict(payload=payload,owners=owners,bound_endpoint_alignment=alignment,**v))
        if v['verdict']=='supported':
            fd=asdict(f);fd['score']=1.;fd['conditions']='[]'
            fd['provenance']['constraint_observations']=v['constraints'];fd['provenance']['constraint_owners']=owners
            fd['provenance']['local_verdict']=v['verdict'];fs.append(fd)
    return dict(facts=fs,detail=dict(generation=g,verification=verification,rejected=rejected))
