"""Assistant source review, not blind expert labels or deployment input."""
from common import *
import csv

SUPPORTED={(1,'GOLDFREE_LEXICAL',0),(2,'ANNOTATED_SUPPORT',0),(2,'GOLDFREE_LEXICAL',0),
    (4,'ANNOTATED_SUPPORT',0),(16,'ANNOTATED_SUPPORT',0),(18,'ANNOTATED_SUPPORT',0),
    (19,'ANNOTATED_SUPPORT',0),(19,'GOLDFREE_LEXICAL',1),(20,'GOLDFREE_LEXICAL',0),
    (22,'ANNOTATED_SUPPORT',0),(23,'ANNOTATED_SUPPORT',0),(26,'ANNOTATED_SUPPORT',0),
    (28,'ANNOTATED_SUPPORT',0),(30,'ANNOTATED_SUPPORT',0)}

CONDITION={(0,'ANNOTATED_SUPPORT',0),(1,'ANNOTATED_SUPPORT',0),(5,'ANNOTATED_SUPPORT',0),
    (6,'GOLDFREE_LEXICAL',0),(11,'GOLDFREE_LEXICAL',0),(22,'GOLDFREE_LEXICAL',0)}
DIRECTION={(8,'GOLDFREE_LEXICAL',0)}
BINDING={(0,'ANNOTATED_SUPPORT',1),(1,'ANNOTATED_SUPPORT',1),(6,'ANNOTATED_SUPPORT',0),(6,'GOLDFREE_LEXICAL',1),
    (7,'GOLDFREE_LEXICAL',0),(8,'ANNOTATED_SUPPORT',0),(8,'ANNOTATED_SUPPORT',1),(8,'GOLDFREE_LEXICAL',1),(8,'GOLDFREE_LEXICAL',2),
    (9,'ANNOTATED_SUPPORT',0),(9,'GOLDFREE_LEXICAL',0),(16,'ANNOTATED_SUPPORT',1),(16,'GOLDFREE_LEXICAL',0),
    (18,'ANNOTATED_SUPPORT',1),(18,'GOLDFREE_LEXICAL',0),(19,'GOLDFREE_LEXICAL',0),
    (21,'ANNOTATED_SUPPORT',0),(21,'GOLDFREE_LEXICAL',0),(21,'GOLDFREE_LEXICAL',1),
    (23,'ANNOTATED_SUPPORT',1),(23,'GOLDFREE_LEXICAL',1),(24,'ANNOTATED_SUPPORT',0),(25,'ANNOTATED_SUPPORT',0),
    (28,'ANNOTATED_SUPPORT',1),(28,'GOLDFREE_LEXICAL',0),(29,'ANNOTATED_SUPPORT',0),(30,'ANNOTATED_SUPPORT',1),(30,'GOLDFREE_LEXICAL',0)}

def table(path,records):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)

def verifier_review():
    variants={}
    for name,file in [('v24','v24_verify.jsonl'),('v26','v26_verify.jsonl'),('v28_nf4','v28_object.jsonl')]:
        variants[name]={(r['index'],r['condition'],r['j']):r for r in rows(LOCAL/file)}
    out=[]
    for r in rows(LOCAL/'v23_B.jsonl'):
        for w in r['windows']:
            for j,f in enumerate(w['facts']):
                key=(r['index'],w['condition'],j);item=dict(index=r['index'],dataset=r['dataset'],condition=w['condition'],fact_index=j,
                    relation=next(s['relation'] for s in r['slots'] if s['id']==f['slot']),source_supported=int(key in SUPPORTED),
                    primary_review_category=('SUPPORTED' if key in SUPPORTED else 'CONDITION_NOT_SUPPORTED' if key in CONDITION else
                        'WRONG_DIRECTION' if key in DIRECTION else 'WRONG_BINDING_OR_ROLE' if key in BINDING else 'INSUFFICIENT_RELATION_EVIDENCE'),
                    v23_fp16_accepted=int(f['score']==1),
                    v24_fp16_accepted=int(variants['v24'][key]['score']==1),
                    v26_fp16_accepted=int((variants['v26'][key]['generation']['raw'] or {}).get('verdict')=='supported'),
                    v28_nf4_accepted=int(variants['v28_nf4'][key]['accepted']))
                out.append(item)
    table(HERE/'VERIFIER_SOURCE_REVIEW.csv',out)
    for name in ('v23_fp16','v24_fp16','v26_fp16','v28_nf4'):
        tp=sum(r['source_supported'] and r[name+'_accepted'] for r in out);fp=sum(not r['source_supported'] and r[name+'_accepted'] for r in out)
        print(name,'n',len(out),'supported',sum(r['source_supported'] for r in out),'TP',tp,'FP',fp,'FN',sum(r['source_supported'] for r in out)-tp)

if __name__=='__main__':verifier_review()
