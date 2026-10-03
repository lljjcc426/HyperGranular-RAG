from core import Window
def make_windows(units,tokenizer):
    bydoc={}
    for u in units:
        doc=u.get('doc_id',u['unit_id'].rsplit('::s',1)[0])
        bydoc.setdefault(doc,[]).append(u)
    result=[]
    for doc,us in bydoc.items():
        us=sorted(us,key=lambda u:u.get('sentence_id',u.get('sentence_index')));offsets={};offset=0
        for u in us:offsets[u['unit_id']]=offset;offset+=len(u['text'])+1
        for j,u in enumerate(us):
            start=offsets[u['unit_id']];text=u['text'];truncated=False
            ids=tokenizer.encode(text,add_special_tokens=False)
            if len(ids)>320:
                # Original-character prefix; do not decode and subtly rewrite text.
                lo,hi=0,len(text)
                while lo<hi:
                    mid=(lo+hi+1)//2
                    if len(tokenizer.encode(text[:mid],add_special_tokens=False))<=320:lo=mid
                    else:hi=mid-1
                text=text[:lo];truncated=True
            selected={j:(u['unit_id'],text,start,start+len(text))}
            if not truncated:
                for k in (j-1,j+1):
                    if k<0 or k>=len(us):continue
                    v=us[k];candidate=dict(selected);a=offsets[v['unit_id']]
                    candidate[k]=(v['unit_id'],v['text'],a,a+len(v['text']))
                    body=' '.join(candidate[i][1] for i in sorted(candidate))
                    if len(tokenizer.encode(body,add_special_tokens=False))<=320:selected=candidate
            sentences=tuple(selected[i] for i in sorted(selected));body=' '.join(s[1] for s in sentences)
            result.append(Window(u['unit_id'],doc,u['title'],body,sentences,truncated))
    return result
