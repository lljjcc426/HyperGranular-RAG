"""Check only the edited tables, anonymous package, and actual PDF builds."""
from pathlib import Path
from statistics import mean
import csv
import json
import math
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent


def read_csv(p):
    with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def main():
    wall,cpu=time.perf_counter(),time.process_time()
    out=HERE/'build/reconstructed'
    result=subprocess.run([sys.executable,str(HERE/'anonymous_supplement/reconstruct.py'),'--out',str(out)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    local=read_csv(HERE/'SAME_PANEL_QA.csv');portable=read_csv(out/'same_panel_qa.csv')
    assert len(local)==len(portable)==19
    max_delta=0.0
    for a,b in zip(local,portable):
        assert (a['seed'],a['method'])==(b['seed'],b['method'])
        for key in ('n','full_count','full','f1','delta_f1_mmr','em','input_tokens'):
            delta=abs(float(a[key])-float(b[key]));max_delta=max(max_delta,delta)
            assert delta<1e-12,(key,a,b)
    assert read_csv(HERE/'H4_PAIRED_COUNTS.csv')==read_csv(out/'paired_counts.csv')
    for folder in ('anonymous_conference','submission_bundle'):
        d=HERE/folder
        assert not any(p.is_dir() for p in d.iterdir()),folder
        assert '../shared' not in (d/'main.tex').read_text(encoding='utf-8')
    patterns=[r'[CE]:[\\/]',r'Users[\\/]',r'lljjcc426',r'hotpotqa_train_distractor_v1_1::',r'musique_ans_v1.0_train::']
    scan_files=0
    for folder in ('anonymous_conference','anonymous_supplement'):
        for path in (HERE/folder).iterdir():
            if path.suffix in ('.tex','.bib','.bbl','.md','.json','.csv','.py'):
                text=path.read_text(encoding='utf-8');scan_files+=1
                for pattern in patterns:assert not re.search(pattern,text), (path.name,pattern)
                assert 'HyperGranular-RAG' not in text,path.name
    for name in ('conference','journal'):
        status=json.loads((HERE/f'BUILD_{name.upper()}.json').read_text(encoding='utf-8'))
        assert status['citations']==status['bibliography_items']
        assert not any(any(key in w for key in ('Overfull','undefined','Missing character')) for w in status['warnings'])
        assert status['pdf_metadata']['author']==''
    source=(HERE.parent/'manuscripts/conference/main.tex').read_text(encoding='utf-8')
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\keywords',source,re.S)[1].strip()
    # Plain text for author registration, preserving the actual submitted-draft wording.
    (HERE/'ABSTRACT_READY.md').write_text('# Current conference abstract\n\n'
        'Title: When Set Scores Fail to Select Evidence: A Controlled Study of Budgeted Multi-hop RAG\n\n'
        +' '.join(abstract.split())+'\n\nRegistration receipt: UNKNOWN. This text is not a registration or submission.\n',encoding='utf-8')
    report=dict(status='NUMERIC_AND_PACKAGE_CHECKS_PASSED',
                reconstruction_stdout=result.stdout.strip(),numeric_rows_checked=19,
                maximum_numeric_roundoff=max_delta,paired_counts_match=True,
                anonymous_text_files_checked=scan_files,source_paths_flat=True,
                conference_cited_entries=11,journal_cited_entries=20,
                research_model_calls=0,new_scoring_or_statistical_tests=0,
                wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,
                visual_review='Recorded separately in EDITORIAL_CHECK.md')
    (HERE/'NUMERIC_PACKAGE_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    with (HERE/'EDITORIAL_COST.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(stage='numeric_package_check',wall_seconds=report['wall_seconds'],
                               cpu_seconds=report['cpu_seconds'],new_model_calls=0,paid=0))+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
