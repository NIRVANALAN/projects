"""Read-only inventory of required page media versus local export caches."""
import argparse
from collections import Counter
import json
from pathlib import Path


def required_files(page):
    text = (page/'static/js/web-examples.js').read_text()
    manifest = json.loads(text.split('window.HOLO4D_PAGE = ',1)[1].rstrip(';\n'))
    files = set()
    for entries in manifest['sections'].values():
        for entry in entries:
            folder = Path(entry['path'])
            files.update([folder/'clean.mp4', folder/'poster.jpg'])
            if entry.get('has_overlay'):
                files.add(folder/'overlay.mp4')
            if entry.get('interleaved'):
                files.add(folder/'interleaved.mp4')
            if entry['kind'] == 'comparison':
                files.update([folder/'baseline.mp4',folder/'baseline-poster.jpg'])
    return files


def inventory(page):
    root = (page/'static/videos/web').resolve(strict=True)
    needed = required_files(page)
    counts, sizes = Counter(), Counter()
    missing = [str(path) for path in sorted(needed) if not (root/path).is_file()]
    unused = []
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        kind = 'required_public' if relative in needed else 'private_provenance' if path.suffix == '.json' else 'unreferenced_export'
        size = path.stat().st_size
        counts[kind] += 1
        sizes[kind] += size
        if kind == 'unreferenced_export':
            unused.append(dict(path=str(relative),bytes=size))
    return dict(media_root=str(root),required_files=len(needed),counts=dict(counts),bytes=dict(sizes),missing=missing,
                unreferenced_exports=unused,
                policies={'clean.mp4':'Required by Clean mode and comparison/long players',
                          'overlay.mp4':'Required by Tracks mode; not redundant with interleave',
                          'interleaved.mp4':'Required by default single-player clean/tracks presentation',
                          'poster.jpg':'Required first-frame lazy placeholder; prevents black loading',
                          'baseline-poster.jpg':'Required comparison placeholder',
                          '*.json':'Private reproducibility/export signatures; retain in cache, omit public package',
                          'unreferenced_export':'Historical exports; exclude from portable page, do not delete scientific sources'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inventory(args.page_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in report.items() if key!='unreferenced_exports'},indent=2))
    if report['missing']:
        raise SystemExit('Required media missing; storage must not be pruned.')


if __name__ == '__main__':
    main()
