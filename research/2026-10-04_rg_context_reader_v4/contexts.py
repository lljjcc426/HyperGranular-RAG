"""Automatic selection is label-free; reference selection lives elsewhere."""
from common import *
from protocols import body,prompt,ids,PROTOCOLS
Delivery=load_module('rg_v4_delivery_dependency',V3/'delivery.py').Delivery
class Builder:
    def __init__(self,question,windows,tok,base):
        self.q=question;self.tok=tok
        self.d=Delivery(question,windows,lambda p:ids(tok,p),base)
        self.original_dense=list(self.d.dense_order)
        self.dense=list(self.original_dense)
        while self.dense and not self.fits(self.dense):self.dense.pop()
        if not self.dense:raise ValueError('EMPTY_SHARED_DENSE')
    def ordered(self,ks):return self.d.sorted(set(ks))
    def body(self,ks):return body([self.d.units[k] for k in self.ordered(ks)])
    def body_tokens(self,ks):return len(self.tok.encode(self.body(ks),add_special_tokens=False))
    def fits(self,ks):return all(len(ids(self.tok,prompt(self.q,self.body(ks),p)))<=1024 for p in PROTOCOLS)
    def record(self,ks,status,**extra):
        ks=self.ordered(ks);original=set(self.original_dense);now=set(ks);added=now-original;removed=original-now
        change='identical' if not added and not removed else 'mixed' if added and removed else 'additional' if added else 'subset'
        return dict(body=self.body(ks),visible_spans=[list(k) for k in ks],status=status,body_tokens=self.body_tokens(ks),
            input_tokens={p:len(ids(self.tok,prompt(self.q,self.body(ks),p))) for p in PROTOCOLS},
            source_change=change,retained=len(now&original),added=len(added),removed=len(removed),order_only=False,
            shared_cap_adjustment=self.dense!=self.original_dense,**extra)
    def dense_record(self):return self.record(self.dense,'DENSE_SHARED_CAP' if self.dense!=self.original_dense else 'DENSE_ORIGINAL',fallback=False)
    def automatic(self,source):
        options=[];reasons={};required={s['id'] for s in source['slots']}
        observed={t['window'] for t in source['result']['trace']}
        for fs in self.d.components(source['result']['states'],source['slots']):
            if any(f['window'] not in observed or f['score']!=1 for f in fs):raise ValueError('UNOBSERVED_FACT')
            ks=self.d.package(fs)
            if not self.fits(ks):reasons['PACKAGE_TOO_LARGE']=reasons.get('PACKAGE_TOO_LARGE',0)+1;continue
            rels={f['slot'] for f in fs};ws={f['window'] for f in fs}
            key=(-len(rels),-min(f['score'] for f in fs),-sum(self.d.base[w] for w in ws)/len(ws),self.body_tokens(ks),tuple(sorted(ks)))
            options.append((key,fs,ks))
        if not options:return self.record(self.dense,'FALLBACK_NO_PACKAGE',fallback=True,package_windows=[],package_relations=[],missing_slots=sorted(required),reasons=reasons)
        _,fs,ks=min(options,key=lambda z:z[0]);rels={f['slot'] for f in fs}
        return self.record(ks,'AUTOMATIC_PACKAGE',fallback=False,package_windows=sorted({f['window'] for f in fs}),
            package_relations=sorted(rels),missing_slots=sorted(required-rels),reasons=reasons,
            condition_observations=[f.get('conditions') for f in fs],semantic_truth='NOT_CERTIFIED')
    def length_control(self,a):
        if a['fallback']:return self.record(self.dense,'FALLBACK_MATCHED_DENSE',fallback=True,budget_tokens=a['body_tokens'],budget_gap=0)
        target=a['body_tokens'];ks=set();chosen=[]
        for w in self.d.ws:
            trial=ks|self.d.wkeys[w.id]
            if self.body_tokens(trial)<=target and self.fits(trial):ks=trial;chosen.append(w.id)
        if not ks:return self.record(self.dense,'NO_FEASIBLE_CONTROL',fallback=True,budget_tokens=target,budget_gap=target-self.body_tokens(self.dense))
        return self.record(ks,'BUDGET_CONDITIONED_DENSE',fallback=False,budget_tokens=target,budget_gap=target-self.body_tokens(ks),selected_windows=chosen)
