/* Local previews use the cache/portable release; the public GitHub page uses
 * the audited compact HF media (never an absolute Civo filesystem mount).
 */
const holo4dLocalPreview = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
const holo4dPublicMedia = 'https://huggingface.co/yslan/Holo4D-2026/resolve/d961d338edf61d0f3e2786e4ced60be69c02bcda/project_page/media_20261012/';
window.HOLO4D_MEDIA_CONFIG = Object.freeze(window.HOLO4D_MEDIA_CONFIG || {
  videoBase: holo4dLocalPreview ? 'static/videos/web/' : holo4dPublicMedia,
  posterBase: holo4dLocalPreview ? 'static/videos/web/' : holo4dPublicMedia
});

function holo4dMediaBase(value) {
  const base = new URL(value, document.baseURI);
  const local = host => ['localhost', '127.0.0.1', '[::1]'].includes(host);
  const localPreview = local(base.hostname) && local(location.hostname);
  if (!['http:', 'https:'].includes(base.protocol) ||
      (base.protocol !== 'https:' && base.origin !== location.origin && !localPreview) ||
      base.username || base.password || base.search || base.hash) {
    throw new Error('Holo4D media roots must be relative or approved HTTPS directories without credentials/query tokens.');
  }
  if (!base.pathname.endsWith('/')) base.pathname += '/';
  return base;
}

const holo4dVideoBase = holo4dMediaBase(window.HOLO4D_MEDIA_CONFIG.videoBase);
const holo4dPosterBase = holo4dMediaBase(window.HOLO4D_MEDIA_CONFIG.posterBase);
function holo4dMediaURL(entry, filename, poster=false) {
  return new URL(entry.path + '/' + filename, poster ? holo4dPosterBase : holo4dVideoBase).href;
}
