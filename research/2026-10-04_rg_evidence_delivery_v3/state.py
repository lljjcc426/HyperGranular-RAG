"""Semantic hypotheses, separate from the complete provenance ledger."""
from delivery import norm
import itertools,json

def fact_key(f):return (f['slot'],norm(f['head_id']),norm(f['tail_id']),f.get('polarity','positive'),f.get('conditions',''))
def extend(binding,slot,fact):
    b=dict(binding)
    for side in ('head','tail'):
        name=slot[side];value=norm(fact[side+'_id'])
        if name.startswith('?'):
            if name in b and norm(b[name])!=value:return None
            b[name]=value
        elif norm(name)!=norm(fact[side]):return None
    return b
def condition_states(constraints,fs):
    result={}
    for c in constraints:
        vals={r['status'] for f in fs for r in f['provenance'].get('constraint_observations',[]) if r['id']==c['id'] and r['status']!='UNKNOWN'}
        result[c['id']]='CONFLICT' if len(vals)>1 else next(iter(vals)) if vals else 'UNKNOWN'
    return result
def hypothesis_key(binding,keys,conditions):
    return (tuple(sorted((k,norm(v)) for k,v in binding.items())),tuple(sorted(keys)),tuple(sorted(conditions.items())))

def build_states(slots,constraints,facts,base,source_cost,beam=4):
    registry={}
    for f in facts:registry.setdefault(fact_key(f),[]).append(f)
    reps={}
    for k,ws in registry.items():
        unique={json.dumps([w['window'],w['provenance']],sort_keys=True):w for w in ws}
        reps[k]=sorted(unique.values(),key=lambda f:(source_cost([f]),-base[f['window']],f['window']))[:2]
    states=[({},())]
    def materialize(binding,keys):
        combinations=itertools.product(*(reps[k] for k in keys)) if keys else [()]
        fs=min(combinations,key=lambda z:(source_cost(z),-sum(base[f['window']] for f in z),tuple(f['window'] for f in z)))
        # Constraint conflict cannot be hidden by choosing a shorter witness.
        cs=condition_states(constraints,[f for k in keys for f in registry[k]])
        return dict(binding=binding,facts=list(fs),semantic_keys=keys,constraints=cs,
            program_complete=bool(slots) and {k[0] for k in keys}=={s['id'] for s in slots} and all(v=='SUPPORTED' for v in cs.values()),
            provenance_count=sum(len(registry[k]) for k in keys))
    for s in slots:
        candidates=list(states)
        for binding,keys in states:
            for k,ws in reps.items():
                if k[0]!=s['id']:continue
                b=extend(binding,s,ws[0])
                if b is not None:candidates.append((b,keys+(k,)))
        unique={}
        for b,keys in candidates:
            m=materialize(b,keys);unique[hypothesis_key(b,keys,m['constraints'])]=(b,keys,m)
        ordered=sorted(unique.values(),key=lambda z:(-len(z[1]),-min((f['score'] for f in z[2]['facts']),default=0),
            -sum(base[f['window']] for f in z[2]['facts'])/max(1,len(z[1])),source_cost(z[2]['facts']),z[1]))[:beam]
        states=[(b,ks) for b,ks,_ in ordered]
    return [materialize(b,ks) for b,ks in states]

def active_tasks(slots,states):
    out={}
    # Empty start stays available separately, not as a duplicate beam entry.
    for state in states+[dict(binding={},facts=[],constraints={})]:
        b=state['binding'];done={f['slot'] for f in state['facts']}
        for s in slots:
            if s['id'] in done:continue
            if not any(not s[k].startswith('?') or s[k] in b for k in ('head','tail')):continue
            key=(s['id'],tuple(sorted(b.items())),tuple(sorted(state['constraints'].items())))
            out[key]=(s,b,state['constraints'])
    return [out[k] for k in sorted(out)]
