from common import *
from schemas import *
from dataclasses import dataclass,asdict
import re,unicodedata

def normalized(text):return ' '.join(unicodedata.normalize('NFKC',text).split())
def qualifier_origin(question,phrase):
    """Traceable lexical association, allowing omitted function words only."""
    if not isinstance(phrase,str):return None
    q=normalized(question);p=normalized(phrase)
    if p and any(ch.isalnum() for ch in p) and p in q:return dict(text=q[q.index(p):q.index(p)+len(p)],rule='exact')
    def tokens(s):return [(m.group().casefold(),m.start(),m.end()) for m in re.finditer(r'\w+|[^\w\s]',s)]
    qt=tokens(q);pt=tokens(p);skip={'a','an','the','of','in','on','was','is','were','are'}
    if not pt or not any(t[0].isalnum() for t in pt):return None
    for start in range(len(qt)):
        j=start;k=0
        while j<len(qt) and k<len(pt):
            if qt[j][0]==pt[k][0]:j+=1;k+=1
            elif qt[j][0] in skip:j+=1
            else:break
        if k==len(pt):return dict(text=q[qt[start][1]:qt[j-1][2]],rule='case_and_function_word_omission')
    return None
def plan_contract(question,raw):
    errors=[]
    if not isinstance(raw,dict) or set(raw)!= {'status','relations'}:return [],['TOP_OBJECT']
    if raw['status'] not in ('ok','ambiguous','unsupported') or not isinstance(raw['relations'],list):return [],['STATUS_OR_RELATIONS']
    if raw['status']!='ok':return [],['DECLARED_'+raw['status'].upper()]
    rs=raw['relations']
    if not 1<=len(rs)<=4:return [],['RELATION_COUNT']
    slots=[];nodes=set();edges=[];anchors=set()
    for j,r in enumerate(rs):
        if not isinstance(r,dict) or set(r)!= {'head','relation','tail','qualifiers'}:return [],['RELATION_KEYS']
        if any(not isinstance(r[k],str) or not r[k].strip() for k in ('head','relation','tail')):return [],['STRING_TYPE']
        if not isinstance(r['qualifiers'],list) or any(qualifier_origin(question,q) is None for q in r['qualifiers']):errors.append('QUALIFIER_ORIGIN')
        for k in ('head','tail'):
            x=r[k]
            if x.startswith('?'):
                if not re.fullmatch(r'\?(answer|v[1-3])',x):errors.append('VARIABLE_NAME')
            elif normalized(x) not in normalized(question):errors.append('CONSTANT_ORIGIN')
            else:anchors.add(x)
            nodes.add(x)
        if r['head']==r['tail']:errors.append('SELF_LOOP')
        edges.append((r['head'],r['tail']))
        slots.append(dict(id='r'+str(j+1),**r))
    if '?answer' not in nodes:errors.append('ANSWER_MISSING')
    reached=set(anchors)
    for _ in range(4):
        for a,b in edges:
            if a in reached or b in reached:reached.update((a,b))
    if reached!=nodes:errors.append('DISCONNECTED')
    return ([] if errors else slots),sorted(set(errors))

def parse(lm,question,stage):
    if stage.startswith(('v27_','v29_')):
        from parse_develop import SIMPLE
        prompt=SIMPLE
    elif stage.startswith('v25_'):
        from parse_develop import SIMPLE
        prompt=SIMPLE+'''\nDo not drop qualifiers. The answer type (county/date/record label) and defining conditions must appear in the predicate or qualifiers. More examples:\nQ: Dara Lee is 100% owner of a cargo airline headquartered where?\n{"status":"ok","relations":[{"head":"?v1","relation":"owned by","tail":"Dara Lee","qualifiers":["100%","cargo airline"]},{"head":"?v1","relation":"headquartered in","tail":"?answer","qualifiers":[]}]}\nQ: What day did the founder of Elm Press, who was also an American heir and hotelier, die?\n{"status":"ok","relations":[{"head":"Elm Press","relation":"founded by","tail":"?v1","qualifiers":["American heir and hotelier"]},{"head":"?v1","relation":"died on","tail":"?answer","qualifiers":[]}]}\nQ: What county is Nara Reed's birth place the capital of?\n{"status":"ok","relations":[{"head":"Nara Reed","relation":"born in","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"capital of","tail":"?answer","qualifiers":["county"]}]}\nDo not introduce founders, places or unnamed objects as literal noun phrases. Unnamed objects require variables.'''
    else:prompt=PARSE_V22 if not stage.startswith(('v20_','v21_')) else PARSE_PROMPT
    r=lm.generate(question,prompt,512,stage,PLAN)
    draft=r
    if stage.startswith('v21_'):
        r=lm.generate(json.dumps(dict(question=question,draft=r['raw']),ensure_ascii=False),REVISE_PROMPT,512,stage+'_revise',PLAN)
    slots,errors=plan_contract(question,r['raw'])
    return dict(generation=r,draft=draft,slots=slots,errors=errors)

