"""Append-only v4 scoring/description with the existing canonical functions."""
from common import *
from protocols import PROTOCOLS
import statistics,itertools
score=load_module('rg_v4_canonical_dependency',HERE.parent/'2026-10-03_evidence_delivery_repair/score.py')
def gold():
    return {tag:{r['query_id']:r for r in rows(DATA/'processed'/name)} for tag,name in [('hotpot','stage4e_e2e_official_train1000_v1_gold_targets.jsonl'),('musique','stage4f_xdr_musique_train3000_v1_gold_targets.jsonl')]}
def mean(rs,k):return statistics.mean(r[k] for r in rs) if rs else ''
def d0():
    gg=gold();modules=score.scorers();out=[]
    for r in rows(LOCAL/'D0.jsonl'):
        em,f1=score.answer_score(r['tag'],r['parsed_answer'],gg[r['tag']][r['query_id']],modules)
        out.append(dict(query_id=r['query_id'],dataset=r['tag'],protocol=r['protocol'],em=em,f1=f1,
            parse_status=r['parse_status'],unknown=r['unknown'],ended_eos=r['generation']['ended_eos'],hit_output_limit=r['hit_output_limit'],output_tokens=r['generation']['output_tokens'],seconds=r['generation']['seconds']))
    table(HERE/'D0_RESULTS.csv',out)
    for p in PROTOCOLS:
        rs=[r for r in out if r['protocol']==p];print(p,dict(n=len(rs),em=mean(rs,'em'),f1=mean(rs,'f1'),failure=sum(r['parse_status']=='PROTOCOL_FAILURE' for r in rs),limit=sum(r['hit_output_limit'] for r in rs)))
