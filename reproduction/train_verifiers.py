"""Run the original 400-epoch recipe in a new output directory on one GPU."""
import argparse
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / 'experiments/agy_test/independent_candidate_transfer_suite'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--gpu', type=int, default=0)
    p.add_argument('--seeds', type=int, nargs='+', default=[3407, 42, 2024])
    p.add_argument('--splits', nargs='+', choices=['A1', 'A2_alt', 'A3', 'C1', 'C2_alt'], default=['A1', 'A2_alt', 'A3', 'C1', 'C2_alt'])
    p.add_argument('--output', type=Path, default=ROOT / 'reproduction_outputs/verifiers')
    a = p.parse_args()
    # Set the mask before importing torch through the original training module.
    os.environ['CUDA_VISIBLE_DEVICES'] = str(a.gpu)
    spec = importlib.util.spec_from_file_location('original_verifier_training', SUITE / 'scripts/03_run_multi_seed_transfer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.RUNS_DIR = a.output / 'runs'
    module.REPORTS_DIR = a.output / 'reports'
    module.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in a.seeds:
        for split in a.splits:
            folder = module.RUNS_DIR / 'target_specific' / f'seed_{seed}' / split
            if folder.exists(): raise FileExistsError('Choose a new --output; refusing to overwrite ' + str(folder))
            # Preserve source order and one RNG reset per split/seed from the published recipe.
            result = module.process_split_seed(split, seed, 0, regime='target_specific')
            results.append({k: v for k, v in result.items() if k not in ['predictions', 'labels', 'partitions', 'vids']})
            (module.REPORTS_DIR / 'retrained_target_specific.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Saved new checkpoints and query predictions to', a.output)

if __name__ == '__main__': main()
