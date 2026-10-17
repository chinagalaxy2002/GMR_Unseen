from common import ROOT,ASSETS,rows
import copy,importlib,json
import torch
from easydict import EasyDict
from torch.utils.data import DataLoader

def package(bb):return {'moment':'moment_detr_gmr','qd':'qd_detr_gmr'}[bb]
def modules(bb):
    pkg=package(bb)
    return (importlib.import_module('training.'+pkg+'.dataset'),
            importlib.import_module('models.'+pkg+('.moment_detr' if bb=='moment' else '.model')))

def options(bb,device):
    opt=EasyDict(json.loads((ROOT/'configs'/f'{bb}_protocol.json').read_text()))
    opt.device=torch.device(device)
    opt.train_path=str(ROOT/'data/train.jsonl');opt.eval_path=str(ROOT/'data/val.jsonl')
    opt.v_feat_dirs=[str(ASSETS/'clip'),str(ASSETS/'slowfast')];opt.t_feat_dir=str(ASSETS/'clip_text')
    return opt

def build_model(opt):
    _,module=modules(opt.backbone);model,criterion=module.build_model(opt)
    criterion.to(opt.device)
    return model,criterion

def dataset(opt,split,labels,fixture=False):
    module,_=modules(opt.backbone)
    path=ROOT/'tests/fixture_val.jsonl' if fixture else ROOT/'data'/f'{split}.jsonl'
    result=module.StartEndDataset(dset_name=opt.dset_name,domain=None,data_path=str(path),
        v_feat_dirs=opt.v_feat_dirs,q_feat_dir=opt.t_feat_dir,q_feat_type=opt.q_feat_type,
        v_feat_types=opt.v_feat_types,max_q_l=opt.max_q_l,max_v_l=opt.max_v_l,max_a_l=opt.max_a_l,
        ctx_mode=opt.ctx_mode,clip_len=opt.clip_length,max_windows=opt.max_windows,
        span_loss_type=opt.span_loss_type,load_labels=labels,mr_only=True,keep_empty_gt=True)
    assert len(result)==len(rows(path)),'No missing examples may be dropped'
    return result

def early_stop(opt,es):
    if opt.max_es_cnt<0:return False
    return es>=opt.max_es_cnt if opt.early_stop_rule=='>=' else es>opt.max_es_cnt

@torch.no_grad()
def predict(model,data,opt,return_pre_nms=False,capture=None):
    model.eval();module,_=modules(opt.backbone);pkg=package(opt.backbone)
    utils=importlib.import_module('models.'+pkg+'.utils.span_utils')
    gate=importlib.import_module('models.'+pkg+'.gmr_adapter').apply_existence_gate
    processor=importlib.import_module('training.'+pkg+'.postprocessing').PostProcessorDETR
    loader=DataLoader(data,batch_size=opt.eval_bsz,num_workers=0,shuffle=False,collate_fn=module.start_end_collate)
    answer=[]
    if capture is not None:capture.attach(model)
    try:
        for batch in loader:
            inputs,_=module.prepare_batch_inputs(batch[1],opt.device)
            if capture is not None:capture.batch_meta=batch[0]
            out=model(**inputs)
            spans=out['pred_spans'].cpu();fg=out['pred_logits'].softmax(-1)[...,0].cpu()
            logits=out['pred_exist_logits'].reshape(-1).cpu();probs=logits.sigmoid()
            scores=gate(fg,probs,opt.exist_gate_thd,hard=False)
            for i,meta in enumerate(batch[0]):
                xy=utils.span_cxw_to_xx(spans[i])*float(meta['duration'])
                if opt.backbone=='qd':xy=xy.clamp(0,float(meta['duration']))
                def ordered(s):
                    w=torch.cat([xy,s[:,None]],1).tolist()
                    return [[float(f'{v:.4f}') for v in row] for row in sorted(w,key=lambda row:row[2],reverse=True)]
                answer.append({'qid':meta['qid'],'query':meta['query'],'vid':meta['vid'],
                    'pred_relevant_windows':ordered(scores[i]),'pred_relevant_windows_pre_exist':ordered(fg[i]),
                    'pred_exist_score':float(f'{float(probs[i]):.4f}'),'pred_exist_logit_raw':float(logits[i])})
    finally:
        if capture is not None:capture.close()
    postprocess=processor(clip_length=opt.clip_length,min_ts_val=0,max_ts_val=150,
        min_w_l=1,max_w_l=150,move_window_method='left',process_func_names=('clip_ts','round_multiple'))
    answer=postprocess(answer)
    assert [r['qid'] for r in answer]==[r['qid'] for r in data.data]
    # Original Moment/QD evaluate entry points apply no additional NMS.
    return (copy.deepcopy(answer),answer) if return_pre_nms else answer

def native_selection_metrics(pred,gt,opt):
    module=importlib.import_module('training.'+package(opt.backbone)+'.standalone_eval.eval')
    return module.eval_submission(pred,gt,verbose=False)
