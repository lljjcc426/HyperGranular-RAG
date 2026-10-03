"""Pure blind-input gate recording and six fixed masks; no labels or model I/O."""
import os,sys
sys.dont_write_bytecode=True
for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'2026-10-03_evidence_delivery_repair'))
from repair import Context,kmeans,old

GATES=('min_new_terms','size','anchor','units_per_new_term','redundancy','facet_score_threshold')
MASKS={'G0':set(),'G1':{'min_new_terms'},'G2':{'redundancy'},
       'G3':{'min_new_terms','redundancy'},
       'G4':{'min_new_terms','redundancy','units_per_new_term'},
       'G5':{'min_new_terms','redundancy','units_per_new_term','facet_score_threshold'}}
TOL=1e-12

def gate_values(cfg,facets,covered,size,score,similarity,nterms):
    new=facets-covered;shared=facets&covered
    ratio=size/max(1,len(new));redundancy=len(shared)/max(1,len(facets))
    terms={'new':cfg.w_new*len(new)/max(1,nterms),
           'total':cfg.w_total*len(facets)/max(1,nterms),'ball':cfg.w_ball*score,
           'diversity':cfg.w_diversity*(1-similarity),
           'redundancy':-cfg.w_redundancy*redundancy,
           'size':-cfg.w_size*(size/cfg.max_candidate_ball_size if cfg.max_candidate_ball_size>0 else 0.)}
    # Preserve the original arithmetic order, including subtract operations.
    h=(terms['new']+terms['total']+terms['ball']+terms['diversity']
       -cfg.w_redundancy*redundancy-cfg.w_size*(size/cfg.max_candidate_ball_size if cfg.max_candidate_ball_size>0 else 0.))
    passes={'min_new_terms':len(new)>=cfg.min_new_terms,
            'size':cfg.max_candidate_ball_size<=0 or size<=cfg.max_candidate_ball_size,
            'anchor':score>=cfg.min_ball_score or similarity>=cfg.min_seed_similarity,
            'units_per_new_term':cfg.max_units_per_new_term<=0 or ratio<=cfg.max_units_per_new_term,
            'redundancy':redundancy<=cfg.max_redundancy,
            'facet_score_threshold':h>=cfg.min_facet_score}
    failed=[g for g in GATES if not passes[g]]
    return {'new_terms':sorted(new),'shared_terms':sorted(shared),'new_count':len(new),
            'shared_count':len(shared),'units_per_new_term':ratio,'redundancy':redundancy,
            'h':h,'h_terms':terms,'passes':passes,'all_failed_gates':failed}

def record_groups(c,balls):
    old.enrich_balls_goldfree(balls,c.units)
    scored=old.decision_from_balls(c.q,balls)['scored_balls']
    seeds=[b for _,b in scored[:c.cfg.seed_balls]];seedids={b['ball_id'] for b in seeds}
    covered=set().union(*(b['all_terms']&c.qt for b in seeds))
    records=[]
    for score,b in scored:
        ft=b['all_terms']&c.qt;sim=max((old.dot(b['center'],s['center']) for s in seeds),default=0.)
        val=gate_values(c.cfg,ft,covered,b['size'],score,sim,len(c.qt))
        seed=b['ball_id'] in seedids
        first='seed_excluded' if seed else next(iter(val['all_failed_gates']),'eligible')
        if first=='facet_score_threshold':first='score'
        records.append({'ball_id':b['ball_id'],'indices':b['indices'],'size':b['size'],
            'center':b['center'].tolist(),'radius':b['radius'],'base_score':score,
            'is_seed':seed,'facets':sorted(ft),'max_seed_similarity':sim,
            'original_first_failure':first,**val})
    metadata={'seed_ids':[b['ball_id'] for b in seeds],
        'seed_members':sorted(i for b in seeds for i in b['indices']),
        'seed_facets':sorted(covered),'prefix_facets':sorted(c.union(c.prefix)),
        'dense_facets':sorted(c.union(c.d)),'query_facets':sorted(c.qt)}
    return records,metadata

def eligible(records,mask):
    return [r for r in records if not r['is_seed'] and
            all(p for g,p in r['passes'].items() if g not in MASKS[mask])]

def place(c,proposals):
    ins=sorted(set(proposals),key=c.key)[:c.b]
    return c.place(ins),ins

def select(c,records,mask):
    groups=sorted(eligible(records,mask),key=lambda z:(-z['h'],z['ball_id']))
    selected=groups[:min(c.cfg.top_facet_edges,c.cfg.max_expanded_balls)]
    pool=set(i for r in groups for i in r['indices'])
    two=set(i for r in selected for i in r['indices'])
    props=sorted((i for i in two if c.s[i]>=c.cfg.q25_floor and i not in c.prefix),key=c.key)
    final,ins=place(c,props)
    return {'eligible_ids':[r['ball_id'] for r in groups],
            'selected_ids':[r['ball_id'] for r in selected],
            'pre':sorted(pool,key=c.key),'two':sorted(two,key=c.key),'proposal':props,
            'final':final,'inserted':ins,'answer_f1':None,'answer_status':'NOT_GENERATED'}

def count_matched(c,props):
    d=set(c.d);inside=sum(i in d for i in props);outside=len(props)-inside
    f=[i for i in c.order if i not in c.prefix and c.s[i]>=c.cfg.q25_floor]
    matched=[i for i in f if i in d][:inside]+[i for i in f if i not in d][:outside]
    matched.sort(key=c.key)
    assert len(matched)==len(props) and sum(i in d for i in matched)==inside
    final,ins=place(c,matched)
    return {'proposal':matched,'final':final,'inserted':ins,
            'answer_f1':None,'answer_status':'NOT_GENERATED'}

def reached(targets,indices):
    """Existence of one actual sentence in this stage, including for paragraphs."""
    pool=set(indices)
    return {name for name,members in targets.items() if pool.intersection(members)}
