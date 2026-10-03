from io_utils import *
from core import *
import unittest
class Additional(unittest.TestCase):
    def test_homonyms_and_multiple_legitimate_bindings(self):
        a=Window('a','sourceA','Sam','Start knows Sam.',(('a','Start knows Sam.',0,16),))
        b=Window('b','sourceB','Sam','Sam lives in York.',(('b','Sam lives in York.',0,18),))
        catalog=(('Sam','sourceA'),('Sam','sourceB'));slots=[dict(id='r1',head='Start',tail='?person'),dict(id='r2',head='?person',tail='?answer')]
        f1=Fact('r1','Start','Sam',a.text,'a',entity_id('Start',a,catalog),entity_id('Sam',a,catalog),1)
        f2=Fact('r2','Sam','York',b.text,'b',entity_id('Sam',b,catalog),entity_id('York',b,catalog),1)
        self.assertFalse(any(len(fs)==2 for _,fs in bundles(slots,[f1,f2],{'a':a,'b':b},{'a':1,'b':1},catalog)))
        fs=[Fact('r1','Start',p,a.text,'a','start',p,1) for p in ('person1','person2')]
        fs+=[Fact('r2',p,'York',b.text,'b',p,'York',1) for p in ('person1','person2')]
        bs=bundles(slots,fs,{'a':a,'b':b},{'a':1,'b':1},catalog)
        self.assertEqual(sum(len(f)==2 for _,f in bs),2)
    def test_feedback_cannot_activate_unanchored_later_slot(self):
        slots=[dict(id='r1',head='Start',tail='?x'),dict(id='r2',head='?x',tail='?answer')]
        ws={str(i):Window(str(i),'d','d','text',()) for i in range(3)}
        f=Fact('r2','X','Y','text','0','X','Y',1)
        pair=feedback_pair(Group('g',[0,1,2]),{'0':(f,),'1':()},slots,[({},())],{'r2'},ws,(),np.eye(3),['0','1','2'])
        self.assertIsNone(pair)
if __name__=='__main__':
    cpu=time.process_time();wall=time.perf_counter()
    with (HERE/'TEST_OUTPUT_additional.txt').open('x',encoding='utf-8') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Additional))
    charge('additional_contract_tests',cpu,wall,gpu_process_seconds=0)
    print('additional_tests',result.testsRun,result.wasSuccessful())
    if not result.wasSuccessful():raise SystemExit(1)
