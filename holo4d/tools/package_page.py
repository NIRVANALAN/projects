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
    files = ['index.html', 'static/css/index.css', 'static/css/polish.css', 'static/css/yushi-theme.css', 'static/css/editorial.css', 'static/js/media-config.js', 'static/js/gallery.js',
             'static/js/web-examples.js', 'static/js/showcase-selection.js', 'static/images/favicon.svg', 'static/images/favicon-32.png', 'static/images/apple-touch-icon.png',
             'static/images/logo-400.webp', 'static/images/logo-800.webp', 'static/images/logo.png', 'static/images/pipeline.webp', 'static/images/method-overview.jpg',
             'static/videos/method-overview.mp4', 'static/pdfs/holo4d-paper.pdf']
    for entry in [e for entries in manifest['sections'].values() for e in entries]:
        base = f'static/videos/web/{entry["path"]}/'
        files.extend([base+'clean.mp4', base+'poster.jpg'])
        files.append(f'static/posters/web/{entry["path"]}/poster.jpg')
        if entry.get('has_overlay'):
            files.append(base+'overlay.mp4')
        if entry.get('interleaved'):
            files.append(base+'interleaved.mp4')
        if entry['kind'] == 'comparison':
            files.extend([base+'baseline.mp4', base+'baseline-poster.jpg'])
            files.append(f'static/posters/web/{entry["path"]}/baseline-poster.jpg')
            if entry.get('has_source'):
                files.extend([base+'source.mp4',base+'source-poster.jpg',f'static/posters/web/{entry["path"]}/source-poster.jpg'])
    for filename in sorted(set(files)):
        if not (source/filename).is_file():
            raise FileNotFoundError(source/filename)
    for filename in sorted(set(files)):
        dest = args.output/filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source/filename, dest, follow_symlinks=True)
    # Unpublished postgen previews are not silently included in a portable/public
    # release whose media list still refers to the original audited HF export.
    (args.output/'static/js/postgen-preview.js').write_text('window.HOLO4D_POSTGEN_PREVIEW = [];\n')
    assert not any(p.is_symlink() for p in args.output.rglob('*'))
    print('Portable local release:', args.output, 'files=', len(set(files)))


if __name__ == '__main__':
    main()
