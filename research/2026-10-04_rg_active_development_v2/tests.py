import unittest
from frontend import *

class Contracts(unittest.TestCase):
    def test_object_variables_constants_and_graph(self):
        r=dict(status='ok',relations=[dict(head='Atlas Press',relation='founded on',tail='?answer',qualifiers=[])])
        slots,e=plan_contract('When was Atlas Press founded?',r);self.assertFalse(e);self.assertEqual(slots[0]['id'],'r1')
        r['relations'][0]['head']='Invented';self.assertIn('CONSTANT_ORIGIN',plan_contract('When was Atlas Press founded?',r)[1])
        self.assertFalse(plan_contract('Who?',[])[0])
        r=dict(status='ok',relations=[dict(head='?v1',relation='knows',tail='?answer',qualifiers=[])])
        self.assertIn('DISCONNECTED',plan_contract('Who?',r)[1])
    def test_exact_location_occurrence_and_identity(self):
        w=engine.Window('w','d','Ada Lane','Ada Lane wrote Rose. She wrote Rose.',(('u','Ada Lane wrote Rose. She wrote Rose.',0,35),))
        m=dict(sid='s0',text='Rose',occurrence=1,identity='')
        p=locate(m,w);self.assertEqual(w.sentences[0][1][p['start']:p['end']],'Rose')
        m['text']='Röse'
        with self.assertRaises(ValueError):locate(m,w)
        m=dict(sid='s0',text='She',occurrence=0,identity='Ada Lane');self.assertEqual(locate(m,w)['identity_basis'],'title')
        m['identity']='Ada Smith'
        with self.assertRaises(ValueError):locate(m,w)
    def test_unique_name_and_ambiguity(self):
        a=engine.Window('a','docA','Place A','',());b=engine.Window('b','docB','Place B','',())
        cat=[('Ada Lane','bio')]
        self.assertEqual(entity('Ada Lane',a,cat),entity('Ada Lane',b,cat))
        self.assertNotEqual(entity('Smith',a,cat),entity('Smith',b,cat))
        self.assertNotEqual(entity('Ada Lane',a,cat+[('Ada Lane','other')]),entity('Ada Lane',b,cat+[('Ada Lane','other')]))
    def test_multi_span_renderer_and_no_title_only_fact(self):
        w=engine.Window('w','doc','Ada Lane','She wrote Rose.',(('u','She wrote Rose.',0,15),),tokens=5)
        slots=[dict(id='r1',head='Rose',relation='written by',tail='?answer',qualifiers=[])]
        raw=dict(slot=0,head=dict(sid='s0',text='Rose',occurrence=0,identity=''),tail=dict(sid='s0',text='She',occurrence=0,identity='Ada Lane'),support_sids=['s0'],status='supported')
        f,p=recover(raw,w,slots,[('Ada Lane','doc')]);self.assertIn('title',p['EVIDENCE'])
        r=render('Who wrote Rose?',[w],[({},(f,))],1,lambda x:x.split(),100)
        self.assertTrue(r['complete_bundle_visible']);self.assertIn('Title: Ada Lane',r['prompt'])
        raw['tail']['text']='Ada Lane'
        with self.assertRaises(ValueError):recover(raw,w,slots,[])
        r=render('Who wrote Rose?',[w],[({},(f,))],1,lambda x:x.split(),2);self.assertFalse(r['complete_bundle_visible'])
    def test_shared_search_does_not_read_unrequested_facts(self):
        import numpy as np
        ws=[engine.Window(str(i),'d'+str(i),'T'+str(i),'x',(('u'+str(i),'x',0,1),)) for i in range(12)]
        x=engine.norm(np.random.default_rng(1729).normal(size=(12,5)));q=x[0];called=[]
        probe=engine.LazyProbe(lambda w:(called.append(w.id) or []))
        slots=[dict(id='r1',head='X',relation='knows',tail='?answer',qualifiers=[])]
        a=engine.search('GB-feedback','Q',slots,ws,x,q,lambda _:q,probe,.7,max_probes=8)
        b=engine.search('KM-feedback','Q',slots,ws,x,q,lambda _:q,probe,.7,max_probes=8)
        self.assertEqual(len(a['trace']),8);self.assertEqual(len(b['trace']),8)
        self.assertFalse(a['splits']);self.assertFalse(b['splits']);self.assertEqual(len(called),len(set(called)))
        self.assertEqual(b['snapshots'][8]['logical_probes'],8)

    def test_explicit_title_identity_joins_and_wrong_constant_rejected(self):
        a=engine.Window('a','book','Rose','Ada wrote Rose.',(('a0','Ada wrote Rose.',0,15),),tokens=4)
        b=engine.Window('b','bio','Ada Lane','She was born in Rome.',(('b0','She was born in Rome.',0,21),),tokens=5)
        # The first window must itself supply the proposed complete identity.
        a=engine.Window('a','book','Rose','Ada Lane wrote Rose.',(('a0','Ada Lane wrote Rose.',0,20),),tokens=5)
        ss=[dict(id='r1',head='Rose',relation='written by',tail='?v1',qualifiers=[]),dict(id='r2',head='?v1',relation='born in',tail='?answer',qualifiers=[])]
        cat=[('Rose','book'),('Ada Lane','bio')]
        def m(text,identity=''):return dict(sid='s0',text=text,occurrence=0,identity=identity)
        f,_=recover(dict(slot=0,head=m('Rose'),tail=m('Ada Lane'),support_sids=['s0'],status='supported'),a,ss,cat)
        g,_=recover(dict(slot=1,head=m('She','Ada Lane'),tail=m('Rome'),support_sids=['s0'],status='supported'),b,ss,cat)
        states=engine.bundles(ss,[f,g],{'a':a,'b':b},{'a':1.,'b':.9},cat)
        self.assertTrue(any(len(fs)==2 for _,fs in states))
        shown=render('Where was the writer of Rose born?',[a,b],states,2,lambda x:x.split())
        self.assertTrue(shown['complete_bundle_visible']);self.assertIn('Title: Ada Lane',shown['prompt'])
        with self.assertRaisesRegex(ValueError,'CONSTANT_BINDING'):
            recover(dict(slot=0,head=m('Ada Lane'),tail=m('Rose'),support_sids=['s0'],status='supported'),a,ss,cat)

if __name__=='__main__':unittest.main(verbosity=2)
