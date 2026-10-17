"""Add-only media preparation for Opus Task A/B; never changes page layout.

Run on compute. Outputs and provenance are separate from all inference roots.
"""
import argparse
from fractions import Fraction
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

PAGE = Path(__file__).resolve().parents[1]
MEDIA = Path('/scratch/shared/engs2907/open-source/holo4d/project-page-media_20261009')
PREFIX = Path('project_page/media_20261012')
TEASERS = [
    ('01_figure-orbit','robots','robot/figure_0__window00__start00000','subject_orbit_zoom'),
    ('02_tesla-zoom','robots','robot/tesla_0__window02__start00048','vista4d_avocado_slice__left_front_zoom'),
    ('03_droid-gupta','robots','robot/GuptaLab__failure__2023-04-20__Thu_Apr_20_14-22-26_2023__static_1__22246076','static_right_front'),
    ('04_droid-tri','robots','robot/TRI__failure__2023-10-23__Mon_Oct_23_14-34-51_2023__static_1__20252535','safe_high_center_65_r80_fixedheight'),
    ('05_davis-bear','davis','bear','pan_right'),
    ('06_davis-dance','davis','lindy-hop','zoom_out'),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    raw = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=codec_name,pix_fmt,width,height,nb_frames,avg_frame_rate:format=duration',
        '-of','json',str(path)]))
    stream = raw['streams'][0]
    return dict(width=stream['width'],height=stream['height'],frames=int(stream['nb_frames']),
        fps=float(Fraction(stream['avg_frame_rate'])),duration=float(raw['format']['duration']),
        codec=stream['codec_name'],pix_fmt=stream['pix_fmt'],bytes=path.stat().st_size)


def atomic_json(path, payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix('.pending.json')
    tmp.write_text(json.dumps(payload,indent=2)+'\n')
    tmp.replace(path)


def encode(source, output, pingpong=False):
    info = probe(source)
    if info['frames'] != 49:
        raise ValueError(f'Expected49 exact source/model frames: {source}: {info}')
    if output.exists():
        raise FileExistsError(f'Choose a fresh export root: {output}')
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary = output.with_suffix('.encoding.mp4')
    crfs = (22,24,26,28) if pingpong else (22,)
    for crf in crfs:
        command = ['ffmpeg','-nostdin','-v','error','-y','-threads','1','-filter_threads','1',
                   '-filter_complex_threads','1','-i',str(source)]
        if pingpong:
            # f0..f48 + f47..f1: 49+47 frames, no repeated end points.
            graph = ('[0:v]split[a][b];[a]setpts=PTS-STARTPTS[f];'
                     '[b]trim=start_frame=1:end_frame=48,reverse,setpts=PTS-STARTPTS[r];'
                     '[f][r]concat=n=2:v=1:a=0,setpts=N/(16*TB)[out]')
            command += ['-filter_complex',graph,'-map','[out]']
        else:
            command += ['-vf','setpts=N/(16*TB)']
        command += ['-r','16','-an','-c:v','libx264','-preset','slow','-crf',str(crf),
                    '-pix_fmt','yuv420p','-threads','1','-movflags','+faststart',str(temporary)]
        subprocess.run(command,check=True)
        if not pingpong or temporary.stat().st_size <= 1500000:
            break
    if pingpong and temporary.stat().st_size > 1500000:
        raise ValueError(f'Teaser exceeds1.5MB after CRF28: {temporary}')
    temporary.replace(output)
    out = probe(output)
    if (out['frames'] != (96 if pingpong else 49) or out['fps'] != 16
            or (out['width'],out['height']) != (info['width'],info['height'])
            or max(out['width'],out['height']) > 960
            or out['codec'] != 'h264' or out['pix_fmt'] != 'yuv420p'):
        raise ValueError(f'Wrong export contract: {output}: {out}')
    # The MP4 index must precede media bytes for web playback.
    header = output.read_bytes()
    if not (0 < header.find(b'moov') < header.find(b'mdat')):
        raise ValueError(f'Missing faststart: {output}')
    return out, crf


def frame_image(path, frame=0):
    encoded = subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','1',
        '-i',str(path),'-vf',f'select=eq(n\\,{frame})','-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-'])
    return Image.open(BytesIO(encoded)).convert('RGB')


def poster(video, output):
    image = frame_image(video)
    # Same first frame, no labels, no crop/letterbox.
    image = image.resize((480,round(image.height*480/image.width)),Image.Resampling.LANCZOS)
    image.save(output,quality=85)


def load_catalog(page):
    return json.loads((page/'static/js/web-examples.js').read_text().split('window.HOLO4D_PAGE = ',1)[1].rstrip(';\n'))


