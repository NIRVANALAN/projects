/* Fresh clones and the public GitHub page use the audited compact HF media.
 * Explicit localhost ?local_media=1 uses development/portable media copies.
 */
const holo4dLocalPreview = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
// A clean clone has no Civo mounts. Use hosted media unless explicitly reviewing
// local caches; the opt-in is never honored on the public website.
const holo4dUseLocalMedia = holo4dLocalPreview && new URLSearchParams(location.search).get('local_media') === '1';
const holo4dPublicMedia = 'https://huggingface.co/yslan/Holo4D-2026/resolve/f3c23e9107866c7ecb0cefbb52eb829297256146/project_page/media_20261026_native/';
window.HOLO4D_MEDIA_CONFIG = Object.freeze(window.HOLO4D_MEDIA_CONFIG || {
  videoBase: holo4dUseLocalMedia ? 'static/videos/web/' : holo4dPublicMedia,
  // Tiny first-frame covers ship with the page: no HF redirect before a preview.
  posterBase: 'static/posters/web/'
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
  if (holo4dUseLocalMedia && entry.postgen_preview) {
    return new URL(entry.path + '/' + filename, holo4dMediaBase(entry.preview_media_base)).href;
  }
  return new URL(entry.path + '/' + filename, poster ? holo4dPosterBase : holo4dVideoBase).href;
}
