"""Query-text-only parser cache. Run in the separate pinned spaCy environment."""
import argparse
import json
from pathlib import Path
import numpy as np

SKIP_VERBS={'be','start','begin','continue','go','get','have','do','seem','try'}
CLOTHING={'shoe','sock','boot','coat','jacket','shirt','hat','clothe','dress','sweater','pants'}
PRONOUNS={'it','them','something','anything','one','some','this','that','him','her'}

def query_key(doc):
    verb=next((t for t in doc if t.pos_=='VERB' and t.lemma_.lower() not in SKIP_VERBS),None)
    if verb is None:return None
    base=verb.lemma_.lower();base='close' if base=='shut' else base
    particle=None
    if base in {'take','put','pick'}:
        options=[t for t in verb.children if t.dep_=='prt' and t.lower_ in {'off','on','out','in','down','up'}]
        if not options:
            options=[t for t in verb.children if t.dep_=='prep' and (t.lower_ in {'out','in'} or (t.lower_ in {'off','on'} and any(c.lemma_.lower() in CLOTHING for c in t.children if c.dep_=='pobj')))]
        particle=options[0].lower_ if options else None
    action=base+'_'+particle if particle else base
    direct=[t for t in verb.children if t.dep_ in {'dobj','obj','attr','oprd'} and t.pos_ in {'NOUN','PROPN'}]
    obj=direct[0] if direct else None
    if obj is None:
        for prep in verb.children:
            if prep.dep_ in {'prep','prt','agent'}:
                nouns=[t for t in prep.children if t.dep_=='pobj' and t.pos_ in {'NOUN','PROPN'}]
                if nouns:obj=nouns[0];break
    if obj is None or obj.lemma_.lower() in PRONOUNS:return None
    return action+'|'+obj.lemma_.lower()

def parse_queries(queries):
    import spacy
    nlp=spacy.load('en_core_web_sm',disable=['ner'])
    unique=list(dict.fromkeys(map(str,queries)))
    lookup={q:query_key(doc) for q,doc in zip(unique,nlp.pipe(unique,batch_size=256))}
    return [lookup[str(q)] for q in queries]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path(__file__).resolve().parent/'data')
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent/'calibration/query_keys.json')
    a=p.parse_args();queries=[];datasets=[]
    for split in ('A1','A2_alt','A3','C1','C2_alt'):
        for part in ('train','val','test'):
            with np.load(a.data/split/(part+'.npz'),allow_pickle=False) as z:
                texts=z['queries'].tolist();ids=z['qids'].tolist()
            datasets.append((split,part,ids,len(texts)));queries.extend(texts)
    keys=parse_queries(queries);out={};offset=0
    for split,part,ids,count in datasets:
        out.setdefault(split,{})[part]=dict(qids=ids,keys=keys[offset:offset+count]);offset+=count
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2)+'\n')
    print('Parsed',len(queries),'queries using text only:',a.output)

if __name__=='__main__':main()
