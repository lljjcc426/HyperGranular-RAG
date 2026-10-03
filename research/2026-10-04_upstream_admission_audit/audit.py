"""One streaming CPU-only retrospective audit; outputs exclusively under this folder."""
from core import *
import csv,json,hashlib,gzip,time,subprocess,platform
from collections import Counter,defaultdict
import numpy as np
import common as prior

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];PREV=HERE.parent/'2026-10-03_evidence_delivery_repair';LOCAL=HERE/'local'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def stream(p):
    with Path(p).open(encoding='utf-8') as f:
        for s in f:
            if s.strip():yield json.loads(s)
def save(p,obj):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def emit(f,row):f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
def identity(p):
    p=Path(p)
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest().upper()
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name,'bytes':p.stat().st_size,'sha256':h}
def table(name,rows):
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (HERE/name).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def summary_hit(targets,ix):
    h=reached(targets,ix);return h,{'hits':len(h),'targets':len(targets),'er':len(h)/len(targets),'cr':int(len(h)==len(targets))}
def targets_from_loss(tag,loss,units):
    keys=[e['support_id'] for e in loss['missing_support_events']]+[e['support_id'] for e in loss['dense_support_path']]
    if tag=='hotpot':return {k:{i for i,u in enumerate(units) if u['unit_id']==k} for k in keys}
    return {k:{i for i,u in enumerate(units) if str(u['paragraph_index'])==k} for k in keys}

class Aggregate:
    def __init__(self):self.rows=defaultdict(Counter)
    def add(self,key,values):self.rows[key].update(values)