def packet(w):
    return dict(title=w.title,sentences=[dict(sid='s'+str(j),text=s[1]) for j,s in enumerate(w.sentences)])

def locate(mention,w):
    if not isinstance(mention,dict) or set(mention)!= {'sid','text','occurrence','identity'}:raise ValueError('MENTION_SCHEMA')
    sid=mention['sid'];text=mention['text'];occ=mention['occurrence'];identity=mention['identity']
    if not isinstance(sid,str) or not re.fullmatch(r's[0-2]',sid):raise ValueError('SENTENCE_ID')
    j=int(sid[1:])
    if j>=len(w.sentences) or type(occ)!=int or occ<0 or not isinstance(text,str) or not text or text.startswith('?'):raise ValueError('MENTION_VALUE')
    original,body,start,end=w.sentences[j];matches=[m.start() for m in re.finditer(re.escape(text),body)]
    if occ>=len(matches):raise ValueError('SPAN_NOT_FOUND')
    a=matches[occ]
    if not isinstance(identity,str):raise ValueError('IDENTITY_TYPE')
    # Identity is a proposed interpretation, not automatically true. It must have
    # a literal source in this request and survive the same semantic verifier.
    if identity and identity!=w.title and not any(identity in s[1] for s in w.sentences):raise ValueError('IDENTITY_NO_SOURCE')
    return dict(sid=sid,original_id=original,text=text,start=start+a,end=start+a+len(text),identity=identity or text,
                identity_basis='title' if identity and identity==w.title else ('window' if identity else 'mention'))

def entity(name,w,catalog):
    key=normalized(name)
    matches={source for title,source in catalog if normalized(title)==key}
    if len(matches)==1:return 'page:'+next(iter(matches))+'|'+key
    return 'local:'+w.source+':'+key

def verification_payload(w,slot,head,tail,support):
    # Identical code for diagnostic positives/negatives and runtime facts.
    return dict(CLAIM=dict(subject=head['identity'],relation=slot['relation'],object=tail['identity'],qualifiers=slot.get('qualifiers',[])),
        EVIDENCE=dict(title=w.title,sentences=packet(w)['sentences']),
        LOCATIONS=dict(head=head,tail=tail,support_sids=support))

@dataclass(frozen=True)
class Fact(engine.Fact):
    provenance:dict=None

def recover(raw,w,slots,catalog):
    if raw.get('status')!='supported':raise ValueError('UNRESOLVED')
    i=raw.get('slot')
    if type(i)!=int or not 0<=i<len(slots):raise ValueError('SLOT_ID')
    h=locate(raw['head'],w);t=locate(raw['tail'],w);ss=raw['support_sids']
    for role,m in (('head',h),('tail',t)):
        required=slots[i][role]
        if not required.startswith('?') and normalized(required)!=normalized(m['identity']):raise ValueError('CONSTANT_BINDING')
    if not isinstance(ss,list) or not ss or len(ss)>3 or len(set(ss))!=len(ss):raise ValueError('SUPPORT_IDS')
    if not {h['sid'],t['sid']}<=set(ss):raise ValueError('MENTION_OUTSIDE_SUPPORT')
    indices=[]
    for sid in ss:
        if not isinstance(sid,str) or not re.fullmatch(r's[0-2]',sid) or int(sid[1:])>=len(w.sentences):raise ValueError('SUPPORT_ID')
        indices.append(int(sid[1:]))
    spans=[dict(original_id=w.sentences[j][0],text=w.sentences[j][1],start=w.sentences[j][2],end=w.sentences[j][3]) for j in sorted(indices)]
    slot=slots[i];payload=verification_payload(w,slot,h,t,ss)
    f=Fact(slot['id'],h['identity'],t['identity'],json.dumps([s['text'] for s in spans],ensure_ascii=False),w.id,
        entity(h['identity'],w,catalog),entity(t['identity'],w,catalog),0.,conditions=json.dumps(slot.get('qualifiers',[])),
        provenance=dict(head=h,tail=t,spans=spans,title=w.title,payload=payload,
            verification_spans=[dict(original_id=sid,text=text,start=a,end=b) for sid,text,a,b in w.sentences],
            evidence_scope='entire_requested_window; model-cited spans retained separately'))
    return f,payload

