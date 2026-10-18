"""README teaser GIF for the GitHub repo, laid out like the project-page teaser: six Holo4D
results (portrait humanoids as tall end tiles, four landscape tiles between), each with its source video as an inset.

    python tools/make_readme_teaser.py CLIPS_DIR FONTS_DIR OUT.gif [--width 800] [--fps 10]

CLIPS_DIR holds the hosted teaser outputs as 0N_name.mp4 (HF project_page/media_20261012/teaser/0N_name/clean.mp4);
the source insets come from static/videos/teaser-source/ (same ping-pong timing). FONTS_DIR has Lato-Regular/Bold.ttf.
"""
import argparse
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PAGE = Path(__file__).resolve().parents[1]
TILES = [  # name, label, portrait
    ('01_figure-orbit', 'Figure humanoid', True), ('03_droid-gupta', 'DROID · GuptaLab', False),
    ('04_droid-tri', 'DROID · TRI', False), ('05_davis-bear', 'Bear', False),
    ('06_davis-dance', 'Lindy hop', False), ('02_tesla-zoom', 'Tesla humanoid', True),
]


def frames(path, fps):
    w, h = (int(v) for v in subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
            'stream=width,height', '-of', 'csv=p=0', str(path)], capture_output=True, text=True).stdout.split(','))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'fps={fps}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True).stdout
    return [Image.fromarray(f) for f in np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)]


def cover(im, w, h):
    s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def chip(d, xy, text, font, fill=(17, 17, 17)):
    x, y = xy; tw = d.textlength(text, font=font); h = font.size + 6
    d.rounded_rectangle((x, y, x + tw + 12, y + h), 4, fill=fill); d.text((x + 6, y + h / 2), text, font=font, fill='white', anchor='lm')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('clips', type=Path); ap.add_argument('fonts', type=Path); ap.add_argument('out', type=Path)
    ap.add_argument('--width', type=int, default=800); ap.add_argument('--fps', type=int, default=10)
    a = ap.parse_args()
    W, gap, pad = a.width, 4, 12
    unit = (W - 2 * pad - 3 * gap) / 3.3                  # columns .65 : 1 : 1 : .65, as on the page
    lw, pw = round(unit), round(unit * .65); lh = round(lw / 1.75); ph = 2 * lh + gap
    f_lab = ImageFont.truetype(str(a.fonts / 'Lato-Bold.ttf'), 12)
    head = pad                                            # logo and text live in the README (a GIF palette dulls the logo)
    H = head + ph + pad
    res = {n: frames(a.clips / f'{n}.mp4', a.fps) for n, _, _ in TILES}
    src = {n: frames(PAGE / f'static/videos/teaser-source/{n}.mp4', a.fps) for n, _, _ in TILES}
    T = min(len(v) for v in list(res.values()) + list(src.values()))
    xs = [pad, pad + pw + gap, pad + pw + gap + lw + gap, pad + pw + 2 * (lw + gap)]
    slots = [(xs[0], 0, pw, ph), (xs[1], 0, lw, lh), (xs[2], 0, lw, lh), (xs[1], lh + gap, lw, lh), (xs[2], lh + gap, lw, lh), (xs[3], 0, pw, ph)]
    out = []
    for t in range(T):
        fr = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(fr)
        for (name, label, portrait), (x, y, w, h) in zip(TILES, slots):
            y += head; fr.paste(cover(res[name][t], w, h), (x, y))
            iw = round(w * (.44 if portrait else .34)); s = src[name][t]; ih = round(iw * s.height / s.width)
            ix, iy = x + w - iw - 6, y + 6
            d.rectangle((ix - 2, iy - 2, ix + iw + 1, iy + ih + 1), fill='white'); fr.paste(s.resize((iw, ih), Image.LANCZOS), (ix, iy))
            chip(d, (ix + 3, iy + 3), 'Source', f_lab); chip(d, (x + 6, y + h - f_lab.size - 12), label, f_lab)
        out.append(fr)
    raw = b''.join(f.tobytes() for f in out)
    pal = f'[0:v]split[a][b];[a]palettegen=max_colors=256:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(a.fps), '-i', '-',
                    '-filter_complex', pal, '-loop', '0', str(a.out)], input=raw, check=True)
    print(a.out, f'{W}x{H}', T, 'frames', f'{a.out.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
