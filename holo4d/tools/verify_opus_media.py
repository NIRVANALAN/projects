"""Decode every new movie and verify exact frame-index/ping-pong correspondence."""
import argparse
import json
from pathlib import Path
import subprocess

import numpy as np

from prepare_opus_media import PREFIX, atomic_json, probe, sha256


def decode(path):
    info=probe(path)
    raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','1','-i',str(path),
        '-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
    frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,info['height'],info['width'],3)
    if len(frames)!=info['frames']:
        raise ValueError(f'Decoded frame count mismatch: {path}')
    return frames


def verify(root):
    manifest=json.loads((root/'media_manifest.json').read_text())
    results=[]
    for record in manifest['records']:
        source=Path(record['input'])
        output=root/'payload'/PREFIX/record['path']
        if sha256(source)!=record['input_sha256'] or sha256(output)!=record['output_sha256']:
            raise ValueError('Input/output changed since export')
        reference=decode(source)
        actual=decode(output)
        indices=list(range(49))+(list(range(47,0,-1)) if record['task']=='B' else [])
        if len(indices)!=len(actual):
            raise ValueError(f'Timeline mismatch: {record["path"]}')
        errors=[float(np.mean(np.abs(a.astype(np.float32)-reference[i].astype(np.float32)))) for a,i in zip(actual,indices)]
        if max(errors)>10 or np.mean(errors)>5:
            raise ValueError(f'Wrong content/window or excessive compression: {record["path"]}: {errors}')
        results.append(dict(path=record['path'],frames=len(actual),mean_rgb_mae=float(np.mean(errors)),
            max_rgb_mae=max(errors),ffprobe=probe(output),mapping='0..48,47..1' if record['task']=='B' else '0..48'))
        print('[verified]',record['path'],results[-1]['mean_rgb_mae'],flush=True)
    report=dict(status='passed',videos=len(results),records=results,
        scope='Decoded frame-index/content preservation, not generated-video quality or NVS accuracy')
    atomic_json(root/'decoded_validation.json',report)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    verify(args.root)


if __name__=='__main__':
    main()
