from common import *
from runtime import LM
from schemas import PLAN,LOCATOR

def run(fp16=False):
    from contextlib import nullcontext
    lm=LM(quantized=not fp16,adapter=HERE/'adapters/v27');prefix='v29' if fp16 else 'v27'
    try:
        data=read(LOCAL/'adapt_data.json')
        for i,r in enumerate(data):
            if r['split']!='validation':continue
            for mode in ('off','on'):
                with (lm.base_only() if mode=='off' else nullcontext()):
                    g=lm.generate(r['user'],r['system'],512,prefix+'_validation_'+mode,PLAN if r['kind']=='parse' else LOCATOR)
                append(LOCAL/('adapt_validation_fp16.jsonl' if fp16 else 'adapt_validation.jsonl'),dict(index=i,source=r['source'],group=r['group'],kind=r['kind'],mode=mode,target=r['target'],generation=g,exact=g['raw']==r['target']))
                print(i,mode,'exact',g['raw']==r['target'],flush=True)
    finally:lm.close(prefix+'_grouped_development_comparison')

if __name__=='__main__':run('--fp16' in sys.argv)
