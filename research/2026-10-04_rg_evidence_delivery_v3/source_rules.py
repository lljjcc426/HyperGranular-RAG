"""Narrow source grammar checks for observed D0 errors, not query-ID rules.

All names/values are supplied by the proposition. No answers or corpus labels.
Rules require an exact sentence pattern; unfamiliar wording remains with the
model. These rules are shared infrastructure, not a grouping contribution.
"""
import re,copy
from delivery import norm

def decide(claim,evidence):
    h=norm(claim['subject']);t=norm(claim['object']);rel=norm(claim['relation']).lower()
    H=re.escape(h);T=re.escape(t)
    for si,s in enumerate(evidence['sentences']):
        body=norm(s['text']);sid=s['sid']
        if rel in ('has father','father','has mother','mother'):
            kin='father' if 'father' in rel else 'mother'
            if re.search(r'(?<!\w)'+T+r"['’]s "+kin+r' (?:was|is) '+H+r'(?:[.,;]|$)',body):
                return 'unresolved',[], 'explicit_reversed_kinship'
            if re.search(r'(?<!\w)'+H+r"['’]s "+kin+r' (?:was|is) '+T+r'(?:[.,;]|$)',body):
                return 'supported',[sid],'explicit_direct_kinship'
        # Exact, finite transitive verb and literal subject: all coordinated
        # objects are valid; no single-answer recovery or fuzzy entity match.
        if rel in ('directed','wrote','founded','owns'):
            m=re.search(r'(?<!\w)'+H+' '+re.escape(rel)+r' ([^.;]+)(?:[.;]|$)',body)
            if m:
                objects=[norm(x) for x in re.split(r',\s*(?:and\s+)?|\s+and\s+',m[1])]
                if t in objects:return 'supported',[sid],'explicit_coordinated_object'
        if 'first' in rel and ('participat' in rel or 'compet' in rel):
            years=re.findall(r'\b(?:18|19|20)\d{2}\b',t)
            first=re.search(r'\bfirst (?:appearance|participation) in ((?:18|19|20)\d{2})\b',body)
            anchored=body.startswith(h+' ') or (norm(evidence.get('title',''))==h and body.startswith(('It ','He ','She ')))
            if si==1 and body.startswith('It is the') and norm(evidence['sentences'][0]['text']).startswith(h+' '):anchored=True
            if len(years)==1 and first and first[1]!=years[0] and anchored:return 'refuted',[sid],'explicit_first_year_mismatch'
        if 'latitude' in rel and re.search(r'\bkm (?:long|wide)\b',t) and t in body and h in body:
            return 'unresolved',[],'length_is_not_latitude'
        if rel in ('release year','released in') and re.fullmatch(r'\d{4}',t):
            if re.search(r'(?<!\w)'+H+r' was released in '+T+r'(?:\W|$)',body):return 'supported',[sid],'explicit_release_year'
    return None

def apply(payload,constraints,owners,result):
    r=copy.deepcopy(result);r['model_verdict']=r['verdict'];r['source_rules']=[]
    d=decide(payload['CLAIM'],payload['EVIDENCE'])
    if d:r['verdict'],r['support_sids'],rule=d;r['source_rules'].append(dict(target='local',rule=rule))
    for c in constraints:
        owner=owners.get(c['id'])
        if c['scope']=='unresolved_scope' or not isinstance(owner,str):continue
        d=decide(dict(subject=owner,relation=c['predicate'],object=c['value_or_text']),payload['EVIDENCE'])
        if d:
            verdict,sids,rule=d
            for z in r['constraints']:
                if z['id']==c['id']:z.update(status={'supported':'SUPPORTED','refuted':'REFUTED','unresolved':'UNKNOWN'}[verdict],support_sids=sids)
            r['source_rules'].append(dict(target=c['id'],rule=rule))
    return r
