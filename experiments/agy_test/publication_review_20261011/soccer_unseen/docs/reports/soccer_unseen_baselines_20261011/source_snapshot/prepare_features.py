"""Extract missing Soccer CLIP/SlowFast videos and exact-query CLIP text tokens."""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
import numpy as np

from common import ROOT, REPO, digest, save_json
from prepare_experiment import inventory, SOCCER

LIGHTHOUSE = Path('/home/guoxiangyu/VLMbasedIter_momentretrival/lighthouse')
CLIP_CODE = Path('/home/guoxiangyu/paper/新建文件夹/MomentofUntruth/UniVTG-NA/run_on_video')
CLIP_WEIGHTS = Path('/home/guoxiangyu/Beyond_Caption-Based_Queries_for_Video_Moment_Retrieval/experiments_and_data/evaluations/flash_vtg_subset_consistency_eval/models/ViT-B-32.pt')
SF_WEIGHTS = ROOT / 'weights/SLOWFAST_8x8_R50.pkl'
sys.path[:0] = [str(ROOT / 'vendor'), str(LIGHTHOUSE), str(CLIP_CODE)]


def atomic_npz(path, **values):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp.npz')
    np.savez_compressed(tmp, **values)
    tmp.replace(path)


def initialize():
    rows = inventory()
    stems = sorted({Path(r['vid']).stem for r in rows.values()})
    missing = []
    manifest = {}
    for name in ('clip', 'slowfast', 'clip_text', 'generated_text'):
        (ROOT / 'features' / name).mkdir(parents=True, exist_ok=True)
    for stem in stems:
        for name, dim in [('clip', 512), ('slowfast', 2304)]:
            existing = SOCCER / name / (stem + '.npz')
            dest = ROOT / 'features' / name / (stem + '.npz')
            if existing.exists():
                with np.load(existing) as d:
                    a = d['features']
                    assert a.ndim == 2 and a.shape[1] == dim and np.isfinite(a).all()
                if not dest.exists():
                    dest.symlink_to(existing)
                manifest[str(dest.relative_to(ROOT))] = dict(source=str(existing), sha256=digest(existing))
        if not all((ROOT / 'features' / n / (stem + '.npz')).exists() for n in ('clip', 'slowfast')):
            video = SOCCER / 'WC2022-GMR' / (stem + '.mp4')
            assert video.is_file(), str(video)
            missing.append(stem)
    save_json(ROOT / 'VIDEO_FEATURE_REUSE.json', manifest)
    save_json(ROOT / 'MISSING_VIDEO_FEATURES.json', missing)
    save_json(ROOT / 'FEATURE_STATUS.json', dict(stage='preparing_features', missing_video_count=len(missing),
        total_videos=len(stems), unique_texts=len({r['query'] for r in rows.values()}),
        protocol='CLIP ViT-B/32 + SlowFast 8x8 R50 K400; 2-second clips, center crop 224',
        existing_features='original Soccer-GMR standard feature archive; only missing videos extracted'))
    print('Videos needing extraction:', len(missing), flush=True)


def text_features():
    import torch
    import clip
    rows = inventory()
    texts = {hashlib.sha256(r['query'].encode()).hexdigest(): r['query'] for r in rows.values()}
    hashes = sorted(texts)
    missing = [h for h in hashes if not (ROOT / 'features/generated_text' / (h + '.npz')).exists()]
    model, _ = clip.load(str(CLIP_WEIGHTS), device='cuda:0', jit=False)
    model.eval()
    with torch.no_grad():
        for start in range(0, len(missing), 64):
            hs = missing[start:start+64]
            tokens = clip.tokenize([texts[h] for h in hs]).to('cuda:0')
            states = model.encode_text(tokens)['last_hidden_state'].float().cpu().numpy()
            masks = (tokens != 0).cpu().numpy().astype(np.int64)
            for h, a, mask in zip(hs, states, masks):
                atomic_npz(ROOT / 'features/generated_text' / (h + '.npz'), last_hidden_state=a, attention_mask=mask)
            print('Text encoding', min(start+64, len(missing)), '/', len(missing), flush=True)
    manifest = []
    for qid, row in rows.items():
        h = hashlib.sha256(row['query'].encode()).hexdigest()
        src = ROOT / 'features/generated_text' / (h + '.npz')
        dest = ROOT / 'features/clip_text' / ('qid' + qid + '.npz')
        if not dest.exists():
            dest.symlink_to(src)
        manifest.append(dict(qid=qid, query_sha256=h, feature_sha256=digest(src), source=str(src)))
    save_json(ROOT / 'TEXT_FEATURE_MANIFEST.json', manifest)
    save_json(ROOT / 'TEXT_ENCODER.json', dict(code=str(CLIP_CODE), weights=str(CLIP_WEIGHTS),
        weights_sha256=digest(CLIP_WEIGHTS), unique_texts=len(texts), context=77,
        output='unprojected last_hidden_state (77,512), attention_mask; all exact-query texts encoded anew'))


def decode(path, fps):
    import torch
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))
    stream = next(s for s in info['streams'] if s['codec_type'] == 'video')
    h, w = int(stream['height']), int(stream['width'])
    height, width = (int(h*224/w), 224) if h >= w else (224, int(w*224/h))
    vf = f'fps={fps},scale={width}:{height},crop=224:224:{int((width-224)/2)}:{int((height-224)/2)}'
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-threads', '2', '-filter_threads', '2',
        '-i', str(path), '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    frames = torch.from_numpy(np.frombuffer(data, np.uint8).reshape(-1,224,224,3).copy())
    rate = stream['avg_frame_rate'].split('/')
    original_fps = math.floor(float(rate[0])/float(rate[1]))
    return frames, {'fps': original_fps, 'duration': float(stream['duration'])}


