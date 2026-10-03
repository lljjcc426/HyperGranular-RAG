from io_utils import *
def main():
    cpu=time.process_time();wall=time.perf_counter()
    source=rows(OLD/'local/pilot_inputs.jsonl')
    previous=read(OLD/'sample_ids.json')
    print('sample_registry_type',type(previous).__name__,flush=True)
    metadata={}
    for tag,file in [('hotpot','stage4e_e2e_official_train1000_v1_descriptive_metadata.jsonl'),
                     ('musique','stage4f_xdr_musique_train3000_v1_sealed_metadata.jsonl')]:
        metadata[tag]={r['query_id']:r for r in rows(DATA/'processed'/file)}
    pools={}
    for r in source:
        q=r['query'];m=metadata[r['tag']][q['query_id']]
        stratum=m['type'] if r['tag']=='hotpot' else ('2hop' if m['hop_count']==2 else '3_4hop')
        key=hashlib.sha256(('rg-refinement-v1\0'+q['dataset']+'\0'+q['query_id']).encode()).hexdigest()
        pools.setdefault((r['tag'],stratum),[]).append((key,r))
    plan=[('hotpot','bridge',16,32),('hotpot','comparison',0,8),
          ('musique','2hop',16,16),('musique','3_4hop',0,8)]
    public=[];private=[];deficits=[]
    for tag,s,n0,n1 in plan:
        pool=sorted(pools.get((tag,s),[]),key=lambda z:z[0])
        if len(pool)<n0+n1: deficits.append([tag,s,len(pool),n0+n1])
        for j,(h,r) in enumerate(pool[:n0+n1]):
            role=('D0_DEV' if j<8 else 'D0_CHECK') if j<n0 else 'D1'
            record=dict(query_id=r['query']['query_id'],dataset=r['query']['dataset'],tag=tag,stratum=s,role=role,sampling_hash=h)
            public.append(record);private.append(dict(**record,query=r['query'],units=r['units']))
    save(HERE/'DATA_ROLES.json',dict(status='HISTORICALLY_EXPOSED_DEVELOPMENT',separator='U+0000',
         source='previous fixed 400',native_metadata_available=True,deficits=deficits,samples=public))
    save(LOCAL/'inputs.json',private)
    print('roles', {k:sum(r['role']==k for r in public) for k in ['D0_DEV','D0_CHECK','D1']},'deficits',deficits,flush=True)
    charge('prepare',cpu,wall,gpu_process_seconds=0)
if __name__=='__main__':main()
