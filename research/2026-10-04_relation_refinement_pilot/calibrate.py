"""D0 only. No D1 labels or model outcomes are read here."""
from io_utils import *
from models import LM,PARSE,EXTRACT,json_object
from core import parse_contract,witnessed,render
from windows import make_windows
from dataclasses import asdict

def prepare():
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    cases=read(LOCAL/'inputs.json');gold={}
    for tag,name in [('hotpot','stage4e_e2e_official_train1000_v1_gold_targets.jsonl'),('musique','stage4f_xdr_musique_train3000_v1_gold_targets.jsonl')]:
        wanted={c['query_id'] for c in cases if c['tag']==tag and c['role'].startswith('D0')}
        # Only previously opened E/F labels; no Stage6 path exists in this module.
        for r in rows(DATA/'processed'/name):
            if r['query_id'] in wanted:gold[r['query_id']]=r
    packets=[]
    for c in cases:
        if not c['role'].startswith('D0'):continue
        ws=make_windows(c['units'],tok);g=gold[c['query_id']]
        if c['tag']=='hotpot':support={z['unit_id'] for z in g['supporting_facts']}
        else:support={u['unit_id'] for u in c['units'] if u['paragraph_index'] in g['supporting_paragraph_indices']}
        anchors=[w for w in ws if w.id in support]
        # Calibration packets show first support window for controlled proposition annotation.
        packets.append(dict(**{k:c[k] for k in ('query_id','tag','role','stratum')},question=c['query']['question'],
            gold=g,windows=[asdict(w) for w in ws],support_ids=sorted(support),annotation_window=asdict(anchors[0])))
    save(LOCAL/'d0_packets.json',packets)
    for j,p in enumerate(packets):print(j,p['role'],p['tag'],p['question'],'\n',p['annotation_window']['text'],flush=True)

def run(phase):
    packets=read(LOCAL/'d0_packets.json');lm=LM()
    try:
        if phase=='parse':
            for j,p in enumerate(packets):
                r=lm.generate(p['question'],PARSE,224,'D0_parse');raw=json_object(r['text'])
                append(LOCAL/'d0_parses.jsonl',dict(index=j,query_id=p['query_id'],role=p['role'],raw=raw,slots=parse_contract(p['question'],raw),**r))
        elif phase=='extract':
            parses={z['index']:z for z in rows(LOCAL/'d0_parses.jsonl')}
            from core import Window
            for j,p in enumerate(packets):
                slots=parses[j]['slots'];w=Window(**p['annotation_window'])
                if not slots:
                    append(LOCAL/'d0_extractions.jsonl',dict(index=j,status='PARSE_FAIL',facts=[]));continue
                r=lm.generate(json.dumps(dict(question=p['question'],slots=slots,body=w.text)),EXTRACT,320,'D0_extract')
                raw=json_object(r['text']);facts=[];catalog=[(v['title'],v['source']) for v in p['windows']]
                for f in raw.get('facts',[])[:3]:
                    v=witnessed(f,w,slots,catalog,.5)
                    if v is None:continue
                    s=next(s for s in slots if s['id']==v.slot)
                    claim=v.head+' -- '+s['relation']+' --> '+v.tail+'; conditions: '+v.conditions
                    b=lm.binary(w.text,claim,'D0_extracted_fact')
                    facts.append(dict(raw=f,score=b['score']))
                append(LOCAL/'d0_extractions.jsonl',dict(index=j,status='EXTRACTED',facts=facts,**r))
        elif phase=='verify':
            for a in read(LOCAL/'annotations.json'):
                p=packets[a['index']];r=lm.binary(p['annotation_window']['text'],a['claim'],'D0_annotation')
                append(LOCAL/'d0_verification.jsonl',dict(**a,role=p['role'],**r))
        elif phase=='reader':
            sys.path.insert(0,str(OLD));from score import scorers,answer_score
            scor=scorers();from core import Window
            for j,p in enumerate(packets):
                ws=[Window(**w) for w in p['windows'] if w['id'] in p['support_ids']]
                for condition in ('SUPPLIED_SUPPORT','NO_RETRIEVAL'):
                    context=ws if condition=='SUPPLIED_SUPPORT' else []
                    r=render(p['question'],context,[],1,lm.ids,1024)
                    out=lm.generate(r['prompt'],'You are a careful evidence assistant.',32,'D0_reader_'+condition)
                    em,f1=answer_score(p['tag'],out['text'],p['gold'],scor)
                    append(LOCAL/'d0_reader.jsonl',dict(index=j,role=p['role'],tag=p['tag'],condition=condition,
                         em=em,f1=f1,**out,visible_ids=r['visible_ids']))
        else:raise ValueError(phase)
    finally:lm.close('D0_'+phase)
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    else:run(sys.argv[1])
