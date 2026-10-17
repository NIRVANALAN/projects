/* Videos load and play only while on screen; data saver / reduced motion keep native controls instead. */
const quiet = matchMedia('(prefers-reduced-motion: reduce)').matches || navigator.connection?.saveData;
const onScreen = new IntersectionObserver(entries => entries.forEach(({ target: v, isIntersecting }) => {
  if (!isIntersecting) return v.pause();
  if (!v.src) v.src = v.dataset.src;
  v.play().catch(() => {});
}), { threshold: 0.25 });
document.querySelectorAll('video[data-src]').forEach(v => {
  v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'none';
  if (quiet) { v.controls = true; v.src = v.dataset.src; } // preload=none: nothing downloads until Play
  else onScreen.observe(v);
});

const copy = document.querySelector('[data-copy]');
copy?.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(document.getElementById(copy.dataset.copy).innerText); copy.textContent = 'Copied'; }
  catch { copy.textContent = 'Select to copy'; }
  setTimeout(() => { copy.textContent = 'Copy'; }, 1500);
});
