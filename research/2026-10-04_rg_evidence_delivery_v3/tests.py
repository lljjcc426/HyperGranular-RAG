import unittest
from common import *
from frontend import scope_contract,owner_value,task_identity,verify
from delivery import Delivery
from state import build_states,fact_key,extend
from contextlib import nullcontext

def fact(slot,h,t,w,head_id=None,tail_id=None):
    return dict(slot=slot,head=h,tail=t,head_id=head_id or h,tail_id=tail_id or t,window=w.id,score=1.,polarity='positive',conditions='[]',
        provenance=dict(title=w.title,verification_spans=[dict(original_id=i,text=s,start=a,end=b) for i,s,a,b in w.sentences]))
def window(i,text):return engine.Window(str(i),str(i),'T'+str(i),text,[(str(i),text,0,len(text))])
class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from transformers import AutoTokenizer
        tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
        cls.ids=staticmethod(lambda p:tok.encode(tok.apply_chat_template([{'role':'system','content':'You are a careful evidence assistant.'},{'role':'user','content':p}],tokenize=False,add_generation_prompt=True),add_special_tokens=False))
    def fixture(self):
        ws=[window(i,('Ordinary evidence sentence. '*18)+str(i)) for i in range(15)]
        ws.append(window(15,'Anchor connects to source entity.'))
        d=Delivery('What connects to Anchor?',ws,self.ids)
        f=fact('r1','Anchor','source entity',ws[-1]);slots=[dict(id='r1',head='Anchor',tail='?v1'),dict(id='r2',head='?v1',tail='?answer')]
        # The short window may fit Dense; make its body a full medium window.
        if d.wkeys['15']<=d.dense:
            ws[-1]=window(15,'Anchor connects to source entity. '+'Additional source context. '*35);d=Delivery('What connects to Anchor?',ws,self.ids);f=fact('r1','Anchor','source entity',ws[-1])
        return d,ws,f,slots
    def test_partial_source_delivery_and_dense_fallback(self):
        d,ws,f,slots=self.fixture();r=d.partial([dict(binding={},facts=[f])],slots)
        self.assertTrue(r['prompt_changed']);self.assertEqual(r['missing_slots'],['r2']);self.assertLessEqual(r['input_tokens'],1024)
        self.assertNotIn('?v1',r['prompt']);self.assertIn(ws[-1].text,r['prompt'])
        self.assertEqual(d.partial([],slots)['prompt'],d.prompt(d.dense))
    def test_already_dense_no_forced_change(self):
        d,ws,_,slots=self.fixture();f=fact('r1','Anchor','x',ws[0]);r=d.partial([dict(facts=[f])],slots)
        self.assertFalse(r['prompt_changed']);self.assertEqual(r['prompt'],d.prompt(d.dense))
    def test_provenance_and_oversize(self):
        d,ws,f,slots=self.fixture();f['provenance']['verification_spans'][0]['text']='invented answer'
        r=d.partial([dict(facts=[f])],slots);self.assertTrue(r['fallback']);self.assertIn('PROVENANCE_MISMATCH',r['reasons'])
        extra=[window(100+i,'Grounded original sentence. '*60) for i in range(3)]
        d=Delivery('How is Anchor linked?',ws[:15]+extra,self.ids)
        slots=[dict(id='r1',head='Anchor',tail='?v1'),dict(id='r2',head='?v1',tail='?v2'),dict(id='r3',head='?v2',tail='?answer')]
        fs=[fact('r1','Anchor','B',extra[0]),fact('r2','B','C',extra[1]),fact('r3','C','D',extra[2])]
        r=d.partial([dict(binding={},facts=fs)],slots)
        self.assertTrue(r['fallback']);self.assertIn('PACKAGE_TOO_LARGE',r['reasons']);self.assertEqual(r['prompt'],d.prompt(d.dense))
    def test_semantic_beam_keeps_alternative(self):
        ws=[window(i,'source '+str(i)) for i in range(6)];slots=[dict(id='r1',head='A',tail='?v1'),dict(id='r2',head='?v1',tail='?answer')]
        fs=[fact('r1','A','X',w) for w in ws[:4]]+[fact('r1','A','Y',ws[4]),fact('r2','Y','Z',ws[5])]
        rs=build_states(slots,[],fs,{w.id:1 for w in ws},lambda f:len({x['window'] for x in f}))
        self.assertTrue(any(r['binding'].get('?answer')=='Z' for r in rs));self.assertTrue(any(r['provenance_count']==4 for r in rs))
        self.assertEqual(len({json.dumps(r['semantic_keys']) for r in rs}),len(rs))
    def test_polarity_conditions_and_normalization(self):
        w=window(0,'x');f=fact('r1','Ａ  B','C',w);s=dict(head='A B',tail='?answer')
        self.assertIsNotNone(extend({},s,f));self.assertNotEqual(fact_key(f),fact_key(dict(f,polarity='negative')))
        self.assertNotEqual(fact_key(f),fact_key(dict(f,conditions='year=2000')))
    def test_scoped_owner_and_missing_preservation(self):
        s=dict(id='r1',head='?film',relation='directed by',tail='Kent',qualifiers=['Australian'])
        cs=scope_contract('Which Australian film did Kent direct?',[s],{})
        self.assertEqual(cs[0]['scope'],'unresolved_scope');self.assertIsNone(owner_value(cs[0],s,'Movie','Kent',{}))
        c=dict(cs[0],owner='?film',scope='entity');self.assertEqual(owner_value(c,s,'Movie','Kent',{}),'Movie')
    def test_task_cache_identity(self):
        w=window(0,'x');args=['Q',{'p':1},{'id':'r1'},{},{},w,{'version':'v3'}]
        k=task_identity(*args)
        for i,v in [(2,{'id':'r2'}),(3,{'?x':'Y'}),(4,{'c1':'SUPPORTED'}),(6,{'version':'v4'})]:
            a=list(args);a[i]=v;self.assertNotEqual(k,task_identity(*a))
    def test_verifier_source_and_unknown_owner(self):
        class Stub:
            def base_only(self):return nullcontext()
            def generate(self,*a):return dict(text='yes',raw=dict(support_sids=['s0']),seconds=0,input_tokens=1,output_tokens=1)
        payload=dict(CLAIM=dict(subject='Ada',relation='directed',object='Y',qualifiers=[]),
            EVIDENCE=dict(title='Ada',sentences=[dict(sid='s0',text='Ada directed X and Y.')]),
            LOCATIONS=dict(head=dict(text='Ada',identity='Ada',identity_basis='mention'),tail=dict(text='Y',identity='Y',identity_basis='mention')))
        r=verify(Stub(),payload,[dict(id='c1',scope='unresolved_scope')],{},'test')
        self.assertEqual(r['verdict'],'supported');self.assertEqual(r['constraints'][0]['status'],'UNKNOWN')
    def test_feedback_compares_only_requested_same_relation(self):
        from search import feedback_pair
        import numpy as np
        g=engine.Group('g',[0,1,2]);a=dict(index=0,slot='r1',binding={},facts=[dict(head_id='A',tail_id='X')])
        b=dict(index=1,slot='r2',binding={},facts=[])
        self.assertIsNone(feedback_pair(g,[a,b],['a','b','c'],np.eye(3)))
        b['slot']='r1';self.assertEqual(feedback_pair(g,[a,b],['a','b','c'],np.eye(3))[2],'relation_heterogeneity')
    def test_source_rules_multivalue_direction_and_dimensions(self):
        from source_rules import decide
        e=lambda body:dict(title='Source',sentences=[dict(sid='s0',text=body)])
        for tail in ('River','Forest'):
            self.assertEqual(decide(dict(subject='Nora',relation='wrote',object=tail),e('Nora wrote River and Forest.'))[0],'supported')
        self.assertEqual(decide(dict(subject='Luca',relation='has father',object='Tara'),e("Tara's father is Luca."))[0],'unresolved')
        self.assertEqual(decide(dict(subject='Tara',relation='has father',object='Luca'),e("Tara's father is Luca."))[0],'supported')
        self.assertEqual(decide(dict(subject='G',relation='has latitude',object='7 km long'),e('G is 7 km long.'))[0],'unresolved')
        self.assertIsNone(decide(dict(subject='G',relation='has length',object='7 km long'),e('G is 7 km long.')))
    def test_prompt_ids_follow_actual_order(self):
        d,_,_,_=self.fixture();r=d.record(d.dense,'Dense')
        items=[d.units[tuple(k)] for k in r['visible_spans']]
        from delivery import text_prompt
        self.assertEqual(text_prompt(d.q,items),r['prompt'])
    def test_scope_program_preserves_source_phrase(self):
        from frontend import scope
        class Stub:
            def base_only(self):return nullcontext()
            def generate(self,*a):return dict(raw=dict(assignments=[dict(index=0,owner='?answer',predicate='nationality',scope='entity')]))
        slots=[dict(id='r1',head='Mara',relation='directed',tail='?answer',qualifiers=['Australian'])]
        cs,_=scope(Stub(),'Which Australian film did Mara direct?',slots,'test')
        self.assertEqual(cs[0]['value_or_text'],'Australian');self.assertEqual(cs[0]['question_span'],'Australian');self.assertEqual(cs[0]['owner'],'?answer')
    def test_bound_endpoint_alignment_is_then_verified(self):
        from frontend import extract_task
        class Stub:
            def base_only(self):return nullcontext()
            def generate(self,user,system,tokens,stage,schema=None):
                raw=dict(support_sids=['s0'])
                if stage.endswith('_extract'):
                    raw=dict(facts=[dict(head=dict(sid='s0',text='X',identity=''),tail=dict(sid='s0',text='H',identity=''),support_sids=['s0'])])
                return dict(raw=raw,text='yes',seconds=0.,input_tokens=1,output_tokens=1)
        w=window(0,'H owns X.');s=dict(id='r1',head='H',relation='owns',tail='?answer',qualifiers=[])
        r=extract_task(Stub(),'What does H own?',[s],[],s,{},w,[(w.title,w.source)],'test')
        self.assertEqual((r['facts'][0]['head'],r['facts'][0]['tail']),('H','X'))
        self.assertTrue(r['detail']['verification'][0]['bound_endpoint_alignment'])

if __name__=='__main__':unittest.main(verbosity=2)
