"""Decode unchanged selected web media and export temporal selection sheets."""
import argparse
import json
from pathlib import Path

import imageio.v2 as imageio
from PIL import Image, ImageDraw


def review_pair(entries, media, output):
    width = 480
    indices = [0, 16, 32, 48]
    rows = []
    for entry in entries:
        path = media / entry['path'] / 'clean.mp4'
        reader = imageio.get_reader(path)
        try:
            frames = [Image.fromarray(frame) for frame in reader]
        finally:
            reader.close()
        if len(frames) != 49:
            raise ValueError(f'Expected49 frames, got{len(frames)}: {path}')
        height = round(frames[0].height * width / frames[0].width)
        rows.append((entry, frames, height))
    cell_height = max(row[2] for row in rows) + 34
    canvas = Image.new('RGB', (width * 4, cell_height * len(rows)), '#111111')
    draw = ImageDraw.Draw(canvas)
    for row, (entry, frames, height) in enumerate(rows):
        for col, index in enumerate(indices):
            x, y = col * width, row * cell_height
            canvas.paste(frames[index].resize((width, height), Image.Resampling.LANCZOS), (x, y))
            draw.text((x+4, y+height+4), f"{entry['scene']} | {entry['camera']} | frame{index}", fill='white')
    canvas.save(output, quality=94)
    return dict(sheet=str(output), ids=[entry['id'] for entry in entries], frames_shown=indices,
                decoded_frames_per_video=49, caveat='Temporal visual screen; not a fidelity metric')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-report', type=Path, required=True)
    parser.add_argument('--media-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selection = json.loads(args.browser_report.read_text())['selection']
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for section in ['robots', 'reshooting']:
        entries = selection[section]
        for index in range(0, len(entries), 2):
            pair = entries[index:index+2]
            if len(pair) != 2 or pair[0]['scene_id'] != pair[1]['scene_id']:
                raise ValueError('Selection does not preserve same-scene pairs')
            output = args.output / f'{section}_{index//2+1:02d}.jpg'
            records.append(review_pair(pair, args.media_root, output))
    (args.output/'review_inventory.json').write_text(json.dumps(records, indent=2)+'\n')
    print(f'Reviewed{sum(len(record["ids"]) for record in records)} videos; {len(records)} sheets', flush=True)


if __name__ == '__main__':
    main()