def extract(lm,question,slots,w,catalog,stage):
    if not stage.startswith(('v20_','v21_')):return extract_locators(lm,question,slots,w,catalog,stage)
    prompt=json.dumps(dict(question=question,relations=[{k:s[k] for k in ('head','relation','tail','qualifiers')} for s in slots],window=packet(w)),ensure_ascii=False)
    r=lm.generate(prompt,EXTRACT_PROMPT,512,stage,EXTRACTION);fs=[];rejected=[];verifications=[]
    raw=r['raw']
    if not isinstance(raw,dict) or not isinstance(raw.get('facts'),list):return [],dict(generation=r,rejected=['EXTRACTION_SCHEMA'],verification=[])
    if len(raw['facts'])>3:return [],dict(generation=r,rejected=['TOO_MANY_FACTS'],verification=[])
    for item in raw['facts']:
        try:f,payload=recover(item,w,slots,catalog)
        except (ValueError,KeyError,TypeError) as e:rejected.append(str(e));continue
        v=lm.verify(payload,stage+'_verify');verifications.append(dict(**v,payload=payload))
        f=Fact(**{**asdict(f),'score':v['score']});fs.append(f)
    return fs,dict(generation=r,rejected=rejected,verification=verifications)

def extract_locators(lm,question,slots,w,catalog,stage):
    fs=[];rejected=[];verifications=[];generations=[]
    for i,slot in enumerate(slots):
        prompt=json.dumps(dict(relation={k:slot[k] for k in ('head','relation','tail','qualifiers')},window=packet(w)),ensure_ascii=False)
        r=lm.generate(prompt,LOCATE_PROMPT,384,stage+'_r'+str(i),LOCATOR);generations.append(r)
        if not isinstance(r['raw'],dict):rejected.append('EXTRACTION_SCHEMA');continue
        for item in r['raw']['facts']:
            # First literal occurrence within the model-selected sentence. This
            # only chooses an offset for an identical string, never an entity.
            raw=dict(slot=i,head=dict(item['head'],occurrence=0),tail=dict(item['tail'],occurrence=0),support_sids=item['support_sids'],status='supported')
            try:f,payload=recover(raw,w,slots,catalog)
            except (ValueError,KeyError,TypeError) as e:rejected.append(str(e));continue
            v=lm.verify(payload,stage+'_verify');verifications.append(dict(**v,payload=payload))
            fs.append(Fact(**{**asdict(f),'score':v['score']}))
    return fs,dict(generation=generations,rejected=rejected,verification=verifications)

def render(question,windows,states,slot_count,tokenize,limit=1024):
    wm={w.id:w for w in windows};rank={w.id:i for i,w in enumerate(windows)}
    def add(u,o,w):
        for sid,text,a,b in w.sentences:
            k=(sid,a,b)
            if k not in u:u[k]=(w.title,text);o.append(k)
    def prompt(u,o):
        body='\n'.join(f'[{j+1}] Title: {u[k][0]}\n{u[k][1]}' for j,k in enumerate(o))
        return 'Answer the question using only the evidence. Return a short answer, or UNKNOWN if insufficient.\nQuestion: '+question+'\nEvidence:\n'+body
    units={};order=[];chosen=None;oversized=0
    for _,fs in states:
        if len(fs)!=slot_count:continue
        u={};o=[]
        for w in sorted((wm[i] for i in {f.window for f in fs}),key=lambda w:rank[w.id]):add(u,o,w)
        visible={(k[0],k[1],k[2],u[k][1]) for k in o}
        if len(tokenize(prompt(u,o)))<=limit and all((s['original_id'],s['start'],s['end'],s['text']) in visible for f in fs for s in f.provenance.get('verification_spans',f.provenance['spans'])):
            units,order,chosen=u,o,fs;break
        oversized+=1
    skipped=0
    for w in windows:
        u=dict(units);o=list(order);add(u,o,w)
        if len(tokenize(prompt(u,o)))<=limit:units,order=u,o
        else:skipped+=1
    p=prompt(units,order)
    return dict(prompt=p,input_tokens=len(tokenize(p)),visible_ids=list(dict.fromkeys(k[0] for k in order)),visible_spans=[list(k) for k in order],
        complete_bundle_visible=chosen is not None,fallback=chosen is None,oversized_bundles=oversized,skipped_windows=skipped)
