"""Refresh progress until the current diagnostic finishes; never launch training."""
import json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];run=Path(sys.argv[1]).resolve();assert run.is_relative_to(HERE/'runs')
while True:
    with (run/'progress_monitor_console.log').open('a') as f:
        result=subprocess.run([sys.executable,str(HERE/'code/summarize_progress.py'),str(run)],stdout=f,stderr=subprocess.STDOUT)
    diag=json.loads((run/'diagnostics_status.json').read_text());tr=json.loads((run/'status.json').read_text())
    if diag['state'] in ('completed','partial_failure','blocked_training_incomplete') or tr['state']=='failed':break
    try:os.kill(tr['pid'],0)
    except ProcessLookupError:break
    time.sleep(30)
