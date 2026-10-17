"""Read-only unauthenticated HTTPS checks of the pinned public page export."""
import argparse
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def check(url, ranged=False):
    start = time.monotonic()
    request = Request(url, headers={'Range':'bytes=0-1023'} if ranged else {})
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read(1024 if ranged else 200000)
            # Never record signed CDN redirect URLs in reports.
            return dict(status=response.status, seconds=round(time.monotonic()-start,3),
                        bytes_read=len(body), content_type=response.headers.get('Content-Type'),
                        content_range=response.headers.get('Content-Range'))
    except Exception as error:
        return dict(error=type(error).__name__, seconds=round(time.monotonic()-start,3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.page_root
    base = re.search(r"const holo4dPublicMedia = '([^']+)'", (root/'static/js/media-config.js').read_text()).group(1)
    raw = (root/'static/js/web-examples.js').read_text().split('window.HOLO4D_PAGE = ',1)[1].rstrip(';\n')
    sections = json.loads(raw)['sections']
    report = dict(base=base, scope='Unauthenticated first short / long / comparison; not all CDN files', probes=[])
    for name in ['robots','long','comparisons']:
        entry = sections[name][0]
        files = ['poster.jpg', 'interleaved.mp4' if entry.get('interleaved') else 'clean.mp4']
        if name == 'comparisons':
            files += ['baseline.mp4']
        for filename in files:
            result = check(urljoin(base, entry['path']+'/'+filename), filename.endswith('.mp4'))
            report['probes'].append(dict(section=name, path=entry['path']+'/'+filename, **result))
            print(name, filename, result, flush=True)
    # New additions are all checked, not just the representative legacy clips.
    additions=[(e,'source.mp4') for e in sections['comparisons'] if e.get('has_source')]
    additions += [(e,'clean.mp4') for e in sections.get('teaser',[])]
    for entry,filename in additions:
        result=check(urljoin(base,entry['path']+'/'+filename),True)
        report['probes'].append(dict(section='new_additions',path=entry['path']+'/'+filename,**result))
        print('new_addition',entry['path'],result,flush=True)
    report['all_passed'] = all(p.get('status') == (206 if p['path'].endswith('.mp4') else 200) for p in report['probes'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if not report['all_passed']:
        raise SystemExit('Some public media checks failed; inspect report before publication')


if __name__ == '__main__':
    main()
