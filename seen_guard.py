"""Frozen, training-free Seen Guard; no target annotations required for scoring."""
import numpy as np
from dec import BACKBONES, cdf, route_evidence, score

def blend_score(train, target, backbone, alpha):
    d = cdf(train['X'][:, BACKBONES[backbone]], target['X'][:, BACKBONES[backbone]]) ** .65
    e = cdf(route_evidence(train['queries'], train['X']), route_evidence(target['queries'], target['X'])) ** .85
    return (1-alpha)*d + alpha*d*e

def score_seen_guard(train, target, setting, query_keys, inventory):
    """Return one score, decoded with score >= 0; keys come only from query text."""
    bb, cal = setting['backbone'], setting['calibration']
    if len(query_keys) != len(target['X']):
        raise ValueError('Query keys and samples must be aligned')
    original = score(train, target, bb, 'dec')
    if setting['mode'] == 'preserve_dec_decisions':
        d = target['X'][:, BACKBONES[bb]].astype(np.float64)
        familiar = np.where(original >= cal['dec_threshold'], 1., -1.) + .25 + np.arctan(d)/(2*np.pi)
    else:
        config = setting['config']
        if config['family'] == 'baseline':
            known_score = target['X'][:, BACKBONES[bb]]
        elif config['family'] == 'blend':
            known_score = blend_score(train, target, bb, config['alpha'])
        else:
            raise ValueError('Unsupported frozen Seen config: '+str(config))
        familiar = (known_score.astype(np.float64)-cal['known_threshold'])/cal['known_scale']
    uncovered = (original-cal['dec_threshold'])/cal['dec_scale']
    covered = np.array([inventory.get(k, 0) > 0 for k in query_keys])
    return np.where(covered, familiar, uncovered)
