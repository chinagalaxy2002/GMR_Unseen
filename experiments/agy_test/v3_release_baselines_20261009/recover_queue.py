import fcntl
from run_baselines import ROOT, main
with (ROOT/'recovery.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    main()
