"""Real Chromium desktop/mobile regression checks against locally served assets."""
import argparse
import functools
import http.server
import json
import threading
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright
from preview_page import MediaHandler, byte_range


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    assert byte_range('bytes=0-63', 100) == (0, 63)
    assert byte_range('bytes=-10', 100) == (90, 99)
    assert byte_range('bytes=95-', 100) == (95, 99)
    handler = functools.partial(MediaHandler, directory=str(args.page_root))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/'
    errors, requests = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda r: requests.append(r.url) if '.mp4' in r.url else None)
        page.goto(url, wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll("[data-hero] video[src]").length === 2')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-hero] video")).every(v => v.readyState >= 2 && !v.paused)')
        assert len(set(requests)) == 2, f'Initial page eagerly fetched non-hero MP4s: {requests}'
        request = urllib.request.Request(requests[0], headers={'Range': 'bytes=0-63'})
        with urllib.request.urlopen(request) as response:
            assert response.status == 206 and len(response.read()) == 64
            assert response.headers['Accept-Ranges'] == 'bytes'
        page.locator('[data-hero] [data-mode="tracks"]').click()
        assert page.locator('[data-hero] .show-tracks').count() == 1
        page.locator('[data-hero] [data-mode="clean"]').click()
        assert page.locator('[data-hero] .show-tracks').count() == 0
        page.locator('[data-hero] [data-mode="auto"]').click()
        page.evaluate('document.querySelectorAll("[data-hero] video").forEach(v => {v.currentTime=v.duration-.15})')
        page.wait_for_function('document.querySelector("[data-hero] .show-tracks") !== null')
        page.locator('[data-hero]').screenshot(path=str(args.output/'hero.png'))
        page.locator('[data-gallery="robots"]').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelectorAll("[data-gallery=robots] video[src]").length === 4')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=robots] video[src]")).every(v => v.readyState >= 2 && !v.paused)')
        assert page.locator('[data-hero] video[src]').count() == 0, 'Offscreen hero was not unloaded'
        page.locator('[data-gallery="robots"] [data-playback]').click()
        assert page.evaluate('Array.from(document.querySelectorAll("[data-gallery=robots] video[src]")).every(v => v.paused)')
        page.locator('[data-gallery="robots"] [data-playback]').click()
        page.locator('[data-gallery="robots"] .next').click()
        page.wait_for_function('document.querySelector("[data-gallery=robots] [data-counter]").textContent.startsWith("3–4")')
        page.wait_for_timeout(500)  # Finish the420ms slide transition before screenshots.
        page.locator('[data-gallery="robots"]').screenshot(path=str(args.output/'robots.png'))
        page.locator('[data-gallery="comparisons"]').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelectorAll("[data-gallery=comparisons] video[src]").length === 4')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=comparisons] video[src]")).every(v => v.readyState >= 2 && !v.paused)')
        page.locator('[data-gallery="comparisons"]').screenshot(path=str(args.output/'comparison.png'))
        page.locator('[data-gallery="long"]').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelectorAll("[data-gallery=long] video[src]").length === 2')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=long] video[src]")).every(v => v.readyState >= 2 && !v.paused)')
        page.locator('[data-gallery="long"]').screenshot(path=str(args.output/'long.png'))
        assert page.locator('[data-gallery="archive"] video[src]').count() == 0
        page.locator('summary.archive-summary').click()
        page.locator('[data-gallery="archive"]').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelectorAll("[data-gallery=archive] video[src]").length === 4')
        page.locator('[data-gallery="archive"] .next').click()
        assert page.locator('[data-gallery="robots"] [data-counter]').inner_text().startswith('3–4'), 'Carousels were cross-wired'
        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        mobile.on('pageerror', lambda error: errors.append(str(error)))
        mobile.goto(url, wait_until='networkidle')
        mobile.locator('[data-gallery="robots"]').scroll_into_view_if_needed()
        assert mobile.locator('video[src]').count() == 0, 'Reduced-motion media loaded without consent'
        mobile.locator('[data-gallery="robots"] [data-playback]').click()
        mobile.wait_for_function('document.querySelectorAll("[data-gallery=robots] video[src]").length === 2')
        mobile.locator('[data-gallery="robots"] [data-playback]').click()
        assert mobile.evaluate('Array.from(document.querySelectorAll("[data-gallery=robots] video[src]")).every(v => v.paused)'), 'Reduced-motion autoplay'
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
        assert mobile.evaluate('Math.abs(document.querySelector("[data-gallery=robots] .carousel-viewport").getBoundingClientRect().height-document.querySelector("[data-gallery=robots] .result-slide").getBoundingClientRect().height) <= 3'), 'Mobile carousel retains tallest hidden-slide whitespace'
        mobile.locator('[data-gallery="robots"]').screenshot(path=str(args.output/'mobile.png'))
        assert not errors, errors
        report = dict(status='passed', checks=['initial hero only', 'manual clean/tracks', 'automatic full-loop interleave', 'viewport lazy loading',
            'offscreen unload', 'play/pause', 'independent navigation', 'baseline playback', 'long playback',
            'collapsed archive lazy loading', 'mobile one-up', 'reduced-motion explicit load and pause', 'no horizontal overflow', 'visible-slide height fit', 'HTTP byte ranges', 'no JS errors'],
            requested_unique_mp4s=len(set(requests)))
        (args.output/'browser_validation.json').write_text(json.dumps(report, indent=2)+'\n')
        browser.close()
    server.shutdown()
    print(report)


if __name__ == '__main__':
    main()
