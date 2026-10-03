"""Fixed 2x2x8 oracle experiment. No outcome-dependent geometry selection."""
from io_utils import *
from core import *
from dataclasses import asdict
import csv,unittest

def instance(seed,redundancy,mixing):
    rng=np.random.default_rng(20261004+seed);hops=2+seed%3;n=48
    # Geometry depends on relation family and random nuisance, not chain membership.
    centers=norm(rng.normal(size=(4,12)));x=[];windows=[];oracle={}
    slots=[dict(id=f'r{i}',head='Start' if i==0 else f'?v{i}',relation=f'relation{i}',tail=f'?v{i+1}') for i in range(hops)]
    entities=['Start']+[f'Entity{i}' for i in range(1,hops+1)]
    records=[]
    for i in range(n):
        relation=i%hops
        binding=0 if i<hops else ((i//hops)%(2 if redundancy else 8))
        head=entities[relation] if binding==0 else f'Other{binding}_{relation}'
        tail=entities[relation+1] if binding==0 else f'Other{binding}_{relation+1}'
        records.append((relation,head,tail))
        family=relation if not mixing else int(rng.integers(4))
        x.append(centers[family]+rng.normal(0,.15,size=12))
    permutation=rng.permutation(n);x=norm(np.asarray(x)[permutation]);records=[records[i] for i in permutation]
    for i,(rel,h,t) in enumerate(records):
        wid=f'w{i:02}';text=f'{h} relation{rel} {t}.'
        w=Window(wid,'synthetic','synthetic',text,((wid,text,0,len(text)),));windows.append(w)
        oracle[wid]=(Fact(f'r{rel}',h,t,text,wid,'local:synthetic:'+h,'local:synthetic:'+t,1.),)
    qvector=norm(centers[0]);embed=lambda text:norm(centers[next((j for j in range(hops) if f'relation{j}' in text),0)])
    return slots,windows,x,qvector,embed,oracle

def run():
    cpu=time.process_time();wall=time.perf_counter();out=[]
    for redundancy,mixing in itertools.product((0,1),repeat=2):
        for seed in range(8):
            slots,ws,x,q,embed,truth=instance(seed,redundancy,mixing)
            for method in METHODS[1:]:
                oracle=LazyProbe(lambda w:truth[w.id])
                r=search(method,'Start',slots,ws,x,q,embed,oracle,1.)
                first=None;observed=[];wm={w.id:w for w in ws};base={w.id:float(x[i]@q) for i,w in enumerate(ws)}
                false=0
                for a in r['trace']:
                    observed.extend(truth[a['window']]);bs=bundles(slots,observed,wm,base,())
                    if first is None and any(len(fs)==len(slots) for _,fs in bs):first=a['step']
                    for binding,fs in bs:
                        if len(fs)==len(slots):
                            false+=any(fs[j].tail_id!=fs[j+1].head_id for j in range(len(fs)-1))
                out.append(dict(redundancy=redundancy,mixing=mixing,seed=seed,hops=len(slots),method=method,
                    first_complete_probe=first,complete8=int(r['snapshots'][8]['complete']),
                    complete16=int(r['snapshots'][16]['complete']),complete32=int(r['snapshots'][32]['complete']),
                    false_joins=false,splits=len(r['splits']),split_seconds=sum(z['seconds'] for z in r['splits']),
                    actual_probes=oracle.actual_calls,seconds=r['seconds']))
    with (HERE/'SYNTHETIC_RESULTS.csv').open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    charge('synthetic_32',cpu,wall,gpu_process_seconds=0)
    print('SYNTHETIC',len(out),'false_joins',sum(x['false_joins'] for x in out),flush=True)

class Contracts(unittest.TestCase):
    def test_bindings_and_legal_alternatives(self):
        slots,ws,x,q,e,t=instance(0,0,0);wm={w.id:w for w in ws};base={w.id:0 for w in ws}
        fs=[f for v in t.values() for f in v];bs=bundles(slots,fs,wm,base,())
        self.assertTrue(any(len(f)==2 for _,f in bs))
        wrong=[f for f in fs if not(f.head=='Entity1' and f.tail=='Entity2')]
        self.assertFalse(any(len(f)==2 for _,f in bundles(slots,wrong,wm,base,())))
        b={};s=dict(id='r',head='?x',tail='?y')
        self.assertIsNotNone(extend(b,s,fs[0],ws[0],()))
        self.assertIsNotNone(extend(b,s,fs[-1],ws[0],()))
    def test_provenance_and_parser(self):
        w=Window('w','d','Title','Alice knows Bob.',(('u','Alice knows Bob.',0,16),))
        raw=dict(slot_id='r',head='Alice',tail='Bob',quote='Alice knows Bob.',polarity='positive',conditions='',explicit=True)
        self.assertIsNotNone(witnessed(raw,w,[{'id':'r'}],(),.8))
        raw['quote']='Title knows Bob.';self.assertIsNone(witnessed(raw,w,[{'id':'r'}],(),.8))
        self.assertFalse(parse_contract('Who?',{'slots':[dict(id='r',head='Secret',relation='x',tail='?a')],'answer_var':'?a'}))
    def test_lazy_and_cost_and_budget(self):
        slots,ws,x,q,e,t=instance(2,1,1);requested=[]
        p=LazyProbe(lambda w:(requested.append(w.id) or t[w.id]))
        a=search('GB-feedback','Start',slots,ws,x,q,e,p,1.)
        self.assertEqual(len(requested),32);self.assertEqual(len(set(requested)),32)
        self.assertEqual(a['snapshots'][32]['logical_probes'],32)
        b=search('GB-feedback','Start',slots,ws,x,q,e,p,1.)
        self.assertEqual(b['snapshots'][32]['cache_hits'],32);self.assertEqual(p.actual_calls,32)
        self.assertEqual([v['window'] for v in a['trace']],[v['window'] for v in b['trace']])
    def test_feedback_same_signal_and_fact_preservation(self):
        slots,ws,x,q,e,t=instance(1,1,1)
        for m in METHODS[1:]:
            r=search(m,'Start',slots,ws,x,q,e,LazyProbe(lambda w:t[w.id]),1.)
            self.assertLessEqual(r['snapshots'][32]['leaf_count'],16)
            self.assertEqual(r['snapshots'][32]['accepted_facts'],32)
            if m.endswith('fixed'):self.assertFalse(r['splits'])
            if m.endswith('feedback'):
                for split in r['splits']:
                    seen={v['window'] for v in r['trace'][:split['step']]}
                    self.assertTrue(set(split['seeds'])<=seen)
    def test_degenerate_geometry(self):
        for x in (np.zeros((7,3)),np.ones((7,3)),np.array([[1.,0],[-1,0],[0,1],[0,-1]])):
            for kind in ('GB','KM'):
                g,_=initialize(x,[str(i) for i in range(len(x))],kind)
                self.assertEqual(sorted(i for z in g for i in z.members),list(range(len(x))))
                self.assertEqual(len(g),min(4,len(x)))
                self.assertTrue(np.isfinite(norm(x)).all())
    def test_renderer_no_answer_leak_and_failure_fallback(self):
        w=Window('w','d','unused','Alice knows Bob.',(('u','Alice knows Bob.',0,16),))
        f=Fact('r','Alice','Bob',w.text,'w','a','b',1.)
        a=render('Who?', [w],[({'?answer':'INJECTED'},(f,))],1,lambda x:x.split(),40)
        self.assertNotIn('INJECTED',a['prompt']);self.assertTrue(a['complete_bundle_visible'])
        bad=Fact('r','Alice','Bob','missing quote','w','a','b',1.)
        b=render('Who?',[w],[({},(bad,))],1,lambda x:x.split(),40)
        self.assertFalse(b['complete_bundle_visible']);self.assertTrue(b['fallback'])
if __name__=='__main__':
    if '--tests' in sys.argv:
        cpu=time.process_time();wall=time.perf_counter()
        with (HERE/'TEST_OUTPUT.txt').open('x',encoding='utf-8') as f:
            result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
        charge('tests',cpu,wall,gpu_process_seconds=0)
        print('tests',result.testsRun,'success',result.wasSuccessful())
        if not result.wasSuccessful():raise SystemExit(1)
    else:run()
