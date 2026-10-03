from io_utils import *
from core import Window,Fact,render
from windows import make_windows
import unittest
class WhitespaceTokenizer:
    def encode(self,text,**kwargs):return text.split()
class Windows(unittest.TestCase):
    def test_sentence_relative_offsets_and_source_isolation(self):
        units=[dict(unit_id='q::p0::s0',paragraph_index=0,sentence_index=0,text='first sentence.',title='A'),
               dict(unit_id='q::p0::s1',paragraph_index=0,sentence_index=1,text='word '*330,title='A'),
               dict(unit_id='q::p1::s0',paragraph_index=1,sentence_index=0,text='other document.',title='B')]
        ws=make_windows(units,WhitespaceTokenizer());source={u['unit_id']:u['text'] for u in units}
        for w in ws:
            self.assertLessEqual(w.tokens,320)
            for sid,text,start,end in w.sentences:
                self.assertEqual(text,source[sid][start:end]);self.assertEqual(sid.rsplit('::s',1)[0],w.source)
        self.assertTrue(ws[1].truncated)
    def test_multisentence_quote_survives_display_markers(self):
        w=Window('w','d','d','Alice wrote Blue. Blue won.',(('a','Alice wrote Blue.',0,17),('b','Blue won.',0,9)))
        f=Fact('r','Alice','Blue',w.text,'w','a','b',1)
        result=render('Who won?',[w],[({},(f,))],1,lambda s:s.split(),100)
        self.assertTrue(result['complete_bundle_visible']);self.assertIn('[2]',result['prompt'])
        tiny=render('Who won?',[w],[({},(f,))],1,lambda s:s.split(),10)
        self.assertFalse(tiny['complete_bundle_visible'])
if __name__=='__main__':
    cpu=time.process_time();wall=time.perf_counter()
    with (HERE/'TEST_OUTPUT_windows.txt').open('x',encoding='utf-8') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Windows))
    charge('window_contract_tests',cpu,wall,gpu_process_seconds=0)
    print('window_tests',result.testsRun,result.wasSuccessful())
    if not result.wasSuccessful():raise SystemExit(1)
