"""Summarize all finished experiments and print comparison table."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def summarize():
    runs_dir = ROOT / 'runs'
    reports = []
    
    for run_path in sorted(runs_dir.iterdir()):
        if not run_path.is_dir():
            continue
        test_metrics_file = run_path / 'test_metrics.json'
        config_file = run_path / 'CONFIG.json'
        selected_file = run_path / 'selected.json'
        
        if test_metrics_file.exists() and config_file.exists():
            test_m = json.loads(test_metrics_file.read_text())
            cfg = json.loads(config_file.read_text())
            sel = json.loads(selected_file.read_text()) if selected_file.exists() else {}
            
            reports.append({
                'run_name': run_path.name,
                'job': cfg['job']['run_id'],
                'seed': cfg['seed'],
                'val_epoch': sel.get('epoch', 'N/A'),
                'val_AUROC': sel.get('AUROC', 0.0),
                'test_AUROC': test_m['AUROC'],
                'test_G_04': test_m['gate_04']['G-mIoU@1'],
                'test_G_05': test_m['fixed_05']['G-mIoU@1'],
                'test_G_06': test_m['gate_06']['G-mIoU@1'],
                'test_G_val_BA': test_m['val_BA_calibrated']['G-mIoU@1'],
                'test_G_val_G': test_m['val_G_calibrated']['G-mIoU@1'],
                'test_G_max': test_m['max_gmiou_scan'],
                'neg_rec_05': test_m['fixed_05']['negative_recall'],
                'pos_rec_05': test_m['fixed_05']['positive_recall'],
                'rej_f1_05': test_m['fixed_05']['Rej-F1'],
            })
            
    if not reports:
        print("No completed test metrics found yet.")
        return

    print("\n" + "=" * 120)
    print("MOMENT-CONDITIONED EVENT VERIFICATION (MCEV) - EXPERIMENTAL BENCHMARK SUMMARY")
    print("=" * 120)
    header = f"{'Run Name':<30} | {'Test AUROC':<10} | {'G@0.5':<7} | {'Val-BA->G':<9} | {'Val-G->G':<8} | {'Max-G':<7} | {'NegRec':<7} | {'PosRec':<7} | {'Rej-F1':<7}"
    print(header)
    print("-" * 120)
    
    # Baselines for context (Seed 2026)
    print(f"{'E0 Baseline (s2026)':<30} | {'74.30%':<10} | {'43.57%':<7} | {'42.35%':<9} | {'54.40%':<8} | {'54.85%':<7} | {'70.9%':<7} | {'61.4%':<7} | {'66.4%':<7}")
    print(f"{'Task A Control (s2026)':<30} | {'74.01%':<10} | {'49.13%':<7} | {'52.82%':<9} | {'54.15%':<8} | {'54.66%':<7} | {'84.3%':<7} | {'52.4%':<7} | {'71.2%':<7}")
    print(f"{'A3 minneg (s2026)':<30} | {'75.30%':<10} | {'54.70%':<7} | {'48.71%':<9} | {'54.61%':<8} | {'54.75%':<7} | {'99.2%':<7} | {'41.0%':<7} | {'75.0%':<7}")
    print("-" * 120)

    for r in reports:
        line = (f"{r['run_name']:<30} | "
                f"{r['test_AUROC']:<9.2f}% | "
                f"{r['test_G_05']:<7.2f} | "
                f"{r['test_G_val_BA']:<9.2f} | "
                f"{r['test_G_val_G']:<8.2f} | "
                f"{r['test_G_max']:<7.2f} | "
                f"{r['neg_rec_05']:<6.1f}% | "
                f"{r['pos_rec_05']:<6.1f}% | "
                f"{r['rej_f1_05']:<7.2f}")
        print(line)
    print("=" * 120 + "\n")
    
    # Save as JSON and Markdown
    summary_path = ROOT / 'reports' / 'BENCHMARK_SUMMARY.json'
    summary_path.write_text(json.dumps(reports, indent=2))
    
    md_lines = [
        "# MCEV Experimental Benchmark Summary\n",
        "| Run | Test AUROC | G@0.5 | Val-BA Calibrated | Val-G Calibrated | Test Max G | NegRec@0.5 | PosRec@0.5 | Rej-F1@0.5 |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        "| **E0 Baseline (s2026)** | 74.30% | 43.57% | 42.35% | 54.40% | 54.85% | 70.9% | 61.4% | 66.4% |",
        "| **Task A Control (s2026)** | 74.01% | 49.13% | 52.82% | 54.15% | 54.66% | 84.3% | 52.4% | 71.2% |",
        "| **A3 minneg (s2026)** | 75.30% | 54.70% | 48.71% | 54.61% | 54.75% | 99.2% | 41.0% | 75.0% |",
    ]
    for r in reports:
        md_lines.append(f"| **{r['run_name']}** | {r['test_AUROC']:.2f}% | {r['test_G_05']:.2f}% | {r['test_G_val_BA']:.2f}% | {r['test_G_val_G']:.2f}% | {r['test_G_max']:.2f}% | {r['neg_rec_05']:.1f}% | {r['pos_rec_05']:.1f}% | {r['rej_f1_05']:.2f}% |")
    
    (ROOT / 'reports' / 'BENCHMARK_SUMMARY.md').write_text('\n'.join(md_lines) + '\n')


if __name__ == '__main__':
    summarize()
