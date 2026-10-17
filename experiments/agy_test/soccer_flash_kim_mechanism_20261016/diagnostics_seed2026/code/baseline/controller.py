"""Run exactly E0/E2 sequentially, only on an idle GPU; never stop other jobs."""
from common import ROOT,save,scope_audit
import os,json,sys,fcntl,subprocess,time

def main():
    lock=(ROOT/'controller.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert json.loads((ROOT/'DATA_AUDIT.json').read_text())['state']=='PASS'
    for device in ['cpu','cuda']:
        assert json.loads((ROOT/'tests'/f'MODEL_CHECKS_{device}.json').read_text())['state']=='PASS'
    for variant in ['E0','E2']:
        assert json.loads((ROOT/'tests/smoke_runs'/variant/'COMPLETE.json').read_text())['smoke_only'] is True
    # GPU inventory only. A near-empty device avoids competing with the main
    # conversation's existing training queue. Child sees one GPU as cuda:0.
    for variant in ['E0','E2']:
        if (ROOT/'runs'/variant/'COMPLETE.json').exists():continue
        child=None;last=0;handle=None
        while True:
            if child is None:
                info=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
                eligible=[]
                for line in info.splitlines():
                    idx,mem,util=[int(x.strip()) for x in line.split(',')]
                    if mem<1500 and util<10:eligible.append(idx)
                if eligible:
                    gpu=eligible[0];env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu))
                    handle=(ROOT/'logs'/f'{variant}.log').open('a')
                    child=subprocess.Popen([sys.executable,'-B',str(ROOT/'code/run.py'),'--variant',variant],
                        cwd=ROOT,env=env,stdout=handle,stderr=subprocess.STDOUT)
                    save(ROOT/'QUEUE_STATUS.json',{'state':'running','variant':variant,'pid':child.pid,'gpu':gpu,'updated':time.time()})
                else:
                    save(ROOT/'QUEUE_STATUS.json',{'state':'waiting_for_idle_gpu','next':variant,'updated':time.time(),
                        'condition':'memory.used<1500MiB and utilization<10%; existing jobs left running'})
            if child is not None and child.poll() is not None:
                handle.close()
                if child.returncode:
                    save(ROOT/'QUEUE_STATUS.json',{'state':'failed','variant':variant,'returncode':child.returncode,'updated':time.time()})
                    return
                break
            if time.time()-last>60:
                subprocess.run([sys.executable,'-B',str(ROOT/'code/status.py')],cwd=ROOT,check=True);last=time.time()
            time.sleep(20)
    subprocess.run([sys.executable,'-B',str(ROOT/'code/status.py')],cwd=ROOT,check=True)
    save(ROOT/'QUEUE_STATUS.json',{'state':'complete','updated':time.time(),'outside_source':scope_audit()})
if __name__=='__main__':main()
