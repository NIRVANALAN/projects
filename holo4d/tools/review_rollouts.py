"""Compute-node contact sheets for honest long-video visual selection (no GPU)."""
import argparse
import json
from pathlib import Path
import cv2
from PIL import Image, ImageDraw

LOG = Path('/scratch/shared/engs2907/logs/track4d-360/benchmark')


def sheet(videos, output):
    width, height = 224, 180
    canvas = Image.new('RGB', (width * 8, (height + 30) * len(videos)), '#101827')
    draw = ImageDraw.Draw(canvas)
    for row, path in enumerate(videos):
        cap = cv2.VideoCapture(str(path))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        picks = sorted(set([0, max(0, n//4), max(0, n//2), max(0, n-1)] + [min(n-1, i) for i in (47, 48, 49, 53)]))
        draw.text((4, row*(height+30)), path.parent.name, fill='white')
        for col, index in enumerate(picks):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f'Missing frame {index}: {path}')
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img.thumbnail((width, height-18))
            xy = (col*width, row*(height+30)+30)
            canvas.paste(img, xy)
            draw.text((xy[0]+4, xy[1]+height-17), f'frame {index}/{n}', fill='white')
        cap.release()
    canvas.save(output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--comparisons-only', action='store_true')
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    if a.comparisons_only:
        plan = json.loads(Path('/scratch/shared/engs2907/open-source/holo4d/project-page-media_20261009/curation.json').read_text())
        for case in plan['sections']['comparisons']:
            sheet([Path(case['clean']), Path(case['baseline'])], a.output/(case['id'].replace('/','__')+'.jpg'))
        print('[comparisons reviewed]',flush=True)
        return
    root = LOG/'robot_selected40_full_i2v_20261007/long_rollout'
    groups = []
    for source in sorted(root.iterdir()):
        paths = sorted(source.glob('*/source_generated_full_labeled.mp4'))
        sheet(paths, a.output/(source.name+'.jpg'))
        groups.append(dict(source=source.name, videos=list(map(str, paths))))
    root = LOG/'davis50_full_i2v_20261007/long_rollout'
    paths = [root/s/t/'source_generated_full_labeled.mp4' for s,t in [('bear','pan_right'), ('classic-car','translate_right'), ('camel','orbit_left'), ('blackswan','pan_up'), ('lindy-hop','zoom_out'), ('koala','zoom_in')]]
    sheet(paths, a.output/'davis_old_showcase.jpg')
    (a.output/'review_inputs.json').write_text(json.dumps(groups, indent=2)+'\n')
    print('[contact sheets]', a.output, flush=True)


if __name__ == '__main__':
    main()
