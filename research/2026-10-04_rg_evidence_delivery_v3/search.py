"""Targeted requests: no cache lookahead; feedback uses paid compatible tasks."""
from common import engine,digest,time
from frontend import display,task_identity
from state import build_states,active_tasks
import numpy as np,itertools

def feedback_pair(group,observed,ids,x):
    pairs=[]
    for a,b in itertools.combinations(observed,2):
        if a['index']==b['index'] or a['index'] not in group.members or b['index'] not in group.members:continue
        if a['slot']!=b['slot'] or a['binding']!=b['binding'] or a.get('constraints',{})!=b.get('constraints',{}):continue
        sa={(f['head_id'],f['tail_id']) for f in a['facts']};sb={(f['head_id'],f['tail_id']) for f in b['facts']}
        if sa==sb:
            ca={(c['id'],c['status']) for f in a['facts'] for c in f['provenance'].get('constraint_observations',[])}
            cb={(c['id'],c['status']) for f in b['facts'] for c in f['provenance'].get('constraint_observations',[])}
            if ca==cb:continue
            reason='unmet_constraint'
        else:reason='binding_divergence' if sa and sb else 'relation_heterogeneity'
        pairs.append((a['index'],b['index'],reason))
    return min(pairs,key=lambda ab:(-float(np.sum((x[ab[0]]-x[ab[1]])**2)),ids[ab[0]],ids[ab[1]])) if pairs else None

def search(method,question,slots,constraints,windows,x,q,embed,request,identity,delivery,max_tasks=8):
    ids=[w.id for w in windows];base={w.id:float(x[i]@q) for i,w in enumerate(windows)}
    kind=method.split('-')[0];groups,repairs=engine.initialize(x,ids,kind) if kind!='Flat' else ([],0)
    observed=[];paid=set();facts=[];states=[];trace=[];splits=[];vectors={};t0=time.perf_counter()
    source_cost=lambda fs:delivery.tokens(delivery.package(fs)) if fs else 0
    plan=dict(slots=slots,constraints=constraints)
    for step in range(max_tasks):
        tasks=active_tasks(slots,states);choices=[]
        for slot,binding,cs in tasks:
            cs={c['id']:cs.get(c['id'],'UNKNOWN') for c in constraints}
            text=' '.join([display(binding.get(slot[k],slot[k])) for k in ('head','tail') if not binding.get(slot[k],slot[k]).startswith('?')]+[slot['relation']])
            if text not in vectors:vectors[text]=embed(text)
            scores=x@vectors[text]
            for i,w in enumerate(windows):
                key=task_identity(question,plan,slot,binding,cs,w,identity)
                if key not in paid:choices.append(dict(slot=slot,binding=binding,cs=cs,index=i,key=key,score=float(scores[i]),text=text))
        if not choices:break
        def ckey(c):return (-c['score'],-base[ids[c['index']]],c['slot']['id'],tuple(sorted(c['binding'].items())),ids[c['index']])
        if kind=='Flat':pick=min(choices,key=ckey);gid=None
        else:
            opts=[]
            for g in groups:
                available=[c for c in choices if c['index'] in g.members]
                if not available:continue
                feedback=feedback_pair(g,observed,ids,x)
                center=engine.norm(x[sorted({c['index'] for c in available})].mean(0))
                score=max(float(center@vectors[c['text']]) for c in available)
                # Preserve v1/v2 group prioritization for every grouped arm;
                # uniform versus feedback changes the split trigger, not this.
                opts.append(((feedback is None,-score,g.id),g,available))
            _,g,available=min(opts,key=lambda t:t[0]);gid=g.id
            known={o['index'] for o in observed if o['index'] in g.members}
            top=sorted(available,key=ckey)[:4]
            if len(known)==1:
                j=next(iter(known));pick=min(top,key=lambda c:(-float(np.sum((x[c['index']]-x[j])**2)),ckey(c)))
            else:pick=min(available,key=ckey)
        paid.add(pick['key']);w=windows[pick['index']]
        # Only this call can expose cache content, after a task has been selected.
        result,hit=request(pick['key'],pick['slot'],pick['binding'],pick['cs'],w)
        facts.extend(result['facts']);observed.append(dict(index=pick['index'],slot=pick['slot']['id'],binding=pick['binding'],constraints=pick['cs'],facts=result['facts']))
        states=build_states(slots,constraints,facts,base,source_cost)
        trace.append(dict(step=step+1,task=pick['key'],window=w.id,slot=pick['slot']['id'],binding=pick['binding'],group=gid,
            cache_hit=hit,accepted=len(result['facts']),semantic_states=len(states),detail=result['detail']))
        candidates=[g for g in groups if not g.terminal and g.depth<8 and len(g.members)>1]
        chosen=None;seeds=None;reason=None
        if len(groups)<16 and method.endswith('uniform') and (step+1)%4==0 and candidates:
            known={o['index'] for o in observed};chosen=min(candidates,key=lambda g:(-sum(i not in known for i in g.members),g.id));reason='uniform'
        elif len(groups)<16 and method.endswith('feedback'):
            for g in sorted(candidates,key=lambda g:g.id):
                pair=feedback_pair(g,observed,ids,x)
                if pair:chosen=g;seeds=pair[:2];reason=pair[2];break
        if chosen:
            children,meta=engine.split_members(chosen.members,x,ids,kind,seeds);repairs+=meta['repairs']
            groups.remove(chosen);groups.extend(engine.Group(chosen.id+str(j),m,chosen.depth+1,meta['degenerate']) for j,m in enumerate(children))
            splits.append(dict(step=step+1,parent=chosen.id,seeds=None if seeds is None else [ids[i] for i in seeds],reason=reason))
    return dict(states=states,trace=trace,splits=splits,facts=facts,conditional_texts=list(vectors),seconds=time.perf_counter()-t0,group_repairs=repairs)
