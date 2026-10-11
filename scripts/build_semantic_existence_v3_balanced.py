#!/usr/bin/env python3
"""Add traceable CLIP-ranked cross-video pseudo negatives to the audited v3 release."""
import argparse
import copy
import csv
import datetime
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('A1_v3', 'A2_v3', 'A3_v3', 'C1_v3', 'C2_v3')
SPLITS = ('train', 'val', 'test')
VERSION = 'v3-balanced-clip-cross-video-1.0.0'
PAPER = 'https://openaccess.thecvf.com/content/WACV2025/papers/Flanagan_Moment_of_Untruth_Dealing_with_Negative_Queries_in_Video_Moment_WACV_2025_paper.pdf'


def read_rows(path):
    with path.open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def file_inventory(folder):
    return {str(p.relative_to(folder)): sha256(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def canon(value):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', (value or '').lower())).strip()


# These held-out predicates reproduce apply_full_semantic_audit_v3.py, whose
# top-level audit mutation makes importing that script unsafe.
def text_forms(event):
    values = [event.get(k) for k in ('anchor_concept', 'concept', 'anchor_object', 'theme')]
    return [re.sub(r'\s+', ' ', str(v).lower().replace('_', ' ')).strip() for v in values if v]


def has_concept(event, target):
    forms = text_forms(event)
    if target == 'couch':
        return any(re.search(r'\b(couch|sofa)\b', form) for form in forms)
    if target == 'cabinet':
        return any(form == 'cabinet' or 'cabinet entry' in form or 'cabinet door' in form
                   or 'cabinet drawer' in form or 'drawer in cabinet' in form
                   or 'door of cabinet' in form for form in forms)
    if target == 'box':
        return any(form == 'box' or 'box lid' in form or 'lid of box' in form
                   or 'box door' in form for form in forms)
    return any(re.search(rf'\b{re.escape(target)}\b', form) for form in forms)


def active(event):
    return event.get('assertion', 'asserted') not in {'purpose', 'intended', 'negated'}


def held_event(event, spec):
    if not active(event):
        return False
    action = event.get('action_family')
    if spec['axis'] == 'action_family':
        return action in spec['held_action_families']
    for family, concept in spec['held_compositions']:
        if action != family or not has_concept(event, concept):
            continue
        role = event.get('anchor_role')
        if family == 'sit' and role in {'support_surface', 'location'}:
            return True
        if family in {'open', 'close'} and role == 'theme':
            return True
    return False


def row_held(row, spec):
    return any(held_event(e, spec) for e in row.get('events', []))


ACTION_ALIASES = {
    'take': 'physical_take', 'pick_up': 'physical_take', 'take_out': 'physical_take',
    'grab': 'physical_take', 'grasp': 'physical_take', 'remove': 'physical_take',
    'place': 'physical_place', 'put_in': 'physical_place', 'put_down': 'physical_place',
    'sit_down': 'sit', 'stand_up': 'stand', 'lie_down': 'lie',
    'take_picture': 'photograph', 'switch_on': 'turn_on', 'light_up': 'turn_on',
    'groom_hair': 'groom', 'view': 'look', 'inspect': 'look', 'stare': 'look',
    'toss': 'throw', 'wake': 'awaken', 'attempt_open': 'open', 'attempt_close': 'close',
}
OPPOSITES = {frozenset(pair) for pair in (
    ('open', 'close'), ('turn_on', 'turn_off'), ('dress', 'undress'),
    ('physical_take', 'physical_place'), ('sit', 'stand'), ('enter', 'exit'))}


def event_action(event):
    action = event.get('action_family')
    return ACTION_ALIASES.get(action, action)


def event_objects(event):
    forms = text_forms(event)
    for key in ('location', 'support_surface'):
        if isinstance(event.get(key), str):
            forms.append(event[key])
    aliases = {'sofa': 'couch', 'refrigerator': 'fridge', 'cellphone': 'phone',
               'cell phone': 'phone', 'mobile phone': 'phone', 'television': 'tv',
               'cupboard': 'cabinet'}
    result = set()
    for form in forms:
        form = canon(form.replace('_', ' '))
        for before, after in aliases.items():
            form = re.sub(rf'\b{re.escape(before)}\b', after, form)
        form = re.sub(r'^(a |an |the |some |their |his |her )', '', form)
        result.add(form)
    return result


def event_conflict(donor, target_rows):
    """Conservative annotation-only veto; this cannot certify video absence."""
    if any(canon(donor['query']) == canon(r['query']) for r in target_rows):
        return 'identical_positive_query'
    for first in donor['events']:
        if not active(first):
            continue
        action_a, objects_a = event_action(first), event_objects(first)
        for row in target_rows:
            for second in row['events']:
                if not active(second):
                    continue
                action_b, objects_b = event_action(second), event_objects(second)
                same_action = action_a == action_b
                opposite = frozenset((action_a, action_b)) in OPPOSITES
                if not (same_action or opposite):
                    continue
                # Generic or agent-only anchors do not establish distinct events.
                generic = {'', 'person', 'man', 'woman', 'someone', 'object', 'something',
                           'food', 'drink', 'liquid', 'clothes', 'clothing', 'item', 'thing'}
                forms = objects_a | objects_b
                broad = (not objects_a or not objects_b or bool(forms & generic)
                         or any(re.search(r'\b(unspecified|unknown|something|objects?|items?|things?)\b', s)
                                for s in forms)
                         or first.get('anchor_role') != second.get('anchor_role'))
                overlap = any(a == b or f' {a} ' in f' {b} ' or f' {b} ' in f' {a} '
                              for a in objects_a for b in objects_b if a and b)
                if broad or overlap:
                    return 'positive_event_overlap' if same_action else 'opposite_event_same_anchor'
    return None


def encode_queries(queries, args, source_hash):
    import torch
    sys.path.insert(0, str(args.clip_code.resolve()))
    import clip

    args.cache.mkdir(parents=True, exist_ok=True)
    weights_hash = sha256(args.clip_weights)
    key = hashlib.sha256(json.dumps([queries, weights_hash, VERSION, 'full-bpe-77-no-truncation']).encode()).hexdigest()
    path = args.cache / f'clip_text_{key}.npz'
    metadata = {'model': 'OpenAI CLIP ViT-B/32', 'checkpoint': str(args.clip_weights.resolve()),
                'checkpoint_sha256': weights_hash, 'clip_code': str(args.clip_code.resolve()),
                'clip_model_code_sha256': sha256(Path(clip.__file__).parent / 'model.py'),
                'embedding': 'EOT hidden state projected by text_projection, L2 normalized',
                'context_length': 77, 'truncation': False,
                'tokenization': 'CLIP SimpleTokenizer BPE, full text, SOT/EOT, zero padding; fail if >77 tokens',
                'tokenizer_code_sha256': sha256(Path(clip.__file__).parent / 'simple_tokenizer.py'),
                'unique_queries': len(queries),
                'torch_version': torch.__version__, 'numpy_version': np.__version__,
                'device': args.device, 'source_positive_sha256': source_hash,
                'cache_file': str(path.resolve())}
    if path.exists():
        with np.load(path, allow_pickle=False) as data:
            if data['queries'].tolist() != queries:
                raise ValueError('Embedding cache query mismatch')
            embeddings = data['embeddings'].copy()
        print(f'Reused CLIP sentence vectors: {path}', flush=True)
    else:
        torch.manual_seed(args.seed)
        model, _ = clip.load(str(args.clip_weights), device=args.device, jit=False)
        model.eval()
        from clip.simple_tokenizer import SimpleTokenizer
        tokenizer = SimpleTokenizer()
        sot = tokenizer.encoder['<|startoftext|>']
        eot = tokenizer.encoder['<|endoftext|>']
        batches = []
        with torch.inference_mode():
            for start in range(0, len(queries), args.batch_size):
                batch_queries = queries[start:start + args.batch_size]
                tokens = torch.zeros((len(batch_queries), 77), dtype=torch.long, device=args.device)
                for index, query in enumerate(batch_queries):
                    ids = [sot] + tokenizer.encode(query) + [eot]
                    if len(ids) > 77:
                        raise ValueError(f'Query exceeds CLIP context; refusing silent truncation: {query}')
                    tokens[index, :len(ids)] = torch.tensor(ids, device=args.device)
                encoded = model.encode_text(tokens)
                features = encoded['pooler_output'] if isinstance(encoded, dict) else encoded
                features = torch.nn.functional.normalize(features.float(), dim=-1)
                batches.append(features.cpu().numpy())
                if start % (args.batch_size * 10) == 0:
                    print(f'CLIP encoded {min(start + args.batch_size, len(queries))}/{len(queries)}', flush=True)
        embeddings = np.concatenate(batches)
        np.savez_compressed(path, queries=np.asarray(queries), embeddings=embeddings)
    if not np.isfinite(embeddings).all() or not np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-5):
        raise ValueError('Invalid CLIP sentence vectors')
    metadata['cache_sha256'] = sha256(path)
    return embeddings, metadata


def pseudo_scores(donors, targets, references, embeddings, query_index, device, batch_size):
    import torch
    torch.backends.cuda.matmul.allow_tf32 = False
    reference_rows = [r for vid in targets for r in references[vid]]
    target_index = {vid: i for i, vid in enumerate(targets)}
    ref_video = torch.tensor([target_index[r['vid']] for r in reference_rows], device=device)
    ref = torch.tensor(embeddings[[query_index[r['query']] for r in reference_rows]], device=device)
    scores = np.empty((len(donors), len(targets)), dtype=np.float32)
    with torch.inference_mode():
        for start in range(0, len(donors), batch_size):
            rows = donors[start:start + batch_size]
            vec = torch.tensor(embeddings[[query_index[r['query']] for r in rows]], device=device)
            sims = vec @ ref.T
            maximum = torch.full((len(rows), len(targets)), -float('inf'), device=device)
            maximum.scatter_reduce_(1, ref_video.expand(len(rows), -1), sims, reduce='amax', include_self=True)
            scores[start:start + len(rows)] = maximum.cpu().numpy()
    return scores


def quotas(rows, needed):
    positives = Counter(r['partition'][0] for r in rows if r['exist_label'] == 1)
    # Largest remainder allocation; these quotas concern additions, not total S/U balance.
    total = sum(positives.values())
    result = {kind: needed * count // total for kind, count in positives.items()}
    remainder_order = sorted(positives, key=lambda k: (-(needed * positives[k] % total), k))
    for kind in remainder_order[:needed - sum(result.values())]:
        result[kind] += 1
    return result


def add_negatives(group, split, rows, spec, references, embeddings, query_index, args):
    npos = sum(r['exist_label'] == 1 for r in rows)
    needed = npos - (len(rows) - npos)
    if needed < 0:
        raise ValueError(f'{group}/{split}: preserving originals cannot achieve balance by adding negatives')
    # One representative per text avoids overweighting frequent duplicate annotations.
    by_query = {}
    for row in sorted(rows, key=lambda r: r['qid']):
        if row['exist_label'] == 1:
            by_query.setdefault(row['query'], row)
    donors = list(by_query.values())
    targets = sorted({r['vid'] for r in rows})
    if any(not references[vid] for vid in targets):
        raise ValueError(f'{group}/{split}: target video without positive references')
    scores = pseudo_scores(donors, targets, references, embeddings, query_index, args.device, args.batch_size)
    target_index = {vid: i for i, vid in enumerate(targets)}
    all_rows = {r['vid']: r for r in rows}
    existing = {(r['vid'], canon(r['query'])) for r in rows}
    quota = quotas(rows, needed)
    local_seed = int.from_bytes(hashlib.sha256(f'{args.seed}/{group}/{split}'.encode()).digest()[:8], 'big')
    rng = np.random.default_rng(local_seed)
    candidate_lists, rank_maps, donor_kinds, cutoffs = [], [], [], []
    pool_counts = Counter()
    for i, donor in enumerate(donors):
        eligible = np.delete(np.arange(len(targets)), target_index[donor['vid']])
        # Stable sort breaks cosine ties by lexicographic target video ID.
        order = eligible[np.argsort(scores[i, eligible], kind='stable')]
        low = order[:len(order) // 2]
        ranks = np.zeros(len(targets), dtype=np.int32)
        ranks[low] = np.arange(1, len(low) + 1)
        rank_maps.append(ranks)
        cutoffs.append(float(scores[i, low[-1]]) if len(low) else None)
        candidate_lists.append(rng.permutation(low).astype(np.int32))
        kind = 'U' if row_held(donor, spec) else 'S'
        donor_kinds.append(kind)
        pool_counts[kind] += len(low)
    cursor = [0] * len(donors)
    added, selected_counts, rejected = [], Counter(), Counter()
    # Round-robin donors: reuse a query on distinct target videos only as needed.
    while len(added) < needed:
        progress = False
        for i in rng.permutation(len(donors)):
            kind = donor_kinds[i]
            if selected_counts[kind] >= quota.get(kind, 0):
                continue
            donor = donors[i]
            choices = candidate_lists[i]
            while cursor[i] < len(choices):
                j = choices[cursor[i]]
                cursor[i] += 1
                vid = targets[j]
                pair = (vid, canon(donor['query']))
                if pair in existing:
                    rejected['existing_or_duplicate_video_query'] += 1
                    continue
                reason = event_conflict(donor, references[vid])
                if reason:
                    rejected[reason] += 1
                    continue
                n = len(targets) - 1
                rank = int(rank_maps[i][j])
                qid = 'balneg_' + hashlib.sha256(f'{VERSION}/{group}/{split}/{vid}/{donor["qid"]}'.encode()).hexdigest()[:24]
                annotation = {
                    'qid': qid, 'query': donor['query'], 'vid': vid, 'video_id': vid,
                    'duration': all_rows[vid]['duration'], 'split': split, 'group': group,
                    'exist_label': 0, 'relevant_windows': [], 'partition': kind + '-',
                    'semantic_status': 'unseen' if kind == 'U' else 'seen',
                    'novelty_type': 'unseen' if kind == 'U' else 'seen',
                    'events': copy.deepcopy(donor['events']),
                    'semantic_graph': copy.deepcopy(donor.get('semantic_graph')),
                    'construction_type': 'clip_in_domain_cross_video_pseudo_negative',
                    'existence_status': 'pseudo_absent_unverified',
                    'verification_status': 'clip_rank_and_annotation_veto_only_no_video_review',
                    'source_qid': donor['qid'], 'source_vid': donor['vid'], 'source_split': split,
                    'source_query': donor['query'], 'source_windows': donor['relevant_windows'],
                    'generation_rule_version': VERSION,
                    'clip_filter': {
                        'pseudo_similarity': float(scores[i, j]), 'rank_ascending': rank,
                        'candidate_video_count': n, 'retained_video_count': n // 2,
                        'rank_fraction': rank / n, 'retained_fraction': 0.5,
                        'cutoff_similarity': cutoffs[i],
                        'ranking_scope': 'same_group_same_split_videos_except_donor_video',
                        'tie_break': 'lexicographic_target_vid',
                        'target_positive_reference_count': len(references[vid]),
                        'reference_pool': 'all_clean_v3_positive_annotations_of_target_video',
                        'formula': 'max cosine(CLIP(query), CLIP(target_positive_query))',
                        'embedding_metadata': '../../clip_metadata.json',
                        'paper_section': '3.3 In-Domain Negatives',
                    },
                    'annotation_conflict_check': 'all_target_clean_positive_queries_and_active_events_passed',
                    'label_caveat': 'Low text similarity does not prove event absence; no video verification.',
                }
                added.append(annotation)
                existing.add(pair)
                selected_counts[kind] += 1
                progress = True
                break
        if not progress:
            raise RuntimeError(f'{group}/{split}: insufficient candidates for quotas {quota}; got {dict(selected_counts)}')
    print(f'{group}/{split}: positive={npos}, old_negative={len(rows)-npos}, added={len(added)}, partitions={dict(selected_counts)}', flush=True)
    return added, {
        'group': group, 'split': split, 'positive': npos, 'original_negative': len(rows) - npos,
        'added_negative': len(added), 'negative': npos, 'rows': npos * 2,
        'original_quadrants': dict(Counter(r['partition'] for r in rows)),
        'quadrants': dict(Counter(r['partition'] for r in rows + added)),
        'added_quadrant_quotas': quota, 'donor_unique_query_count': len(donors),
        'target_video_count': len(targets), 'bottom_half_pool_before_veto': dict(pool_counts),
        'visited_rejected_candidates': dict(rejected), 'sampling_seed': local_seed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/release/semantic_existence_v3_release')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/release/semantic_existence_v3_balanced')
    parser.add_argument('--cache', type=Path, default=ROOT / 'data/processed/semantic_existence_v3_balanced')
    parser.add_argument('--clip-code', type=Path, required=True)
    parser.add_argument('--clip-weights', type=Path, required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--seed', type=int, default=3407)
    parser.add_argument('--batch-size', type=int, default=128)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f'Refusing to overwrite {args.output}')
    source_inventory = file_inventory(args.source)
    positives = read_rows(args.source / 'master/positive_clean.jsonl')
    references = defaultdict(list)
    for row in positives:
        references[row['vid']].append(row)
    queries = sorted({r['query'] for r in positives})
    embeddings, metadata = encode_queries(queries, args, source_inventory['master/positive_clean.jsonl'])
    query_index = {query: i for i, query in enumerate(queries)}
    specs = json.loads((args.source / 'selection/split_specs.json').read_text())['groups']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='v3_balanced_stage_', dir=args.output.parent) as tmp:
        stage = Path(tmp) / args.output.name
        stage.mkdir()
        shutil.copytree(args.source / 'ontology', stage / 'ontology')
        shutil.copytree(args.source / 'selection', stage / 'selection')
        shutil.copytree(args.source / 'master', stage / 'master')
        summary, all_added = [], []
        for group in GROUPS:
            folder = stage / 'splits' / group
            folder.mkdir(parents=True)
            for name in ('matched_u_pairs.jsonl', 'test_matched_u.jsonl'):
                shutil.copy2(args.source / 'splits' / group / name, folder / name)
            group_stats = []
            for split in SPLITS:
                rows = read_rows(args.source / 'splits' / group / f'{split}.jsonl')
                added, stats = add_negatives(group, split, rows, specs[group], references, embeddings, query_index, args)
                write_rows(folder / f'{split}.jsonl', rows + added)
                write_rows(stage / 'provenance' / group / f'{split}_added.jsonl', added)
                if split == 'val':
                    write_rows(folder / 'val_seen.jsonl', [r for r in rows + added if r['partition'].startswith('S')])
                all_added.extend(added)
                group_stats.append(stats)
            summary.extend(group_stats)
            dump(folder / 'statistics.json', {'group': group, 'rows': sum(r['rows'] for r in group_stats),
                 **{r['split']: r['rows'] for r in group_stats}, 'by_split': group_stats,
                 'partition_counts': dict(sum((Counter(r['quadrants']) for r in group_stats), Counter())),
                 'test_matched_u_rows': len(read_rows(folder / 'test_matched_u.jsonl')),
                 'revision': VERSION})
            counts = {f'{r["split"]}_{part}': count for r in group_stats for part, count in r['quadrants'].items()}
            dump(folder / 'semantic_inventory.json', {'group': group, 'spec': specs[group], 'counts': counts,
                 'revision': VERSION, 'inherited_audit_status': 'complete',
                 'new_negative_status': 'pseudo_negative_no_video_verification'})
        write_rows(stage / 'master/negative_added.jsonl', all_added)
        # negative_clean remains the reviewed v3 pool; additions are explicitly separate.
        dump(stage / 'clip_metadata.json', metadata)
        dump(stage / 'source_manifest.json', {'source': str(args.source.resolve()), 'sha256': source_inventory})
        dump(stage / 'splits/summary.json', summary)
        dump(stage / 'statistics.json', summary)
        with (stage / 'statistics.csv').open('w', newline='') as stream:
            fields = ['group', 'split', 'positive', 'original_negative', 'added_negative', 'negative', 'rows', 'S+', 'S-', 'U+', 'U-']
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for r in summary:
                writer.writerow({**{k: r[k] for k in fields[:7]}, **{p: r['quadrants'].get(p, 0) for p in fields[7:]}})
        protocol = {
            'version': VERSION, 'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source': str(args.source.resolve()), 'seed': args.seed, 'paper': PAPER,
            'official_repository': 'https://github.com/keflanagan/MomentofUntruth',
            'official_repository_reference_commit': 'ac2adcdd56230a3169adf965fc7926d3ee2784ce',
            'builder_sha256': sha256(Path(__file__)),
            'paper_verified': 'Section 3.3, page 5339; official repository does not publish the offline sampling script.',
            'ranking': 'For each donor query: score every same-split target video except its donor video by maximum CLIP text cosine; sort ascending; retain floor(N/2).',
            'ties': 'Exact float32 ties resolved by lexicographic target video ID; no absolute cosine cutoff.',
            'target_reference_policy': 'All clean source-master positives of each eligible target video, including held-out queries omitted from train, are used solely for annotation filtering; these queries are not training samples.',
            'donor_policy': 'Only positive rows already released in this group and split; one representative (smallest qid) per exact text; repeated donor use on distinct videos allowed.',
            'selection': 'Seeded donor round robin with randomly permuted retained target lists, rejecting duplicate canonical video-query pairs and annotation conflicts.',
            'added_S_U_allocation': 'Largest remainder quotas proportional to original S+/U+ counts within each split; only S- in train; no requirement of separate S/U balance.',
            'annotation_veto': 'Exact canonical query match, any active overlapping event with the same action and compatible/generic anchor, or listed opposite actions on the same anchor; includes conservative aliases in builder.',
            'original_rows': 'All source train/val/test rows retained byte-for-byte as file prefixes; original qids, video assignments, labels and partitions unchanged.',
            'matched_u': 'Original matched-U files retained unchanged; cross-video additions do not constitute source-matched counterfactual pairs.',
            'shared_negative_pools': 'Original reviewed pools retained; new train negatives are group-specific because train positive counts and held-out definitions differ. The complete new train pools are not identical across axis groups.',
            'video_review_performed': False, 'new_labels_are_pseudo': True,
            'limitation': 'Low CLIP text similarity and annotation veto do not prove video event absence; video annotations can be incomplete.',
            'command': sys.argv,
        }
        dump(stage / 'construction_protocol.json', protocol)
        report_lines = ['# Semantic Existence v3 Balanced', '',
            'Independent extension of `semantic_existence_v3_release`; all original rows are retained.', '',
            '## Counts', '', '| Group | Split | Positive | Original negative | Added pseudo negative | Final negative | S+ | S− | U+ | U− |',
            '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in summary:
            q = r['quadrants']
            report_lines.append(f'| {r["group"]} | {r["split"]} | {r["positive"]} | {r["original_negative"]} | {r["added_negative"]} | {r["negative"]} | {q.get("S+",0)} | {q.get("S-",0)} | {q.get("U+",0)} | {q.get("U-",0)} |')
        report_lines.extend(['', '## Construction and interpretation', '',
            f'Implements the per-query lowest 50% video ranking in [Moment of Untruth, Section 3.3]({PAPER}). Scores are maxima of L2-normalized projected CLIP EOT sentence vectors against all clean positive query annotations of the target video. Candidate videos come from the same group and split, excluding the donor video. The bottom floor(N/2) is selected before annotation vetoes; exact ties use video ID order. A cosine value of 0.5 is never used as a threshold.', '',
            'The v3 full-event held-out predicates are preserved, including assertion state, object aliases and anchor roles. Donors are existing group/split positives; train additions contain S− only. Validation/test addition quotas follow original S+/U+ proportions. Total split balance does not imply balance within Seen/Unseen; inherited C1 U− already outnumbers U+.', '',
            'All target-video clean positive annotations are used for filtering, including held-out train-video annotations that are never inserted into training. Exact query matches and conservative semantic overlaps/opposites on the same anchor are vetoed. These checks cannot detect all false negatives. **Every added label is a pseudo negative, without video verification; low similarity does not prove absence.**', '',
            'Each negative stores its donor qid/video/split, independent qid, cosine score, ascending rank, candidate count, cutoff and reference count. `provenance/` and `master/negative_added.jsonl` contain only additions. `master/negative_clean.jsonl` remains the original reviewed pool, avoiding any claim that additions were reviewed. Original matched-U files are retained unchanged.', '',
            'Original shared reviewed pools are preserved in `selection/`; full augmented training pools are group-specific. Original audit metadata is in the source release. Source SHA256 checksums are frozen in `source_manifest.json`; `checksums.sha256` covers this release. `clip_metadata.json` identifies weights, encoder code, embedding cache and numeric environment. Feature vectors remain in ignored `data/processed/`.', '',
            'Use `val_seen.jsonl` for checkpoint/threshold selection. Freeze Seen-validation choices before Unseen evaluation. Report AUROC, actual Rej-F1 and G-mIoU separately on Seen/Unseen; class proportions influence Rej-F1 and G-mIoU, including after this augmentation. This construction does not establish any model performance improvement.', '',
            '## Reproduce / validate', '', 'Exact build arguments are recorded in `construction_protocol.json`.', '',
            '```bash', 'python scripts/validate_semantic_existence_v3_balanced.py', '```', ''])
        (stage / 'README.md').write_text('\n'.join(report_lines), encoding='utf-8')
        dump(stage / 'release_info.json', {'release': args.output.name, 'based_on': args.source.name,
             'version': VERSION, 'status': 'built_pending_validation', 'added_pseudo_negative_qids': len(all_added),
             'groups': list(GROUPS), 'new_negative_video_verification': False})
        if file_inventory(args.source) != source_inventory:
            raise RuntimeError('Source release changed during construction')
        # Preserve even the source JSONL whitespace for every original row.
        for group in GROUPS:
            for split in SPLITS:
                path = stage / 'splits' / group / f'{split}.jsonl'
                additions = (stage / 'provenance' / group / f'{split}_added.jsonl').read_bytes()
                original = (args.source / 'splits' / group / f'{split}.jsonl').read_bytes()
                if original and not original.endswith(b'\n'):
                    raise ValueError('Source JSONL requires a final newline for byte-preserving extension')
                path.write_bytes(original + additions)
        stage.rename(args.output)
    print(f'Built {args.output}; added {len(all_added)} pseudo negatives', flush=True)


if __name__ == '__main__':
    main()
