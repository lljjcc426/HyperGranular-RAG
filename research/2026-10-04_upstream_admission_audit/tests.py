import sys,unittest,itertools,math,io,time
from pathlib import Path
from core import *
import numpy as np

def fixture(n=27):
    rng=np.random.default_rng(41);x=rng.normal(size=(n,5)).astype('float32');x[:,0]+=3
    x/=np.linalg.norm(x,axis=1,keepdims=True)
    units=[{'unit_id':f'u{i:02}','title':'alpha','text':'beta' if i%2 else 'gamma'} for i in range(n)]
    return Context({'query_id':'synthetic','question':'alpha beta gamma'},units,x,np.array([1,0,0,0,0],dtype='float32'))

class GateTests(unittest.TestCase):
    def val(self,ft,covered,size=2,score=.3,sim=.3):
        return gate_values(old.RetrievalConfig(),set(ft),set(covered),size,score,sim,3)
    def test_nonempty_new_zero_redundancy(self):
        v=self.val(['a'],['a']);self.assertEqual(v['redundancy'],1.)
        r=dict(v,is_seed=False);self.assertFalse(eligible([r],'G1'))
    def test_empty_facet_separate_branch(self):
        v=self.val([],[]);self.assertEqual(v['redundancy'],0.)
        self.assertIn('min_new_terms',v['all_failed_gates']);self.assertNotIn('redundancy',v['all_failed_gates'])
    def test_next_layer_ratio_and_score(self):
        v=self.val(['a'],['a'],size=7)
        self.assertIn('units_per_new_term',v['all_failed_gates'])
        self.assertIn('facet_score_threshold',v['all_failed_gates'])
        self.assertFalse(eligible([dict(v,is_seed=False)],'G3'))
        self.assertFalse(eligible([dict(v,is_seed=False)],'G4'))
        self.assertTrue(eligible([dict(v,is_seed=False)],'G5'))
    def test_all_failures_not_first(self):
        v=self.val(['a'],['a'],size=10,score=-1,sim=-1)
        self.assertEqual(v['all_failed_gates'][0],'min_new_terms')
        self.assertTrue({'size','anchor','redundancy','units_per_new_term'}<=set(v['all_failed_gates']))
    def test_relaxation_can_displace(self):
        c=fixture();outside=c.order[20:23]
        def row(name,h,i,fail=()):
            return {'ball_id':name,'h':h,'indices':[i],'is_seed':False,'passes':{g:g not in fail for g in GATES}}
        rs=[row('old1',.2,outside[0]),row('old2',.1,outside[1]),row('new',.3,outside[2],['min_new_terms'])]
        a,b=select(c,rs,'G0'),select(c,rs,'G1')
        self.assertLess(set(a['pre']),set(b['pre']))
        self.assertNotIn('old2',b['selected_ids'])
        self.assertTrue(set(a['final'])-set(b['final']))
    def test_paragraph_same_sentence_path(self):
        rs=[{'is_seed':False,'passes':{'min_new_terms':False,'redundancy':True},'indices':[1]},
            {'is_seed':False,'passes':{'min_new_terms':True,'redundancy':False},'indices':[2]}]
        actual=set(i for r in eligible(rs,'G0') for i in r['indices'])
        self.assertEqual(reached({'p':{1,2}},actual),set())
        self.assertTrue(all(any(r['passes'][g] for r in rs) for g in ('min_new_terms','redundancy')))
    def test_matched_composition_and_short(self):
        for n in (1,8,19,27):
            c=fixture(n);f=[i for i in c.order if i not in c.prefix and c.s[i]>=c.cfg.q25_floor]
            for p in ([],f[::2],f):
                m=count_matched(c,p)
                self.assertEqual(len(p),len(m['proposal']))
                self.assertEqual(len(set(p)&set(c.d)),len(set(m['proposal'])&set(c.d)))
    def test_saturation_theorem_and_non_saturated(self):
        c=fixture(24);c.t=[{'alpha'} for _ in c.t]
        for subset in itertools.combinations(range(24),20):
            for lam in (0.,.7,.85,1.):self.assertLessEqual(c.phi(subset,lam),c.phi(c.d,lam)+TOL)
        c.t=[set() for _ in c.t];c.t[c.order[-1]]={'alpha'}
        other=c.d[:-1]+[c.order[-1]]
        self.assertGreater(c.phi(other,0),c.phi(c.d,0))
    def test_label_poison_and_original_h0(self):
        c=fixture();other=Context(dict(c.query,answer='poison',supporting_facts=['u01']),
            [dict(u,answer='poison',support=True) for u in c.units],c.x,c.q)
        for a,b in [(c.balls,other.balls),(kmeans(c)[0],kmeans(other)[0])]:
            ra,_=record_groups(c,a);rb,_=record_groups(other,b)
            for mask in MASKS:self.assertEqual(select(c,ra,mask),select(other,rb,mask))
        r,_=record_groups(c,c.balls);out=select(c,r,'G0')
        self.assertEqual(out['final'],c.h0);self.assertEqual(out['inserted'],c.hi)

if __name__=='__main__':
    started=time.process_time();buf=io.StringIO()
    result=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GateTests))
    text=buf.getvalue()+f'CPU seconds: {time.process_time()-started:.6f}\n'
    print(text);Path(__file__).with_name('TEST_OUTPUT.txt').write_text(text,encoding='utf-8')
    sys.exit(0 if result.wasSuccessful() else 1)
