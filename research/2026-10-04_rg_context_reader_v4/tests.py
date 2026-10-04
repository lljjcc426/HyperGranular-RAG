import unittest
from common import *
from protocols import *
from contexts import Builder
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from transformers import AutoTokenizer
        cls.tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
    def fixture(self):
        ws=[engine.Window('w0','doc0','Ada', 'Ada wrote Book. It was published.',(('s0','Ada wrote Book.',0,15),('s1','It was published.',0,17))),
            engine.Window('w1','doc1','Other','Other text.',(('s2','Other text.',0,11),))]
        b=Builder('What did Ada write?',ws,self.tok,{'w0':1.,'w1':.5})
        f=dict(slot='r0',head='Ada',tail='Book',head_id='Ada',tail_id='Book',score=1,window='w0',
            provenance=dict(title='Ada',verification_spans=[dict(original_id=s,start=a,end=z,text=t) for s,t,a,z in ws[0].sentences]))
        src=dict(slots=[dict(id='r0',head='Ada',tail='?answer')],result=dict(states=[dict(facts=[f])],trace=[dict(window='w0')]))
        return b,src
    def test_dense_member_package_delivered_without_fill(self):
        b,s=self.fixture();a=b.automatic(s)
        self.assertFalse(a['fallback']);self.assertEqual(len(a['visible_spans']),2)
        self.assertLess(a['body_tokens'],b.dense_record()['body_tokens'])
        self.assertEqual(set(map(tuple,a['visible_spans'])),b.d.wkeys['w0'])
    def test_no_package_falls_back_and_budget_control(self):
        b,s=self.fixture();a=b.automatic(s);l=b.length_control(a)
        self.assertLessEqual(l['body_tokens'],a['body_tokens'])
        s['result']['states']=[];a=b.automatic(s)
        self.assertEqual(a['body'],b.dense_record()['body']);self.assertEqual(b.length_control(a)['body'],a['body'])
    def test_unobserved_or_missing_provenance_rejected(self):
        b,s=self.fixture();s['result']['trace']=[]
        with self.assertRaisesRegex(ValueError,'UNOBSERVED'):b.automatic(s)
        b,s=self.fixture();s['result']['states'][0]['facts'][0]['provenance']['verification_spans']=[]
        with self.assertRaisesRegex(ValueError,'VERIFICATION_SCOPE'):b.automatic(s)
    def test_field_protocol_has_no_answer_cleaning(self):
        self.assertEqual(parse('{"answer":"long explanation remains"}','P2'),('long explanation remains','VALID_ANSWER_FIELD'))
        for raw in ('{"answer":1}','{"answer":"a","extra":"b"}','{"answer":"a","answer":"b"}','```json\n{"answer":"a"}\n```','{"answer":'):
            self.assertEqual(parse(raw,'P2'),('','PROTOCOL_FAILURE'))
        self.assertEqual(parse('The answer is Ada.','P1')[0],'The answer is Ada.')
    def test_cache_cannot_cross_protocol_length_precision(self):
        q='Which book?';p=prompt(q,'Evidence','P0');x=identity(self.tok,p,'P0');y=identity(self.tok,p,'P1')
        self.assertEqual(x['input_ids'],y['input_ids']);self.assertNotEqual(digest(x),digest(y))
        z=identity(self.tok,prompt(q,'Evidence','P2'),'P2');self.assertNotEqual(digest(y),digest(z))
        z=dict(x,precision='NF4');self.assertNotEqual(digest(x),digest(z))
    def test_actual_constructed_sources_and_shared_cap(self):
        rs=read(LOCAL/'contexts.json');cc={c['query_id']:c for c in selected()}
        self.assertEqual(len(rs),128)
        for r in rs:
            um={u['unit_id']:u for u in cc[r['query_id']]['units']}
            rebuilt=body([(s['title'],s['text']) for s in r['source_items']]);self.assertEqual(rebuilt,r['body'])
            for s in r['source_items']:self.assertEqual(um[s['id']]['text'][s['start']:s['end']],s['text'])
            for p in PROTOCOLS:
                user=prompt(cc[r['query_id']]['query']['question'],r['body'],p)
                self.assertEqual(user.split('\nEvidence:\n',1)[1],r['body']);self.assertLessEqual(len(ids(self.tok,user)),1024)
        # Automatic constructors have no annotation parameter or reference import.
        import inspect,ast,contexts
        imports=[n.module for n in ast.walk(ast.parse(inspect.getsource(contexts))) if isinstance(n,ast.ImportFrom)]
        self.assertNotIn('reference',imports)
        self.assertEqual(list(inspect.signature(Builder.automatic).parameters),['self','source'])
if __name__=='__main__':unittest.main(verbosity=2)
