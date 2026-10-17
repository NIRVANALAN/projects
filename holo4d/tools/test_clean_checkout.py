"""Validate a Git-only checkout with hosted MP4s and same-origin covers."""
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
    parser.add_argument('--page-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    assert not (args.page_root/'static/videos/web').exists(), 'Test a Git-only checkout, not a Civo mount'
    assert not any(p.is_symlink() for p in args.page_root.rglob('*')), 'Checkout contains nonportable symlinks'
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0), functools.partial(QuietHandler, directory=str(args.page_root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport=dict(width=1440,height=1000), reduced_motion='reduce')
        page.set_default_timeout(90000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
        assert page.evaluate('holo4dUseLocalMedia === false')
        assert page.evaluate('holo4dVideoBase.protocol === "https:" && holo4dVideoBase.hostname === "huggingface.co"')
        assert page.locator('video[src]').count() == 0
        assert page.locator('[data-gallery="robots"] video').evaluate_all('(vs)=>vs.every(v=>!v.dataset.src.includes("postgen_20261012"))')
        root = page.locator('[data-gallery="robots"][data-orientation="portrait"]')
        root.scroll_into_view_if_needed()
        assert root.locator('.is-active video').evaluate_all('(vs)=>vs.every(v=>new URL(v.poster).origin===location.origin)')
        posters = root.locator('.is-active video').evaluate_all('(vs)=>vs.map(v=>v.poster)')
        for url in posters:
            assert page.request.get(url).status == 200
        root.locator('.is-active .card-playback').first.click()
        page.wait_for_function('''() => {
          const vs=[...document.querySelectorAll('[data-gallery="robots"][data-orientation="portrait"] .is-active video')];
          return vs.length===2 && vs.every(v=>v.readyState>=2 && !v.error && !v.paused && v.currentTime>.15);
        }''')
        urls = root.locator('video[src]').evaluate_all('(vs)=>vs.map(v=>v.src)')
        assert all(url.startswith('https://huggingface.co/') for url in urls)
        root.screenshot(path=str(args.output/'hosted_pair_playing.png'))
        page.locator('#citation').scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        assert root.locator('video[src]').count() == 0
        assert not errors, errors
        browser.close()
    server.shutdown()
    report = dict(status='passed', errors=errors, hosted_players=urls, checks=[
        'Git-only checkout: no local video mounts or symlinks',
        'default localhost uses pinned hosted videos',
        'regular same-origin posters HTTP200',
        'no MP4 before click under reduced motion',
        'both actual hosted videos decoded and playing',
        'offscreen players unload'])
    (args.output/'clean_checkout_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
