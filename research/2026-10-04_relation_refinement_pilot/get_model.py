"""Only the explicitly authorized public 3B checkpoint; no alternate models."""
from io_utils import *
MODEL=DOWNLOAD_MODEL
if '--http-resume' in sys.argv:os.environ['HF_HUB_DISABLE_XET']='1'
def main():
    from huggingface_hub import HfApi,hf_hub_download
    cpu=time.process_time();wall=time.perf_counter()
    api=HfApi();info=api.model_info('Qwen/Qwen2.5-3B-Instruct',files_metadata=True)
    files=[s for s in info.siblings if s.rfilename.endswith('.safetensors') or s.rfilename in
           ('config.json','generation_config.json','tokenizer.json','tokenizer_config.json','merges.txt','vocab.json','model.safetensors.index.json','LICENSE')]
    total=sum(s.size or 0 for s in files)
    assert not info.gated and total<7_700_000_000,(info.gated,total)
    plan=dict(model_id=info.id,revision=info.sha,bytes=total,
        files=[s.rfilename for s in files],license='qwen-research',purpose='noncommercial research/evaluation',
        license_source='https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/raw/main/LICENSE')
    if (HERE/'MODEL_DOWNLOAD_PLAN.json').exists():assert read(HERE/'MODEL_DOWNLOAD_PLAN.json')==plan
    else:save(HERE/'MODEL_DOWNLOAD_PLAN.json',plan)
    for s in files:
        print('DOWNLOAD',s.rfilename,s.size,flush=True)
        hf_hub_download(info.id,s.rfilename,revision=info.sha,local_dir=MODEL)
    charge('model_download',cpu,wall,gpu_process_seconds=0,bytes=sum(p.stat().st_size for p in MODEL.rglob('*') if p.is_file()))
if __name__=='__main__':main()
