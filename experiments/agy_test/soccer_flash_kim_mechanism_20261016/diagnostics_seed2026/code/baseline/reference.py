"""Evaluate the already frozen released checkpoint, without training/tuning."""
from common import ROOT,ASSETS,save,sha,options,dataset,scope_audit
import torch,json
from models.flash_vtg_gmr.model import build_model1
from event_model import EventModel
from evaluation import predict,evaluate

def main():
    torch.set_num_threads(2);opt=options('cpu');base,_=build_model1(opt)
    cp=ASSETS/'checkpoint/flashVTG_gmr';ck=torch.load(cp,map_location='cpu',weights_only=False)
    state=ck.get('model',ck.get('state_dict'));base.load_state_dict({k.removeprefix('module.'):v for k,v in state.items()},strict=True)
    model=EventModel(base,'E0');data=dataset(opt,'test',False)
    pred=predict(model,data,opt);result=evaluate(pred,data.data,opt)
    folder=ROOT/'reference';folder.mkdir(exist_ok=True)
    (folder/'test_predictions.jsonl').write_text(''.join(json.dumps(p)+'\n' for p in pred))
    save(folder/'metrics.json',result)
    save(folder/'PROVENANCE.json',{'checkpoint_sha256':sha(cp),'checkpoint':str(cp),'initialization':'published weights, no training',
        'purpose':'reproduction reference; frozen configuration, not used for tuning','outside_source':scope_audit()})
    print(json.dumps(result['brief']),flush=True)
if __name__=='__main__':main()
