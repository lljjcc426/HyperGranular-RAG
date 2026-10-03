"""Reuse revision2 official pure functions, without modifying its outputs."""
import ast,collections,re,string,hashlib
from common import ROOT
SPECS={'hotpot':'D35FC91A6DB21D791DBDDA11DAF3856E9359F5701D54E3EEFBA20D88FECC02C0',
       'musique':'10368F619B4D5EF5D83748C05A96C0AFD332A14AB5C010740C98D58DFAEFE974'}
def scorers():
    out={}
    for tag,sha in SPECS.items():
        p=ROOT/'temp/revision2_official_sources'/f'{tag}.py';b=p.read_bytes()
        assert hashlib.sha256(b).hexdigest().upper()==sha
        tree=ast.parse(b.decode());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
        env={'re':re,'string':string,'collections':collections,'Counter':collections.Counter}
        exec(compile(tree,str(p),'exec'),env);out[tag]=env
    return out
def answer_score(tag,pred,g,modules):
    o=modules[tag]
    if tag=='hotpot':return float(o['exact_match_score'](pred,g['answer'])),float(o['f1_score'](pred,g['answer'])[0])
    return float(max(o['compute_exact'](a,pred) for a in g['answers'])),float(max(o['compute_f1'](a,pred) for a in g['answers']))
