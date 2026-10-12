"""Prepare a portable static page without scratch symlinks or private manifests.

This stages local files only; it does not publish the website.
"""
import argparse
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output directory; existing releases are never overwritten')
    source = args.page_root
    raw = (source/'static/js/web-examples.js').read_text()
    manifest = json.loads(raw.split('window.HOLO4D_PAGE = ', 1)[1].rstrip(';\n'))
    files = ['index.html', 'static/css/index.css', 'static/css/polish.css', 'static/css/yushi-theme.css', 'static/js/media-config.js', 'static/js/gallery.js',
             'static/js/web-examples.js', 'static/images/favicon.svg', 'static/pdfs/holo4d-paper.pdf']
    for entry in [e for entries in manifest['sections'].values() for e in entries]:
        base = f'static/videos/web/{entry["path"]}/'
        files.extend([base+'clean.mp4', base+'poster.jpg'])
        if entry['has_overlay']:
            files.append(base+'overlay.mp4')
        if entry.get('interleaved'):
            files.append(base+'interleaved.mp4')
        if entry['kind'] == 'comparison':
            files.extend([base+'baseline.mp4', base+'baseline-poster.jpg'])
    for filename in sorted(set(files)):
        if not (source/filename).is_file():
            raise FileNotFoundError(source/filename)
    for filename in sorted(set(files)):
        dest = args.output/filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source/filename, dest, follow_symlinks=True)
    assert not any(p.is_symlink() for p in args.output.rglob('*'))
    print('Portable local release:', args.output, 'files=', len(set(files)))


if __name__ == '__main__':
    main()
