"""Assemble the requested single manifest after actual evaluation/verification."""
from common import *
import subprocess

def main():
    assert load(HERE/'FINAL_VERIFICATION.json')['status']=='PASS'
    ledger=rows(HERE/'RESOURCE_LEDGER.jsonl');generation=load(HERE/'GENERATION_SUMMARY.json')
    group_stats={}
    for tag in CONFIGS:
        cases=[z for z in rows(LOCAL/'pilot_inputs.jsonl') if z['tag']==tag]
        assert all(len(z['gb_sizes'])==len(z['kmeans']['sizes']) for z in cases)
        group_stats[tag]={'queries':len(cases),'matched_actual_k':len(cases),
            'mean_k':float(np.mean([len(z['gb_sizes']) for z in cases])),
            'mean_sorted_size_l1':float(np.mean([sum(abs(a-b) for a,b in zip(sorted(z['gb_sizes']),sorted(z['kmeans']['sizes']))) for z in cases])),
            'size_distribution_equal_queries':sum(sorted(z['gb_sizes'])==sorted(z['kmeans']['sizes']) for z in cases),
            'empty_repairs':sum(z['kmeans']['empty_repairs'] for z in cases),
            'max_iterations':max(z['kmeans']['iterations'] for z in cases)}
    if (HERE/'GROUP_MATCHING.json').exists():assert load(HERE/'GROUP_MATCHING.json')==group_stats
    else:save(HERE/'GROUP_MATCHING.json',group_stats)
    prior_paths=[ROOT/'research/2026-10-02_bounded_upgrade',ROOT/'literature_refresh/2026-10-02_bounded',ROOT/'temp/bounded_literature']
    prior_bytes=sum(p.stat().st_size for d in prior_paths for p in d.rglob('*') if p.is_file())
    current_bytes=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    manifest={'date':'2026-10-03','research_role':'HISTORICALLY_EXPOSED_EXPLORATORY',
        'input_roles':load(HERE/'DATA_ROLES.json'),'generation_binding':load(HERE/'GENERATION_BINDING.json'),
        'sample':identity(HERE/'sample_ids.json'),'frozen_rankings':identity(HERE/'pilot_rankings.jsonl'),
        'generation':generation,'resource_ledger':ledger,
        'measured_cpu_seconds':sum(z['cpu_seconds'] for z in ledger),
        'prior_unmetered_document_cpu_seconds':None,'unknown_cpu_not_treated_as_zero':True,
        'prior_experiment_gpu_seconds':0,'current_gpu_process_seconds':sum(z.get('gpu_process_seconds',0) for z in ledger),
        'prior_derived_files_bytes':prior_bytes,'current_round_bytes_at_manifest':current_bytes,
        'paid_cost':0,'new_reranker_calls':0,'new_embedding_calls':0,
        'limits':{'gpu_process_seconds':43200,'cpu_process_seconds':86400,'new_disk_bytes':10000000000,'new_generation_calls':5464},
        'artifact_identities':{p.name:identity(p) for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py','.csv','.json') and p.name!='manifest.json'},
        'local_private_artifacts':{p.name:identity(p) for p in LOCAL.iterdir() if p.is_file()},
        'source_at_finalization':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        'missing_or_limited':['Prior document CPU unmetered','No independent confirmation','Query bootstrap does not resolve shared-document dependence','Historical prompts have no stored input IDs; pilot anchor prompts reconstructed and compared by archived prompt SHA/visible IDs/token count'],
        'manuscripts_figures_modified':False,'historical_results_modified':False}
    if '--refresh-manifest' in sys.argv:
        (HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:save(HERE/'manifest.json',manifest)
    print(json.dumps({'group_matching':group_stats,'calls':generation,'cpu_seconds':manifest['measured_cpu_seconds'],'disk_bytes':prior_bytes+current_bytes}),flush=True)
if __name__=='__main__':main()
