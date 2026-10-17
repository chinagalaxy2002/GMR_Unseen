"""Check diagnostic definitions and verify hooks leave predictions identical."""
from common import ROOT,save,options,dataset
from diagnostics import candidate_stats,pair_ranking,FeatureCapture,fixed_val_panel
from evaluation import predict,native_selection_metrics
from event_model import EventModel
from models.flash_vtg_gmr.model import build_model1
import torch,json

def main():
    torch.set_num_threads(2)
    gt=[{'qid':1,'vid':'v','query':'a','relevant_windows':[[0,10]]},
        {'qid':2,'vid':'v','query':'b','relevant_windows':[]},
        {'qid':3,'vid':'v','query':'c','relevant_windows':[[0,10],[20,30]]}]
    pred=[{'qid':1,'pred_exist_score':.2,'pred_exist_logit_raw':-1.,'pred_relevant_windows':[[20,30,.9],[0,10,.8]]},
          {'qid':2,'pred_exist_score':.8,'pred_exist_logit_raw':1.,'pred_relevant_windows':[[0,10,.9]]},
          {'qid':3,'pred_exist_score':.9,'pred_exist_logit_raw':2.,'pred_relevant_windows':[[0,10,.9],[20,30,.8]]}]
    stats,_=candidate_stats(pred,gt,[.4,.95]);s=stats['top10']
    assert s['coverage_iou05']==1 and s['P3_wrong_given_coverage']==.5
    assert s['thresholds']['0.4']['P4_rejection_given_coverage']==.5
    assert s['thresholds']['0.95']['P4_rejection_given_coverage']==1
    assert s['thresholds']['0.4']['N_acc']==0
    assert s['mean_gt_recall_iou05']==1
    assert pair_ranking(pred,gt)['micro_accuracy']==.5
    opt=options('cpu');ds=dataset(opt,'val',False,True);records=[]
    for variant in ['E0','E2']:
        torch.manual_seed(2024);base,_=build_model1(opt);model=EventModel(base,variant)
        plain,pre=predict(model,ds,opt,return_pre_nms=True)
        capture=FeatureCapture(fixed_val_panel(ds.data))
        captured,captured_pre=predict(model,ds,opt,return_pre_nms=True,capture=capture)
        assert plain==captured and pre==captured_pre,'Diagnostics altered predictions'
        assert len(capture.records)==len(ds) and not capture.handles
        assert all('temporal_encoder_2' in r['tensors'] for r in capture.records.values())
        if variant=='E2':assert all('event_query_after_temporal_2' in r['tensors'] for r in capture.records.values())
        native=native_selection_metrics(pre,ds.data,opt)
        assert 'MR-full-mAP' in native['brief']
        records.append({'variant':variant,'prediction_parity':True,'captured':len(capture.records),
                        'native_pre_nms_selection_score':native['brief']['MR-full-mAP']})
    save(ROOT/'tests/DIAGNOSTICS_CHECKS.json',{'state':'PASS','known_candidate_P3_P4_Nacc_and_pair_definitions':'PASS',
         'diagnostic_hooks_preserve_predictions':True,'records':records,
         'data':'Val fixtures and explicitly synthetic definition checks; no Test model selection'})
    print(json.dumps(records),flush=True)
if __name__=='__main__':main()
