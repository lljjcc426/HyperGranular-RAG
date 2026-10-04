"""One-time post-run binding of v5's just-built ordered arrays, not a re-encode."""
from common import *
import numpy as np

def main():
    corpus=read(LOCAL/'corpus.json');queries=read(LOCAL/'queries.json');identities={}
    for tag in corpus:
        qq=[q for q in queries if q['tag']==tag]
        for kind,texts in [('blocks',[b['title']+'\n'+b['text'] for b in corpus[tag]]),('queries',['Represent this sentence for searching relevant passages: '+q['question'] for q in qq])]:
            ids=[b['id'] for b in corpus[tag]] if kind=='blocks' else [q['query_id'] for q in qq]
            assert np.load(LOCAL/f'{tag}_{kind}.npy',mmap_mode='r').shape==(len(ids),1024)
            identities[tag+'_'+kind]=dict(model_revision=BGE.name,tokenizer_revision=BGE.name,pooling='CLS/L2',precision='float32',max_length=512,query_instruction='Represent this sentence for searching relevant passages: ',text_digest=digest(texts),row_ids=ids)
    if (LOCAL/'embedding_identity.json').exists():assert read(LOCAL/'embedding_identity.json')==identities
    else:save(LOCAL/'embedding_identity.json',identities)
    save(HERE/'ENCODING_BINDING_STATUS.json',dict(status='POST_RUN_ORDER_AND_CONFIG_BINDING',rows={k:len(v['row_ids']) for k,v in identities.items()},source='Unchanged corpus/queries and completed encoding loop at c110195; no re-encoding or changed row order.',claim_limit='Records executed construction/order; not an independent second embedding computation.'))
if __name__=='__main__':main()
