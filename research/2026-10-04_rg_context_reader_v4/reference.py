"""Annotation-only diagnostic; no answer string is returned to constructors."""
from common import *
def support_maps():
    result={}
    for tag,name in [('hotpot','stage4e_e2e_official_train1000_v1_gold_targets.jsonl'),('musique','stage4f_xdr_musique_train3000_v1_gold_targets.jsonl')]:
        result[tag]={r['query_id']:([s['unit_id'] for s in r['supporting_facts']] if tag=='hotpot' else r['supporting_unit_ids']) for r in rows(DATA/'processed'/name)}
    return result
def reference(c,b,support):
    um={u['unit_id']:u for u in c['units']};missing=[s for s in support if s not in um]
    top64=set(b.d.wm);outside=any(s not in top64 for s in support)
    if c['tag']=='hotpot':
        wm={w.id:w for w in make_windows(c['units'],b.tok)}
        spans=[z for s in support if s in wm for z in wm[s].sentences]
    else:spans=[(s,um[s]['text'],0,len(um[s]['text'])) for s in support if s in um]
    ks=set();source_order={u['unit_id']:i for i,u in enumerate(c['units'])}
    truncated=[]
    for sid,text,a,z in spans:
        k=(sid,a,z);title=um[sid]['title']
        if um[sid]['text'][a:z]!=text:raise ValueError('REFERENCE_SOURCE_MISMATCH')
        if sid in support and (a!=0 or z!=len(um[sid]['text'])):truncated.append(sid)
        b.d.units[k]=(title,text)
        if k not in b.d.order:b.d.order[k]=(100000+source_order[sid],a,sid,a,z)
        ks.add(k)
    full_tokens=b.body_tokens(ks);full_inputs={p:len(__import__('protocols').ids(b.tok,__import__('protocols').prompt(b.q,b.body(ks),p))) for p in ('P0','P1','P2')}
    selected=set()
    for k in sorted(ks,key=lambda k:(source_order[k[0]],k[1],k[2])):
        if b.fits(selected|{k}):selected.add(k)
    omitted=ks-selected;complete=not missing and not omitted and not truncated
    if not selected:status='REFERENCE_UNMAPPABLE'
    elif complete:status='REFERENCE_COMPLETE'
    else:status='REFERENCE_CAPPED' if omitted or truncated else 'REFERENCE_MAPPING_MISSING'
    return b.record(selected,status,fallback=False,reference_complete=complete,reference_outside_top64=outside,
        missing_reference_ids=sorted(set(missing+[k[0] for k in omitted]+truncated)),full_reference_body_tokens=full_tokens,
        full_reference_input_tokens=full_inputs,annotation_granularity='sentence_with_neighbours' if c['tag']=='hotpot' else 'support_paragraph_sentences')
