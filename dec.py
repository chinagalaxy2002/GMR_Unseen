"""Fixed DEC power gate. No learned weights or test-distribution calibration."""
import numpy as np

SPLITS = ('A1', 'A2_alt', 'A3', 'C1', 'C2_alt')
BACKBONES = {'moment': 1, 'qd': 2, 'flash': 0}


def cdf(reference, values):
    """Train-reference empirical CDF with midpoint ties."""
    reference = np.sort(reference)
    if len(reference) == 0:
        raise ValueError('Empty calibration reference')
    return (np.searchsorted(reference, values, 'left') +
            np.searchsorted(reference, values, 'right')) / (2.0 * len(reference))


def route_evidence(queries, features):
    """Historical ordered substring routes; float32 arithmetic preserved."""
    evidence = np.zeros(len(queries), dtype=np.float32)
    for i, query in enumerate(queries):
        query = query.lower()
        if any(word in query for word in ('run', 'walk', 'slow', 'fast')):
            evidence[i] = .50 * features[i, 5] + .35 * features[i, 8] + .15 * features[i, 12]
        elif any(word in query for word in ('chair', 'couch', 'bed', 'sofa', 'box', 'cabinet', 'shelf', 'table', 'cup', 'book')):
            evidence[i] = .45 * features[i, 5] + .35 * features[i, 6] + .20 * features[i, 3]
        else:
            evidence[i] = .55 * features[i, 5] + .30 * features[i, 3] + .15 * features[i, 12]
    return evidence


def score(train, target, backbone, method='dec'):
    column = BACKBONES[backbone]
    if method == 'baseline':
        return target['X'][:, column].copy()
    if method != 'dec':
        raise ValueError(method)
    detector_rank = cdf(train['X'][:, column], target['X'][:, column])
    evidence_rank = cdf(route_evidence(train['queries'], train['X']),
                        route_evidence(target['queries'], target['X']))
    return detector_rank ** .65 * evidence_rank ** .85


def select_threshold(labels, scores):
    """Best Seen-val BA among 91 percentiles (5..95); earliest tie wins."""
    best_threshold, best_ba = .5, -1.
    for threshold in np.percentile(scores, np.linspace(5, 95, 91)):
        accept = scores >= threshold
        positive, negative = labels == 1, labels == 0
        ba = .5 * (accept[positive].mean() + (~accept[negative]).mean())
        if ba > best_ba:
            best_threshold, best_ba = float(threshold), float(ba)
    return best_threshold
