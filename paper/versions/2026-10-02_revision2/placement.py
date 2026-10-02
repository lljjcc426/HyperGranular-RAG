"""Reconstruct historical Stage4I prompts without a model, retrieval or Gold."""
import collections
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer
from rescore import REPO, OUT, load, rows, save, table, IDENTITIES, H, M

P='BGE_HGRAG_PROTECTED_TOP20'
U='BGE_HGRAG_UNPROTECTED_TOP20'

def membership(d,ins,k):
    assert len(d)==k and len(set(d))==k and len(ins)==len(set(ins))<=4
    assert not set(d)&set(ins)
    assert k==20 or not ins
    p=(d[:10]+ins+d[10:])[:k];u=(ins+d)[:k]
    assert set(p)==set(u)==set(ins+d[:k-len(ins)])
    return p,u

def main():
    c=load(REPO/'configs/stage4i_sdc_official.json');par=load(REPO/'configs/stage4h_cbe_official.json')
    blind=rows(c['paths']['blind'],c['inputs']['blind'])
    ranks=rows(c['paths']['rankings'],c['inputs']['rankings'])
    prompt=rows(c['paths']['prompt_audit_main'],c['inputs']['prompt_audit_main'])
    bm={r['query_id']:r for r in blind};pm={(r['query_id'],r['method']):r for r in prompt}
    tokenizer=AutoTokenizer.from_pretrained(par['paths']['generator_snapshot'],local_files_only=True)
    outputs=[];counters={d:collections.Counter() for d in (H,M)}
    for r in ranks:
        q=r['query_id'];b=bm[q];counts=counters[r['dataset']]
        units={a['unit_id']:a for a in b['candidate_units']};k=min(20,len(units))
        assert r['effective_k']==k
        d=r['methods']['BGE_TOP20'];ins=r['full_inserted_unit_ids']
        p,u=membership(d,ins,k);assert p==r['methods'][P] and u==r['methods'][U]
        visible=[];hashes=[];tokens=[]
        for method,rank in ((P,p),(U,u)):
            a=pm[q,method];assert a['evidence_unit_ids']==rank[:len(a['evidence_unit_ids'])]
            lines=[f"[{i}] {units[x]['title']}: {units[x]['text']}" for i,x in enumerate(rank,1)]
            def messages(lines):
                return [{'role':'system','content':c['generation']['system_message']},{'role':'user','content':'Evidence:\n'+'\n'.join(lines)+'\n\nQuestion: '+b['question']+'\nFinal answer:'}]
            full=tokenizer.apply_chat_template(messages(lines),tokenize=False,add_generation_prompt=True)
            encoded=tokenizer.apply_chat_template(messages(lines),tokenize=True,add_generation_prompt=True)
            n=len(encoded['input_ids'] if hasattr(encoded,'keys') else encoded)
            if n<=4096:
                assert a['evidence_unit_ids']==rank and a['rank1_truncated'] is False
            else:
                # Reconstruct whole-unit prefix. Rank-1 partial needs a separate explicit audit.
                assert not a['rank1_truncated'], 'Partial rank1 content requires explicit token-prefix reconstruction'
                lines=lines[:len(a['evidence_unit_ids'])]
                full=tokenizer.apply_chat_template(messages(lines),tokenize=False,add_generation_prompt=True)
                encoded=tokenizer.apply_chat_template(messages(lines),tokenize=True,add_generation_prompt=True)
                n=len(encoded['input_ids'] if hasattr(encoded,'keys') else encoded)
                assert n<=4096
            sha=hashlib.sha256(full.encode()).hexdigest().upper()
            assert sha==a['prompt_sha256'] and n==a['input_token_count'], (q,method,'serialized prompt mismatch')
            contents=[(x,units[x]['title'],units[x]['text']) for x in a['evidence_unit_ids']]
            visible.append(collections.Counter(contents));hashes.append(sha);tokens.append(n)
        same=visible[0]==visible[1];assert same or len(pm[q,P]['evidence_unit_ids'])<k or len(pm[q,U]['evidence_unit_ids'])<k
        counts['queries']+=1;counts['membership_identical']+=1;counts['visible_content_identical']+=int(same)
        counts['serialized_prompts_verified']+=2;counts['with_insertions']+=int(bool(ins));counts['under20']+=int(k<20)
        counts['prompt_order_changed']+=int(hashes[0]!=hashes[1]);counts['tokens_differ']+=int(tokens[0]!=tokens[1])
        digest=lambda content:hashlib.sha256(json.dumps(sorted(content.elements()),ensure_ascii=False,separators=(',',':')).encode()).hexdigest().upper()
        outputs.append(dict(query_id=q,dataset=r['dataset'],effective_k=k,insertions=len(ins),membership_equal=True,visible_content_equal=same,protected_visible_digest=digest(visible[0]),unprotected_visible_digest=digest(visible[1]),protected_prompt_verified=True,unprotected_prompt_verified=True,protected_tokens=tokens[0],unprotected_tokens=tokens[1],protected_partial=pm[q,P]['rank1_truncated'],unprotected_partial=pm[q,U]['rank1_truncated'],protected_dropped=k-len(pm[q,P]['evidence_unit_ids']),unprotected_dropped=k-len(pm[q,U]['evidence_unit_ids'])))
    table('PLACEMENT_QUERY_CHECKS.csv',outputs)
    save('PLACEMENT_SUMMARY.json',{d:dict(v) for d,v in counters.items()})
    save('PLACEMENT_INPUT_IDENTITIES.json',IDENTITIES)
    print(json.dumps({d:dict(v) for d,v in counters.items()},indent=2))

if __name__=='__main__':main()
