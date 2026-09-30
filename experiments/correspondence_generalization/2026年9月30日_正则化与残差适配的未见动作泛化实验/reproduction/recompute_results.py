"""Recompute archived test metrics; no checkpoint, features, GPU or training."""
import gzip, json
from pathlib import Path
from sklearn.metrics import roc_auc_score

STAGE = Path(__file__).resolve().parents[1]
def read(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return f.read()
def rows(path):
    return [json.loads(line) for line in read(path).splitlines()]
def iou(a, b):
    intersection = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return intersection / union if union > 0 else 0.0
def mean(values):
    return sum(values) / len(values)
def check(actual, expected, name):
    assert abs(actual - expected) < 1e-12, (name, actual, expected)

def main():
    count = 0
    for run in sorted((STAGE / 'logs').glob('formal_*')):
        report = json.loads(read(run / 'test/report.json.gz'))
        truth = rows(run / 'views/test.jsonl.gz')
        pred = {str(p['qid']): p for p in rows(run / 'test/test_predictions.jsonl.gz')}
        assert len(pred) == len(truth) and all(str(r['qid']) in pred for r in truth)
        def hit(r, raw=True):
            p = pred[str(r['qid'])]
            windows = p.get('pred_relevant_windows_pre_exist', p['pred_relevant_windows']) if raw else p['pred_relevant_windows']
            windows = sorted(windows, key=lambda w: w[2], reverse=True)
            return max((iou(windows[0], gt) for gt in r['relevant_windows']), default=0) if windows else 0
        if 'quadrants' in report:
            threshold = json.loads(read(run / 'threshold_frozen.json.gz'))['threshold']
            for name, partitions in [('seen', ('S+', 'S-')), ('unseen', ('U+', 'U-'))]:
                rr = [r for r in truth if r['partition'] in partitions]
                pos = [r for r in rr if r['exist_label'] == 1]
                neg = [r for r in rr if r['exist_label'] == 0]
                score = lambda r: pred[str(r['qid'])]['pred_exist_score']
                ref = report['quadrants'][name]
                check(float(roc_auc_score([r['exist_label'] for r in rr], [score(r) for r in rr])), ref['auroc'], name + '_auroc')
                check(mean([score(r) < threshold for r in pos]), ref['positive_frr'], 'frr')
                check(mean([score(r) < threshold for r in neg]), ref['negative_rr'], 'rr')
                for th in (.5, .7):
                    key = f'R1@{th}'
                    check(mean([hit(r) >= th for r in pos]), ref['raw'][key], 'raw_' + key)
                    check(mean([hit(r, False) >= th for r in pos]), ref['official_gated'][key], 'official_' + key)
                    check(mean([hit(r) >= th and score(r) >= threshold for r in pos]), ref['diagnostic_hard'][key], 'hard_' + key)
                    correct = [r for r in pos if hit(r) >= th]
                    check(mean([score(r) < threshold for r in correct]), ref['raw_correct_positive_frr'][str(th)], 'correct_frr')
        else:
            for partition in ('S+', 'U+'):
                rr = [r for r in truth if r['partition'] == partition]
                ref = report['positive_vtg'][partition]
                assert len(rr) == ref['n']
                for th in (.5, .7):
                    check(mean([hit(r, False) >= th for r in rr]), ref[f'R1@{th}'], partition)
                check(mean([hit(r, False) for r in rr]), ref['miou'], 'miou')
        count += 1
        print('PASS', run.name)
    assert count == 6, count
    print('All six runs reproduce the archived ranking, rejection and localization metrics.')

if __name__ == '__main__':
    main()
