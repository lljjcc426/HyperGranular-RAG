"""Read-only dependency/schema inspection; no model generation."""
import json
from pathlib import Path
import importlib.metadata
import torch

ROOT=Path(__file__).resolve().parents[2]
def main():
    print({x:importlib.metadata.version(x) for x in ['torch','transformers','numpy']})
    print('CUDA',torch.cuda.is_available())
    for name in ['stage4e_e2e_official_train1000_v1','stage4f_xdr_official']:
        c=json.loads((ROOT/'configs'/f'{name}.json').read_text(encoding='utf-8'))
        print(name)
        for key in ['blind','gold','embedding_cache','rankings','prompt_audit_main']:
            p=Path(c['paths'][key]);print(key,p.exists(),p.stat().st_size if p.exists() else None)
            if p.exists() and key in ['blind','gold','rankings','prompt_audit_main']:
                with p.open(encoding='utf-8') as f:r=json.loads(next(f))
                print('keys',list(r))
                if key=='gold': print('target_schema',{k:(type(v).__name__,len(v) if hasattr(v,'__len__') else None) for k,v in r.items()})
        with Path(c['paths']['telemetry_main']).open(encoding='utf-8') as f:print('old_cost',json.load(f))
if __name__=='__main__':main()
