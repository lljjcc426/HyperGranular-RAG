"""Deterministic, source-only partial delivery. No Gold or new verification."""
import unicodedata,itertools
def norm(s):return ' '.join(unicodedata.normalize('NFKC',s).split())
def text_prompt(question,items):
    body='\n'.join(f'[{j+1}] Title: {title}\n{text}' for j,(title,text) in enumerate(items))
    return 'Answer the question using only the evidence. Return a short answer, or UNKNOWN if insufficient.\nQuestion: '+question+'\nEvidence:\n'+body

class Delivery:
    def __init__(self,question,windows,tokenize,base=None,limit=1024):
        self.q=question;self.ws=windows;self.tokenize=tokenize;self.limit=limit
        self.wm={w.id:w for w in windows};self.rank={w.id:i for i,w in enumerate(windows)}
        self.base=base or {w.id:-i for i,w in enumerate(windows)}
        self.units={};self.order={};self.wkeys={}
        for i,w in enumerate(windows):
            keys=[]
            for j,(sid,text,a,b) in enumerate(w.sentences):
                k=(sid,a,b);keys.append(k)
                if k not in self.units:self.units[k]=(w.title,text);self.order[k]=(i,j,sid,a,b)
                elif self.units[k][1]!=text:raise ValueError('SOURCE_SPAN_CONFLICT')
            self.wkeys[w.id]=set(keys)
        # Reproduce v2 Dense's accepted-window insertion order exactly. A span
        # from a skipped early window must not retroactively move a later one.
        dense_order=[];dense=set()
        for w in windows:
            trial=list(dense_order)
            for sid,text,a,b in w.sentences:
                k=(sid,a,b)
                if k not in trial:trial.append(k)
            p=text_prompt(question,[self.units[k] for k in trial])
            if len(tokenize(p))<=limit:dense_order=trial;dense=set(trial)
        self.dense=dense;self.dense_order=dense_order
        self.dense_prompt=text_prompt(question,[self.units[k] for k in dense_order])
        empty=self.tokens(set());available=limit-empty
        self.prefix=set()
        for k in dense_order:
            z=self.prefix|{k}
            if self.tokens(z)-empty>available/2:break
            self.prefix=z
    def sorted(self,ks):return sorted(ks,key=self.order.__getitem__)
    def prompt(self,ks):
        if hasattr(self,'dense') and ks==self.dense:return self.dense_prompt
        return text_prompt(self.q,[self.units[k] for k in self.sorted(ks)])
    def tokens(self,ks):return len(self.tokenize(self.prompt(ks)))
    def fill(self,ks):
        ks=set(ks)
        for w in self.ws:
            trial=ks|self.wkeys[w.id]
            if self.tokens(trial)<=self.limit:ks=trial
        return ks
    def package(self,fs):
        ks=set()
        for f in fs:
            p=f['provenance'];wid=f['window']
            if wid not in self.wm:raise ValueError('UNKNOWN_WINDOW')
            spans=p.get('verification_spans')
            if not spans:raise ValueError('MISSING_VERIFICATION_SCOPE')
            if p['title']!=self.wm[wid].title:raise ValueError('TITLE_MISMATCH')
            for s in spans:
                k=(s['original_id'],s['start'],s['end'])
                if k not in self.wkeys[wid] or self.units[k][1]!=s['text']:raise ValueError('PROVENANCE_MISMATCH')
                ks.add(k)
        return ks
    def components(self,states,slots):
        anchors={norm(s[side]) for s in slots for side in ('head','tail') if not s[side].startswith('?')}
        for state in states:
            fs=state['facts'];remaining=set(range(len(fs)))
            while remaining:
                seen={remaining.pop()};nodes={fs[next(iter(seen))][s+'_id'] for s in ('head','tail')}
                changed=True
                while changed:
                    changed=False
                    for j in list(remaining):
                        ends={fs[j]['head_id'],fs[j]['tail_id']}
                        if ends&nodes:seen.add(j);remaining.remove(j);nodes|=ends;changed=True
                group=[fs[j] for j in sorted(seen)]
                if any(norm(f[s]) in anchors for f in group for s in ('head','tail')):yield group
    def record(self,ks,kind,**extra):
        new=ks-self.dense;lost=self.dense-ks
        return dict(kind=kind,prompt=self.prompt(ks),input_tokens=self.tokens(ks),visible_spans=[list(k) for k in self.sorted(ks)],
            new_spans=[list(k) for k in self.sorted(new)],displaced_spans=[list(k) for k in self.sorted(lost)],
            prompt_changed=bool(new or lost),order_only=False,prefix_sentences=len(self.prefix),**extra)
    def partial(self,states,slots):
        options=[];reasons={};required={s['id'] for s in slots}
        for fs in self.components(states,slots):
            try:ks=self.package(fs)
            except ValueError as e:reasons[str(e)]=reasons.get(str(e),0)+1;continue
            if not ks-self.dense:reasons['ALREADY_DENSE']=reasons.get('ALREADY_DENSE',0)+1;continue
            n=self.tokens(self.prefix|ks)
            if n>self.limit:reasons['PACKAGE_TOO_LARGE']=reasons.get('PACKAGE_TOO_LARGE',0)+1;continue
            relations={f['slot'] for f in fs};wids={f['window'] for f in fs}
            key=(-len(relations),-min(f['score'] for f in fs),-sum(self.base[w] for w in wids)/len(wids),n,
                 tuple(sorted((f['slot'],f['window'],f['head_id'],f['tail_id']) for f in fs)))
            options.append((key,fs,ks))
        if not options:return self.record(self.dense,'Partial-grounded',package_windows=[],package_relations=[],missing_slots=sorted(required),
            missing_conditions=[q for s in slots for q in s.get('qualifiers',[])],fallback=True,reasons=reasons,new_window_target=0)
        _,fs,ks=min(options,key=lambda z:z[0]);selected={f['slot'] for f in fs};wids=sorted({f['window'] for f in fs},key=self.rank.__getitem__)
        target=sum(bool(self.wkeys[w]-self.dense) for w in wids)
        final=self.fill(self.prefix|ks)
        return self.record(final,'Partial-grounded',package_windows=wids,package_relations=sorted(selected),missing_slots=sorted(required-selected),
            missing_conditions=[q for s in slots for q in s.get('qualifiers',[])],fallback=False,reasons=reasons,new_window_target=target)
    def count_dense(self,partial):
        target=partial['new_window_target'];ks=set(self.prefix);chosen=[]
        if target:
            for w in self.ws:
                if not self.wkeys[w.id]-self.dense:continue
                trial=ks|self.wkeys[w.id]
                if self.tokens(trial)<=self.limit:ks=trial;chosen.append(w.id)
                if len(chosen)==target:break
        final=self.fill(ks) if target else self.dense
        return self.record(final,'Count-conditioned-Dense',package_windows=chosen,new_window_target=target,new_window_actual=len(chosen),
            status='COUNT_MATCH_INFEASIBLE' if len(chosen)!=target else 'MATCHED',fallback=not target)
