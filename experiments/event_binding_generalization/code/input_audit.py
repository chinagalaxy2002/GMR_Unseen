"""Stage A: full cache/span audit after the motion readout diagnostic."""
from common import *
import collections, importlib.util, re

CLIP_CODE = Path('/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video/clip')

def tokenizer():
    spec = importlib.util.spec_from_file_location('isolated_clip_tokenizer', CLIP_CODE / 'simple_tokenizer.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.SimpleTokenizer()

IRREGULAR = {'sit':['sitting','sat'], 'stand':['standing','stood'], 'throw':['throwing','threw','thrown'],
             'lie':['lying','lay','lain'], 'run':['running','ran'], 'take':['taking','took','taken'],
             'put':['putting'], 'begin':['beginning','began','begun'], 'hold':['holding','held'],
             'drink':['drinking','drank','drunk'], 'eat':['eating','ate','eaten'], 'wear':['wearing','wore','worn'],
             'leave':['leaving','left'], 'get':['getting','got'], 'read':['reading'], 'fall':['falling','fell','fallen']}

def role_span(row, role):
    """Use original spans or unique graph-surface lexical match; no result-based parse."""
    graph = row['semantic_graph']; key = role+'_span'
    if graph.get(key) is not None:
        return graph[key], 'original_graph_span'
    values = [graph.get('action'), graph.get('action_base'), graph.get('action_class')] if role=='action' else [graph.get('object')]
    variants = set()
    for value in values:
        if not value:
            continue
        value = value.lower(); variants.add(value)
        if role == 'action' and ' ' not in value:
            variants.update([value+'s', value+'es', value+'ed', value+'ing'])
            if value.endswith('e'):
                variants.update([value+'d', value[:-1]+'ing'])
            if value.endswith('y'):
                variants.update([value[:-1]+'ies', value[:-1]+'ied'])
            variants.update(IRREGULAR.get(value, []))
    matches = {(m.start(),m.end()) for value in variants for m in re.finditer(r'(?<!\w)'+re.escape(value)+r'(?!\w)', row['query'].lower())}
    if len(matches)==1:
        return list(next(iter(matches))), 'unique_graph_lexical_inflection'
    return None, 'missing_or_ambiguous_graph_lexical_match'

def tokenize_span(row, tokmodule, tok, cache_len):
    query = row['query']
    clean = tokmodule.whitespace_clean(tokmodule.basic_clean(query)).lower()
    ids = [tok.encoder['<|startoftext|>']]; offsets = [None]
    for match in tok.pat.finditer(clean):
        encoded = ''.join(tok.byte_encoder[b] for b in match.group().encode('utf-8'))
        bpe = tok.bpe(encoded).split(' ')
        ids.extend(tok.encoder[x] for x in bpe)
        offsets.extend([list(match.span())] * len(bpe))
    ids.append(tok.encoder['<|endoftext|>']); offsets.append(None)
    assert ids[1:-1] == tok.encode(query)
    length_ok = cache_len == len(ids)
    unchanged = clean == query.lower()
    valid_n = min(cache_len, 32)
    non_special = [i for i in range(1, min(len(ids)-1, valid_n))]
    masks = {}; failures = {}; span_sources = {}; resolved_spans = {}
    for role, key in [('action', 'action_span'), ('object', 'object_span')]:
        span, span_sources[role] = role_span(row, role)
        resolved_spans[role] = span
        indices = []
        if length_ok and unchanged and span is not None and len(span) == 2 and 0 <= span[0] < span[1] <= len(query):
            indices = [i for i, off in enumerate(offsets[:valid_n]) if off and off[0] < span[1] and off[1] > span[0]]
        masks[role] = indices if indices else non_special
        failures[role] = None if indices else ('cache_length' if not length_ok else 'cleaning_changes_offsets' if not unchanged else 'missing_or_truncated_span')
    return {'qid': str(row['qid']), 'query': query, 'cache_length': cache_len, 'bpe_length_with_special': len(ids),
            'length_matches': length_ok, 'clean_unchanged': unchanged, 'token_ids': ids, 'token_offsets': offsets,
            'special_sot': ids[0], 'special_eot': ids[-1], 'eot_in_loaded_32': len(ids) <= 32,
            'truncated_tokens': max(0, len(ids)-32), 'loaded_tokens': valid_n,
            'action_indices': masks['action'], 'object_indices': masks['object'], 'fallback': failures,
            'resolved_spans': resolved_spans, 'span_sources': span_sources,
            'graph_action_span': row['semantic_graph'].get('action_span'), 'graph_object_span': row['semantic_graph'].get('object_span'),
            'graph_action_class': row['semantic_graph'].get('action_class'), 'graph_object_concept': row['semantic_graph'].get('object_concept'),
            'canonicalization_confidence': row['semantic_graph'].get('canonicalization_confidence')}

def main():
    assert (BASE / 'audit/ACTION_PROBE.json').exists(), 'Motion probe must finish first.'
    assert not (BASE / 'audit/INPUT_AUDIT.json').exists()
    status('input_audit', 'running')
    module, tok = tokenizer()
    allrows = {}; used_vids = {}; coverage = {}
    for fam in FAMILIES:
        for split in ['train', 'seen', 'pseudo']:
            rs = rows(fam, split)
            for x in rs:
                qid = str(x['qid'])
                if qid in allrows:
                    assert allrows[qid]['query'] == x['query']
                allrows[qid] = x; used_vids[x['vid']] = x['duration']
    spans = {}; token_coverage = collections.Counter(); text_records = []
    for qid, x in sorted(allrows.items()):
        p = TEXT / f'qid{qid}.npz'
        with np.load(p) as archive:
            assert archive.files == ['last_hidden_state'], (p, archive.files)
            feat = archive['last_hidden_state']
            assert feat.ndim == 2 and feat.shape[1] == 512 and np.isfinite(feat).all()
        record = tokenize_span(x, module, tok, len(feat)); spans[qid] = record
        token_coverage['total'] += 1
        token_coverage['length_match'] += record['length_matches']
        token_coverage['offset_clean_unchanged'] += record['clean_unchanged']
        token_coverage['eot_loaded'] += record['eot_in_loaded_32']
        for role in ['action', 'object']:
            token_coverage[role+'_span_valid'] += record['fallback'][role] is None
        token_coverage['positive_symlink'] += x['exist_label'] == 1 and p.is_symlink()
        token_coverage['negative_symlink'] += x['exist_label'] == 0 and p.is_symlink()
        text_records.append({'qid': qid, 'label': x['exist_label'], 'path': str(p), 'resolved_path': str(p.resolve()), 'sha256': sha(p), 'shape': list(feat.shape), 'normalized_loaded_hash': hashlib.sha256(normalized(feat[:32]).tobytes()).hexdigest()})
    jsonl('audit/QUERY_DECOMPOSITION.jsonl', spans.values())
    jsonl('audit/TEXT_CACHE_PROVENANCE.jsonl', text_records)
    video_records = []; mismatches = collections.Counter()
    for vid, duration in sorted(used_vids.items()):
        record = {'vid': vid, 'duration': duration, 'streams': {}}
        lengths = []
        for stream, dim in [('vid_clip', 512), ('vid_slowfast', 2304)]:
            p = VIDEO / stream / (vid+'.npz')
            with np.load(p) as archive:
                keys = archive.files; a = archive['features']
                assert a.ndim == 2 and a.shape[1] == dim and np.isfinite(a).all()
            record['streams'][stream] = {'shape': list(a.shape), 'npz_keys': keys, 'sha256': sha(p), 'bins_minus_duration_seconds': float(len(a)-duration)}
            lengths.append(len(a))
        record['min_len'] = min(*lengths, 200)
        record['clip_minus_slowfast_bins'] = lengths[0]-lengths[1]
        mismatches[str(lengths[0]-lengths[1])] += 1
        video_records.append(record)
    jsonl('audit/VIDEO_TIME_AUDIT.jsonl', video_records)
    primitive_records = []
    hashes = {x['qid']:x['normalized_loaded_hash'] for x in text_records}
    for fam in FAMILIES:
        coverage[fam] = {}
        for split in ['train', 'seen', 'pseudo']:
            rs = rows(fam, split); byvid = collections.defaultdict(list); byquery = collections.defaultdict(list)
            for x in rs:
                if x['exist_label'] == 1:
                    byvid[x['vid']].append(x)
                byquery[x['query']].append(x)
            supported = 0; overlapping = 0
            for x in rs:
                if x['exist_label'] != 0:
                    continue
                g = x['semantic_graph']; action = g.get('action_class'); entity = g.get('object_concept')
                action_rows = [p for p in byvid[x['vid']] if action and p['semantic_graph'].get('action_class') == action]
                entity_rows = [p for p in byvid[x['vid']] if entity and p['semantic_graph'].get('object_concept') == entity]
                overlap = any(max(a[0], b[0]) < min(a[1], b[1]) for p in action_rows for q in entity_rows for a in p['relevant_windows'] for b in q['relevant_windows'])
                both = bool(action_rows and entity_rows); supported += both; overlapping += overlap
                primitive_records.append({'family':fam, 'split':split, 'qid':str(x['qid']), 'vid':x['vid'], 'action':action, 'object':entity,
                                          'event_absent_source':x.get('verification_status'), 'construction_type':x.get('construction_type'),
                                          'action_annotated_positive_qids':[str(p['qid']) for p in action_rows], 'object_annotated_positive_qids':[str(p['qid']) for p in entity_rows],
                                          'both_video_level_entailments':both, 'positive_witness_windows_overlap':overlap,
                                          'binding_label':'unknown; event entailment and canonical graph do not establish identity/role binding'})
            groups = [g for g in byquery.values() if {x['exist_label'] for x in g}=={0,1} and len({x['vid'] for x in g})>1]
            coverage[fam][split] = {'rows':len(rs), 'action_span_valid':sum(spans[str(x['qid'])]['fallback']['action'] is None for x in rs),
                                    'object_span_valid':sum(spans[str(x['qid'])]['fallback']['object'] is None for x in rs),
                                    'negative_video_primitive_witnesses':supported, 'negative_overlapping_witness_windows':overlapping,
                                    'mixed_label_same_query_groups':len(groups), 'mixed_label_same_query_rows':sum(map(len, groups)),
                                    'already_identical_actual_text_groups':sum(len({hashes[str(x['qid'])] for x in g})==1 for g in groups)}
    jsonl('audit/PRIMITIVE_LABEL_COVERAGE.jsonl', primitive_records)
    audit = {'created':now(), 'token_coverage':dict(token_coverage), 'unique_videos':len(video_records), 'clip_minus_slowfast_bin_histogram':dict(mismatches),
             'source_sha256':{str(CLIP_CODE / 'simple_tokenizer.py'):sha(CLIP_CODE / 'simple_tokenizer.py'), str(CLIP_CODE / 'bpe_simple_vocab_16e6.txt.gz'):sha(CLIP_CODE / 'bpe_simple_vocab_16e6.txt.gz')},
             'stream_order':'CLIP512 | SlowFast2304 | TEF2 original; new semantic heads exclude TEF',
             'token_interpretation':'BPE lengths/spans audited with original tokenizer; cached positive old encoder token IDs/weights not embedded, so length agreement is necessary, not proof of exact encoder provenance. Role vectors remain contextual.',
             'temporal_alignment':{'status':'UNVERIFIED_ASSUMPTION', 'timestamps_present':False, 'extraction_manifest_available':False,
                                   'reason':'Caches store features only, no extraction command/stride/start-center provenance tied by hash to these arrays. Available run_on_video scripts default clip_len=2 and are not linked to Charades archives.',
                                   'preserved_behavior':'original min_len truncation and clip_length=1; no invented interpolation or resampling',
                                   'consequence':'subsequent B results conditional on original index alignment; cannot PASS for joint temporal mechanism'},
             'coverage':coverage, 'roles':'one primary action/object from original graph; no comprehensive multi-role parse, no identity evidence',
             'primitive_labels':'S- only event absence. Positive event witnesses provide canonical video-level/overlapping-window entailments, not exhaustive human primitive or binding labels.'}
    dump('audit/INPUT_AUDIT.json', audit)
    status('input_audit', 'completed', token_rows=len(spans), videos=len(video_records), time_alignment='unverified assumption')
    print(json.dumps({'token_coverage':dict(token_coverage), 'videos':len(video_records), 'alignment':'unverified assumption'}, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        status('input_audit', 'failed', error=repr(e)); raise
