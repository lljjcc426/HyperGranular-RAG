import unittest,itertools,math
import numpy as np
from repair import Context,r1,r2,all_methods,kmeans

def fixture(n=28,question='alpha beta gamma'):
    rng=np.random.default_rng(19);x=rng.normal(size=(n,7)).astype('float32');x[:,0]+=4
    x/=np.linalg.norm(x,axis=1,keepdims=True);q=np.array([1,0,0,0,0,0,0],dtype='float32')
    u=[{'unit_id':f'u{i:02}','title':'alpha' if i%5==0 else '',
        'text':'beta' if i%3 else 'gamma'} for i in range(n)]
    return Context({'query_id':'synthetic','question':question},u,x,q)

class RepairTests(unittest.TestCase):
    def test_contracts_and_poison(self):
        c=fixture();out,km=all_methods(c)
        poisoned=dict(c.query,answer='poison',supporting_facts=['u00'],question_type='poison')
        other=Context(poisoned,[dict(u,answer='poison') for u in c.units],c.x,c.q)
        out2,_=all_methods(other)
        for m,r in out.items():
            self.assertEqual(r['ranking'],out2[m]['ranking'])
            self.assertEqual(len(set(r['ranking'])),len(r['ranking']))
            if m!='Dense40':self.assertEqual(r['ranking'][:10],[c.ids[i] for i in c.prefix])
        for l in (.85,.70):
            a,b=out[f'R1_{l:.2f}'],out[f'R2_{l:.2f}']
            self.assertEqual(a['inserted'],b['inserted']);self.assertGreaterEqual(b['phi'],a['phi'])
            self.assertEqual(len(a['inserted']),len(c.hi))
        self.assertEqual(len(km['sizes']),len(c.balls));self.assertEqual(sum(km['sizes']),c.n)

    def test_independent_enumeration(self):
        c=fixture();cands=c.order[10:];a,ins,_=r1(c,cands,.70);b,meta=r2(c,a,ins,.70)
        # Force outside insertions too, independent of greedy outcome.
        for ins in [ins,c.order[20:24]]:
            a=c.place(ins);b,meta=r2(c,a,ins,.70)
            removable=set(c.d)-set(c.prefix)-set(ins);count=len(set(ins)-set(c.d))
            def objective(s):
                ranks=[sum(v<=c.s[i] for v in c.s)/c.n for i in sorted(s)]
                terms=set().union(*(c.t[i] for i in s))
                return .70*math.fsum(ranks)/c.k+.30*len(terms)/max(1,len(c.qt))
            alternatives=[(objective((set(c.d)-set(r))|set(ins)),r) for r in itertools.combinations(removable,count)]
            self.assertAlmostEqual(objective(set(b)),max(s for s,r in alternatives),places=14)
            self.assertLessEqual(meta['combinations'],210)

    def test_short_and_all_promotions(self):
        for n in (1,8,13,20):
            c=fixture(n);a,i,_=r1(c,c.order[c.p:],.85);b,_=r2(c,a,i,.85)
            self.assertEqual(a,b);self.assertEqual(len(a),n)
    def test_no_terms_and_saturated_marginals(self):
        c=fixture(question='who is the');a,i,steps=r1(c,c.order[10:],.85)
        self.assertEqual(c.union(a),set())
        self.assertTrue(all(z['proxy_delta']==0 for z in steps))
        c=fixture();c.t=[{'alpha'} for _ in c.t]
        a,i,steps=r1(c,c.order[10:],.70)
        self.assertTrue(all(z['proxy_delta']==0 for z in steps))
    def test_eviction_tie_prefers_original(self):
        c=fixture();c.r[:]=1;c.t=[set() for _ in c.t];ins=c.order[20:24]
        a=c.place(ins);b,_=r2(c,a,ins,.85);self.assertEqual(a,b)
    def test_duplicate_vectors_keep_k(self):
        c=fixture();c.x[:]=c.x[0];balls,info=kmeans(c)
        self.assertEqual(len(balls),len(c.balls));self.assertTrue(all(info['sizes']))

    def test_title_only_facet_and_recomputed_duplicate(self):
        base=fixture();outside=base.order[20:22]
        units=[dict(u,title='novel' if i in outside else '',text='anchor') for i,u in enumerate(base.units)]
        c=Context({'query_id':'synthetic','question':'novel anchor'},units,base.x,base.q)
        self.assertIn('novel',c.title[outside[0]]);self.assertNotIn('novel',c.body[outside[0]])
        candidates=outside+c.d[10:12]
        a,ins,steps=r1(c,candidates,.70)
        self.assertEqual(steps[0]['unit_id'],c.ids[outside[0]])
        self.assertGreater(steps[0]['proxy_delta'],0)
        self.assertEqual(steps[1]['proxy_delta'],0)
        self.assertIn(steps[1]['unit_id'],[c.ids[i] for i in c.d])

if __name__=='__main__':unittest.main(verbosity=2)
