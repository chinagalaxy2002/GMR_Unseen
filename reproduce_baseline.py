"""Baseline-only reproduction; compare with evaluate.py for DEC regressions."""
from evaluate import run
if __name__ == '__main__':
    run(methods=('baseline',))
