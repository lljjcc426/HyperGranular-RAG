"""One bounded NF4 + LoRA fit; answer-only loss; adapter-only checkpoint."""
from common import *
import random

def run():
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
    from peft import LoraConfig,get_peft_model,prepare_model_for_kbit_training
    cpu=time.process_time();wall=time.perf_counter();torch.set_num_threads(1);torch.manual_seed(1729);random.seed(1729)
    status='STARTED';step=0
    try:
        tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
        source=[r for r in read(LOCAL/'adapt_data.json') if r['split']=='train'];encoded=[]
        for r in source:
            msgs=[dict(role='system',content=r['system']),dict(role='user',content=r['user'])]
            prefix=tok.apply_chat_template(msgs,tokenize=True,add_generation_prompt=True)
            target=json.dumps(r['target'],ensure_ascii=False,separators=(',',':'))
            ids=tok.apply_chat_template(msgs+[dict(role='assistant',content=target)],tokenize=True,add_generation_prompt=False)
            if hasattr(ids,'input_ids'):ids=ids.input_ids
            if hasattr(prefix,'input_ids'):prefix=prefix.input_ids
            assert ids[:len(prefix)]==prefix and len(ids)>len(prefix)
            if len(ids)>1024:raise RuntimeError(('TRAIN_TARGET_WOULD_TRUNCATE',r['source'],len(ids)))
            labels=[-100]*len(prefix)+ids[len(prefix):]
            encoded.append((ids,labels,r['source']))
        q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
        base=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,quantization_config=q,device_map={'':'cuda:0'},dtype=torch.bfloat16)
        base=prepare_model_for_kbit_training(base,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False})
        model=get_peft_model(base,LoraConfig(r=8,lora_alpha=16,lora_dropout=.05,target_modules=['q_proj','k_proj','v_proj','o_proj'],bias='none',task_type='CAUSAL_LM'))
        model.config.use_cache=False;model.train();opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4)
        torch.cuda.reset_peak_memory_stats();opt.zero_grad();losses=[];order=list(range(len(encoded)))
        for epoch in range(3):
            random.shuffle(order)
            for batchstart in range(0,len(order),8):
                indices=order[batchstart:batchstart+8]
                for i in indices:
                    ids,labels,src=encoded[i];x=torch.tensor([ids],device='cuda');y=torch.tensor([labels],device='cuda')
                    with torch.autocast('cuda',dtype=torch.bfloat16):loss=model(input_ids=x,attention_mask=torch.ones_like(x),labels=y).loss
                    if not torch.isfinite(loss):raise RuntimeError('NONFINITE_TRAIN_LOSS')
                    losses.append(float(loss));(loss/len(indices)).backward()
                gn=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
                if not torch.isfinite(gn):raise RuntimeError('NONFINITE_TRAIN_GRADIENT')
                opt.step();opt.zero_grad();step+=1
                entry=dict(step=step,epoch=epoch,mean_loss=sum(losses[-len(indices):])/len(indices),gradient_norm=float(gn),peak_gpu_bytes=torch.cuda.max_memory_allocated())
                append(LOCAL/'train_steps.jsonl',entry);print(entry,flush=True)
                if step==1:
                    save(HERE/'TRAIN_STEP_CHECK.json',dict(**entry,status='REAL_OPTIMIZER_STEP_PASSED',microbatch=1,accumulation=8,
                        target_only_loss=True,max_tokens=max(len(x[0]) for x in encoded),train_records=len(encoded),
                        trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad)))
                budget(time.perf_counter()-wall,time.process_time()-cpu)
                if step>=150:break
            if step>=150:break
        dest=HERE/'adapters'/'v27';dest.mkdir(parents=True,exist_ok=True);model.save_pretrained(dest)
        status='TRAINED_ADAPTER_ONLY';save(HERE/'TRAIN_RESULT.json',dict(status=status,steps=step,epochs=3,mean_loss=sum(losses)/len(losses),rank=8,alpha=16,dropout=.05,lr=1e-4,
            quantization='NF4 double quant BF16 compute',base=str(MODEL),adapter='adapters/v27',selection='PENDING_GROUPED_DEVELOPMENT_COMPARISON'))
    except Exception as e:
        append(LOCAL/'training_errors.jsonl',dict(type=type(e).__name__,message=str(e),steps=step));raise
    finally:charge('v27_train',cpu,wall,gpu_process_seconds=time.perf_counter()-wall,status=status,optimizer_steps=step)

if __name__=='__main__':run()
