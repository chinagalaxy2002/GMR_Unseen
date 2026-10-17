"""Original Flash postprocessing and official Soccer-GMR evaluation."""
from common import ROOT,rows
import copy,numpy as np,torch
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score
from training.flash_vtg_gmr.dataset import start_end_collate
from training.flash_vtg_gmr.inference import compute_mr_results,post_processing_mr_nms
from eval.eval_main import evaluate_gmr
from models.flash_vtg_gmr.standalone_eval.eval import eval_submission

@torch.no_grad()
def predict(model,data,opt,return_pre_nms=False,capture=None):
    logits=[]
    def hook(module,args,out):logits.extend(out['pred_exist_logits'].detach().cpu().double().tolist())
    handle=model.register_forward_hook(hook)
    if capture is not None:capture.attach(model)
    try:
        loader=DataLoader(data,batch_size=1,shuffle=False,num_workers=0,collate_fn=start_end_collate)
        pred,_=compute_mr_results(model,loader,opt,None,None,None)
    finally:
        handle.remove()
        if capture is not None:capture.close()
    assert [p['qid'] for p in pred]==[p['qid'] for p in data.data]
    assert len(logits)==len(pred)
    for p,s in zip(pred,logits):p['pred_exist_logit_raw']=s
    post=post_processing_mr_nms(copy.deepcopy(pred),opt.nms_thd,opt.max_before_nms,opt.max_after_nms,opt.nms_type)
    return (post,pred) if return_pre_nms else post

def native_selection_metrics(pre_nms,gt,opt):
    """Exactly the metric path consumed by the released Flash training loop."""
    return eval_submission(pre_nms,gt,verbose=False,match_number=True,
                           full_only=opt.eval_full_only,mr_only=opt.mr_only)

def evaluate(pred,gt,opt):
    assert len(pred)==len(gt) and {p['qid'] for p in pred}=={p['qid'] for p in gt}
    result=evaluate_gmr(pred,gt,k_list=(1,3,5),max_pred_windows=10,
        cls_thresholds=tuple(opt.cls_thresholds),gmiou_cls_threshold=opt.gmiou_cls_threshold,
        map_num_workers=0,verbose=False)
    ordered={p['qid']:p for p in pred};y=np.asarray([bool(p['relevant_windows']) for p in gt])
    logits=np.asarray([ordered[p['qid']]['pred_exist_logit_raw'] for p in gt])
    scores=np.asarray([ordered[p['qid']]['pred_exist_score'] for p in gt])
    result['brief']['AUROC_raw']=100*roc_auc_score(y,logits)
    for threshold in opt.cls_thresholds:
        result['brief'][f'N-acc@{threshold}']=100*float((scores[~y]<threshold).mean())
        result['brief'][f'PositiveRecall@{threshold}']=100*float((scores[y]>=threshold).mean())
    return result
