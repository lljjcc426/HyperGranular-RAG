from common import *
from frontend import plan_contract
from review_measure import table
import csv,collections

def main():
    out=[]
    def add(version,dataset,path,condition,metric,num,den,scope):
        out.append(dict(version=version,dataset=dataset,path=path,condition=condition,metric=metric,numerator=num,denominator=den,
            value=num/den if den else 'NA',scope=scope))
    reviews=list(csv.DictReader((HERE/'PARSE_REVIEW.csv').open(encoding='utf-8')))
    for tag in sorted({r['dataset'] for r in reviews}|{'all'}):
        rr=[r for r in reviews if tag=='all' or r['dataset']==tag]
        for k in ('schema_valid','contract_pass','direction','target_role','variable_roles','conditions','semantic_usable'):
            add('v27',tag,'A','QUESTION_ONLY',k,sum(int(r[k]) for r in rr),len(rr),'assistant_question_review; exposed D0; partly adapted')
    for path in ('B','C'):
        rr=rows(LOCAL/('v27_'+path+'.jsonl'))
        if len(rr)!=32:raise RuntimeError(('D0_INCOMPLETE',path,len(rr)))
        for tag in sorted({r['dataset'] for r in rr}|{'all'}):
            selected=[r for r in rr if tag=='all' or r['dataset']==tag]
            for cond in ('ANNOTATED_SUPPORT','GOLDFREE_LEXICAL'):
                ww=[w for r in selected for w in r['windows'] if w['condition']==cond]
                n=len(selected);facts=[f for w in ww for f in w['facts']];accepted=[f for f in facts if f['score']==1]
                for metric,num,den in [('windows_available',len(ww),n),('queries_with_located_fact',sum(bool(w['facts']) for w in ww),n),
                    ('queries_with_accepted_witness',sum(any(f['score']==1 for f in w['facts']) for w in ww),n),
                    ('accepted_fraction_of_located_facts',len(accepted),len(facts))]:
                    add('v27',tag,path,cond,metric,num,den,'REFERENCE_PLAN_DIAGNOSTIC' if path=='B' else 'PREDICTED_PLAN_CASCADE; no reference plan injection')
                add('v27',tag,path,cond,'hard_rejected_candidates',sum(len(w['detail']['rejected']) for w in ww),n,'per query; not semantic error count')
            complete=0
            for r in selected:
                ws=[engine.Window(**w['window']) for w in r['windows']];wm={w.id:w for w in ws};base={w.id:1 for w in ws};cat=[(w.title,w.source) for w in ws]
                from frontend import Fact
                fs=[Fact(**f) for w in r['windows'] for f in w['facts'] if f['score']==1]
                states=engine.bundles(r['slots'],fs,wm,base,cat) if r['slots'] else []
                complete+=int(any(len(f)==len(r['slots']) for _,f in states))
            add('v27',tag,path,'TWO_DIAGNOSTIC_WINDOWS','complete_bundle_queries',complete,len(selected),'includes one support-selected window; not deployment recall')
    val=rows(LOCAL/'adapt_validation.jsonl')
    for mode in ('off','on'):
        for kind in ('parse','extract','all'):
            rs=[r for r in val if r['mode']==mode and (kind=='all' or r['kind']==kind)]
            add('v27_nf4_adapter_'+mode,'mixed','ADAPT_VALIDATION',kind,'exact_target_match',sum(r['exact'] for r in rs),len(rs),'grouped exposed development; exact match is stricter than semantic equivalence')
    vr=list(csv.DictReader((HERE/'VERIFIER_SOURCE_REVIEW.csv').open(encoding='utf-8')))
    for version in ('v23_fp16','v24_fp16','v26_fp16','v28_nf4'):
        for tag in sorted({r['dataset'] for r in vr}|{'all'}):
            rs=[r for r in vr if tag=='all' or r['dataset']==tag]
            tp=sum(int(r['source_supported']) and int(r[version+'_accepted']) for r in rs);fp=sum(not int(r['source_supported']) and int(r[version+'_accepted']) for r in rs)
            pos=sum(int(r['source_supported']) for r in rs)
            add(version,tag,'VERIFIER','58_SOURCE_REVIEWED_CANDIDATES','true_accept_recall',tp,pos,'assistant source review of model-generated candidates; not overall extraction recall')
            add(version,tag,'VERIFIER','58_SOURCE_REVIEWED_CANDIDATES','false_accept_rate',fp,len(rs)-pos,'exposed development; versions and precision differ as stated')
    add('v1_3b','all','A','QUESTION_ONLY','schema_valid',2,32,'reused historical report; not rerun')
    add('v1_3b','all','A','QUESTION_ONLY','semantic_usable',0,32,'reused historical report; changed interface and adaptation in v2')
    table(HERE/'FRONTEND_RESULTS.csv',out)
    print('Frontend report built from complete D0 A/B/C and observed development records')

if __name__=='__main__':main()
