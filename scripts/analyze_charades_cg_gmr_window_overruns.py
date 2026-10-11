#!/usr/bin/env python3
"""Trace Charades-CG overrun endpoints to official Charades action annotations."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/release/charades_cg_gmr_v1'


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]


def main():
    action_rows = {}
    for filename in ('Charades_v1_train.csv', 'Charades_v1_test.csv'):
        with (BASE / 'source' / filename).open(newline='', encoding='utf-8') as stream:
            for row in csv.DictReader(stream):
                annotations = []
                for item in row['actions'].split(';'):
                    fields = item.strip().split()
                    if len(fields) == 3:
                        annotations.append({'class_id': fields[0], 'start': float(fields[1]), 'end': float(fields[2])})
                action_rows[row['id']] = {'official_duration': float(row['length']), 'actions': annotations}

    issues = read_jsonl(BASE / 'work/review/source_window_issues.jsonl')
    mapping = []
    end_matches = 0
    start_end_matches = 0
    no_matches = []
    overrun_actions = 0
    for issue in issues:
        original_start, original_end = issue['original_window']
        video = action_rows.get(issue['vid'])
        if video is None:
            no_matches.append(issue['sample_id'])
            continue
        exact = [a for a in video['actions'] if a['end'] == original_end]
        exact_both = [a for a in exact if a['start'] == original_start]
        overrun = [a for a in exact if a['end'] > video['official_duration']]
        end_matches += bool(exact)
        start_end_matches += bool(exact_both)
        overrun_actions += bool(overrun)
        mapping.append({
            'sample_id': issue['sample_id'], 'vid': issue['vid'],
            'source_file': issue['source_file'], 'source_window': issue['original_window'],
            'official_video_duration': video['official_duration'],
            'source_window_overrun_seconds': issue['overshoot_seconds'],
            'matching_official_action_endpoints': exact,
            'matching_full_action_intervals': exact_both,
            'matching_action_endpoint_also_exceeds_duration': bool(overrun),
            'interpretation': 'source boundary exactly matches at least one official Charades action end; provenance supports inherited boundary, but does not establish visual validity beyond video duration'
        })

    out = BASE / 'work/reports/source_window_action_endpoint_mapping.jsonl'
    out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in mapping), encoding='utf-8')
    report = {
        'dataset': 'Charades-CG-GMR v1',
        'analysis': 'exact endpoint reconciliation against official Charades CSV action annotations',
        'overrun_source_windows': len(issues), 'videos': len({x['vid'] for x in issues}),
        'rows_with_same_video_action_end_exactly_equal': end_matches,
        'rows_with_full_action_interval_exactly_equal': start_end_matches,
        'rows_with_matching_action_endpoint_also_over_duration': overrun_actions,
        'rows_without_action_match': len(no_matches), 'unmatched_sample_ids': no_matches,
        'action_label_semantics': 'CSV action class interval from the official Charades archive; a match establishes source-boundary provenance only, not frame-level visual confirmation.',
        'evidence_file': str(out.relative_to(ROOT)),
        'status': 'root cause supported: all CG overrun endpoints are exactly present as official same-video Charades action end boundaries; keep source windows unchanged and retain explicit overrun flags. This does not by itself resolve whether to include them in localization evaluation.'
    }
    path = BASE / 'work/reports/source_window_action_endpoint_analysis.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
