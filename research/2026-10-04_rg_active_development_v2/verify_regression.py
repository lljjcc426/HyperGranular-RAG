from common import *
from runtime import LM

if __name__=='__main__':
    lm=LM()
    try:
        for r in rows(LOCAL/'v23_B.jsonl'):
            for w in r['windows']:
                for j,f in enumerate(w['facts']):
                    p=f['provenance']['payload'];v=lm.verify(p,'v24_verify')
                    append(LOCAL/'v24_verify.jsonl',dict(index=r['index'],condition=w['condition'],j=j,claim=p['CLAIM'],old_score=f['score'],**v))
                    print(r['index'],j,v['label'],flush=True)
    finally:lm.close('v24_verify_regression')
