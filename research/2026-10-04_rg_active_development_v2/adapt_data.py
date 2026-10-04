"""Assistant-reviewed D0 and invented minimal pairs, never D1/Gold answers."""
from common import *
from references import plans,R
from frontend import packet,plan_contract
from schemas import LOCATE_PROMPT
from parse_develop import SIMPLE

def build():
    out=[]
    def add(group,kind,user,target,source):
        split='validation' if group in ('family2','family6','d0_0','d0_8','d0_12','d0_16','d0_24') else 'train'
        out.append(dict(group=group,split=split,kind=kind,system=SIMPLE if kind=='parse' else LOCATE_PROMPT,user=user,target=target,source=source))
    for family in range(8):
        for i in range(4):
            work=f'Silver Lake {i}';person=f'Mira Lane {i}';place=f'Foxford {i}'
            if family==0:q=f'Who was the father of {work}\'s composer?';rs=[R(work,'composed by','?v1'),R('?v1','has father','?answer')];body=f'{person} composed {work}.';slot=rs[0];h=work;t=person
            elif family==1:q=f'Where was the writer of {work} born?';rs=[R(work,'written by','?v1'),R('?v1','born in','?answer')];body=f'{person} wrote {work}.';slot=rs[0];h=work;t=person
            elif family==2:q=f'Who was the publisher of the graphic novel by {person} adapted into a film?';rs=[R('?v1','written by',person,'graphic novel','adapted into a film'),R('?v1','published by','?answer')];body=f'The film adapts {work}, a graphic novel published by Elm Press.';slot=rs[1];h=work;t='Elm Press'
            elif family==3:q=f'{person} is 100% owner of a cargo airline headquartered where?';rs=[R('?v1','owned by',person,'100%','cargo airline'),R('?v1','headquartered in','?answer')];body=f'Cloud Air is a cargo airline headquartered in {place}.';slot=rs[1];h='Cloud Air';t=place
            elif family==4:q=f'What was the record label of the artist who recorded {work}?';rs=[R(work,'recorded by','?v1'),R('?v1','has record label','?answer')];body=f'{work} is an album by {person}.';slot=rs[0];h=work;t=person
            elif family==5:q=f'What is the largest city in the county where {place} is found?';rs=[R(place,'in county','?v1'),R('?v1','has largest city','?answer')];body=f'{place} is in Willow County.';slot=rs[0];h=place;t='Willow County'
            elif family==6:q=f'What day did the founder of {work}, an American heir and hotelier, die?';rs=[R(work,'founded by','?v1','American heir and hotelier'),R('?v1','died on','?answer')];body=f'{person} died on 4 May 1980.';slot=rs[1];h=person;t='4 May 1980'
            else:q=f'What race is the majority of the population in the country {work} is found?';rs=[R(work,'located in country','?v1'),R('?v1','has majority race','?answer')];body=f'{work} is a building in the country of Ardan.';slot=rs[0];h=work;t='Ardan'
            target=dict(status='ok',relations=rs)
            assert not plan_contract(q,target)[1]
            add('family'+str(family),'parse',q,target,'invented_template_'+str(family)+'_variant_'+str(i))
            # Two positives and two unrelated-evidence negatives per family.
            if i>=2:body=f'{person} enjoys walking.'
            user=json.dumps(dict(relation=slot,window=dict(title='Invented source',sentences=[dict(sid='s0',text=body)])),ensure_ascii=False)
            target=dict(facts=[] if i>=2 else [dict(head=dict(sid='s0',text=h,identity=''),tail=dict(sid='s0',text=t,identity=''),support_sids=['s0'])])
            if i<2:assert h in body and t in body
            add('family'+str(family),'extract',user,target,'invented_template_'+str(family)+'_variant_'+str(i))
    packets=read(V1/'local/d0_packets.json')
    families={1:3,5:6,7:2,18:4,20:5,26:0,28:7}
    def group(i):return 'family'+str(families[i]) if i in families else 'd0_'+str(i)
    for i in [1,2,3,5,7,8,9,10,11,12,14,16,18,20,22,23,24,26,28,29,30]:
        q=packets[i]['question'];rs=[{k:s[k] for k in ('head','relation','tail','qualifiers')} for s in plans(i)]
        target=dict(status='ok',relations=rs)
        if plan_contract(q,target)[1]:raise ValueError((i,plan_contract(q,target)[1]))
        add(group(i),'parse',q,target,'D0_question_only_'+str(i))
    byindex={r['index']:r for r in rows(LOCAL/'v23_B.jsonl')}
    # Each target is reviewed against the actual displayed sentence(s), not the answer key.
    specs=[(1,1,1,'North Star Air','Thunder Bay, Ontario'),(2,0,1,'Christopher Paul Mullin','July 30, 1963'),
        (4,0,1,'Frank Lloyd Wright','June 8, 1867'),(7,1,1,'The Coldest City','Oni Press'),
        (8,1,1,'Cleveland State University','Michael J. Thomas'),(9,0,1,'Super Bowl XVII','Washington Redskins'),
        (16,0,0,'Timken High School','Ohio'),(18,0,0,'Roses in the Snow','Emmylou Harris'),
        (19,0,0,'Crawl','Chris Brown'),(20,1,1,'Sierra Suroeste','Jerez de los Caballeros'),
        (23,0,0,'Badsworth','City of Wakefield'),(28,0,0,'Comcentre','Singapore'),(30,0,0,'Llanddeusant','Anglesey')]
    for i,wi,si,h,t in specs:
        r=byindex[i];w=engine.Window(**r['windows'][wi]['window']);slot={k:r['slots'][si][k] for k in ('head','relation','tail','qualifiers')}
        def mention(name):
            js=[j for j,s in enumerate(w.sentences) if name in s[1]]
            if not js:raise ValueError((i,name))
            return dict(sid='s'+str(js[0]),text=name,identity='')
        mh,mt=mention(h),mention(t)
        support=sorted({mh['sid'],mt['sid']})
        # City/county anaphora needs both original sentences, and Comcentre's
        # second sentence explicitly identifies the same place as a city-state.
        if i in (20,28):support=['s'+str(j) for j in range(len(w.sentences))]
        target=dict(facts=[dict(head=mh,tail=mt,support_sids=support)])
        add(group(i),'extract',json.dumps(dict(relation=slot,window=packet(w)),ensure_ascii=False),target,'D0_displayed_source_'+str(i)+'_'+str(wi))
    assert not ({r['group'] for r in out if r['split']=='train'} & {r['group'] for r in out if r['split']=='validation'})
    save(LOCAL/'adapt_data.json',out)
    save(HERE/'ADAPT_DATA_MANIFEST.json',dict(records=len(out),train=sum(r['split']=='train' for r in out),validation=sum(r['split']=='validation' for r in out),
        review='Assistant-reviewed question/source-derived labels; not expert or independent validation.',
        groups={g:next(r['split'] for r in out if r['group']==g) for g in sorted({r['group'] for r in out})},
        sources=[r['source'] for r in out],no_d1=True,no_gold_answers=True))
    print(len(out),sum(r['split']=='train' for r in out))

if __name__=='__main__':build()
