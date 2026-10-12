"""Real-browser gate for homepage identity and grouped, lazy video cards."""
import argparse
import functools
import http.server
import json
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from preview_page import MediaHandler


def hold_response(route, held, enabled):
    if enabled[0]:
        held.append(route)
    else:
        route.continue_()


def wait_videos(page, selector, count):
    page.wait_for_function("([s,n])=>{const vs=[...document.querySelectorAll(s+' video[src]')];return vs.length===n && vs.every(v=>v.readyState>=2 && !v.error)}", arg=[selector, count])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--url', help='Validate the deployed page instead of the local server')
    parser.add_argument('--media-base', help='Override media with the pinned public HTTPS export')
    parser.add_argument('--ui-only', action='store_true', help='Validate existing media while the DAVIS re-export is pending')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(MediaHandler, directory=str(args.page_root))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440, 'height':1000}, reduced_motion='reduce')
        page.set_default_timeout(90000)
        if args.media_base:
            page.add_init_script('window.HOLO4D_MEDIA_CONFIG = '+json.dumps({'videoBase':args.media_base,'posterBase':args.media_base})+';')
        page.on('pageerror', lambda error: errors.append(str(error)))
        url=args.url or f'http://127.0.0.1:{server.server_port}/'
        page.goto(url, wait_until='networkidle')
        assert page.locator('[data-hero]').count() == 0
        assert page.locator('video[src]').count() == 0
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(255, 255, 255)'
        assert page.evaluate('getComputedStyle(document.querySelector(".authors a")).color') == 'rgb(23, 114, 208)'
        assert page.locator('.paper-kicker').inner_text() == 'NeurIPS 2026'
        assert page.evaluate('getComputedStyle(document.querySelector(".paper-kicker")).textTransform') == 'none'
        assert page.evaluate('document.querySelector(".paper-kicker").getBoundingClientRect().top > document.querySelector(".equal-contribution").getBoundingClientRect().top')
        assert page.evaluate('HOLO4D_PAGE.sections.robots.length') == 53
        assert page.evaluate('HOLO4D_PAGE.sections.results.length') == 27
        if not args.ui_only:
            assert page.evaluate('HOLO4D_PAGE.sections.davis.length') == 8
            assert page.evaluate('HOLO4D_PAGE.sections.davis.filter(e=>e.scene==="Classic car").every(e=>e.backend==="vggt_omega_cowtracker" && e.id.includes("davis_cow"))')
        assert page.evaluate('document.querySelector("#robots").offsetTop < document.querySelector("#results").offsetTop')
        assert page.locator('[data-gallery="davis"]').count() == 0
        assert page.locator('[data-gallery="reshooting"] h3').filter(has_text='Classic car').count() == 0
        assert page.evaluate('HOLO4D_PAGE.sections.long.length') == 9
        page.screenshot(path=str(args.output/'desktop_header.png'))
        selectors = ['[data-gallery="robots"][data-orientation="portrait"]',
                     '[data-gallery="robots"][data-orientation="landscape"]',
                     '[data-gallery="reshooting"]',
                     '[data-gallery="long"][data-orientation="portrait"]',
                     '[data-gallery="long"][data-orientation="landscape"]',
                     '[data-gallery="comparisons"]']
        long_urls = set()
        for i, selector in enumerate(selectors):
            root = page.locator(selector)
            root.scroll_into_view_if_needed()
            if root.get_attribute('data-same-scene') is not None:
                for option in range(0,root.locator('select option').count(),2):
                    root.locator('select').select_option(str(option))
                    cards = root.locator('.result-slide[aria-hidden="false"]')
                    assert cards.count() == 2
                    assert cards.evaluate_all('(cs)=>cs[0].dataset.sceneId===cs[1].dataset.sceneId && cs[0].dataset.trajectory!==cs[1].dataset.trajectory')
                root.locator('select').select_option('0')
                assert not root.locator('h3').evaluate_all('(hs)=>hs.some(h=>/humanoid robot/.test(h.textContent))')
            assert root.locator('.result-slide[aria-hidden="false"]').count() == 2
            assert root.locator('video[src]').count() == 0
            root.locator('.result-slide[aria-hidden="false"] .card-playback').first.click()
            count = 4 if 'comparisons' in selector else 2
            wait_videos(page, selector, count)
            page.wait_for_function('(s)=>[...document.querySelectorAll(s+" .result-slide[aria-hidden=false] video")].every(v=>!v.paused && v.currentTime>.15)',arg=selector)
            assert root.locator('video[src]').evaluate_all('(vs)=>Math.max(...vs.map(v=>v.currentTime))-Math.min(...vs.map(v=>v.currentTime))<.3')
            selected = root.locator('select').input_value()
            root.locator('.result-slide[aria-hidden="false"] .timeline input').first.focus()
            page.keyboard.press('ArrowRight')
            assert root.locator('select').input_value() == selected
            root.locator('.result-slide[aria-hidden="false"] .card-playback').first.click()
            assert root.locator('.result-slide[aria-hidden="false"]').first.locator('video').evaluate_all('(vs)=>vs.every(v=>v.paused)')
            root.locator('.result-slide[aria-hidden="false"] .card-playback').first.click()
            if 'robots' in selector:
                for mode, filename in [('auto','interleaved.mp4'), ('tracks','overlay.mp4'), ('clean','clean.mp4')]:
                    root.locator(f'[data-mode="{mode}"]').click()
                    wait_videos(page, selector, 2)
                    assert root.locator('video[src]').evaluate_all('(vs)=>vs.every(v=>v.src.endsWith("'+filename+'"))')
            if 'long' in selector:
                for option in range(root.locator('select option').count()):
                    root.locator('select').select_option(str(option))
                    root.locator('[data-playback]').click()
                    wait_videos(page, selector, 2)
                    long_urls.update(root.locator('video[src]').evaluate_all('(vs)=>vs.map(v=>v.src)'))
            # Select last case of an odd-size gallery: two filled cards, not a blank half.
            last = root.locator('select option').count()-1
            root.locator('select').select_option(str(last))
            assert root.locator('.result-slide[aria-hidden="false"]').count() == 2
            assert root.locator('select').input_value() == str(last)
            root.locator('[data-playback]').click()
            wait_videos(page, selector, count)
            if 'comparisons' in selector:
                root.locator('[data-playback]').click()
                root.locator('.result-slide[aria-hidden="false"] .timeline input').first.evaluate('(s)=>{s.value="500";s.dispatchEvent(new Event("input",{bubbles:true}));}')
                page.wait_for_function('(s)=>[...document.querySelector(s+" .is-active").querySelectorAll("video")].every(v=>Math.abs(v.currentTime-v.duration*.5)<.1)', arg=selector)
            root.screenshot(path=str(args.output/f'gallery_{i}.png'))
        assert len(long_urls) == 9
        response = page.request.get(sorted(long_urls)[0], headers={'Range':'bytes=0-1023'})
        assert response.status == 206 and len(response.body()) == 1024
        # Deliberately hold the RIGHT media response. The left must remain on
        # its first frame until the pair is buffered, rather than starting early.
        buffered = browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        buffered.set_default_timeout(90000)
        if args.media_base:
            buffered.add_init_script('window.HOLO4D_MEDIA_CONFIG = '+json.dumps({'videoBase':args.media_base,'posterBase':args.media_base})+';')
        buffered.on('pageerror',lambda error: errors.append(str(error)))
        buffered.goto(url,wait_until='networkidle')
        pair = buffered.locator(selectors[0])
        pair.scroll_into_view_if_needed()
        right_url = pair.locator('.result-slide[aria-hidden="false"] video').last.evaluate('(v)=>new URL(v.dataset.src,document.baseURI).href')
        held = []
        enabled = [True]
        buffered.route(right_url,functools.partial(hold_response,held=held,enabled=enabled))
        pair.locator('.card-playback').first.click()
        buffered.wait_for_function('(s)=>document.querySelector(s+" .result-slide[aria-hidden=false] video").readyState>=3',arg=selectors[0])
        assert held
        assert pair.locator('.result-slide[aria-hidden="false"] video').first.evaluate('(v)=>v.paused && v.currentTime===0')
        enabled[0] = False
        for route in held:
            if not route.request.failure:
                route.continue_()
        wait_videos(buffered,selectors[0],2)
        buffered.wait_for_function('(s)=>[...document.querySelectorAll(s+" .result-slide[aria-hidden=false] video")].every(v=>!v.paused && v.currentTime>.15)',arg=selectors[0])
        buffered.screenshot(path=str(args.output/'buffered_scene_pair.png'))
        buffered.close()
        mobile = browser.new_page(viewport={'width':390,'height':844}, reduced_motion='reduce')
        mobile.set_default_timeout(90000)
        if args.media_base:
            mobile.add_init_script('window.HOLO4D_MEDIA_CONFIG = '+json.dumps({'videoBase':args.media_base,'posterBase':args.media_base})+';')
        mobile.on('pageerror', lambda error: errors.append(str(error)))
        mobile.goto(url, wait_until='networkidle')
        assert mobile.locator('video[src]').count() == 0
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
        mobile.screenshot(path=str(args.output/'mobile_header.png'))
        root = mobile.locator(selectors[0])
        root.scroll_into_view_if_needed()
        assert root.locator('.result-slide[aria-hidden="false"]').count() == 1
        mobile.wait_for_function('(s)=>Boolean(document.querySelector(s+" .result-slide[aria-hidden=false] video")?.poster)', arg=selectors[0])
        root.locator('.result-slide[aria-hidden="false"] .card-playback').click()
        wait_videos(mobile, selectors[0], 1)
        source = root.locator('.result-slide[aria-hidden="false"]').get_attribute('data-scene-id')
        trajectory = root.locator('.result-slide[aria-hidden="false"]').get_attribute('data-trajectory')
        root.locator('.next').click()
        assert root.locator('.result-slide[aria-hidden="false"]').get_attribute('data-scene-id') == source
        assert root.locator('.result-slide[aria-hidden="false"]').get_attribute('data-trajectory') != trajectory
        assert not errors, errors
        browser.close()
    server.shutdown()
    (args.output/'home_style_validation.json').write_text(json.dumps(dict(status='passed', scope='existing-media UI only; DAVIS additions not yet verified' if args.ui_only else 'complete updated gallery', errors=errors,
        checks=['homepage colors','no hero duplication','NeurIPS placement/case','53 robots grouped by actual source ID',
                'robots first','same-scene distinct-camera desktop pairs','paired DAVIS additions pending' if args.ui_only else 'eight DAVIS assets; six paired demos; classic car CoW/GMOS25 review withheld','individual play/pause',
                'buffered paired startup/playback including deliberately delayed right response',
                'interleave/manual clean/tracks','nine long videos decoded','no empty final pair',
                'paired seeking','poster-first no eager MP4','mobile one-card/on-demand','HTTP206']),indent=2)+'\n')


if __name__ == '__main__':
    main()
