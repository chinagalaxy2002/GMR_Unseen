#!/usr/bin/env python3
"""Create a per-source-row, immutable-window quality flag mapping."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def main():
    videos = {}
    for filename in ('Charades_v1_train.csv', 'Charades_v1_test.csv'):
        with (BASE / 'source' / filename).open(newline='', encoding='utf-8') as stream:
            for row in csv.DictReader(stream):
                actions = []
                for part in row['actions'].split(';'):
                    fields = part.strip().split()
                    if len(fields) == 3:
                        actions.append({'class_id': fields[0], 'start': float(fields[1]), 'end': float(fields[2])})
                videos[row['id']] = {'duration': float(row['length']), 'actions': actions}
    source = read_jsonl(BASE / 'work/staging/positive_source_rows.jsonl')
    out, counters = [], Counter()
    for row in source:
        window = row['relevant_windows'][0]
        video = videos[row['vid']]
        overrun = max(0.0, round(float(window[1]) - video['duration'], 6))
        matches = [a for a in video['actions'] if a['start'] == window[0] and a['end'] == window[1]]
        flag = overrun > 0
        counters['rows'] += 1
        counters['out_of_bounds'] += flag
        counters['exact_official_action_interval_match'] += bool(matches)
        counters['overrun_with_exact_action_match'] += flag and bool(matches)
        out.append({
            'source_qid': row['source_qid'], 'vid': row['vid'],
            'source_file': row['source_file'], 'source_window': window,
            'duration': video['duration'],
            'source_action_interval_exceeds_csv_length': flag,
            'overrun_seconds': overrun,
            'source_action_interval_match': bool(matches),
            'source_action_interval_ids': matches,
            'window_source': 'official Charades-CG JSON; unchanged',
            'visual_confirmation': False,
        })
    path = BASE / 'work/review/source_window_quality_flags.jsonl'
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in out), encoding='utf-8')
    report = {
        'source_rows': counters['rows'],
        'source_action_interval_exceeds_csv_length': counters['out_of_bounds'],
        'exact_official_action_interval_matches': counters['exact_official_action_interval_match'],
        'out_of_bounds_with_exact_source_action_match': counters['overrun_with_exact_action_match'],
        'source_intervals_modified': 0,
        'visual_confirmation_claimed': False,
        'quality_mapping': str(path.relative_to(ROOT)),
    }
    (BASE / 'work/reports/source_window_quality_flag_summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
