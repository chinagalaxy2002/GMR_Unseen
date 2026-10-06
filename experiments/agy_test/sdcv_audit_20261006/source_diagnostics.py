"""Check whether Seen validation negatives use the same source video."""
import sys
sys.dont_write_bytecode = True
import audit_sdcv as a

def main():
    result = {}
    for split in a.SPLITS:
        rows = a.rows(a.ROOT / 'data/release/semantic_existence_v2' / split / 'val.jsonl')
        mapping = {str(r['qid']): r for r in rows}
        neg = [r for r in rows if r['partition'] == 'S-']
        resolved = [r for r in neg if str(r.get('source_qid')) in mapping]
        result[split] = {'seen_validation_negative_count': len(neg), 'source_qid_resolved': len(resolved), 'same_source_video': sum(r['vid'] == mapping[str(r['source_qid'])]['vid'] for r in resolved)}
    a.write('source_diagnostics.json', result)

if __name__ == '__main__':
    main()
