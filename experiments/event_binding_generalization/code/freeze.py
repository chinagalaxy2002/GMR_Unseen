"""Freeze all decisions before any probe or event-module fit."""
from common import *

def main():
    assert not (BASE / 'EXECUTION_FREEZE.json').exists(), 'Do not reset an existing execution.'
    old = json.loads((STAGE / 'temporal_representation_analysis/FREEZE.json').read_text())
    protected = dict(old['protected_files_sha256'])
    sources = list((REPO / 'models').rglob('*.py')) + list((REPO / 'training').rglob('*.py')) + list((REPO / 'scripts').rglob('*.py')) + list((OLD / 'code').rglob('*.py'))
    for p in sources:
        if '__pycache__' not in str(p):
            protected[str(p)] = sha(p)
    for fam, run in RUNS.items():
        for name in ['pseudo_predictions.jsonl', 'best_seen_predictions.jsonl', 'threshold_frozen.json']:
            protected[str(run / name)] = sha(run / name)
    print('Checking', len(protected), 'protected assets', flush=True)
    bad = [p for p, h in protected.items() if not Path(p).exists() or sha(p) != h]
    assert not bad, bad
    coverage = {}
    for fam in FAMILIES:
        rr = {split: rows(fam, split) for split in ['train', 'seen', 'pseudo']}
        assert not {x['vid'] for x in rr['train']} & {x['vid'] for x in rr['pseudo']}
        for split, rs in rr.items():
            assert all(x.get('source_split') != 'test' and x['partition'] in ['S+', 'S-'] for x in rs)
            # Negative construction rows need not repeat source_split. Views are hash-
            # verified originals; enforce byte membership in legal release train/seen.
            source = (REPO / 'features/semantic_existence_v2/A1/val_seen.jsonl' if split == 'seen'
                      else REPO / 'data/release/semantic_existence_v2/A1/train.jsonl')
            legal_source = read(source)
            assert all(x['partition'] in ['S+', 'S-'] for x in legal_source)
            source_rows = {str(x['qid']): x for x in legal_source}
            assert all(str(x['qid']) in source_rows and x == source_rows[str(x['qid'])] for x in rs)
            coverage[f'{fam}/{split}'] = {'rows': len(rs), 'positive': sum(x['exist_label'] == 1 for x in rs), 'videos': len({x['vid'] for x in rs})}
    config = {
        'created': now(), 'seed': SEED, 'families': FAMILIES, 'release_split': 'A1', 'model': 'QD',
        'allowed': 'A/A1/B only; original model and backbone frozen; training-side pseudo only',
        'forbidden': ['R', 'full model training', 'new decoder', 'boundary regression', 'new features', 'official U/test', 'sit continuation', 'next stage'],
        'action_probe': {'labels': 'semantic_graph.action_class, classes >=10 usable S_train positive GT segments; no test-class fit',
                         'controls': ['motion_temporal', 'motion_mean', 'motion_static', 'appearance_mean'],
                         'projection': 'fixed Gaussian random projection to 128; same parameter count per probe; train-only standardization',
                         'motion_temporal': 'GT segment mean, standard deviation, last-minus-first; no query tokens',
                         'static': 'middle GT segment vector; still retains SlowFast clip-internal motion',
                         'fit': 'multiclass affine; Adam lr .01, weight_decay .0001, 20 epochs, batch512, inverse-frequency class weights; seen balanced accuracy selects epoch'},
        'event_modules': {'width': 32, 'H': 'two raw visual projections, holistic query to both, concat MLP64->72->1',
                          'P': 'motion/action and appearance/object separate projections; two MLP32->64->1; additive logits/sqrt2',
                          'C': 'same independent primitive branches, probability product converted to logit (same-time AND)',
                          'J': 'same primitive projections; concat(zA,zE,zA*zE) MLP96->48->1; visual values even single pair',
                          'T': 'concat holistic/action/object text vectors MLP1536->64->64->1; time-constant',
                          'shared_training': 'five independently fitted models; P/C branches NOT shared across models',
                          'streams': 'raw normalized CLIP512 then SlowFast2304; multiply each by sqrt(dim); no TEF',
                          'context': 'one original temporal bin; pooled features; no identity tracks',
                          'fit': 'AdamW lr .001 weight_decay .0001, batch64, 8 epochs maximum, gradient norm clip5',
                          'loss': 'balanced event BCE on top20%-mean temporal logits plus .5 local softplus: S+ GT only, S- all valid bins; never negative outside positive GT',
                          'checkpoint': 'highest seen AUROC, earliest tie; no pseudo inspection until all models selected',
                          'aggregation': 'top ceil(.2*T) logits mean; same valid mask for positive/negative',
                          'fallback': 'missing/untrusted action or object span uses whole non-special query; all rows retained and flagged'},
        'token_audit': 'same original CLIP BPE vocabulary/tokenizer; original graph character spans or unique graph lexical/regular+fixed irregular inflection match; ambiguous span whole-query fallback; SOT/EOT and 32-token truncation; cache length/provenance audit; no encoder rerun',
        'time_audit': 'all used video shapes/duration; search available extraction source; preserve original min_len and one-second assumption; unverifiable timing forbids PASS',
        'primitive_control': {'scores': 'separate P action and object top20%-mean logits, trained only with original event labels (not pure primitive probabilities)',
                              'support': 'both >= median S_train positive scores; frozen before pseudo inference',
                              'matching': 'all opposite-label, different-video pairs in same joint quartile bins from S_train scores, within high-support subset; pair weighted equally, bootstrap endpoint weight product',
                              'coverage_gate': '>=20 positive and >=20 negative distinct videos per family; operational control, not confirmed primitive labels'},
        'actual_text': 'all pseudo mixed-label exact query groups; canonical lexicographic qid feature/mask AND role vectors for every video in group; T must tie',
        'localization': {'candidates': 'original saved pred_relevant_windows_pre_exist, original order/windows/scores unchanged',
                         'rerank': 'map-only candidate-specific mean logit over centers inside candidate; overlapping-bin fallback if no center; empty support=-1e6; ties original order',
                         'selection': 'fixed map-only rule before evaluation, no coefficient sweep or GT selection',
                         'metric': 'raw R1@.5, all original pseudo positives including missing candidates; T NA',
                         'diagnostics': 'candidate coverage, repairs, damage, chosen original candidate index; GT only for evaluation'},
        'threshold': 'seen-only Youden J, largest threshold ties; module calibrated on seen, not pseudo; original baseline threshold preserved',
        'guardrails': 'seen AUROC/raw and pseudo FRR/RR no worse than original baseline point estimates; PASS additionally needs positive paired J gains and controlled evidence',
        'statistics': '1000 seed3407 bootstrap, union of original videos shared across families/models/controls; query-weighted AUROC and raw R1 within family, families equally weighted; exploratory95% CI; pair endpoint multiplicity product',
        'budget': {'action_fits': 12, 'event_fits': 15, 'event_epochs_per_fit': 8, 'action_epochs_per_fit': 20, 'width_sweeps': 0, 'training_seeds': 1, 'backbone_updates': 0},
        'coverage': coverage, 'protected_files_sha256': protected,
        'code_sha256': {str(p.relative_to(BASE)): sha(p) for p in (BASE / 'code').glob('*.py')},
    }
    dump('EXECUTION_FREEZE.json', config)
    dump('audit/SOURCE_CHECK.json', {'assets_checked': len(protected), 'all_prior_hashes_match': True, 'coverage': coverage})
    status('freeze', 'completed', protected_assets=len(protected))
    print('Execution frozen', flush=True)

if __name__ == '__main__':
    main()
