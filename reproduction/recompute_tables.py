"""Recompute published tables into an isolated directory; no training."""
import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT / 'reproduction_outputs/paper_tables')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    path = ROOT / 'experiments/agy_test/paper_tables_20261006/build_tables.py'
    spec = importlib.util.spec_from_file_location('published_table_builder', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = a.output.resolve()
    module.main()
    print('Tables, JSON, CSV and input hashes:', module.OUT)

if __name__ == '__main__': main()
