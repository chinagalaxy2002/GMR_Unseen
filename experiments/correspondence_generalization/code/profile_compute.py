"""Measure original-model inference cost separately; no training exposure."""
import hashlib,json,sys,time
from pathlib import Path
import torch
from torch.utils.data import DataLoader
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE/'code'),str(ROOT),str(ROOT/'training/qd_detr_gmr')]
from vendor.qd_dataset import StartEndDataset,start_end_collate,prepare_batch_inputs
from vendor.qd_train import build_dataset_config
from models.qd_detr_gmr import build_model
run=Path(sys.argv[1]).resolve();assert run.is_relative_to(HERE/'runs')
out=run/'compute_profile.json';assert not out.exists()
torch.set_num_threads(4)
c=torch.load(run/'stage_001.ckpt',map_location='cpu',weights_only=False);opt=c['opt'];opt.device='cuda:1';opt.num_workers=0
model,_=build_model(opt);model.load_state_dict(c['model']);model.to(opt.device).eval()
ds=StartEndDataset(**build_dataset_config(opt,opt.eval_path,False,True));meta,batch=next(iter(DataLoader(ds,batch_size=16,num_workers=0,shuffle=False,collate_fn=start_end_collate)));x,_=prepare_batch_inputs(batch,opt.device)
with torch.no_grad():
    model(**x);torch.cuda.synchronize()
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,torch.profiler.ProfilerActivity.CUDA],with_flops=True,record_shapes=True) as prof:model(**x)
    torch.cuda.synchronize()
    s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True)
    s.record()
    for _ in range(20):model(**x)
    e.record();torch.cuda.synchronize()
records=prof.key_averages();flops=sum(k.flops for k in records)
report={'state':'completed_partial_operator_accounting','checkpoint_sha256':hashlib.sha256((run/'stage_001.ckpt').read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'parameters':sum(p.numel() for p in model.parameters()),'batch_qids':[r['qid'] for r in meta],'input_shapes':{k:list(v.shape) for k,v in x.items()},'torch_profile_reported_forward_flops':flops,'profiled_cuda_event_sum_us':sum(getattr(k,'self_device_time_total',0) for k in records),'cuda_event_ms_per_forward_20_repeats':s.elapsed_time(e)/20,'model_inference_forwards':22,'training_updates':0,'training_row_exposures':0,'limitations':'One fixed seen batch, inference only. Torch FLOP counting omits unsupported operators and may omit fused attention; do not multiply this into claimed full training FLOPs. CUDA event elapsed includes launch gaps; not aggregate active GPU time for the training run. GPU0 concurrent training may affect measurement.','operators_with_flop_estimate':[{ 'operator':k.key,'flops':k.flops,'calls':k.count} for k in records if k.flops]}
out.write_text(json.dumps(report,indent=2));print(out)
