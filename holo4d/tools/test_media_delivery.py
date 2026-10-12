"""Real Chromium checks for download consent, paired failure recovery and media roots.

HTTPS CDN requests are intercepted and served by a second local origin. This
checks browser delivery behavior; it does not certify or publish a real CDN.
"""
import argparse
import functools
import http.server
import json
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from preview_page import MediaHandler


class QuietMediaHandler(MediaHandler):
    def log_message(self, format, *args):
        pass


class DelayedMediaHandler(QuietMediaHandler):
    release = threading.Event()

    def do_GET(self):
        if self.path.split('?', 1)[0].endswith('.mp4'):
            self.release.wait(timeout=10)
        super().do_GET()


def playing(page, selector, count):
    page.wait_for_function('''([selector,count]) => {
      const videos=[...document.querySelectorAll(selector+" video[src]")];
      return videos.length===count && videos.every(v=>v.readyState>=2 && !v.paused);
    }''', arg=[selector, count])


def proxy_media(route, upstream):
    response = route.fetch(url=route.request.url.replace('https://media.example.test/', upstream))
    route.fulfill(response=response)


def fail_overlay_once(route, state):
    if not state['failed']:
        state['failed'] = True
        route.fulfill(status=503, body='Intentional test outage')
    else:
        route.continue_()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(QuietMediaHandler, directory=str(args.page_root))
    servers = [http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler) for _ in range(2)]
    for server in servers:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{servers[0].server_port}/'
    upstream = f'http://127.0.0.1:{servers[1].server_port}/'
    errors, checks = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        saver = browser.new_page(viewport={'width': 1440, 'height': 1000})
        saver.on('pageerror', lambda error: errors.append(str(error)))
        saver.add_init_script('Object.defineProperty(navigator,"connection",{get:()=>({saveData:true,effectiveType:"4g"})})')
        requested = []
        saver.on('request', lambda request: requested.append(request.url) if '.mp4' in request.url else None)
        saver.goto(url, wait_until='networkidle')
        assert not requested and saver.locator('video[src]').count() == 0
        assert saver.locator('[data-media-policy]').input_value() == 'click'
        saver.wait_for_function('document.querySelector("[data-hero] video").poster.endsWith("poster.jpg")')
        saver.locator('[data-hero]').screenshot(path=str(args.output/'data-saver-posters.png'))
        saver.locator('[data-hero] [data-playback]').click()
        playing(saver, '[data-hero]', 2)
        robots = '[data-gallery="robots"]'
        saver.locator(robots).scroll_into_view_if_needed()
        saver.wait_for_function('document.querySelectorAll("[data-hero] video[src]").length===0')
        assert saver.locator(robots+' video[src]').count() == 0
        saver.locator(robots+' [data-playback]').click()
        playing(saver, robots, 4)
        saver.locator(robots+' .next').click()
        assert saver.locator(robots+' video[src]').count() == 0
        assert saver.locator(robots+' .result-slide').first.evaluate('node=>node.inert')
        saver.locator(robots+' [data-playback]').click()
        playing(saver, robots, 4)
        saver.locator('[data-media-policy]').select_option('viewport')
        saver.locator('[data-media-policy]').select_option('click')
        saver.wait_for_function('document.querySelectorAll("video[src]").length===0')
        checks.extend(['Save-Data zero MP4 requests at startup', 'real first-frame poster before consent',
                       'click consent scoped to one gallery', 'next-page consent does not prefetch; hidden cards inert',
                       'policy switching unloads active media'])
        saver.close()

        slow = browser.new_page()
        slow.add_init_script('Object.defineProperty(navigator,"connection",{get:()=>({saveData:false,effectiveType:"slow-2g"})})')
        slow.goto(url, wait_until='networkidle')
        assert slow.locator('[data-media-policy]').input_value() == 'click'
        assert slow.locator('video[src]').count() == 0
        checks.append('slow-2G automatically uses click-to-load')
        slow.close()

        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        mobile.on('pageerror', lambda error: errors.append(str(error)))
        mobile.goto(url, wait_until='networkidle')
        assert mobile.locator('video[src]').count() == 0
        mobile.locator(robots).scroll_into_view_if_needed()
        mobile.locator(robots+' [data-playback]').click()
        playing(mobile, robots, 2)
        mobile.locator(robots+' [data-expand]').first.click()
        mobile.wait_for_function('document.fullscreenElement?.classList.contains("web-stage")')
        playing(mobile, robots, 2)
        assert mobile.locator(robots+' .media-loading').first.is_hidden()
        mobile.evaluate('document.exitFullscreen()')
        mobile.wait_for_function('document.fullscreenElement===null')
        mobile.emulate_media(reduced_motion='no-preference')
        mobile.locator(robots+' [data-playback]').click()
        mobile.emulate_media(reduced_motion='reduce')
        mobile.wait_for_function('document.querySelectorAll("video[src]").length===0')
        for width in (320, 390, 768):
            mobile.set_viewport_size({'width': width, 'height': 844})
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
        mobile.locator('.media-toolbar').scroll_into_view_if_needed()
        mobile.screenshot(path=str(args.output/'mobile-policy.png'))
        checks.extend(['reduced-motion zero automatic MP4s', 'portrait fullscreen playback and exit',
                       'live reduced-motion change unloads media', '320/390/768px layout fit'])
        mobile.close()

        remote = browser.new_page(viewport={'width': 1440, 'height': 1000})
        remote.on('pageerror', lambda error: errors.append(str(error)))
        config = dict(videoBase='https://media.example.test/static/videos/web/', posterBase='static/videos/web/')
        remote.add_init_script('window.HOLO4D_MEDIA_CONFIG='+json.dumps(config))
        remote.route('https://media.example.test/**', functools.partial(proxy_media, upstream=upstream))
        remote.goto(url, wait_until='networkidle')
        playing(remote, '[data-hero]', 2)
        assert remote.evaluate('[...document.querySelectorAll("video[src]")].every(v=>v.src.startsWith("https://media.example.test/"))')
        assert remote.evaluate('document.querySelector("[data-hero] video").poster.startsWith(location.origin)')
        invalid = ['http://unapproved.example/media/', 'https://user:password@example.test/media/',
                   'https://example.test/media/?token=secret', 'https://example.test/media/#fragment',
                   'javascript:alert(1)', 'file:///scratch/media/']
        assert remote.evaluate('''values=>values.every(value=>{
          try {holo4dMediaBase(value);return false;} catch (_) {return true;}
        })''', invalid)
        remote.evaluate('Object.defineProperty(document,"hidden",{configurable:true,get:()=>true});document.dispatchEvent(new Event("visibilitychange"))')
        assert remote.locator('video[src]').count() == 0
        remote.evaluate('delete document.hidden;document.dispatchEvent(new Event("visibilitychange"))')
        playing(remote, '[data-hero]', 2)
        checks.extend(['mock HTTPS video host with independent local posters decodes',
                       'reject credentials/tokens/unsafe or non-HTTPS external roots',
                       'hidden-tab unload/resume (simulated visibility event)'])
        remote.close()

        retry = browser.new_page(viewport={'width': 1440, 'height': 1000})
        retry.on('pageerror', lambda error: errors.append(str(error)))
        failed = {'failed': False}
        retry.route('**/overlay.mp4', functools.partial(fail_overlay_once, state=failed))
        retry.goto(url, wait_until='networkidle')
        retry.locator('[data-hero] .media-retry').wait_for(state='visible')
        assert retry.evaluate('[...document.querySelectorAll("[data-hero] video")].every(v=>v.paused)')
        retry.evaluate('document.querySelector("[data-hero] video").dispatchEvent(new Event("canplay"))')
        assert retry.locator('[data-hero] .media-error').is_visible(), 'Healthy paired video masked the other error'
        retry.locator('[data-hero]').screenshot(path=str(args.output/'retry-outage.png'))
        retry.locator('[data-hero] .media-retry').click()
        playing(retry, '[data-hero]', 2)
        assert retry.locator('[data-hero] .media-error').is_hidden()
        assert retry.locator('[data-hero] .media-retry').is_hidden()
        checks.extend(['intentional503 pauses entire pair', 'healthy pair member does not erase error',
                       'explicit Retry recovers both synchronized videos'])
        retry.close()

        loading = browser.new_page(viewport={'width': 1440, 'height': 1000})
        loading.on('pageerror', lambda error: errors.append(str(error)))
        delayed = http.server.ThreadingHTTPServer(('127.0.0.1', 0),
            functools.partial(DelayedMediaHandler, directory=str(args.page_root)))
        threading.Thread(target=delayed.serve_forever, daemon=True).start()
        loading.goto(f'http://127.0.0.1:{delayed.server_port}/', wait_until='domcontentloaded')
        loading.locator('[data-hero] .media-loading').wait_for(state='visible')
        assert loading.locator('[data-hero] .web-stage').get_attribute('aria-busy') == 'true'
        loading.locator('[data-hero]').screenshot(path=str(args.output/'loading-status.png'))
        DelayedMediaHandler.release.set()
        playing(loading, '[data-hero]', 2)
        loading.locator('[data-hero] .media-loading').wait_for(state='hidden')
        assert loading.locator('[data-hero] .web-stage').get_attribute('aria-busy') == 'false'
        checks.append('delayed delivery shows and clears accessible loading status')
        loading.close()
        delayed.shutdown()
        assert not errors, errors
        checks.append('no JavaScript errors')
        browser.close()
    for server in servers:
        server.shutdown()
    report = dict(status='passed', page_root=str(args.page_root), check_count=len(checks), checks=checks)
    (args.output/'media_delivery_validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report)


if __name__ == '__main__':
    main()
