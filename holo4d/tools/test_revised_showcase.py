"""Browser gate for single-video interleave and robot-only long showcase."""
import argparse
import functools
import http.server
import json
import threading

from pathlib import Path
from playwright.sync_api import sync_playwright
from preview_page import MediaHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(MediaHandler, directory=str(args.page_root))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors, requests = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440, 'height':1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url) if '.mp4' in request.url else None)
        page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
        page.wait_for_function('document.querySelector("[data-hero] video").readyState >= 2')
        page.screenshot(path=str(args.output/'desktop_header.png'))
        assert page.locator('[data-hero] video').count() == 1
        assert all('interleaved.mp4' in request for request in requests)
        assert page.evaluate('HOLO4D_PAGE.sections.robots.length') == 53
        assert page.evaluate('HOLO4D_PAGE.sections.results.length') == 27
        assert page.evaluate('HOLO4D_PAGE.sections.long.every(e => e.id.startsWith("long_robot/"))')
        assert page.evaluate('HOLO4D_PAGE.sections.long.length') == 9
        assert page.evaluate('HOLO4D_PAGE.sections.long.some(e => e.id.endsWith("figure_1__window00__start00000/vista4d_avocado_slice__close_crane_above"))')
        assert page.evaluate('!HOLO4D_PAGE.sections.long.some(e => e.id.endsWith("/static_up"))')
        assert page.evaluate('HOLO4D_PAGE.sections.comparisons.some(e=>e.id==="comparison/golf/dolly-out")')
        assert page.evaluate('HOLO4D_PAGE.sections.comparisons.some(e=>e.id==="comparison/drive-desert/back-follow")')
        assert page.locator('[data-gallery="archive"]').count() == 0
        page.locator('[data-hero] [data-mode="tracks"]').click()
        page.wait_for_function('document.querySelector("[data-hero] video[src]").src.endsWith("overlay.mp4")')
        page.wait_for_function('document.querySelector("[data-hero] video").readyState >= 2')
        page.locator('[data-hero] [data-mode="clean"]').click()
        page.wait_for_function('document.querySelector("[data-hero] video[src]").src.endsWith("clean.mp4")')
        page.locator('[data-hero] [data-mode="auto"]').click()
        page.wait_for_function('document.querySelector("[data-hero] video[src]").src.endsWith("interleaved.mp4")')
        page.locator('[data-hero]').screenshot(path=str(args.output/'single_interleave.png'))
        page.locator('[data-gallery="robots"]').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelectorAll("[data-gallery=robots] video[src]").length === 2')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=robots] video[src]")).every(v=>v.readyState>=2)')
        assert page.locator('[data-hero] video[src]').count() == 0
        page.locator('[data-gallery="robots"]').screenshot(path=str(args.output/'robots.png'))
        assert page.locator('[data-gallery="robots"] select option').count() == 53
        page.locator('[data-gallery="robots"] select').select_option('52')
        page.wait_for_function('document.querySelectorAll("[data-gallery=robots] video[src]").length === 1 && document.querySelector("[data-gallery=robots] video[src]").readyState>=2')
        assert page.locator('[data-gallery="robots"] [data-counter]').inner_text() == '53–53 / 53'
        page.locator('[data-gallery="robots"] select').select_option('0')
        page.wait_for_function('document.querySelectorAll("[data-gallery=robots] video[src]").length === 2')
        page.locator('[data-gallery="robots"] select').select_option('1')
        assert page.locator('[data-gallery="robots"] select').input_value() == '1'
        page.locator('[data-gallery="long"]').scroll_into_view_if_needed()
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=long] video[src]")).length === 2')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=long] video[src]")).every(v=>v.readyState>=2)')
        page.locator('[data-gallery="long"]').screenshot(path=str(args.output/'robot_long.png'))
        long_urls = set()
        for index in range(9):
            page.evaluate('(i) => document.querySelectorAll("[data-gallery=long] .thumbnail-button")[i].click()', index)
            expected_visible = min(2, 9 - (index // 2) * 2)
            page.wait_for_function('(n)=>Array.from(document.querySelectorAll("[data-gallery=long] video[src]")).length===n && Array.from(document.querySelectorAll("[data-gallery=long] video[src]")).every(v=>v.readyState>=2 && !v.error)', arg=expected_visible)
            long_urls.update(page.locator('[data-gallery=long] video[src]').evaluate_all('(vs)=>vs.map(v=>v.src)'))
            assert page.locator('[data-hero] video[src]').count() == 0
        assert len(long_urls) == 9, long_urls
        response = page.request.get(sorted(long_urls)[0], headers={'Range': 'bytes=0-1023'})
        assert response.status == 206
        assert len(response.body()) == 1024
        page.locator('[data-gallery="comparisons"]').scroll_into_view_if_needed()
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=comparisons] video[src]")).every(v=>v.readyState>=2) && document.querySelectorAll("[data-gallery=comparisons] video[src]").length===4')
        page.locator('[data-gallery="comparisons"] [data-playback]').click()
        page.locator('[data-gallery="comparisons"] .timeline input').first.evaluate('(input)=>{input.value="500";input.dispatchEvent(new Event("input",{bubbles:true}));}')
        page.wait_for_function('Array.from(document.querySelectorAll("[data-gallery=comparisons] .is-active:first-child video[src]")).every(v=>Math.abs(v.currentTime-v.duration*.5)<.1)')
        page.locator('[data-gallery="comparisons"]').screenshot(path=str(args.output/'comparisons.png'))
        mobile = browser.new_page(viewport={'width':390,'height':844}, reduced_motion='reduce')
        mobile.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
        assert mobile.locator('video[src]').count() == 0
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        mobile.screenshot(path=str(args.output/'mobile_header.png'))
        mobile.locator('[data-gallery="robots"]').scroll_into_view_if_needed()
        mobile.wait_for_function('Boolean(document.querySelector("[data-gallery=robots] .is-active video")?.poster)')
        assert mobile.locator('video[src]').count() == 0
        mobile.locator('[data-gallery="robots"]').screenshot(path=str(args.output/'mobile_robot_poster.png'))
        mobile.locator('[data-gallery="robots"] [data-playback]').click()
        mobile.wait_for_function('document.querySelectorAll("video[src]").length===1 && document.querySelector("video[src]").readyState>=2')
        tablet = browser.new_page(viewport={'width':820,'height':1000}, reduced_motion='reduce')
        tablet.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
        assert tablet.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert tablet.locator('.contents-sidebar').is_hidden()
        assert tablet.locator('.topbar').is_visible()
        assert tablet.locator('video[src]').count() == 0
        tablet.screenshot(path=str(args.output/'tablet_header.png'))
        assert not errors, errors
        browser.close()
    server.shutdown()
    (args.output/'revised_showcase_validation.json').write_text(json.dumps(
        dict(status='passed', errors=errors, checks=['one-player interleave','manual modes',
             'visible-only media','robot53/native27','robot long9 motion-screened','requested comparisons',
             'archive removed','mobile no autoplay/no overflow','all nine robot videos decoded',
             'HTTP byte-range 206','scene jump without eager media','synchronized comparison seeking',
             'poster-only mobile until explicit click','tablet navigation/no overflow']),indent=2)+'\n')


if __name__ == '__main__':
    main()
