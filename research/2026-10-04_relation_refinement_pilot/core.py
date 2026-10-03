"""Gold-free relation-guided search. Scheduler receives only requested observations."""
from dataclasses import dataclass,field
import itertools, json, math, time
import numpy as np

METHODS=('Dense-window','Flat-binding','GB-fixed','GB-uniform','GB-feedback','KM-fixed','KM-uniform','KM-feedback')
def norm(x):
    x=np.asarray(x,dtype=np.float64);n=np.linalg.norm(x,axis=-1,keepdims=True)
    return np.divide(x,n,out=np.zeros_like(x),where=n>0)

@dataclass(frozen=True)
class Window:
    id:str
    source:str
    title:str
    text:str
    sentences:tuple # (original id, retained text, original char start, char end)
    truncated:bool=False

@dataclass(frozen=True)
class Fact:
    slot:str
    head:str
    tail:str
    quote:str
    window:str
    head_id:str
    tail_id:str
    score:float
    polarity:str='positive'
    conditions:str=''

def parse_contract(question,raw):
    try:
        slots=raw['slots'];av=raw['answer_var']
        assert isinstance(slots,list) and 1<=len(slots)<=4 and isinstance(av,str) and av.startswith('?')
        assert len({s['id'] for s in slots})==len(slots)
        for s in slots:
            assert all(isinstance(s[k],str) and s[k].strip() for k in ('id','head','relation','tail'))
            for k in ('head','tail'):
                assert s[k].startswith('?') or s[k] in question
        assert any(av in (s['head'],s['tail']) for s in slots)
        return slots
    except (KeyError,TypeError,AssertionError): return []

def entity_id(name,w,catalog):
    # Only complete page-name equality bridges sources. No surname/fuzzy matching.
    matches={source for title,source in catalog if name==title}
    if len(matches)==1:return 'page:'+next(iter(matches))+'|'+name
    return 'local:'+w.source+':'+name

def witnessed(raw,w,slots,catalog,score):
    """Explicit body spans only; unsupported coreference stays UNKNOWN in v1."""
    if not isinstance(raw,dict):return None
    required=('slot_id','head','tail','quote','polarity','conditions','explicit')
    if any(k not in raw for k in required):return None
    if raw['explicit'] is not True or raw['polarity']!='positive':return None
    if raw['slot_id'] not in {s['id'] for s in slots}:return None
    if any(not isinstance(raw[k],str) or not raw[k] for k in ('head','tail','quote')):return None
    if any(raw[k] not in w.text for k in ('head','tail','quote')):return None
    if not math.isfinite(score):return None
    return Fact(raw['slot_id'],raw['head'],raw['tail'],raw['quote'],w.id,
                entity_id(raw['head'],w,catalog),entity_id(raw['tail'],w,catalog),float(score),
                raw['polarity'],raw['conditions'])

def extend(binding,slot,fact,window,catalog):
    out=dict(binding)
    for side in ('head','tail'):
        name=slot[side];value=getattr(fact,side+'_id')
        if name.startswith('?'):
            if name in out and out[name]!=value:return None
            out[name]=value
        else:
            # A question constant must be explicitly witnessed; page aliases are not guessed.
            if name!=getattr(fact,side):return None
    return out

def bundles(slots,facts,windows,base,catalog):
    states=[({},())]
    for slot in slots:
        new=list(states)
        for binding,fs in states:
            for f in facts:
                if f.slot!=slot['id']:continue
                b=extend(binding,slot,f,windows[f.window],catalog)
                if b is not None:new.append((b,fs+(f,)))
        # Retain beam at each step, including partial hypotheses; bounded to four.
        unique={}
        for b,fs in new:
            key=(tuple(sorted(b.items())),tuple((f.slot,f.window,f.quote) for f in fs))
            unique[key]=(b,fs)
        states=sorted(unique.values(),key=lambda z:bundle_key(z[1],windows,base))[:4]
    return states

def bundle_key(fs,windows,base):
    return (-len(fs),-min((f.score for f in fs),default=0),
            -sum(base[f.window] for f in fs)/max(1,len(fs)),
            sum(len(windows[i].text.split()) for i in {f.window for f in fs}),
            tuple((f.slot,f.window,f.head_id,f.tail_id) for f in fs))

def active(slots,states):
    queries=[];relevant=set()
    for binding,fs in states or [({},())]:
        done={f.slot for f in fs};missing=[s for s in slots if s['id'] not in done]
        for s in missing:
            h=binding.get(s['head'],s['head']);t=binding.get(s['tail'],s['tail'])
            def display(x):
                if x.startswith('page:'):return x.split('|',1)[1]
                return x.split(':')[-1] if x.startswith('local:') else x
            vals=[display(x) for x in (h,t) if not x.startswith('?')]
            if vals:queries.append(' '.join([*vals,s['relation']]))
            relevant.add(s['id'])
            variables={x for x in (s['head'],s['tail']) if x.startswith('?')}
            relevant.update(z['id'] for z in slots if variables & {z['head'],z['tail']})
    return sorted(set(queries)),relevant

@dataclass
class Group:
    id:str
    members:list
    depth:int=0
    terminal:bool=False

