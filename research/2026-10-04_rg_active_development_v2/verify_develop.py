from common import *
from runtime import LM
from schemas import VERIFY_PROMPT

def plain(payload):
    c=payload['CLAIM'];e=payload['EVIDENCE'];loc=payload['LOCATIONS']
    return ('Claim: "'+c['subject']+'" '+c['relation']+' "'+c['object']+'".\nRequired conditions: '+json.dumps(c['qualifiers'],ensure_ascii=False)+
        '\nSource title: '+e['title']+'\nOriginal evidence:\n'+'\n'.join(s['sid']+': '+s['text'] for s in e['sentences'])+
        '\nMention identities: '+json.dumps({k:dict(mention=loc[k]['text'],identity=loc[k]['identity'],basis=loc[k]['identity_basis']) for k in ('head','tail')},ensure_ascii=False)+
        '\nIs this exact claim, direction and ALL required conditions supported? Answer yes or no.')

if __name__=='__main__':
    lm=LM()
    try:
        for r in rows(LOCAL/'v22_B.jsonl'):
            for w in r['windows']:
                for j,f in enumerate(w['facts']):
                    p=f['provenance']['payload'];prompt=plain(p)
                    out=lm.generate(prompt,VERIFY_PROMPT,8,'v23_verify_free')
                    append(LOCAL/'v23_verify.jsonl',dict(index=r['index'],condition=w['condition'],j=j,claim=p['CLAIM'],old_score=f['score'],text=out['text'],generation=out))
                    print(r['index'],w['condition'],j,out['text'],flush=True)
    finally:lm.close('v23_verify_diagnostic')