def factorial():
    gg=gold();modules=score.scorers();contexts=read(LOCAL/'contexts.json');predictions=[]
    for mode in ('core','extra'):
        if (LOCAL/(mode+'.jsonl')).exists():predictions.extend(rows(LOCAL/(mode+'.jsonl')))
    lookup={(r['query_id'],r['context'],r['protocol']):r for r in predictions}
    historical={}
    for c in selected():
        old=read(V3/'local/natural'/c['sampling_hash']/'answers_16.json')
        for r in old:
            gs=([r['parse']['generation']] if r['parse'] else [])+([r['scope']] if r['scope'] else [])
            for t in r['result']['trace']:
                gs.append(t['detail']['generation'])
                for v in t['detail']['verification']:gs.extend(v.get('generations',[v['generation']]))
            historical[(c['query_id'],r['method'])]=dict(seconds=sum(g['seconds'] for g in gs),calls=len(gs),
                input_tokens=sum(g['input_tokens'] for g in gs),output_tokens=sum(g['output_tokens'] for g in gs),
                conditional_seconds=r['conditional_seconds'],index_seconds=r['index_seconds'],search_transaction_seconds=r['result']['seconds'])
    qs=[]
    for c in contexts:
        for p in PROTOCOLS:
            r=lookup.get((c['query_id'],c['context'],p));g=r['generation'] if r else None
            em,f1=score.answer_score(c['tag'],r['parsed_answer'],gg[c['tag']][c['query_id']],modules) if r else ('','')
            letter=c['context'][-1];method={'G':'GB-feedback-v3','F':'Flat-binding-v3','K':'KM-feedback-v3'}.get(letter,'Dense-window-v3')
            h=historical[(c['query_id'],method)]
            qs.append(dict(query_id=c['query_id'],dataset=c['tag'],context=c['context'],protocol=p,status='COMPLETE' if r else 'NOT_RUN',
                em=em,f1=f1,parse_status=r['parse_status'] if r else '',nonempty=r['nonempty'] if r else '',unknown=r['unknown'] if r else '',
                ended_eos=g['ended_eos'] if g else '',hit_output_limit=r['hit_output_limit'] if r else '',
                input_tokens=g['input_tokens'] if g else c['input_tokens'][p],output_tokens=g['output_tokens'] if g else '',
                reader_seconds=g['seconds'] if g else '',cache_hit=r['cache_hit'] if r else '',origin=r['origin'] if r else '',
                body_tokens=c['body_tokens'],fallback=c['fallback'],package_available=c['status']=='AUTOMATIC_PACKAGE',
                reference_complete=c.get('reference_complete',''),source_change=c['source_change'],
                historical_search_model_seconds=h['seconds'],historical_search_calls=h['calls'],historical_search_input_tokens=h['input_tokens'],
                historical_search_output_tokens=h['output_tokens'],historical_conditional_seconds=h['conditional_seconds'],historical_index_seconds=h['index_seconds'],
                reference_annotation_cost='NOT_MEASURED' if c['context']=='R' else 'NOT_APPLICABLE',
                input_identity=r['key'] if r else '',data_role='EXPOSED_DEVELOPMENT'))
    table(HERE/'FACTORIAL_RESULTS.csv',qs)
    summary=[]
    for ctx,p in itertools.product(('D','A_G','L_G','R','A_F','L_F','A_K','L_K'),PROTOCOLS):
        for tag in ('hotpot','musique','EQUAL_WEIGHT_16'):
            rs=[r for r in qs if r['context']==ctx and r['protocol']==p and (tag=='EQUAL_WEIGHT_16' or r['dataset']==tag)]
            done=[r for r in rs if r['status']=='COMPLETE']
            summary.append(dict(context=ctx,protocol=p,dataset=tag,n_expected=len(rs),n_complete=len(done),
                em=mean(done,'em'),f1=mean(done,'f1'),format_failures=sum(r['parse_status']=='PROTOCOL_FAILURE' for r in done),
                unknown=sum(r['unknown'] for r in done),hit_output_limit=sum(r['hit_output_limit'] for r in done),ended_eos=sum(r['ended_eos'] for r in done),
                mean_input_tokens=mean(done,'input_tokens'),mean_output_tokens=mean(done,'output_tokens'),logical_reader_seconds=sum(r['reader_seconds'] for r in done),
                historical_search_model_seconds=sum(r['historical_search_model_seconds'] for r in done),
                historical_search_calls=sum(r['historical_search_calls'] for r in done),package_available=sum(r['package_available'] for r in done),
                reference_complete=sum(r['reference_complete'] is True for r in done)))
    table(HERE/'SUMMARY.csv',summary)
    bykey={(r['query_id'],r['context'],r['protocol']):r for r in qs}
    cdict={(c['query_id'],c['context']):c for c in contexts};sample=selected();contrasts=[]
    comparisons=[]
    for p in PROTOCOLS:
        for a,b in [('A_G','D'),('A_G','L_G'),('R','D'),('A_G','A_F'),('A_G','A_K'),('A_F','L_F'),('A_K','L_K')]:comparisons.append((a,p,b,p))
    for ctx in ('D','A_G','L_G','R','A_F','L_F','A_K','L_K'):
        comparisons.extend([(ctx,'P1',ctx,'P0'),(ctx,'P2',ctx,'P1')])
    for a,pa,b,pb in comparisons:
        subsets=['ALL16']+(['A_G_PACKAGE_AVAILABLE'] if 'A_G' in (a,b) else [])+(['REFERENCE_COMPLETE'] if 'R' in (a,b) else [])
        for subset in subsets:
            for tag in ('hotpot','musique','EQUAL_WEIGHT_16'):
                cc=[c for c in sample if (tag=='EQUAL_WEIGHT_16' or c['tag']==tag) and
                    (subset!='A_G_PACKAGE_AVAILABLE' or cdict[c['query_id'],'A_G']['status']=='AUTOMATIC_PACKAGE') and
                    (subset!='REFERENCE_COMPLETE' or cdict[c['query_id'],'R'].get('reference_complete',False))]
                pairs=[(bykey[c['query_id'],a,pa],bykey[c['query_id'],b,pb]) for c in cc]
                done=[(x,y) for x,y in pairs if x['status']==y['status']=='COMPLETE']
                for metric in ('em','f1'):
                    ds=[x[metric]-y[metric] for x,y in done]
                    # Equal dataset weight even for unequal post-hoc subset counts.
                    per=[statistics.mean(x[metric]-y[metric] for x,y in done if x['dataset']==t) for t in ('hotpot','musique') if any(x['dataset']==t for x,y in done)]
                    contrasts.append(dict(comparison=f'{a}/{pa} minus {b}/{pb}',subset=subset,dataset=tag,metric=metric,n_expected=len(pairs),n_complete=len(done),
                        delta=statistics.mean(per) if tag=='EQUAL_WEIGHT_16' and len(per)==2 else statistics.mean(ds) if ds and tag!='EQUAL_WEIGHT_16' else '',
                        gain=sum(d>1e-12 for d in ds),same=sum(abs(d)<=1e-12 for d in ds),harm=sum(d< -1e-12 for d in ds)))
    for tag in ('hotpot','musique','EQUAL_WEIGHT_16'):
        for metric in ('em','f1'):
            ds=[]
            for c in sample:
                if tag!='EQUAL_WEIGHT_16' and c['tag']!=tag:continue
                rr=[bykey[c['query_id'],ctx,p] for ctx,p in [('A_G','P2'),('D','P2'),('A_G','P1'),('D','P1')]]
                if all(r['status']=='COMPLETE' for r in rr):ds.append(rr[0][metric]-rr[1][metric]-rr[2][metric]+rr[3][metric])
            contrasts.append(dict(comparison='(A_G-D)/P2 minus (A_G-D)/P1',subset='ALL16',dataset=tag,metric=metric,n_expected=16 if tag=='EQUAL_WEIGHT_16' else 8,n_complete=len(ds),
                delta=statistics.mean(ds) if ds else '',gain=sum(d>1e-12 for d in ds),same=sum(abs(d)<=1e-12 for d in ds),harm=sum(d< -1e-12 for d in ds)))
    table(HERE/'CONTRASTS.csv',contrasts)
    print('logical',len(qs),'complete',len(predictions),'physical',len(rows(LOCAL/'calls.jsonl')))
    for r in summary:
        if r['dataset']=='EQUAL_WEIGHT_16':print(r['context'],r['protocol'],r['em'],r['f1'])
if __name__=='__main__':{'D0':d0,'factorial':factorial}[sys.argv[1]]()
