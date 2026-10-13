"""Published selection/early-stop semantics; no model or RNG operations."""
import json
import re
from pathlib import Path


def calibrate_native(labels, scores):
    import numpy as np
    labels = np.asarray(labels)
    scores = np.asarray(scores, dtype=np.float32)
    best_ba, threshold = -1.0, 0.5
    for candidate in np.percentile(scores, np.linspace(5,95,91)):
        accepted = scores >= candidate
        ba = .5*(accepted[labels==1].mean() + (~accepted[labels==0]).mean())
        if ba > best_ba:
            best_ba, threshold = float(ba), float(candidate)
    return threshold, best_ba


def native_predictions(records, predictions, reference_qids, backbone, threshold, native_source):
    import importlib
    import sys
    import types
    import numpy as np
    name = 'publication_native_eval_' + str(abs(hash(str(native_source))))
    package = types.ModuleType(name)
    package.__path__ = [str(Path(native_source)/'eval')]
    sys.modules[name] = package
    metrics = importlib.import_module(name+'.metrics')
    annotations = {str(x['qid']):x for x in records}
    assert set(predictions)==set(annotations)=={str(x) for x in reference_qids}
    records = [annotations[str(qid)] for qid in reference_qids]
    score_key = 'pred_exist_logit' if backbone=='flash' else 'pred_exist_score'
    accept_iou = np.array([metrics._compute_set_iou_score(
        [w[:2] for w in metrics._clean_pred_windows(predictions[str(x['qid'])]['pred_relevant_windows'],max_pred_windows=1)],
        x['relevant_windows']) for x in records])
    result = dict(qids=np.array([str(x['qid']) for x in records]),vids=np.array([x['vid'] for x in records]),
        labels=np.array([x['exist_label'] for x in records]),partitions=np.array([x['partition'] for x in records]),
        scores=np.array([predictions[str(x['qid'])][score_key] for x in records],dtype=np.float32),
        accept_iou=accept_iou,threshold=np.array(threshold))
    return result, records


def selection_value(backbone, brief):
    if backbone == 'flash':
        return (brief['MR-full-R1@0.5'] + brief['MR-full-R1@0.7']) / 2
    value = brief.get('MR-full-mAP', 0.0)
    if backbone == 'qd' and not isinstance(value, (int, float)):
        value = brief.get('MR-full-mIoU', 0.0)
    return value


def selection_trace(backbone, records, patience=26):
    best, best_epoch, count = 0.0, None, 0
    result = []
    for epoch, brief in records:
        score = selection_value(backbone, brief)
        improved = score > best
        if improved:
            best, best_epoch, count = score, epoch, 0
        else:
            count += 1
        stop = count >= patience if backbone == 'moment' else count > patience
        result.append(dict(epoch=epoch, selection_score=score, improved=improved,
                           best_epoch=best_epoch, best_score=best, non_improving_epochs=count,
                           early_stop=stop, patience=patience,
                           stop_comparison='>=' if backbone == 'moment' else '>'))
        if stop:
            break
    return result


def read_native_validation_log(path):
    records = []
    for line in Path(path).read_text().splitlines():
        if '[Metrics]' not in line:
            continue
        prefix, payload = line.split('[Metrics]', 1)
        epoch = int(re.search(r'\[Epoch\]\s+(-?\d+)', prefix).group(1)) + 1
        if epoch > 0:
            records.append((epoch, json.loads(payload.strip())['brief']))
    return records
