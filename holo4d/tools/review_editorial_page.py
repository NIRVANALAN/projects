"""Browser screenshots, viewport loading checks and read-only reference review."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading
import time

from playwright.sync_api import sync_playwright
from preview_page import MediaHandler


class QuietHandler(MediaHandler):
    def log_message(self, *_args):
        pass


def snapshot(page, url, output):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    start = time.monotonic()
    response = page.goto(url, wait_until='domcontentloaded', timeout=45000)
    page.wait_for_function('window.galleries !== undefined || document.querySelector(".result-slide")')
    page.wait_for_timeout(1500)
    page.screenshot(path=str(output/'desktop_first_screen.png'))
    report = dict(status=response.status, dom_seconds=round(time.monotonic()-start-1.5, 3),
        errors=errors, geometry=page.evaluate('''() => ({
          firstVideoTop: document.querySelector(".blend-stage").getBoundingClientRect().top,
          overflow: document.documentElement.scrollWidth > innerWidth,
          activeMP4s: document.querySelectorAll("video[src]").length,
          posterRequests: performance.getEntriesByType("resource").filter(r=>/\\.jpg(?:[?]|$)/.test(r.name)).length,
          headings: [...document.querySelectorAll("main > section[id]")].map(s=>s.id)
        })'''))
    assert not report['geometry']['overflow']
    assert report['geometry']['activeMP4s'] == 0, 'Reduced-motion first visit must not request MP4'
    assert report['geometry']['firstVideoTop'] < 1000, 'First screen still hides all media'
    root = page.locator('[data-gallery="robots"][data-orientation="portrait"]')
    root.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    root.screenshot(path=str(output/'robot_gallery.png'))
    # Opening provenance must resize the carousel rather than clip its content.
    root.locator('.is-active .sample-details').first.locator('summary').click()
    page.wait_for_timeout(100)
    assert root.locator('.is-active .sample-details[open]').count() == 1
    return report


def reference_snapshot(browser, url, name, output):
    page = browser.new_page(viewport=dict(width=1440, height=1000))
    try:
        response = page.goto(url, wait_until='domcontentloaded', timeout=45000)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(output/f'reference_{name}.png'))
        return dict(url=url, status=response.status, title=page.title())
    except Exception as error:
        return dict(url=url, error=str(error))
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--page-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--references', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0), functools.partial(QuietHandler, directory=str(args.page_root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/?local_media=1'
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport=dict(width=1440,height=1000), reduced_motion='reduce')
        report = snapshot(page, url, args.output)
        page.close()
        mobile = browser.new_page(viewport=dict(width=390,height=844), reduced_motion='reduce')
        mobile.goto(url, wait_until='networkidle')
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
        mobile.screenshot(path=str(args.output/'mobile_first_screen.png'))
        mobile.locator('[data-gallery="robots"][data-orientation="portrait"]').scroll_into_view_if_needed()
        mobile.screenshot(path=str(args.output/'mobile_robot_gallery.png'))
        mobile.close()
        if args.references:
            report['references'] = [reference_snapshot(browser, site, name, args.output) for name,site in [
                ('vggt_omega','https://vggt-omega.github.io/'),
                ('vista4d','https://eyeline-labs.github.io/Vista4D/')]]
        browser.close()
    server.shutdown()
    (args.output/'editorial_review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
