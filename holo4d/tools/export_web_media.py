"""Incremental H.264 web copies, posters, provenance and publishable JS manifest.

Preserves every input frame and original aspect; never modifies inference roots.
Portrait triptychs are optionally rearranged into three equal portrait columns.
"""
import argparse
import concurrent.futures
import json
import os
import subprocess
from pathlib import Path

from link_cowtracker_assets import iter_boxes, probe

PAGE = Path(__file__).resolve().parents[1]


def atomic_json(path, payload):
    tmp = path.with_suffix('.tmp.json')
    tmp.write_text(json.dumps(payload, indent=2)+'\n')
    tmp.replace(path)


def fingerprint(path):
    stat = path.stat()
    return dict(path=str(path), size=stat.st_size, mtime_ns=stat.st_mtime_ns)


def check_web_video(path):
    info = probe(path)
    with path.open('rb') as handle:
        boxes = [b[0] for b in iter_boxes(handle, 0, path.stat().st_size)]
    if boxes.index(b'moov') > boxes.index(b'mdat'):
        raise ValueError(f'Missing faststart: {path}')
    stream = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_name,pix_fmt', '-of', 'json', str(path)]))['streams'][0]
    if stream['codec_name'] != 'h264' or stream['pix_fmt'] != 'yuv420p':
        raise ValueError(f'Browser-incompatible codec: {path}')
    return dict(info, bytes=path.stat().st_size, faststart=True, **stream)


def filters(info, portrait, max_width):
    scale = f'scale=w=min({max_width}\\,iw):h=-2:flags=lanczos'
    if not portrait:
        return None, scale
    # Exact established render_vista4d_style_triptych layout: margin32/header24/gap24.
    width = info['width']
    top_w = (width-88)//2
    top_h = round(top_w*672/384)
    bottom_w = width-64
    bottom_h = round(bottom_w*672/384)
    bottom_h += bottom_h % 2
    if info['height'] != 24+top_h+24+bottom_h+48+(top_h % 2):
        raise ValueError(f'Unexpected portrait triptych canvas: {info}')
    # crop supports odd intermediate sizes in RGB; scale each to an even canvas.
    graph = (f'[0:v]split=3[a][b][c];'
             f'[a]crop={top_w}:{top_h}:32:24,scale=384:672[s];'
             f'[b]crop={top_w}:{top_h}:{32+top_w+24}:24,scale=384:672[q];'
             f'[c]crop={bottom_w}:{bottom_h}:32:{24+top_h+24},scale=384:672[g];'
             f'[s][q][g]hstack=inputs=3,{scale}[web]')
    return graph, None


def encode(source, dest, portrait, args, output_fps=None, review_prediction=None):
    info = probe(source)
    sig = dict(source=fingerprint(source), crf=args.crf, max_width=args.max_width,
               portrait_horizontal=portrait, exporter_version=1)
    if output_fps is not None:
        sig['output_fps'] = output_fps
    if review_prediction:
        sig['chunk_presentation'] = 'clean-generated-panel-no-border-v2'
        sig['review_prediction'] = fingerprint(review_prediction)
    marker = dest.with_suffix('.json')
    if dest.is_file() and marker.is_file() and json.loads(marker.read_text()).get('signature') == sig:
        return json.loads(marker.read_text())
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.stem+'.tmp.mp4')
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '1',
           '-filter_threads', '1', '-filter_complex_threads', '1', '-i', str(source)]
    graph, simple = filters(info, portrait, args.max_width)
    if review_prediction:
        # Rebuild the generated panel from its unchanged full-length RGB.
        # Keep the review's source panel and neutral frame/chunk header; no
        # flashing boundary box, color-mask editing or inference overwrite.
        if graph:
            raise ValueError('Long review expects a source/generated pair')
        pred_info = probe(review_prediction)
        if (pred_info['width']*2 != info['width'] or pred_info['height']+32 != info['height']
                or pred_info['frames'] != info['frames'] or pred_info['fps'] != info['fps']):
            raise ValueError('Long review and generated RGB have different canvases/timelines')
        cmd += ['-threads','1','-i',str(review_prediction)]
        graph = ('[0:v]split[h][s];[h]crop=iw:32:0:0,'
                 'drawbox=x=0:y=31:w=iw:h=1:color=black:t=fill[header];'
                 '[s]crop=iw/2:ih-32:0:32,'
                 'drawbox=x=iw-1:y=0:w=1:h=ih:color=black:t=fill[source];'
                 '[source][1:v]hstack=inputs=2[body];'
                 f'[header][body]vstack=inputs=2,{simple}[web]')
    if output_fps is not None:
        if graph:
            raise ValueError('FPS retiming is only supported for plain comparison videos')
        simple += f',setpts=N/({output_fps}*TB)'
    cmd += ['-filter_complex', graph, '-map', '[web]'] if graph else ['-vf', simple]
    if output_fps is not None:
        cmd += ['-r', str(output_fps)]
    cmd += ['-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', str(args.crf),
            '-pix_fmt', 'yuv420p', '-threads', '1', '-movflags', '+faststart', str(tmp)]
    subprocess.run(cmd, check=True)
    web = check_web_video(tmp)
    expected_fps = info['fps'] if output_fps is None else output_fps
    if web['frames'] != info['frames'] or abs(web['fps']-expected_fps) > 1e-6:
        raise ValueError(f'Frame/timing mismatch: {source}')
    tmp.replace(dest)
    record = dict(signature=sig, original=info, web=web)
    atomic_json(marker, record)
    return record


