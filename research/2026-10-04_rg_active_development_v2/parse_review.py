"""Question-only assistant review; never imported by natural execution."""
from common import *
from frontend import plan_contract
from review_measure import table

# (direction, target role, variable roles, condition retention, issue).
V27={
0:(1,0,0,0,'No answer variable; temporal conflict target lost'),
1:(1,1,1,1,'Usable owner-airline-headquarters chain'),
2:(0,0,0,1,'Answer is player instead of birth date; disconnected'),
3:(0,0,1,0,'Award nomination substitutes for requested performance film'),
4:(0,1,0,0,'Waterfall/work variable is assigned a birth date; year omitted'),
5:(0,0,0,1,'Founder direction reversed and answer missing'),
6:(1,0,0,0,'No requested squadron answer and invented condition phrase'),
7:(1,1,1,1,'Usable novel-author-publisher chain; Anthony spelling remains literal'),
8:(0,0,0,0,'School and director conflated; year target is not preserved'),
9:(1,1,1,1,'Event to NFC team retained; nonstandard predicate wording'),
10:(0,0,0,1,'attended by reverses role; requested stake becomes time relation'),
11:(1,1,1,0,'Current time condition now omitted'),
12:(0,0,0,0,'Invented naming relation; machinery/bell target lost'),
13:(1,0,0,1,'Acquisition condition present but requested answer variable absent'),
14:(0,0,0,0,'Requested guest artist replaced by producer-album target'),
15:(0,0,0,1,'Voicing assigned to series; extra answer role'),
16:(1,0,0,1,'Question asks when; output asks which tournament'),
17:(0,0,0,0,'New island condition attached to filming; location roles wrong'),
18:(1,1,1,1,'Album-artist-label roles retained'),
19:(1,0,0,0,'Requested release date replaced by created work'),
20:(1,1,1,1,'Place-county-largest-city chain retained'),
21:(0,0,0,0,'Invalid body variable and no grounded identity chain'),
22:(1,1,1,1,'Source question complete/compete typo retained; chain and first condition usable'),
23:(0,0,0,0,'Village/city and named-after directions reversed; end date lost'),
24:(1,1,1,1,'Birthplace-county chain retained'),
25:(1,1,1,1,'Glacier-continent-border-latitude roles retained; spelling not repaired'),
26:(1,1,1,1,'Composer has-father direction retained'),
27:(0,0,0,0,'Unidentified island retained as unresolved task; generated founder chain incorrect'),
28:(1,1,1,1,'Building-country-majority group chain retained'),
29:(1,1,1,0,'First Muslim president retained but elected condition omitted'),
30:(0,1,1,1,'Place is made establishment agent rather than school location'),
31:(0,0,0,0,'Producer made versioned object instead of OS X')}

def run():
    out=[]
    for r in rows(LOCAL/'v27_A.jsonl'):
        d,t,v,c,issue=V27[r['index']];slots,errors=plan_contract(r['question'],r['generation']['raw'])
        out.append(dict(index=r['index'],dataset=r['dataset'],schema_valid=int(r['generation']['raw'] is not None and r['generation']['ended_eos']),
            contract_pass=int(bool(slots)),direction=d,target_role=t,variable_roles=v,conditions=c,
            semantic_usable=int(all((d,t,v,c)) and bool(slots)),issue=issue,
            contract_recheck='final lexical provenance validator; original model output unchanged'))
    table(HERE/'PARSE_REVIEW.csv',out)
    print('usable',sum(r['semantic_usable'] for r in out),'of',len(out),'contract',sum(r['contract_pass'] for r in out))

if __name__=='__main__':run()
