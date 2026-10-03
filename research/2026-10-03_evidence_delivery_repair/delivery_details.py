"""Complete title/body/visible facet accounting, without embedding or generation."""
from common import *
from repair import old
from collections import Counter

def main():
    cpu=time.process_time();wall=time.perf_counter();summary={}
    with (LOCAL/'delivery_facets.jsonl').open('x',encoding='utf-8') as out:
        for tag in CONFIGS:
            cfg=config(tag);blind=rows(cfg['paths']['blind']);units,queries=(e if tag=='hotpot' else f).build_units_queries(blind)
            umap={u['unit_id']:u for u in units};rank={r['query_id']:r for r in rows(cfg['paths']['rankings'])}
            audits={(r['query_id'],r['method']):r for r in rows(cfg['paths']['prompt_audit_main'])}
            counts=Counter()
            for q in queries:
                r=rank[q['query_id']];qt=old.content_tokens(q['question']);a=audits[q['query_id'],'STATIC_Q25_TOP20']
                row={'query_id':q['query_id'],'tag':tag,'sets':{}}
                for name,ids in [('prefix',r['dense_top20_unit_ids'][:10]),('dense',r['dense_top20_unit_ids']),
                                 ('inserted',r['q25_inserted_unit_ids']),('final',r['static_q25_top20_unit_ids']),('visible',a['evidence_unit_ids'])]:
                    title=set().union(*(old.content_tokens(umap[i]['title']) for i in ids)) if ids else set()
                    body=set().union(*(old.content_tokens(umap[i]['text']) for i in ids)) if ids else set()
                    row['sets'][name]={'unit_ids':ids,'title_facets':sorted(title&qt),'body_facets':sorted(body&qt),'union_facets':sorted((title|body)&qt)}
                row['rank1_truncated']=a['rank1_truncated'];line(out,row)
                counts['queries']+=1;counts['title_only_final_facets']+=len(set(row['sets']['final']['title_facets'])-set(row['sets']['final']['body_facets']))
                counts['query_with_title_only_final_facet']+=bool(set(row['sets']['final']['title_facets'])-set(row['sets']['final']['body_facets']))
                counts['partial_first_unit']+=a['rank1_truncated']
            summary[tag]=dict(counts)
    save(HERE/'DELIVERY_FACETS_SUMMARY.json',summary);charge('delivery_details',cpu,wall,gpu_process_seconds=0)
    print(json.dumps(summary))
if __name__=='__main__':main()