def main():
    cpu=time.process_time();wall=time.perf_counter();LOCAL.mkdir(exist_ok=True)
    before=subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT).decode()
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    roles=read(PREV/'DATA_ROLES.json');oldmanifest=read(PREV/'manifest.json')
    paths=[PREV/n for n in ('DATA_ROLES.json','manifest.json','sample_ids.json','pilot_rankings.jsonl','PILOT_RESULTS.csv','PROXY_REFERENCE_CORRECTION.json','repair.py')]
    paths += [PREV/'local'/n for n in ('loss_queries.jsonl','pilot_inputs.jsonl','delivery_facets.jsonl')]
    bindings={}
    for p in paths:
        ident=identity(p);bindings[str(p.relative_to(ROOT))]=ident
        expected=oldmanifest.get('artifact_identities',{}).get(p.name) if p.parent==PREV else oldmanifest.get('local_private_artifacts',{}).get(p.name)
        if expected:assert (ident['bytes'],ident['sha256'])==(expected['bytes'],expected['sha256']),p.name
    save(HERE/'START_IDENTITY.json',{'source_commit':source,'bindings':bindings,'numpy':np.__version__,
        'python':platform.python_version(),'existing_worktree_status':before,
        'configuration':old.RetrievalConfig().to_dict(),'masks':{k:sorted(v) for k,v in MASKS.items()}})
    sample=read(PREV/'sample_ids.json');sampleids={s['query_id'] for s in sample}
    assert len(sampleids)==400 and Counter(s['tag'] for s in sample)=={'hotpot':200,'musique':200}
    inputs={r['query']['query_id']:r for r in stream(PREV/'local/pilot_inputs.jsonl')}
    oldranks=defaultdict(dict)
    for r in stream(PREV/'pilot_rankings.jsonl'):oldranks[r['query_id']][r['method']]=r
    losses={r['query_id']:r for r in stream(PREV/'local/loss_queries.jsonl')}
    gates=Counter();denoms=Counter();summ=Aggregate();grouping=Aggregate();full=defaultdict(Counter)
    casepool=defaultdict(list);checks=Counter();masks_count=0;status='COMPLETE';max_phi_excess=0.
    with gzip.open(LOCAL/'group_records.jsonl.gz','xt',encoding='utf-8') as groupfile, \
         gzip.open(LOCAL/'support_paths.jsonl.gz','xt',encoding='utf-8') as supportfile, \
         (LOCAL/'pilot_diagnostics.jsonl').open('x',encoding='utf-8') as pilotfile:
        for tag in ('hotpot','musique'):
            # Bind only the three actual source dependencies; labels reuse prior diagnostics.
            for name in ('blind','embedding_cache','rankings'):
                p=Path(roles[tag][name]['path']);ident=identity(p);expected=roles[tag][name]
                assert (ident['bytes'],ident['sha256'])==(expected['bytes'],expected['sha256']),(tag,name)
                bindings[tag+'/'+name]=ident
            cfg,p,units,queries,x,qx,spans,_=prior.dataset(tag,verify=False)
            archive={r['query_id']:r for r in stream(p['rankings'])}
            for j,q in enumerate(queries):
                if time.process_time()-cpu>7150 or sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())>950_000_000:
                    status='PARTIAL_RESOURCE_STOP';break
                qid=q['query_id'];a,b=spans[qid];us=units[a:b]
                start=time.perf_counter();c=Context(q,us,x[a:b],qx[j]);gbtime=time.perf_counter()-start
                loss=losses[qid];targets=targets_from_loss(tag,loss,us)
                assert len(targets)==loss['dense_support']['total'] and all(targets.values())
                densehits=reached(targets,c.d);missing=set(targets)-densehits
                gr,meta=record_groups(c,c.balls);g0=select(c,gr,'G0')
                ar=archive[qid]
                assert [c.ids[i] for i in g0['final']]==ar['static_q25_top20_unit_ids']
                assert [c.ids[i] for i in g0['inserted']]==ar['q25_inserted_unit_ids']
                assert [c.ids[i] for i in c.d]==ar['dense_top20_unit_ids']
                checks['historical_h0_matches']+=1
                byindex={i:r for r in gr for i in r['indices']}
                selected=set(g0['selected_ids'])
                for r in gr:
                    reason=r['original_first_failure']
                    if reason=='eligible':reason='selected' if r['ball_id'] in selected else 'edge_budget'
                    assert reason==loss['all_ball_gates'][r['ball_id']]['reason'],(qid,r['ball_id'],reason)
                    r['original_first_failure']=reason
                for ev in loss['missing_support_events']:
                    full[tag]['first_'+ev['reason']]+=1
                    for uid,expected in ev['unit_reasons'].items():
                        i=c.ids.index(uid);r=byindex[i];reason=r['original_first_failure']
                        if reason=='selected':
                            if c.s[i]<c.cfg.q25_floor:reason='q25_floor'
                            elif i in c.prefix:reason='prefix_skip'
                            elif i not in g0['inserted']:reason='insertion_capacity'
                            else:reason='delivered'
                        assert reason==expected,(qid,uid,reason,expected)
                full[tag].update({'queries':1,'targets':len(targets),'dense_missing_targets':len(missing),
                    'dense_observable_saturated':int(c.union(c.d)==c.union(range(c.n))),
                    'dense_all_question_terms':int(c.union(c.d)==c.qt),
                    'universe_all_question_terms':int(c.union(range(c.n))==c.qt)})
                def register(groupname,records,metadata,scope):
                    for r in records:
                        strata=['all_groups']+([] if r['is_seed'] else ['nonseed_groups'])
                        missed_here=reached({t:targets[t] for t in missing},r['indices'])
                        if not r['is_seed'] and missed_here:strata+=['nonseed_with_dense_missing_target']
                        for st in strata:
                            key=(scope,tag,groupname,st);denoms[key]+=1
                            gates[key+('joint','+'.join(r['all_failed_gates']) or 'NONE')]+=1
                            gates[key+('first',r['original_first_failure'])]+=1
                            for g in GATES:gates[key+('independent_fail',g)]+=int(not r['passes'][g])
                        if scope=='full' or groupname=='KMeans':
                            emit(groupfile,{'query_id':qid,'dataset':tag,'grouping':groupname,
                                'member_ids':[c.ids[i] for i in r['indices']],**r})
                    if scope=='full' or groupname=='KMeans':
                        emit(supportfile,{'query_id':qid,'dataset':tag,'grouping':groupname,**metadata,
                            'targets':{t:[{'unit_id':c.ids[i],'ball_id':next(r['ball_id'] for r in records if i in r['indices']),
                                'all_failed_gates':next(r['all_failed_gates'] for r in records if i in r['indices']),
                                'q25_pass':c.s[i]>=c.cfg.q25_floor,'prefix':i in c.prefix} for i in sorted(ix)] for t,ix in targets.items()},
                            'dense_missing_targets':sorted(missing)})
                register('GB',gr,meta,'full')
                if qid not in sampleids:continue
                priorin=inputs[qid];assert priorin['query']==q and priorin['units']==us
                assert priorin['gb_sizes']==[b['size'] for b in c.balls]
                start=time.perf_counter();kb,km=kmeans(c);kr,kmmeta=record_groups(c,kb);ktime=time.perf_counter()-start
                assert km==priorin['kmeans'];checks['kmeans_recorded_metadata_match']+=1
                kg0=select(c,kr,'G0')
                assert len(kg0['proposal'])==oldranks[qid]['KMeans-R2_0.85']['proposal_count']
                # Verify directly against unchanged historical selector for this grouping.
                edges,_=old.select_facet_edges_goldfree(c.query,c.q,kb,c.cfg)
                assert kg0['selected_ids']==[e['accepted_ball_ids'][0] for e in edges]
                register('GB',gr,meta,'pilot');register('KMeans',kr,kmmeta,'pilot')
                sat=c.union(c.d)==c.union(range(c.n));checks['pilot_saturated_queries']+=sat
                for oldrow in oldranks[qid].values():
                    if oldrow['method']=='Dense40':continue
                    ix=[c.ids.index(uid) for uid in oldrow['ranking']]
                    for lam in (.85,.70):
                        if sat:
                            excess=c.phi(ix,lam)-c.phi(c.d,lam);max_phi_excess=max(max_phi_excess,excess)
                            assert excess<=TOL;checks['saturation_existing_ranking_checks']+=1
                runs={};f=[i for i in c.order if i not in c.prefix and c.s[i]>=c.cfg.q25_floor]
                for gn,records,metadata in [('GB',gr,meta),('KMeans',kr,kmmeta)]:
                    runs[gn]={mask:select(c,records,mask) for mask in MASKS}
                    base=runs[gn]['G0']
                    for low,high in [('G0','G1'),('G0','G2'),('G1','G3'),('G2','G3'),('G3','G4'),('G4','G5')]:
                        assert set(runs[gn][low]['pre'])<=set(runs[gn][high]['pre'])
                    for mask,out in runs[gn].items():
                        matched=count_matched(c,out['proposal']);masks_count+=1
                        assert out['final'][:c.p]==c.prefix and len(set(out['final']))==c.k
                        for typ,result,stages in [('RULE',out,('pre','two','proposal','final')),('COUNT_MATCHED_DENSE',matched,('proposal','final'))]:
                            for stage in stages:
                                ix=result[stage];hits,vals=summary_hit(targets,ix);basehits=reached(targets,base[stage])
                                vals.update({'queries':1,'units':len(ix),'empty_pool_queries':int(not ix),
                                    'annotated_member_units':sum(any(i in v for v in targets.values()) for i in ix),
                                    'query_annotated_fraction_sum':sum(any(i in v for v in targets.values()) for i in ix)/len(ix) if ix else 0,
                                    'nonempty_pool_queries':int(bool(ix)),
                                    'added_targets_vs_g0':len(hits-basehits),'lost_targets_vs_g0':len(basehits-hits),
                                    'added_targets_vs_dense':len(hits-densehits),'lost_targets_vs_dense':len(densehits-hits),
                                    'changed_members_vs_g0_queries':int(set(ix)!=set(base[stage])),
                                    'units_added_vs_g0':len(set(ix)-set(base[stage])),
                                    'units_lost_vs_g0':len(set(base[stage])-set(ix))})
                                if stage=='final':
                                    vals.update({'new_units_vs_dense':len(set(ix)-set(c.d)),
                                        'evicted_units_vs_dense':len(set(c.d)-set(ix)),
                                        'promotions':len(set(result['inserted'])&set(c.d)),
                                        'insertions':len(result['inserted']),
                                        'selected_groups':len(out['selected_ids']),
                                        'groups_added_vs_g0':len(set(out['selected_ids'])-set(base['selected_ids'])),
                                        'groups_lost_vs_g0':len(set(base['selected_ids'])-set(out['selected_ids']))})
                                summ.add((tag,gn,mask,typ,stage),vals)
                        for stage in ('proposal','final'):
                            h=reached(targets,out[stage]);mh=reached(targets,matched[stage])
                            summ.add((tag,gn,mask,'RULE',stage),{'targets_only_rule_vs_matched':len(h-mh),
                                'targets_only_matched_vs_rule':len(mh-h),'shared_units_with_matched':len(set(out[stage])&set(matched[stage]))})
                        emit(pilotfile,{'query_id':qid,'dataset':tag,'grouping':gn,'mask':mask,
                            'id_order':c.ids,'rule':out,'matched':matched,
                            'support_targets':{t:sorted(v) for t,v in targets.items()},
                            'target_hits_by_stage':{stage:sorted(reached(targets,out[stage])) for stage in ('pre','two','proposal','final')}})
                for name,ix in [('F',f),('Dense20',c.d),('Dense40',c.order[:40])]:
                    _,v=summary_hit(targets,ix);summ.add((tag,'NONE','REFERENCE',name,'reference'),dict(v,queries=1,units=len(ix),empty_pool_queries=int(not ix)))
                metrics={'queries':1,'gb_k':len(gr),'km_k':len(kr),
                    'group_size_sorted_l1':sum(abs(a-b) for a,b in zip(sorted(r['size'] for r in gr),sorted(r['size'] for r in kr))),
                    'gb_max_size':max(r['size'] for r in gr),'km_max_size':max(r['size'] for r in kr),
                    'gb_oversize_groups':sum(not r['passes']['size'] for r in gr),'km_oversize_groups':sum(not r['passes']['size'] for r in kr),
                    'seed_member_symmetric_difference':len(set(meta['seed_members'])^set(kmmeta['seed_members'])),
                    'seed_facet_symmetric_difference':len(set(meta['seed_facets'])^set(kmmeta['seed_facets'])),
                    'gb_seed_missing_targets':len(reached({t:targets[t] for t in missing},meta['seed_members'])),
                    'km_seed_missing_targets':len(reached({t:targets[t] for t in missing},kmmeta['seed_members'])),
                    'observable_saturated':int(sat),'all_question_terms_saturated':int(c.union(c.d)==c.qt),
                    'gb_reconstruction_seconds':gbtime,'km_group_and_gate_seconds':ktime}
                grouping.add((tag,'BASE'),metrics)
                for mask in MASKS:
                    vals={'queries':1}
                    for stage in ('pre','two','proposal','final'):
                        ga=set(runs['GB'][mask][stage]);ka=set(runs['KMeans'][mask][stage])
                        gh=reached(targets,ga);kh=reached(targets,ka)
                        vals.update({stage+'_shared_units':len(ga&ka),stage+'_gb_only_units':len(ga-ka),stage+'_km_only_units':len(ka-ga),
                            stage+'_shared_targets':len(gh&kh),stage+'_gb_only_targets':len(gh-kh),stage+'_km_only_targets':len(kh-gh)})
                    grouping.add((tag,mask),vals)
                # Eligibility is fixed; no answers are read for case selection.
                annotated=set().union(*targets.values());missingunits=set().union(*(targets[t] for t in missing)) if missing else set()
                ca=[i for i in c.order if i in missingunits and not byindex[i]['is_seed'] and byindex[i]['facets'] and byindex[i]['new_count']==0 and c.s[i]>=c.cfg.q25_floor]
                cb=sorted((set(runs['GB']['G5']['proposal'])-set(g0['proposal']))-annotated,key=c.key)
                cc=sorted(set(g0['final'])^set(kg0['final']),key=c.key)
                ch=hashlib.sha256(('upstream-admission-audit-v1\0'+q['dataset']+'\0'+qid).encode()).hexdigest()
                for category,candidates in [('A',ca),('B',cb),('C',cc)]:
                    if candidates:casepool[tag,category].append({'query_id':qid,'dataset':tag,'category':category,'hash':ch,
                        'question':q['question'],'dense':[us[i] for i in c.d],
                        'candidates':[dict(us[i],score=c.s[i],gate_record=byindex[i]) for i in candidates[:2]]})
                if (j+1)%500==0:print(tag,j+1,'CPU diagnosis',flush=True)
            if status!='COMPLETE':break
    selected=[]
    for tag in ('hotpot','musique'):
        used=set()
        for category in ('A','B','C'):
            picked=[z for z in sorted(casepool[tag,category],key=lambda z:z['hash']) if z['query_id'] not in used][:3]
            selected+=picked;used.update(z['query_id'] for z in picked)
    save(LOCAL/'case_packets.json',selected)
    save(HERE/'CASE_SELECTION.json',[{k:z[k] for k in ('dataset','category','hash')} for z in selected])
    gate_rows=[]
    for key,count in sorted(gates.items()):
        scope,tag,gn,stratum,kind,condition=key;denom=denoms[key[:4]]
        gate_rows.append(dict(scope=scope,dataset=tag,grouping=gn,stratum=stratum,kind=kind,condition=condition,
            count=count,denominator_groups=denom,proportion=count/denom))
    table('GATE_JOINT_FAILURES.csv',gate_rows)
    output=[]
    for key,val in sorted(summ.rows.items()):
        tag,gn,mask,typ,stage=key;n=val['queries'];out=dict(dataset=tag,grouping=gn,mask=mask,kind=typ,stage=stage,**val)
        out['query_mean_er']=val['er']/n;out['query_mean_cr']=val['cr']/n
        out['target_micro_coverage']=val['hits']/val['targets'];out['mean_units']=val['units']/n
        out['mean_annotated_fraction_nonempty']=val['query_annotated_fraction_sum']/val['nonempty_pool_queries'] if val['nonempty_pool_queries'] else 'NA'
        out['answer_f1']='NOT_GENERATED';output.append(out)
    table('MASK_AND_BREADTH_COMPARISON.csv',output)
    table('GROUPING_AND_SATURATION.csv',[dict(scope='pilot',dataset=k[0],condition=k[1],**v) for k,v in sorted(grouping.rows.items())]+
          [dict(scope='full',dataset=k,condition='GB_FULL',**v) for k,v in full.items()])
    save(HERE/'RECONCILIATION.json',{'status':status,'checks':checks,'diagnostic_rankings':masks_count,
        'full_history':full,'max_saturated_phi_excess':max_phi_excess,'tolerance':TOL,
        'kmeans_member_hash_comparison':'NOT_AVAILABLE_IN_PRIOR_RECORDS',
        'answer_generation':'NOT_GENERATED'})
    assert status!='COMPLETE' or (masks_count==4800 and checks['historical_h0_matches']==4000)
    manifest={'status':status,'source_commit':source,'input_bindings':bindings,
        'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-wall,
        'disk_bytes':sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()),
        'prior_measured_cpu_seconds':oldmanifest['measured_cpu_seconds'],'past_document_cpu_seconds':None,
        'cpu_limit_seconds':7200,'disk_limit_bytes':1_000_000_000,
        'model_calls':0,'gpu_process_seconds':0,'paid_cost':0,'new_answer_experiments':0,
        'model_modules_loaded':[m for m in ('torch','transformers','sentence_transformers') if m in sys.modules],
        'artifacts':{p.name:identity(p) for p in HERE.iterdir() if p.suffix in ('.csv','.json','.py')},
        'local_artifacts':{p.name:identity(p) for p in LOCAL.iterdir() if p.is_file()},
        'limitations':['Retrospective exposed data','No new answers','No previous KMeans member digest','Past document CPU unknown','No human double case annotation']}
    assert not manifest['model_modules_loaded']
    save(HERE/'manifest.json',manifest)
    print(json.dumps({'status':status,'checks':checks,'rankings':masks_count,'cpu_seconds':manifest['cpu_seconds'],
        'wall_seconds':manifest['wall_seconds'],'disk_bytes':manifest['disk_bytes'],'model_calls':0}),flush=True)

if __name__=='__main__':main()
