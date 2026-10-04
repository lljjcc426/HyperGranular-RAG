import itertools,unittest,math
import numpy as np
import torch
from model import elementary,Selector
from search import es,HScore,Tree,beam
from dataset import coverage,Context

class Feasible:
    def __init__(self,lengths,limit):self.lengths=np.array(lengths);self.limit=limit
    def tokens(self,S):return int(self.lengths[list(S)].sum())
    def __call__(self,S):return self.tokens(S)<=self.limit

class Algebra(unittest.TestCase):
    def test_dp_and_gradient(self):
        torch.manual_seed(2);v=torch.randn(2,6,32,dtype=torch.float64,requires_grad=True);e=elementary(v,4)
        for h in range(1,5):
            direct=sum(v[:,list(c)].prod(1) for c in itertools.combinations(range(6),h))
            torch.testing.assert_close(e[h],direct)
            torch.testing.assert_close(torch.autograd.grad(e[h].sum(),v,retain_graph=True)[0],torch.autograd.grad(direct.sum(),v,retain_graph=True)[0])
    def test_marginal_orders_empty_duplicates(self):
        rng=np.random.default_rng(42)
        for H in (1,2,4):
            s=HScore(rng.normal(size=12),rng.normal(size=(12,32)),rng.normal(size=(max(H-1,0),32)),rng.normal(size=7),H)
            for S in [(),(0,),(0,1),(0,1,2),(0,1,2,3)]:
                v=s.expansion_scores(S)
                for i in set(range(12))-set(S):self.assertAlmostEqual(v[i],s.score((*S,i)),places=11)
            with self.assertRaises(ValueError):s.score((1,1))
    def test_bounds_and_parity(self):
        rng=np.random.default_rng(123);checks=0
        for zero in (False,True):
            for H in (1,2,4):
                for trial in range(8):
                    v=np.zeros((24,32)) if zero else rng.normal(size=(24,32));a=np.zeros(24) if zero else rng.normal(size=24)
                    s=HScore(a,v,rng.normal(size=(max(0,H-1),32)),rng.normal(size=7),H);ids=[f'b{i:03}' for i in range(24)];f=Feasible(rng.integers(1,8,24),23)
                    flat=beam(s,f,ids,(),kind='Flat')
                    for kind in ('GB','KM'):
                        tree=Tree(s.z,kind);leaves=[n['idx'].tolist() for n in tree.nodes if not n['children']]
                        self.assertEqual(sorted(sum(leaves,[])),list(range(24)))
                        t=s.theta((0,1))
                        for node in tree.nodes:self.assertLessEqual(float(np.max(s.z[node['idx']]@t)),float(t@node['c']+np.linalg.norm(t)*node['r'])+1e-10)
                        other=beam(s,f,ids,(),kind=kind);self.assertEqual(flat[0],other[0]);self.assertEqual(flat[2],other[2]);checks+=len(flat[2])
        print('synthetic_per_parent_parity_checks',checks)
    def test_average_radius_fails(self):
        z=np.array([[0.],[0.],[9.]]);c=z.mean(0);mean=np.linalg.norm(z-c,axis=1).mean();mx=np.linalg.norm(z-c,axis=1).max()
        self.assertLess(float(c[0]+mean),9);self.assertGreaterEqual(float(c[0]+mx),9)
    def test_cubic_not_quadratic(self):
        # Third finite difference of x*y*z is one, any degree <=2 polynomial zero.
        cube=sum((-1)**(3-sum(bits))*math.prod(bits) for bits in itertools.product([0,1],repeat=3));self.assertEqual(cube,1)
    def test_beam_not_global(self):
        class Toy:
            n=4
            def score(self,S):return 100 if set(S)=={2,3} else sum([5,4,0,0][i] for i in S)
            def expansion_scores(self,S):return np.array([self.score((*S,i)) for i in range(4)])
        best,_,_=beam(Toy(),Feasible([1]*4,2),list('abcd'),(),width=1,maxk=2)
        self.assertNotEqual(set(best),{2,3});self.assertEqual(Toy().score((2,3)),100)
    def test_coverage_deduplicates(self):
        hot=dict(total=2,coverage={'p':[0,1]});mu=dict(total=2,coverage={'p':[0],'q':[1]})
        self.assertEqual(coverage(hot,['p','p']),(1.,1.));self.assertEqual(coverage(mu,['p','p']),(.5,0.))
    def test_models_train_all_orders(self):
        torch.manual_seed(1729)
        for kind in ('H1','H2','H4','DeepSets'):
            m=Selector(kind,[0,0],[1,1]);q=torch.randn(3,1024);x=torch.randn(3,6,1024);l=torch.ones(3,6);mask=torch.ones(3,6)
            y,terms=m(q,x,l,mask,True);y.square().mean().backward();self.assertTrue(all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None))
            if hasattr(m,'w'):
                for g in m.w.weight.grad.reshape(2,m.order-1,32,128).norm(dim=(2,3)).mean(0):self.assertGreater(float(g),0)
            self.assertLess(sum(p.numel() for p in m.parameters()),2000000)

if __name__=='__main__':unittest.main()