def split_members(ix,x,ids,kind,seeds=None):
    ix=sorted(ix,key=lambda i:ids[i]);arr=x[ix]
    if len(ix)<2:return [],{'degenerate':True,'repairs':0}
    if seeds is None:
        c=arr.mean(0);a=min(ix,key=lambda i:(-float(np.sum((x[i]-c)**2)),ids[i]))
        b=min((i for i in ix if i!=a),key=lambda i:(-float(np.sum((x[i]-x[a])**2)),ids[i]))
        seeds=(a,b)
    centers=x[list(seeds)].copy();labels=None;repairs=0
    for _ in range(20 if kind=='KM' else 1):
        if kind=='KM':lab=(arr@norm(centers).T).argmax(1)
        else:lab=np.sum((arr[:,None,:]-centers[None,:,:])**2,axis=2).argmin(1)
        if len(set(lab.tolist()))<2:
            lab=np.array([0]*(len(ix)//2)+[1]*(len(ix)-len(ix)//2));repairs+=1
        if labels is not None and np.array_equal(lab,labels):break
        labels=lab;centers=np.stack([arr[labels==j].mean(0) for j in (0,1)])
    return [[ix[i] for i in np.flatnonzero(lab==j)] for j in (0,1)],{'degenerate':bool(np.max(np.ptp(arr,axis=0))==0),'repairs':repairs}

def initialize(x,ids,kind):
    n=len(ids);k=min(4,n);repairs=0
    if not n:return [],0
    if kind=='GB':
        groups=[Group('g0',list(range(n)))]
        while len(groups)<k:
            options=[g for g in groups if len(g.members)>1]
            if not options:break
            g=min(options,key=lambda g:(-float(np.sum((x[g.members]-x[g.members].mean(0))**2)),g.id))
            children,meta=split_members(g.members,x,ids,'GB');repairs+=meta['repairs']
            groups.remove(g);groups.extend(Group(g.id+str(j),m,g.depth+1,meta['degenerate']) for j,m in enumerate(children))
        return groups,repairs
    rng=np.random.default_rng(1729);centers=x[rng.choice(n,k,replace=False)].copy();previous=None
    for _ in range(20):
        sim=x@norm(centers).T;lab=sim.argmax(1);size=np.bincount(lab,minlength=k)
        for j in range(k):
            if size[j]:continue
            i=min((i for i in range(n) if size[lab[i]]>1),key=lambda i:(float(sim[i,lab[i]]),ids[i]))
            size[lab[i]]-=1;lab[i]=j;size[j]+=1;repairs+=1
        if previous is not None and np.array_equal(lab,previous):break
        previous=lab.copy();centers=np.stack([x[lab==j].mean(0) for j in range(k)])
    return [Group('g'+str(j),np.flatnonzero(lab==j).tolist()) for j in range(k)],repairs

def feedback_pair(g,observed,slots,states,relevant,windows,catalog,x,ids):
    known=[i for i in g.members if ids[i] in observed]
    if len(known)<2 or len(known)==len(g.members):return None
    pairs=[]
    for a,b in itertools.combinations(known,2):
        for slot in slots:
            if slot['id'] not in relevant:continue
            fa=[f for f in observed[ids[a]] if f.slot==slot['id']]
            fb=[f for f in observed[ids[b]] if f.slot==slot['id']]
            sa={(f.head_id,f.tail_id) for f in fa};sb={(f.head_id,f.tail_id) for f in fb}
            if sa==sb or not(sa or sb):continue
            extends=any(extend(binding,slot,f,windows[f.window],catalog) is not None
                        for binding,_ in states for f in fa+fb)
            if extends:pairs.append((a,b));break
    return min(pairs,key=lambda ab:(-float(np.sum((x[ab[0]]-x[ab[1]])**2)),ids[ab[0]],ids[ab[1]])) if pairs else None

class LazyProbe:
    def __init__(self,callback):self.__callback=callback;self.__cache={};self.actual_calls=0
    def request(self,key,w,uncached=False):
        hit=key in self.__cache and not uncached
        if hit:result=self.__cache[key]
        else:
            result=self.__callback(w);self.actual_calls+=1
            if not uncached:self.__cache[key]=result
        return tuple(result),hit

def search(method,question,slots,windows,x,qvector,embed,probe,threshold=.7,uncached=False,max_probes=32):
    assert method in METHODS and method!='Dense-window'
    start=time.perf_counter();ids=[w.id for w in windows];wm={w.id:w for w in windows}
    catalog=tuple({(w.title,w.source) for w in windows});base={w.id:float(x[i]@qvector) for i,w in enumerate(windows)}
    kind=method.split('-')[0];groups,repairs=initialize(x,ids,kind) if kind!='Flat' else ([],0)
    observed={};facts=[];states=[({},())];conditional={};snapshots={};trace=[];splits=[];hits=0;cap_fallback=0
    for step in range(min(max_probes,len(windows))):
        queries,relevant=active(slots,states);vs=[]
        for text in queries:
            if text not in conditional:
                if len(conditional)>=32:cap_fallback+=1;vs.append(qvector);continue
                conditional[text]=embed(text)
            vs.append(conditional[text])
        if not vs:vs=[qvector]
        scores=np.max(x@np.stack(vs).T,axis=1)
        def key(i):return (-float(scores[i]),-base[ids[i]],ids[i])
        remaining=[i for i in range(len(ids)) if ids[i] not in observed]
        if kind=='Flat':picked=min(remaining,key=key);gid=None
        else:
            eligible=[g for g in groups if any(ids[i] not in observed for i in g.members)]
            def gkey(g):
                rem=[i for i in g.members if ids[i] not in observed]
                feedback=feedback_pair(g,observed,slots,states,relevant,wm,catalog,x,ids)
                center=norm(x[rem].mean(0));return (feedback is None,-max(float(center@v) for v in vs),g.id)
            g=min(eligible,key=gkey);gid=g.id;rem=[i for i in g.members if ids[i] not in observed]
            known=[i for i in g.members if ids[i] in observed]
            if len(known)==1:
                top=sorted(rem,key=key)[:4]
                picked=min(top,key=lambda i:(-float(np.sum((x[i]-x[known[0]])**2)),-base[ids[i]],ids[i]))
            else:picked=min(rem,key=key)
        result,hit=probe.request((question,json.dumps(slots,sort_keys=True),ids[picked]),windows[picked],uncached)
        hits+=hit;observed[ids[picked]]=tuple(f for f in result if f.score>=threshold)
        facts.extend(observed[ids[picked]]);states=bundles(slots,facts,wm,base,catalog)
        queries,relevant=active(slots,states)
        trace.append(dict(step=step+1,window=ids[picked],group=gid,cache_hit=hit,accepted=len(observed[ids[picked]])))
        candidates=[g for g in groups if not g.terminal and g.depth<8 and len(g.members)>1 and any(ids[i] not in observed for i in g.members)]
        chosen=None;seeds=None
        if len(groups)<16 and method.endswith('uniform') and (step+1)%4==0 and candidates:
            chosen=min(candidates,key=lambda g:(-sum(ids[i] not in observed for i in g.members),g.id))
        elif len(groups)<16 and method.endswith('feedback'):
            for g in sorted(candidates,key=lambda g:g.id):
                pair=feedback_pair(g,observed,slots,states,relevant,wm,catalog,x,ids)
                if pair is not None:chosen=g;seeds=pair;break
        if chosen:
            t=time.perf_counter();children,meta=split_members(chosen.members,x,ids,kind,seeds);repairs+=meta['repairs']
            groups.remove(chosen);groups.extend(Group(chosen.id+str(j),m,chosen.depth+1,meta['degenerate']) for j,m in enumerate(children))
            splits.append(dict(step=step+1,parent=chosen.id,seeds=None if seeds is None else [ids[i] for i in seeds],seconds=time.perf_counter()-t))
        if step+1 in (8,16,32) or step+1==len(windows):
            snapshots[step+1]=dict(states=states.copy(),probe_count=step+1,split_count=len(splits),leaf_count=len(groups),
                accepted_facts=len(facts),complete=any(len(fs)==len(slots) for _,fs in states),
                logical_probes=step+1,cache_hits=hits,conditional_strings=len(conditional),cap_fallback=cap_fallback)
    return dict(snapshots=snapshots,trace=trace,splits=splits,repair_count=repairs,seconds=time.perf_counter()-start)

def render(question,windows,states,slot_count,tokenize,limit=1024):
    """Only original sentences enter the reader; no extracted variables or facts."""
    wm={w.id:w for w in windows};rank={w.id:i for i,w in enumerate(windows)}
    def assemble(required):
        units={};ordered=[]
        for w in sorted(required,key=lambda w:rank[w.id]):
            for sid,text,start,end in w.sentences:
                key=(sid,start,end)
                if key not in units:units[key]=text;ordered.append(key)
        return units,ordered
    def prompt(units,order):
        body='\n'.join(f'[{j+1}] {units[k]}' for j,k in enumerate(order))
        return 'Answer the question using only the evidence. Return a short answer, or UNKNOWN if insufficient.\nQuestion: '+question+'\nEvidence:\n'+body
    chosen=None;units={};order=[];oversized=0
    for _,fs in states:
        if len(fs)!=slot_count:continue
        required=[wm[i] for i in {f.window for f in fs}];u,o=assemble(required);p=prompt(u,o)
        if len(tokenize(p))<=limit and all(f.quote in p for f in fs):chosen=fs;units=u;order=o;break
        oversized+=1
    for w in windows:
        u=dict(units);o=list(order)
        for sid,text,start,end in w.sentences:
            k=(sid,start,end)
            if k not in u:u[k]=text;o.append(k)
        if len(tokenize(prompt(u,o)))<=limit:units,order=u,o
    p=prompt(units,order)
    return dict(prompt=p,input_tokens=len(tokenize(p)),visible_ids=list(dict.fromkeys(k[0] for k in order)),
                visible_spans=[list(k) for k in order],complete_bundle_visible=chosen is not None,
                fallback=chosen is None,oversized_bundles=oversized)
