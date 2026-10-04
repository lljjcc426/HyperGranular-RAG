from common import *
from dataset import Store,Context,coverage
from transformers import AutoTokenizer
import numpy as np

def main():
    cpu=0.;wall=time.perf_counter();s=Store();bge=AutoTokenizer.from_pretrained(BGE,local_files_only=True);out=[]
    for tag in s.corpus:
        blocks=s.corpus[tag];lengths=[len(bge.encode(b['title']+'\n'+b['text'])) for b in blocks]
        qq=[q for q in s.queries if q['tag']==tag and q['role']=='TUNE'];fits=[]
        for q in qq:
            t=s.targets[q['query_id']];bb=[blocks[s.index[tag][i]] for i in t['coverage']];ctx=Context(q['question'],bb,s.tok,1024);n=len(bb);fits.append((n,ctx.tokens(tuple(range(n))),int(n<=6 and ctx(tuple(range(n))))))
        out.append(dict(tag=tag,corpus_blocks=len(blocks),encoder_truncated_blocks=sum(l>512 for l in lengths),encoder_limit512_blocks=sum(l==512 for l in lengths),max_encoder_tokens=max(lengths),tune_queries=len(qq),known_support_fits_K6_and_1024=sum(f[2] for f in fits),known_support_exceeds_K6=sum(f[0]>6 for f in fits),known_support_exceeds_1024=sum(f[1]>1024 for f in fits),mean_known_support_prompt_tokens=float(np.mean([f[1] for f in fits]))))
    table(HERE/'CORPUS_AND_BUDGET.csv',out);charge('data_checks',cpu,wall,gpu_process_seconds=0)
if __name__=='__main__':main()