def select_teaser(catalog, spec):
    short,section,source,trajectory = spec
    if section == 'robots':
        matches = [e for e in catalog['sections'][section] if e.get('scene_id') == source and e.get('trajectory_id') == trajectory]
    else:
        matches = [e for e in catalog['sections'][section] if e['id'].endswith(f'/{source}__{trajectory}')]
    if len(matches) != 1:
        raise ValueError(f'Nonunique teaser source: {spec}')
    entry = matches[0]
    provenance = json.loads((MEDIA/entry['path']/'provenance.json').read_text())
    manifest = json.loads(Path(provenance['case']['source_manifest']).read_text())
    prediction = Path(manifest['case']['prediction'])
    if prediction.name != 'pred_rgb.mp4' or not prediction.is_file():
        raise ValueError(f'Teaser must use raw generated RGB, not a composite: {prediction}')
    return entry,prediction


def contacts(records, output):
    cell_w,cell_h = 256,250
    canvas = Image.new('RGB',(5*cell_w,len(records)*cell_h),'white')
    draw = ImageDraw.Draw(canvas)
    for row,record in enumerate(records):
        for column,frame in enumerate([0,12,24,36,48]):
            image = frame_image(Path(record['input']),frame)
            image.thumbnail((cell_w-8,cell_h-40),Image.Resampling.LANCZOS)
            x,y=column*cell_w+4,row*cell_h+4
            canvas.paste(image,(x,y))
            draw.text((x,row*cell_h+cell_h-30),f'{record["path"]} f{frame}',fill='black')
    canvas.save(output,quality=90)


def prepare(page, output):
    catalog = load_catalog(page)
    records,teasers = [],[]
    for entry in catalog['sections']['comparisons']:
        relative = Path(entry['path'])
        provenance = json.loads((MEDIA/relative/'provenance.json').read_text())
        source = Path(provenance['case']['clean']).with_name('source_rgb.mp4')
        reference = probe(MEDIA/relative/'clean.mp4')
        baseline = probe(MEDIA/relative/'baseline.mp4')
        if any(v[k] != reference[k] for v in [probe(source),baseline] for k in ['width','height','frames','fps']):
            raise ValueError(f'Comparison source/baseline contract differs: {relative}')
        if tuple(reference[k] for k in ['width','height','frames','fps']) != (672,384,49,16):
            raise ValueError(f'Expected672x384x49@16fps: {relative}')
        movie = output/'payload'/PREFIX/relative/'source.mp4'
        info,crf = encode(source,movie)
        poster(movie,movie.with_name('source-poster.jpg'))
        records.append(dict(task='A',path=str(relative/'source.mp4'),input=str(source),
            input_sha256=sha256(source),output_sha256=sha256(movie),poster=str(relative/'source-poster.jpg'),
            crf=crf,**info))
    if len(records) != 9:
        raise ValueError('TaskA needs all nine comparison sources')
    for spec in TEASERS:
        entry,source = select_teaser(catalog,spec)
        relative = Path('teaser')/spec[0]
        movie = output/'payload'/PREFIX/relative/'clean.mp4'
        info,crf = encode(source,movie,pingpong=True)
        poster(movie,movie.with_name('poster.jpg'))
        teasers.append(dict(id=str(relative),path=str(relative),scene=entry['scene'],camera=entry['camera'],
            backend=entry['backend'],kind='teaser',aspect=info['width']/info['height'],frames=info['frames'],
            fps=info['fps'],duration=info['duration'],bytes=info['bytes']))
        records.append(dict(task='B',path=str(relative/'clean.mp4'),input=str(source),
            input_sha256=sha256(source),output_sha256=sha256(movie),poster=str(relative/'poster.jpg'),
            crf=crf,**info))
        print('[teaser]',relative,info,flush=True)
    if sum(e['bytes'] for e in teasers)>10000000:
        raise ValueError('Six teasers exceed10MB')
    atomic_json(output/'media_manifest.json',dict(base_page_commit='3558358',records=records,teaser_entries=teasers,
        comparison_patch='add has_source=true only; all existing comparison values unchanged',
        task_c='prepared source/camera gate only; no new diffusion job submitted; optional and deferred'))
    contacts([r for r in records if r['task']=='B'],output/'teaser_review.jpg')
    print('[prepared]',len(records),'videos; teaser bytes=',sum(e['bytes'] for e in teasers),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root',type=Path,default=PAGE)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output root; existing exports are not overwritten')
    args.output.mkdir(parents=True)
    prepare(args.page_root,args.output)


if __name__=='__main__':
    main()
