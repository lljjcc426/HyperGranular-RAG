from common import *
from frontend import *
from runtime import LM
from dataclasses import asdict
import argparse

def run(args):
    path=LOCAL/(args.round+'_'+args.phase+'.jsonl')
    done={r['index'] for r in rows(path)} if path.exists() else set()
    packets=read(V1/'local/d0_packets.json');cc={c['query_id']:c for c in cases('D0')}
    lm=LM(quantized=True,adapter=HERE/'adapters/v27') if args.round=='v27' else LM()
    try:
        for i,p in enumerate(packets):
            if i in done or (args.indices and i not in args.indices):continue
            c=cc[p['query_id']];ws=make_windows(c['units'],lm.tokenizer);q=p['question']
            if args.phase=='A':out=parse(lm,q,args.round+'_A')
            else:
                from references import plans
                ref=plans(i)
                pred={r['index']:r for r in rows(LOCAL/(args.round+'_A.jsonl'))}[i]
                slots=ref if args.phase=='B' else pred['slots']
                selected=[('ANNOTATED_SUPPORT',next(w for w in ws if w.id==p['annotation_window']['id']))]
                words=lambda s:set(re.findall(r'[a-z0-9]+',s.lower()))
                lexical=sorted(ws,key=lambda w:(-len(words(q)&words(w.text)),w.id))
                other=next((w for w in lexical if w.id!=selected[0][1].id),None)
                if other:selected.append(('GOLDFREE_LEXICAL',other))
                catalog=tuple({(w.title,w.source) for w in ws});out=dict(slots=slots,windows=[])
                for condition,w in selected:
                    if slots:fs,detail=extract(lm,q,slots,w,catalog,args.round+'_'+args.phase)
                    else:fs=[];detail=dict(status='NO_PLAN',generation=None,rejected=[],verification=[])
                    out['windows'].append(dict(condition=condition,window=asdict(w),facts=[asdict(f) for f in fs],detail=detail))
            append(path,dict(index=i,query_id=p['query_id'],dataset=p['tag'],role='D0_DEVELOPMENT_EXPOSED',path=args.phase,question=q,**out))
            print(args.round,args.phase,i,'slots',len(out.get('slots',[])),flush=True)
    finally:lm.close(args.round+'_'+args.phase)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['A','B','C']);ap.add_argument('--round',default='v20');ap.add_argument('--indices',type=int,nargs='*');run(ap.parse_args())
