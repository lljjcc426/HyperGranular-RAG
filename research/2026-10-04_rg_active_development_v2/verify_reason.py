from common import *
from runtime import LM
from verification import serialize
from schemas import obj,STR

PROMPT='''Check whether the claim follows from the supplied original evidence. First state briefly the relationship that the evidence actually expresses and any missing condition. Then give verdict supported or unsupported. Paraphrases are allowed but preserve who did what to whom. Missing information is unsupported; do not use outside knowledge. A title may resolve a pronoun, not establish a relationship. Return an object with evidence_relation and verdict.'''
SCHEMA=obj(dict(evidence_relation=dict(type='string',maxLength=350),verdict=dict(type='string',enum=['supported','unsupported'])))

if __name__=='__main__':
    lm=LM()
    try:
        for r in rows(LOCAL/'v23_B.jsonl'):
            for w in r['windows']:
                for j,f in enumerate(w['facts']):
                    p=f['provenance']['payload'];g=lm.generate(serialize(p),PROMPT,160,'v26_verify',SCHEMA)
                    append(LOCAL/'v26_verify.jsonl',dict(index=r['index'],condition=w['condition'],j=j,claim=p['CLAIM'],old_score=f['score'],generation=g))
                    print(r['index'],j,g['raw'],flush=True)
    finally:lm.close('v26_verify_regression')
