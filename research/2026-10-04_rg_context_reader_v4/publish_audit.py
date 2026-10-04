"""Public provenance counts/identity; reference-derived sentence IDs stay local."""
from common import *
def run():
    p=HERE/'CONTEXT_AUDIT.csv';rs=list(csv.DictReader(p.open(encoding='utf-8')))
    if 'source_spans' not in rs[0]:return
    save(LOCAL/'initial_public_audit.json',rs)
    for r in rs:
        spans=json.loads(r.pop('source_spans'));missing=json.loads(r.pop('missing_reference_ids'))
        r['missing_reference_count']=len(missing);r['source_span_count']=len(spans);r['source_identity']=digest(spans)
    table(p,rs);print('Public provenance redacted to counts/identity; contexts and scores unchanged.')
if __name__=='__main__':run()
