#!/usr/bin/env python3
"""Report complete fixed Seen probes; never use partial epochs as complete."""
import argparse
import json
from pathlib import Path

from mechanism_suite import last_row, read_json


def tail_rows(path):
    if not path.exists():
        return []
    with path.open('rb') as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell()-4*1024*1024))
        lines = stream.read().splitlines()
    result = []
    for line in lines:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return result


def report(run):
    epoch = last_row(run/'monitor/fixed_probe.jsonl').get('epoch')
    records = [record for row in tail_rows(run/'monitor/decoder_slots/probe_slots.jsonl')
               if row['epoch'] == epoch for record in row['records']]
    expected = read_json(run/'probe_metadata.json', {}).get('qids', [])
    observed = {r['qid'] for r in records}
    complete = bool(expected) and observed == set(expected)
    groups = []
    for partition, layer in sorted({(r['partition'], r['layer']) for r in records}):
        selected = [r for r in records if r['partition'] == partition and r['layer'] == layer]
        metrics = {}
        for key in ('cosine_offdiag_mean', 'l2_offdiag_mean', 'effective_centered_rank', 'foreground_range',
                    'foreground_std', 'active_count', 'correct_active_count', 'pair_iou_mean',
                    'duplicate_pair_fraction', 'active_duplicate_pair_fraction',
                    'self_attention_slot_cosine', 'cross_attention_slot_cosine'):
            values = [r[key] for r in selected if r.get(key) is not None]
            metrics[key] = sum(values)/len(values) if values else None
        slots = len(selected[0]['foreground_by_slot'])
        metrics['foreground_by_slot'] = [sum(r['foreground_by_slot'][i] for r in selected)/len(selected) for i in range(slots)]
        metrics['self_attention_status'] = sorted({r['self_attention_status'] for r in selected})
        groups.append(dict(partition=partition, layer=layer, n=len(selected), metrics=metrics))
    return dict(run=str(run), epoch=epoch, complete_probe=complete, expected_queries=len(expected),
                observed_queries=len(observed), groups=groups)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', type=Path, required=True)
    args = parser.parse_args()
    print('| Run / epoch | Complete | Subset / layer | n | Slot cosine | Centered rank | Foreground std | Active / correct slots | Duplicate pair fraction | Self / cross attention slot cosine |')
    print('|---|---|---|---:|---:|---:|---:|---|---:|---|')
    def fmt(value):
        return 'N/A' if value is None else f'{value:.4f}'
    for run in args.run:
        result = report(run)
        if not result['groups']:
            print(f"| {run.name} | pending | — | — | — | — | — | — | — | — |")
        for group in result['groups']:
            m = group['metrics']
            print(f"| {run.name} / {result['epoch']} | {result['complete_probe']} | {group['partition']} / {group['layer']} | {group['n']} | {fmt(m['cosine_offdiag_mean'])} | {fmt(m['effective_centered_rank'])} | {fmt(m['foreground_std'])} | {fmt(m['active_count'])} / {fmt(m['correct_active_count'])} | {fmt(m['duplicate_pair_fraction'])} | {fmt(m['self_attention_slot_cosine'])} / {fmt(m['cross_attention_slot_cosine'])} |")


if __name__ == '__main__':
    main()
