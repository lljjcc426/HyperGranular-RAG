from io_utils import *
import collections
PREFIX='3b_' if os.environ.get('RG_MODEL')=='3b' else ''
def local(name):return LOCAL/(PREFIX+name)
def public(name):return HERE/(PREFIX+name)
def threshold():
    data=[r for r in rows(local('d0_verification.jsonl')) if r['role']=='D0_DEV' and not r['unknown']]
    assert len(data)==48
    options=[]
    for t in (.5,.7,.9):
        acc=[r for r in data if r['score']>=t];tp=sum(r['label'] for r in acc)
        options.append(dict(threshold=t,accepted=len(acc),true_positive=tp,false_positive=len(acc)-tp,
            precision=tp/len(acc) if acc else None,recall=tp/sum(r['label'] for r in data)))
    feasible=[r for r in options if r['accepted']>=10 and r['precision']>=.9]
    selected=max(feasible,key=lambda r:(r['recall'],r['threshold']))['threshold'] if feasible else None
    save(public('D0_THRESHOLD.json'),dict(selected=selected,options=options,check_used_for_selection=False))
    print(json.dumps(dict(selected=selected,options=options)),flush=True)
def summarize():
    data=rows(local('d0_verification.jsonl'));t=read(public('D0_THRESHOLD.json'))['selected'];out={}
    for role in ('D0_DEV','D0_CHECK'):
        rs=[r for r in data if r['role']==role];report=[]
        for v in (.5,.7,.9):
            acc=[r for r in rs if r['score']>=v and not r['unknown']];tp=sum(r['label'] for r in acc)
            report.append(dict(threshold=v,accepted=len(acc),correct=tp,wrong=len(acc)-tp,precision=tp/len(acc) if acc else None))
        out[role]=report
    reader=rows(local('d0_reader.jsonl')) if local('d0_reader.jsonl').exists() else []
    summaries=[]
    for role in ('D0_DEV','D0_CHECK'):
        for tag in ('hotpot','musique'):
            for condition in ('SUPPLIED_SUPPORT','NO_RETRIEVAL'):
                rs=[r for r in reader if (r['role'],r['tag'],r['condition'])==(role,tag,condition)]
                if rs:summaries.append(dict(role=role,tag=tag,condition=condition,n=len(rs),em=sum(r['em'] for r in rs)/len(rs),f1=sum(r['f1'] for r in rs)/len(rs)))
    parses=[r for p in ('parse_dev_v2','parse_check') for r in rows(local('d0_'+p+'.jsonl'))]
    extraction=rows(local('d0_extractions.jsonl')) if local('d0_extractions.jsonl').exists() else []
    save(public('CALIBRATION_COUNTS.json'),dict(selected_threshold=t,verification=out,reader=summaries,
        parse_schema_pass={role:sum(bool(r['slots']) for r in parses if r['role']==role) for role in ('D0_DEV','D0_CHECK')},
        extracted_windows=len(extraction),windows_with_provenance_valid_facts=sum(bool(r['facts']) for r in extraction),
        provenance_valid_facts=sum(len(r['facts']) for r in extraction)))
    print(json.dumps(read(public('CALIBRATION_COUNTS.json'))),flush=True)
if __name__=='__main__':threshold() if sys.argv[1]=='threshold' else summarize()
