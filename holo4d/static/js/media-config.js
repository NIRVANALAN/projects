/* Deployment settings only: this does not publish or upload any media.
 * Relative defaults work in the self-contained release. After publication,
 * videoBase and posterBase can point at separate approved HTTPS directories.
 */
window.HOLO4D_MEDIA_CONFIG = Object.freeze(window.HOLO4D_MEDIA_CONFIG || {
  videoBase: 'static/videos/web/',
  posterBase: 'static/videos/web/'
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