def export_case(task):
    case, args = task
    folder = args.output/case['id']
    records = {}
    for key in ('clean', 'overlay', 'baseline'):
        if key in case:
            output_fps = records['clean']['web']['fps'] if key == 'baseline' else None
            review_prediction = Path(case['source_manifest']).parent/'pred_rgb_full.mp4' if case['kind']=='long' else None
            records[key] = encode(Path(case[key]), folder/(key+'.mp4'), case.get('portrait_horizontal', False) and key != 'baseline', args, output_fps, review_prediction=review_prediction)
    if 'overlay' in records:
        for key in ('width', 'height', 'frames', 'fps'):
            if records['clean']['web'][key] != records['overlay']['web'][key]:
                raise ValueError(f'Unaligned clean/overlay: {case["id"]}')
        n = records['clean']['web']['frames']
        dest = folder/'interleaved.mp4'
        sig = dict(clean=fingerprint(folder/'clean.mp4'), overlay=fingerprint(folder/'overlay.mp4'), version=1)
        marker = folder/'interleaved.json'
        if not dest.is_file() or not marker.is_file() or json.loads(marker.read_text()).get('signature') != sig:
            # One forward/reverse timeline, with gentle overlay fade around
            # its quarter/three-quarter points. No two-player mode switching.
            edge = max(1, n//2-4)
            end = 2*n-edge-1
            weight = f'min(1,max(0,(N-{edge})/8))*min(1,max(0,({end}-N)/8))'
            graph = ('[0:v]split[a][b];[b]reverse[br];[a][br]concat=n=2:v=1:a=0[c];'
                     '[1:v]split[d][e];[e]reverse[er];[d][er]concat=n=2:v=1:a=0[o];'
                     f"[c][o]blend=all_expr='A*(1-({weight}))+B*({weight})'[out]")
            tmp = folder/'interleaved.tmp.mp4'
            subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-threads','1','-filter_complex_threads','1',
                '-i',str(folder/'clean.mp4'),'-i',str(folder/'overlay.mp4'),'-filter_complex',graph,'-map','[out]',
                '-an','-c:v','libx264','-crf',str(args.crf),'-preset','fast','-pix_fmt','yuv420p',
                '-threads','1','-movflags','+faststart',str(tmp)],check=True)
            checked = check_web_video(tmp)
            if checked['frames'] != 2*n or abs(checked['fps']-records['clean']['web']['fps']) > 1e-6:
                raise ValueError(f'Interleave timing mismatch: {case["id"]}')
            tmp.replace(dest)
            atomic_json(marker,dict(signature=sig,web=checked, forward_frames=n, fade_frames=8,
                                    semantics='presentation forward/reverse; not an inference/metric video'))
        records['interleaved'] = json.loads(marker.read_text())
    if 'baseline' in records:
        if records['baseline']['web']['frames'] != records['clean']['web']['frames']:
            raise ValueError(f'Unmatched comparison frame counts: {case["id"]}')
        if records['baseline']['web']['fps'] != records['clean']['web']['fps']:
            raise ValueError(f'Unmatched comparison playback rate: {case["id"]}')
    for key in ('clean', 'baseline'):
        if key not in records:
            continue
        poster = folder/('poster.jpg' if key == 'clean' else 'baseline-poster.jpg')
        if not poster.is_file() or poster.stat().st_mtime_ns < (folder/(key+'.mp4')).stat().st_mtime_ns:
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '1',
                            '-i', str(folder/(key+'.mp4')), '-frames:v', '1', '-vf', 'scale=480:-2',
                            '-threads', '1', '-q:v', '3', str(poster)], check=True)
    web = records['clean']['web']
    entry = {k: v for k, v in case.items() if k not in ('clean', 'overlay', 'baseline', 'source_manifest')}
    entry.update(path=case['id'], aspect=web['width']/web['height'], frames=web['frames'],
                 duration=web['duration'], fps=web['fps'], has_overlay='overlay' in records,
                 bytes=sum(r['web']['bytes'] for r in records.values()))
    entry['interleaved'] = 'interleaved' in records
    atomic_json(folder/'provenance.json', dict(case=case, media=records))
    print('[exported]', case['id'], entry['bytes'], flush=True)
    return entry, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--crf', type=int, default=22)
    parser.add_argument('--max-width', type=int, default=960)
    parser.add_argument('--limit', type=int, default=0, help='Smoke only; does not publish page manifest')
    parser.add_argument('--smoke-section', help='With --limit only: validate one section without publishing a partial page')
    parser.add_argument('--publish-dir', type=Path, default=PAGE)
    args = parser.parse_args()
    if args.workers < 1 or args.max_width < 2 or args.max_width % 2:
        parser.error('workers >=1 and even max-width required')
    plan = json.loads(args.manifest.read_text())
    cases = [c for section in plan['sections'].values() for c in section]
    if args.smoke_section:
        if not args.limit or args.smoke_section not in plan['sections']:
            parser.error('--smoke-section requires --limit and an existing section')
        cases = plan['sections'][args.smoke_section]
    if args.limit:
        cases = cases[:args.limit]
    args.output.mkdir(parents=True, exist_ok=True)
    results, failures = {}, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(export_case, (c, args)): c for c in cases}
        for future in concurrent.futures.as_completed(futures):
            case = futures[future]
            try:
                results[case['id']] = future.result()
            except Exception as exc:
                failures.append(dict(case=case['id'], error=repr(exc)))
                print('[FAILED]', failures[-1], flush=True)
    originals = sum(r['signature']['source']['size'] for _, records in results.values() for r in records.values() if 'source' in r['signature'])
    compressed = sum(r['web']['bytes'] for _, records in results.values() for r in records.values())
    report = dict(expected=len(cases), completed=len(results), failures=failures,
                  original_bytes=originals, web_bytes=compressed, compression_ratio=originals/max(compressed, 1))
    atomic_json(args.output/('smoke_validation.json' if args.limit else 'export_validation.json'), report)
    if failures:
        raise SystemExit(1)
    if not args.limit:
        public = dict(hero=plan['hero'], sections={k: [results[c['id']][0] for c in v] for k, v in plan['sections'].items()})
        dest = args.publish_dir/'static/js/web-examples.js'
        temp = dest.with_suffix('.tmp.js')
        temp.write_text('// Generated by tools/export_web_media.py; web copies only.\nwindow.HOLO4D_PAGE = '+json.dumps(public, indent=2)+';\n')
        temp.replace(dest)
        link = args.publish_dir/'static/videos/web'
        if link.is_symlink() and link.resolve() != args.output.resolve():
            raise ValueError('Existing web media symlink targets another root; preserve it and choose a new publish directory')
        if not link.exists():
            link.symlink_to(args.output, target_is_directory=True)
    print('[complete]', report, flush=True)


if __name__ == '__main__':
    main()
