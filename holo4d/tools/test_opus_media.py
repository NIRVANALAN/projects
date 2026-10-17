"""Browser gate for add-only Opus media; does not change gallery layout."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

from preview_page import MediaHandler


class QuietHandler(MediaHandler):
    def log_message(self, *_args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--media-root', type=Path, required=True)
    args = parser.parse_args()
    export = json.loads((args.media_root/'media_manifest.json').read_text())
    uploaded = json.loads((args.media_root/'hf_upload.json').read_text())
    base = 'https://huggingface.co/yslan/Holo4D-2026/resolve/' + uploaded['revision'] + '/project_page/media_20261012/'
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
        functools.partial(QuietHandler, directory=str(args.page_root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors, console_errors, decoded = [], [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport=dict(width=1440, height=1000), reduced_motion='reduce')
        page.set_default_timeout(60000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: console_errors.append(message.text) if message.type == 'error' else None)
        for name, width in [('desktop',1440), ('mobile',390)]:
            page.set_viewport_size(dict(width=width, height=1000))
            page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
            assert page.evaluate('holo4dUseLocalMedia === false')
            assert page.locator('video[src]').count() == 0, 'Lazy loading regressed'
            page.screenshot(path=str(args.media_root/f'page_{name}_top.png'))
            page.screenshot(path=str(args.media_root/f'page_{name}.png'), full_page=True)
        for record in export['records']:
            poster_url = f'http://127.0.0.1:{server.server_port}/static/posters/web/{record["poster"]}'
            assert page.request.get(poster_url).status == 200, poster_url
            actual = page.evaluate('''url => new Promise((resolve,reject) => {
                const video=document.createElement('video');
                const timer=setTimeout(()=>reject(new Error('Media timeout')),45000);
                video.muted=true; video.preload='auto';
                video.onloadeddata=()=>{const result={width:video.videoWidth,height:video.videoHeight,duration:video.duration};
                    clearTimeout(timer); video.removeAttribute('src'); video.load(); resolve(result);};
                video.onerror=()=>{clearTimeout(timer);reject(new Error('Media decode failed'));};
                video.src=url; video.load();
            })''', base+record['path'])
            assert actual['width'] == record['width'] and actual['height'] == record['height']
            assert abs(actual['duration'] - record['duration']) < .01
            decoded.append(dict(path=record['path'], **actual))
            print('[browser decoded]', record['path'], flush=True)
        assert not errors, errors
        assert not console_errors, console_errors
        browser.close()
    server.shutdown()
    report = dict(status='passed', revision=uploaded['revision'], errors=errors, console_errors=console_errors,
        decoded=decoded, checks=['desktop/mobile initial page loads without JS exceptions',
        'no eager MP4 src in reduced-motion mode', '15 same-origin posters return200',
        '15 immutable anonymous hosted videos decode with exact size/duration'])
    (args.media_root/'browser_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], decoded=len(decoded), errors=errors)),flush=True)


if __name__ == '__main__':
    main()
