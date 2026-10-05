import unittest
import torch
from aligned import direct_pair_loss,preferences
from support import stratified

class AlignedTests(unittest.TestCase):
    def test_partial_coverage_trains_deployed_logit(self):
        g=torch.tensor([0.,0.],requires_grad=True);y=torch.tensor([[0.,.8],[0.,.2]])
        loss=direct_pair_loss(g,y,[(0,1)]);loss.backward()
        self.assertLess(g.grad[0].item(),0);self.assertGreater(g.grad[1].item(),0)
        self.assertAlmostEqual(loss.item(),torch.nn.functional.softplus(torch.tensor(.06)).item(),places=6)
    def test_empty_pairs_are_masked(self):
        g=torch.tensor([1.],requires_grad=True);loss=direct_pair_loss(g,torch.zeros(1,2),[]);loss.backward()
        self.assertEqual(loss.item(),0);self.assertEqual(g.grad.item(),0)
    def test_parent_pair_and_no_false_positive(self):
        rs=[dict(indices=[0],full=0.,cov=.5,tokens=100),dict(indices=[1],full=0.,cov=0.,tokens=110),dict(indices=[0,2],full=1.,cov=1.,tokens=200)]
        final,front=preferences(rs,[[(0,),(1,)]],{(0,),(1,),(0,2)})
        self.assertEqual(final,[(0,1)]);self.assertEqual(front,[(0,1)])
    def test_sampling_not_outcome_and_group_intact(self):
        qs=[dict(query_id=str(i),group=str(i//2),stratum='a') for i in range(12)]
        out=stratified(qs,7,'rg-v6-mine');self.assertEqual(len(out),6)
        self.assertEqual(out,stratified(list(reversed(qs)),7,'rg-v6-mine'))
        for g in {q['group'] for q in out}:self.assertEqual(sum(q['group']==g for q in out),2)
if __name__=='__main__':unittest.main(verbosity=2)