def video_features(worker, probe=False, num_workers=2):
    import torch
    import clip
    from lighthouse.feature_extractor.vision_encoders.slowfast import SlowFast
    from lighthouse.frame_loaders.slowfast_loader import Preprocessing
    torch.set_num_threads(2)
    model, _ = clip.load(str(CLIP_WEIGHTS), device='cuda:0', jit=False)
    model.eval()
    sf = SlowFast('cuda:0', str(SF_WEIGHTS))
    sf._slowfast_extractor.eval()
    preprocess = Preprocessing('3d', device='cuda:0', target_fps=30, size=224, clip_len=2., padding_mode='tile', min_num_clips=1)
    pending = json.loads((ROOT / 'MISSING_VIDEO_FEATURES.json').read_text())
    assert num_workers > 0 and 0 <= worker < num_workers
    stems = pending[worker::num_workers]
    if probe:
        stems = [next(p.stem for p in (SOCCER / 'clip').glob('WC*.npz'))]
    error_path = ROOT/f'FEATURE_ERRORS_{worker}.json'
    decode_failures = json.loads(error_path.read_text()) if error_path.exists() else []
    qids_by_video = {}
    for qid, row in inventory().items():
        qids_by_video.setdefault(Path(row['vid']).stem, []).append(qid)
    with torch.no_grad():
        for index, stem in enumerate(stems):
            destinations = {n: ROOT / 'features' / n / (stem + '.npz') for n in ('clip','slowfast')}
            if not probe and all(p.exists() for p in destinations.values()):
                continue
            started = time.time()
            path = SOCCER / 'WC2022-GMR' / (stem + '.mp4')
            try:
                frames, _ = decode(path, .5)
                frames = frames.permute(0,3,1,2).float()/255.
                mean = torch.tensor([.48145466,.4578275,.40821073]).view(1,3,1,1)
                std = torch.tensor([.26862954,.26130258,.27577711]).view(1,3,1,1)
                frames = (frames-mean)/std
                cf = torch.cat([model.encode_image(chunk.to('cuda:0')).float().cpu() for chunk in frames.split(32)]).numpy()
                del frames
                frames, info = decode(path, 30)
                chunks = preprocess(frames, info)
                sf_features = sf(chunks, bsz=4).float().cpu().numpy()
                del chunks, frames
                count = min(len(cf),len(sf_features))
                assert count > 0 and np.isfinite(cf).all() and np.isfinite(sf_features).all()
                if not probe:
                    for name, a in [('clip',cf[:count]),('slowfast',sf_features[:count])]:
                        if not destinations[name].exists():
                            atomic_npz(destinations[name],features=a.astype(np.float32))
            except Exception as error:
                import traceback
                import gc
                record = dict(video=stem,qids=qids_by_video.get(stem,[]),error=repr(error),
                    traceback=traceback.format_exc(),action='record_and_skip',
                    updated=time.strftime('%Y-%m-%dT%H:%M:%S'))
                decode_failures.append(record)
                save_json(error_path,decode_failures)
                save_json(ROOT/f'FEATURE_WORKER_{worker}.json',dict(processed=index+1,total=len(stems),
                    errors=len(decode_failures),last_video=stem,last_status='skipped_error'))
                print(worker,index+1,'/',len(stems),stem,'skipped_error',repr(error),flush=True)
                # Clear large failed-video tensors before the next video.
                frames = chunks = cf = sf_features = None
                gc.collect()
                torch.cuda.empty_cache()
                if probe:
                    return
                continue
            if probe:
                result = {}
                for name, a in [('clip',cf[:count]),('slowfast',sf_features[:count])]:
                    old = np.load(SOCCER/name/(stem+'.npz'))['features']
                    n=min(len(old),len(a)); cosine=np.sum(old[:n]*a[:n],axis=1)/(np.linalg.norm(old[:n],axis=1)*np.linalg.norm(a[:n],axis=1)+1e-8)
                    result[name] = dict(existing_shape=list(old.shape),new_shape=list(a.shape),mean_cosine=float(cosine.mean()),min_cosine=float(cosine.min()))
                    atomic_npz(ROOT/'feature_probe'/(name+'.npz'),features=a)
                save_json(ROOT/'FEATURE_PROBE.json',dict(stem=stem,results=result))
                print(json.dumps(result),flush=True)
                return
            save_json(ROOT/f'FEATURE_WORKER_{worker}.json',dict(completed=index+1,total=len(stems),last_video=stem,
                seconds=time.time()-started,updated=time.strftime('%Y-%m-%dT%H:%M:%S')))
            print(worker,index+1,'/',len(stems),stem,round(time.time()-started,1),flush=True)
    save_json(ROOT/f'FEATURE_WORKER_{worker}_EXIT.json',dict(complete=True,total=len(stems),
        errors=len(decode_failures),meaning='all assigned videos attempted; see coverage report for missing features'))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage', choices=['initialize','text','video','probe'])
    parser.add_argument('--worker',type=int,default=0)
    parser.add_argument('--num_workers',type=int,default=2)
    args=parser.parse_args()
    if args.stage=='initialize': initialize()
    elif args.stage=='text': text_features()
    else: video_features(args.worker,probe=args.stage=='probe',num_workers=args.num_workers)
