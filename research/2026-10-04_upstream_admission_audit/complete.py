"""Finalize this round's provisional manifest; no scientific recomputation."""
import json,time,hashlib,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent

def ident(p):
    with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest().upper()
    return {'bytes':p.stat().st_size,'sha256':h}

def main():
    start=time.process_time()
    p=HERE/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
    assert 'completion' not in m
    v=json.loads((HERE/'SUPPLEMENTARY_CHECKS.json').read_text(encoding='utf-8'))
    assert v['status']=='PASS' and m['status']=='COMPLETE'
    m['completion']={'decision':'C_DESCRIPTIVE_EVIDENCE_INSUFFICIENT_FOR_MECHANISM_UPGRADE',
        'completed_cases':18,'case_candidates_read':29,'case_review':'NONBLIND_ASSISTANT_NOT_DOUBLE_HUMAN_ANNOTATION',
        'synthetic_tests_passed':9,'synthetic_cpu_seconds':.359375,
        'output_verification':v['checks'],'output_verification_cpu_seconds':v['cpu_seconds'],
        'measured_main_test_verification_cpu_seconds':m['cpu_seconds']+v['cpu_seconds']+.359375,
        'auxiliary_display_git_document_cpu_seconds':None,
        'current_source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE).decode().strip(),
        'public_artifacts':{f.name:ident(f) for f in HERE.iterdir() if f.is_file() and f.name!='manifest.json'},
        'disk_bytes_before_manifest_completion':sum(f.stat().st_size for f in HERE.rglob('*') if f.is_file()),
        'note':'Initial run identity/resource fields preserved. Completion adds derived checks and authored interpretation; no old-round file or result overwritten.'}
    m['completion']['bookkeeping_cpu_seconds']=time.process_time()-start
    p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:m['completion'][k] for k in ('decision','measured_main_test_verification_cpu_seconds','disk_bytes_before_manifest_completion')}))

if __name__=='__main__':main()
