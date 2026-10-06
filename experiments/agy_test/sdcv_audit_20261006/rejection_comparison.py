"""Compare rejection at each model's own Seen-selected fixed threshold."""
import sys
sys.dont_write_bytecode = True
import json
import numpy as np
import audit_sdcv as a

def main():
    metrics = json.loads((a.OUT / 'audit_metrics.json').read_text())
    result = {'protocol': 'HQ QD, FlashVTG, DDV thresholds from independent ddv_audit_20261006 Seen-val selection; SDCV threshold independently replayed in this audit. No test-statistic adaptation.', 'splits': {}, 'macro': {}}
    for split in a.SPLITS:
        old = a.load(a.PREV / split / 'audit_predictions.npz')
        new = a.load(a.OUT / (split + '_replay.npz'))
        assert all(np.array_equal(old[k], new[k]) for k in ['qids', 'vids', 'labels', 'partitions'])
        mapping = {str(q): i for i, q in enumerate(new['qids'])}
        pairs = np.array([[mapping[str(p['positive_qid'])], mapping[str(p['negative_qid'])]] for p in a.rows(a.ROOT / 'data/release/semantic_existence_v2' / split / 'matched_u_pairs.jsonl')])
        th = json.loads(old['thresholds_json'].item())
        th['sdcv'] = metrics['splits'][split]['calibration']['seen_threshold']
        result['splits'][split] = {n: a.helper.metrics(new[n], new, pairs, th[n]) for n in ['hq_qd', 'flash_logit', 'ddv', 'sdcv']}
    for n in result['splits']['A1']:
        ms = [result['splits'][s][n] for s in a.SPLITS]
        result['macro'][n] = {k: float(np.mean([m[k] for m in ms])) for k in ms[0] if k != 'threshold'}
    a.write('rejection_comparison.json', result)

if __name__ == '__main__':
    main()
