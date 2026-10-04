from common import *
from frontend import plan_contract
from schemas import PLAN,PARSE_V22
from runtime import LM

SIMPLE='''Decompose a question into linked factual relations, without answering it.
Return a JSON object with status and relations. Each relation contains head, relation, tail, qualifiers. Use unknown variables ?v1, ?v2, ?v3 and the final answer variable ?answer. Copy literal anchors from the question. Do NOT use a generic description as an entity name. Unknown intermediate entities are expected, NOT ambiguity. Use status ok for ordinary multihop questions. Use unsupported for comparisons or negation. Use ambiguous only if there is no named anchor and no identifying description. qualifiers are exact phrases from the question. Preserve the asked answer role and all defining conditions.
Examples:
Question: Where is the publisher of Cloud Song based?
{"status":"ok","relations":[{"head":"Cloud Song","relation":"published by","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"based in","tail":"?answer","qualifiers":[]}]}
Question: Who was the publisher of the graphic novel by Mira Reed on which a spy thriller film was adapted?
{"status":"ok","relations":[{"head":"?v1","relation":"written by","tail":"Mira Reed","qualifiers":["graphic novel","a spy thriller film was adapted"]},{"head":"?v1","relation":"published by","tail":"?answer","qualifiers":[]}]}
Question: What race is the majority of the population in the country Elm Tower is found?
{"status":"ok","relations":[{"head":"Elm Tower","relation":"located in country","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"has majority race","tail":"?answer","qualifiers":[]}]}
Question: Who was the father of Silver Lake's composer?
{"status":"ok","relations":[{"head":"Silver Lake","relation":"composed by","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"has father","tail":"?answer","qualifiers":[]}]}
Question: What is the largest city in the county where Foxford is found?
{"status":"ok","relations":[{"head":"Foxford","relation":"in county","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"has largest city","tail":"?answer","qualifiers":[]}]}
Return only the requested object.'''

if __name__=='__main__':
    lm=LM()
    try:
        ps=read(V1/'local/d0_packets.json')
        for i in [1,7,18,24,26,27,28,5]:
            q=ps[i]['question']
            for mode in ('unconstrained','v24'):
                r=lm.generate(q,PARSE_V22 if mode=='unconstrained' else SIMPLE,512,'parse_'+mode,None if mode=='unconstrained' else PLAN)
                append(LOCAL/'parse_develop.jsonl',dict(index=i,mode=mode,question=q,**r));print(i,mode,r['text'],flush=True)
    finally:lm.close('v24_parse_diagnostic')
