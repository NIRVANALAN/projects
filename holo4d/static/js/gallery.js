/* Poster-first, viewport-scoped galleries; no MP4 src at startup. */
const connection = navigator.connection;
let mediaPolicy = connection?.saveData || /(^slow-)?2g$/.test(connection?.effectiveType || '') ? 'click' : 'viewport';
const desktopQuery = matchMedia('(min-width: 761px)');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const galleries = [];
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text) n.textContent = text;
  return n;
}
function playbackTime(seconds) {
  const value = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(value / 60)}:${String(value % 60).padStart(2, '0')}`;
}
function sceneKey(entry) {
  if (entry.scene_id) return entry.scene_id;
  // Compatibility with previously exported manifests; display names are not IDs.
  const source = entry.id.match(/(?:figure|tesla)_\d+__window\d+__start\d+|(?:[A-Za-z]+Lab|TRI|RAD)__.*?__static_[12]__\d+/)?.[0];
  return source ? 'robot/'+source : entry.id.includes('/long/') ? entry.id : entry.scene;
}
function sameScenePairs(entries) {
  const scenes = new Map();
  entries.forEach(entry => {
    if (entry.review_pending || (entry.id.includes('/davis_cow/') && !entry.review_approved)) return;
    const key = sceneKey(entry);
    if (!scenes.has(key)) scenes.set(key, []);
    if (!scenes.get(key).some(e => e.camera === entry.camera)) scenes.get(key).push(entry);
  });
  const pairs = [];
  scenes.forEach(group => {
    // Singletons stay in the evidence/media archive, not a misleading paired row.
    for (let i=0; i<group.length-1; i+=2) pairs.push(group.slice(i,i+2));
    if (group.length>2 && group.length%2) pairs.push(group.slice(-2));
  });
  return pairs.flat();
}
function displayScene(entry) {
  if (/^Figure humanoid/.test(entry.scene)) return 'Figure humanoid';
  if (/^Tesla humanoid/.test(entry.scene)) return 'Tesla humanoid';
  return entry.scene;
}
function video(entry, key) {
  const v = el('video', 'blend-layer blend-' + key);
  v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'none';
  v.dataset.src = holo4dMediaURL(entry, key + '.mp4');
  v.dataset.poster = holo4dMediaURL(entry, key === 'baseline' ? 'baseline-poster.jpg' : 'poster.jpg', true);
  v.setAttribute('aria-label', `${displayScene(entry)}: ${key === 'baseline' ? 'Vista4D' : 'Holo4D '+key}`);
  return v;
}
class Card {
  constructor(entry) {
    this.entry = entry; this.active = false; this.loop = 0; this.last = 0; this.localPaused = false;
    this.node = el('article', 'result-slide');
    const header = el('header', 'slide-heading');
    header.append(el('h3', '', displayScene(entry)), el('p', '', 'Target camera: '+entry.camera));
    this.node.dataset.sceneId = sceneKey(entry);
    this.node.dataset.trajectory = entry.camera;
    this.stage = el('div', 'blend-stage web-stage');
    this.stage.style.setProperty('--slide-aspect', entry.aspect);
    this.videos = [video(entry, entry.interleaved ? 'interleaved' : 'clean')];
    if (entry.has_overlay && !entry.interleaved) this.videos.push(video(entry, 'overlay'));
    if (entry.kind === 'comparison') {
      this.stage.classList.add('comparison-stage');
      this.videos.push(video(entry, 'baseline'));
      ['Holo4D','Vista4D'].forEach((name, i) => {
        const panel = el('div', 'comparison-panel');
        panel.append(el('span', 'method-label', name), this.videos[i]);
        this.stage.append(panel);
      });
    } else this.stage.append(...this.videos);
    this.state = el('span', 'web-state', entry.kind === 'long' ? 'Source / generated' : 'Clean');
    if (entry.kind !== 'comparison') this.stage.append(this.state);
    this.error = el('span', 'media-error', 'Video unavailable — check the media host.');
    this.error.hidden = true; this.stage.append(this.error);
    this.error.setAttribute('role', 'alert');
    this.loading = el('span', 'media-loading', 'Loading video…');
    this.loading.hidden = true; this.loading.setAttribute('role', 'status');
    this.stage.append(this.loading);
    this.retry = el('button', 'media-retry', 'Retry video');
    this.retry.type = 'button'; this.retry.hidden = true;
    this.retry.addEventListener('click', () => {
      if (!this.active || !this.allowLoad) return;
      this.resetMedia(); this.onWaiting?.(); this.load();
    });
    this.stage.append(this.retry);
    this.stage.setAttribute('aria-busy', 'false');
    const figure = el('figure', 'blend-visual');
    const caption = entry.kind === 'comparison' ? 'Same native target trajectory · different source geometry backends' : entry.kind === 'long' ? 'Source · Generated continuation · labelled chunk boundaries' : 'Source · Projected track condition · Holo4D';
    figure.append(this.stage, el('figcaption', '', caption));
    this.node.append(header, figure, el('p', 'asset-note', entry.note));
    const timeline = el('div', 'timeline');
    this.seek = el('input'); this.seek.type = 'range';
    this.seek.min = '0'; this.seek.max = '1000'; this.seek.value = '0';
    this.seek.disabled = true;
    this.seek.setAttribute('aria-label', `Playback time: ${displayScene(entry)}, ${entry.camera}`);
    this.clock = el('output', '', 'First-frame preview');
    this.playback = el('button', 'card-playback', 'Play');
    this.playback.type = 'button';
    this.playback.setAttribute('aria-label', `Play or pause: ${displayScene(entry)}, ${entry.camera}`);
    this.playback.addEventListener('click', () => {
      if (!this.active) return;
      if (!this.allowLoad || this.paused) {
        this.localPaused = false;
        this.onPlayRequest?.();
      } else {
        this.localPaused = !this.localPaused;
        if (this.localPaused) this.videos.forEach(v => v.pause());
        else this.play();
      }
      this.updateTimeline();
    });
    timeline.append(this.playback, this.seek, this.clock); this.node.append(timeline);
    this.seek.addEventListener('input', () => {
      const anchor = this.videos[0];
      if (!Number.isFinite(anchor.duration) || anchor.duration <= 0) return;
      const requested = Number(this.seek.value) / 1000 * anchor.duration;
      this.videos.forEach(v => {
        if (v.readyState >= 1 && Number.isFinite(v.duration)) {
          v.currentTime = Math.min(requested, Math.max(0, v.duration - .01));
        }
      });
      this.updateTimeline(); this.sync();
    });
    const expand = el('button', 'expand-video', 'Expand video');
    expand.type = 'button'; expand.dataset.expand = '';
    expand.hidden = !this.stage.requestFullscreen;
    expand.addEventListener('click', () => this.stage.requestFullscreen?.().catch(() => {}));
    this.node.append(expand);
    if (entry.metrics) {
      const m = entry.metrics;
      this.node.append(el('p','metric-note',`Pi3 RotErr ↓: ${m.ours_pi3_rotation_error_deg.toFixed(3)}° / ${m.vista4d_pi3_rotation_error_deg.toFixed(3)}° · VGGT RPE-R ↓: ${m.ours_rot_err.toFixed(3)}° / ${m.vista4d_rot_err.toFixed(3)}° (Holo4D / Vista4D)`));
    }
    if (entry.kind === 'long') this.node.append(el('p','asset-note','Clean full-length export; continuous track overlay not yet available.'));
    this.videos.forEach(v => {
      v.addEventListener('error', () => {
        if (!v.hasAttribute('src')) return;
        this.failed = true; this.error.hidden = false; this.retry.hidden = false;
        this.setBusy(false); this.videos.forEach(other => other.pause());
        this.onReady?.();
      });
      v.addEventListener('canplay', () => {
        if (this.videos.every(other => other.hasAttribute('src') && other.readyState >= 2)) this.setBusy(false);
        this.updateTimeline();
        this.play();
        this.onReady?.();
      });
      ['canplaythrough','progress'].forEach(event => v.addEventListener(event, () => this.onReady?.()));
      v.addEventListener('waiting', () => {
        if (!this.active || this.failed || !v.hasAttribute('src')) return;
        this.setBusy(true); this.videos.forEach(other => other.pause());
        this.onWaiting?.();
      });
    });
    this.videos[0].addEventListener('timeupdate', () => { this.sync(); this.updateTimeline(); });
  }
  updateTimeline() {
    const anchor = this.videos[0];
    const ready = anchor.hasAttribute('src') && anchor.readyState >= 1 && Number.isFinite(anchor.duration) && anchor.duration > 0;
    this.seek.disabled = !ready;
    this.seek.value = ready ? String(Math.round(anchor.currentTime / anchor.duration * 1000)) : '0';
    this.clock.textContent = ready ? `${playbackTime(anchor.currentTime)} / ${playbackTime(anchor.duration)}` : 'First-frame preview';
    this.seek.setAttribute('aria-valuetext', this.clock.textContent);
    const paused = this.localPaused || this.paused || !this.allowLoad;
    this.playback.textContent = paused ? '▶ Play' : 'Ⅱ Pause';
    this.playback.setAttribute('aria-pressed', String(!paused));
  }
  load() {
    if (this.failed) return;
    this.videos.forEach(v => {
      if (!v.poster) v.poster = v.dataset.poster;
      if (!v.hasAttribute('src')) { this.setBusy(true); v.preload = 'auto'; v.src = v.dataset.src; v.load(); }
    });
    this.updateTimeline();
  }
  activate(active, paused, mode, allowLoad) {
    this.active = active; this.paused = paused; this.mode = mode; this.allowLoad = allowLoad;
    if (this.entry.interleaved) {
      const key = mode === 'auto' ? 'interleaved' : mode === 'tracks' ? 'overlay' : 'clean';
      const src = holo4dMediaURL(this.entry, key+'.mp4');
      if (this.videos[0].dataset.src !== src) { this.resetMedia(); this.videos[0].dataset.src = src; }
    }
    this.node.classList.toggle('is-active', active);
    if (active && allowLoad) this.load();
    if (!active || paused || this.localPaused || document.hidden) this.videos.forEach(v => v.pause());
    else this.play();
    this.sync();
    this.updateTimeline();
  }
  play() {
    if (!this.active || !this.allowLoad || this.paused || this.localPaused || this.failed || this.groupBlocked || document.hidden || !this.ready()) return;
    this.videos.forEach(v => v.play().catch(() => {}));
  }
  ready() {
    return this.videos.every(v => {
      if (!v.hasAttribute('src') || v.readyState < 3) return false;
      const needed = Math.min(.75, Math.max(0,v.duration-v.currentTime));
      for (let i=0; i<v.buffered.length; i++) {
        if (v.buffered.start(i)<=v.currentTime+.05 && v.buffered.end(i)>=v.currentTime+needed-.05) return true;
      }
      return v.readyState>=4;
    });
  }
  sync() {
    const a = this.videos[0];
    if (this.entry.interleaved) {
      const frame = a.currentTime*this.entry.fps;
      this.state.textContent = !a.hasAttribute('src') ? 'First-frame poster' : this.mode === 'clean' ? 'Clean' : this.mode === 'tracks' ? '3D tracks' : frame < this.entry.frames/2 || frame > this.entry.frames*1.5 ? 'Clean ↔ tracks' : '3D tracks ↔ clean';
      return;
    }
    if (a.currentTime + 0.5 < this.last) this.loop++;
    this.last = a.currentTime;
    const tracks = this.entry.has_overlay && (this.mode === 'tracks' || (this.mode === 'auto' && this.loop%2 === 1));
    this.stage.classList.toggle('show-tracks', tracks);
    if (this.entry.has_overlay) this.state.textContent = !a.hasAttribute('src') ? 'First-frame poster' : tracks ? '3D tracks' : 'Clean';
    if (this.active && a.readyState >= 2) this.videos.slice(1).forEach(v => {
      if (v.readyState >= 2 && Math.abs(v.currentTime-a.currentTime) > .08) v.currentTime = a.currentTime;
    });
  }
  setBusy(busy) {
    this.loading.hidden = !busy;
    this.stage.setAttribute('aria-busy', String(busy));
  }
  resetMedia() {
    this.loop = 0; this.last = 0; this.failed = false;
    this.error.hidden = true; this.retry.hidden = true; this.setBusy(false);
    this.videos.forEach(v => {
      v.pause();
      if (v.hasAttribute('src')) { v.preload = 'none'; v.removeAttribute('src'); v.load(); }
    });
    this.updateTimeline();
  }
  unload() {
    this.active = false; this.resetMedia();
  }
}
class Gallery {
  constructor(root, entries, hero=false) {
    this.root=root; this.hero=hero; this.index=0; this.visible=false;
    this.paired = root.hasAttribute('data-same-scene');
    if (this.paired) entries = sameScenePairs(entries);
    this.requested=false;
    this.paused=reducedMotion.matches || mediaPolicy==='click'; this.mode=reducedMotion.matches ? 'clean' : 'auto';
    this.cards=entries.map(e => new Card(e));
    this.cards.forEach(c => {
      c.onReady = () => this.releasePlayback();
      c.onWaiting = () => this.holdPlayback();
    });
    this.cards.forEach(c => { c.onPlayRequest = () => { this.requested = true; this.paused = false; this.update(); }; });
    root.innerHTML='<div class="view-controls" role="group" aria-label="Display mode"><button data-mode="auto">Auto: clean ↔ tracks</button><button data-mode="clean">Clean</button><button data-mode="tracks">3D tracks</button><button data-playback>Pause</button><span data-counter></span></div><div class="carousel" tabindex="0"><button class="carousel-button previous" aria-label="Previous examples">‹</button><div class="carousel-viewport"><div class="carousel-track"></div></div><button class="carousel-button next" aria-label="Next examples">›</button></div><div class="thumbnail-nav" aria-label="Choose an example"></div>';
    if (hero) root.classList.add('hero-gallery');
    if (!hero) {
      const picker = el('label', 'example-picker');
      picker.append(el('span', '', 'Choose a scene'));
      this.select = el('select');
      this.select.setAttribute('aria-label', `Choose ${root.dataset.orientation || ''} ${root.dataset.gallery} example`.trim());
      entries.forEach((entry, i) => {
        const option = el('option', '', `${String(i + 1).padStart(2, '0')} · ${displayScene(entry)} — ${entry.camera}`);
        option.value = String(i); this.select.append(option);
      });
      this.select.addEventListener('change', () => this.move(Number(this.select.value)));
      picker.append(this.select); root.querySelector('.view-controls').after(picker);
    }
    this.track=root.querySelector('.carousel-track'); this.nav=root.querySelector('.thumbnail-nav');
    this.viewport=root.querySelector('.carousel-viewport');
    this.cards.forEach((c,i) => {
      this.track.append(c.node);
      const b=el('button','thumbnail-button'); b.type='button';
      b.setAttribute('aria-label',`Show ${displayScene(c.entry)}, ${c.entry.camera}`);
      const img=el('img'); img.alt=''; img.loading='lazy'; img.decoding='async';
      img.dataset.src=holo4dMediaURL(c.entry,'poster.jpg',true);
      b.append(img,el('span','',displayScene(c.entry)+' · '+c.entry.camera));
      b.addEventListener('click',() => this.move(i)); this.nav.append(b);
    });
    const thumbs=new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.src=e.target.dataset.src; thumbs.unobserve(e.target); } });
    },{root:this.nav,rootMargin:'0px 120px'});
    this.nav.querySelectorAll('img').forEach(img => thumbs.observe(img));
    root.querySelectorAll('[data-mode]').forEach(b => {
      b.type='button'; b.disabled=!this.cards.some(c => c.entry.has_overlay);
      b.addEventListener('click',() => { this.mode=b.dataset.mode; this.update(); });
    });
    const playback = root.querySelector('[data-playback]');
    playback.type = 'button';
    playback.addEventListener('click',() => { this.requested=true; this.paused=!this.paused; this.cards.forEach(c => { c.localPaused = false; }); this.update(); });
    root.querySelector('.previous').addEventListener('click',() => this.move(this.index-this.perView()));
    root.querySelector('.next').addEventListener('click',() => this.move(this.index+this.perView()));
    root.querySelector('.carousel').addEventListener('keydown',e => {
      if (e.target.closest('input,select,button')) return;
      if (['ArrowLeft','ArrowRight'].includes(e.key)) { e.preventDefault(); this.move(this.index+(e.key==='ArrowRight'?1:-1)*this.perView()); }
    });
    let pointer=null;
    this.track.addEventListener('pointerdown',e => { pointer=e.target.closest('input,select,button') ? null : e.clientX; });
    this.track.addEventListener('pointerup',e => {
      if (pointer!==null && Math.abs(e.clientX-pointer)>45) this.move(this.index+(e.clientX<pointer?1:-1)*this.perView());
      pointer=null;
    });
    this.track.addEventListener('pointercancel',() => { pointer=null; });
    const observer=new IntersectionObserver(([e]) => { this.visible=e.isIntersecting; this.update(); },{threshold:.05});
    observer.observe(root.querySelector('.carousel'));
    let lastWidth=0;
    const resize=new ResizeObserver(([entry]) => {
      if (Math.abs(entry.contentRect.width-lastWidth)>1) { lastWidth=entry.contentRect.width; this.update(); }
    });
    resize.observe(root);
    galleries.push(this); this.update();
  }
  perView() { return this.hero ? 1 : (desktopQuery.matches ? 2 : 1); }
  visibleCards() { return this.cards.filter(c => c.active && !c.localPaused && !c.failed); }
  holdPlayback() {
    this.visibleCards().forEach(c => {
      c.groupBlocked = true;
      if (!c.paused && c.allowLoad) c.setBusy(true);
      c.videos.forEach(v => v.pause());
    });
  }
  releasePlayback() {
    const cards = this.visibleCards();
    if (!cards.length || !cards.every(c => c.ready())) {
      cards.forEach(c => { if (!c.paused && c.allowLoad) c.setBusy(true); });
      return;
    }
    // Do not overwrite individual seek positions when a seek fires waiting.
    // New media starts at zero naturally; buffering only gates play/pause.
    cards.forEach(c => { c.groupBlocked = false; c.setBusy(false); c.play(); });
  }
  move(index) {
    const count=this.cards.length;
    const requested=index<0 ? count-1 : index>=count ? 0 : index;
    // Overlap the final pair when the count is odd; never leave an empty slot.
    this.index=Math.min(Math.floor(requested/this.perView())*this.perView(), Math.max(0,count-this.perView()));
    this.selection = requested;
    if (mediaPolicy==='click' || reducedMotion.matches) { this.requested=false; this.paused=true; }
    this.update();
    const thumb=this.nav.children[this.index];
    if (thumb) this.nav.scrollTo({left:Math.max(0,thumb.offsetLeft-this.nav.offsetLeft-this.nav.clientWidth/2+56),behavior:'smooth'});
  }
  update() {
    const fullscreen=document.fullscreenElement;
    const visible=fullscreen ? this.root.contains(fullscreen) : this.visible;
    this.track.style.transform=`translate3d(-${this.index*100/this.perView()}%,0,0)`;
    const height=Math.max(...this.cards.slice(this.index,this.index+this.perView()).map(c => c.node.getBoundingClientRect().height));
    if (height>0) this.viewport.style.height=`${Math.ceil(height)+2}px`;
    this.holdPlayback();
    this.cards.forEach((c,i) => {
      const selected=i>=this.index && i<this.index+this.perView();
      c.node.setAttribute('aria-hidden',String(!selected));
      c.node.inert=!selected;
      // Posters load only for selected visible cards; MP4s also need policy consent.
      if (selected && visible) c.videos.forEach(v => { if (!v.poster) v.poster=v.dataset.poster; });
      const allowLoad=this.requested || (mediaPolicy==='viewport' && !reducedMotion.matches);
      const active=selected && visible && !document.hidden && (!fullscreen || fullscreen===c.stage);
      if (active) c.groupBlocked = true;
      c.activate(active,this.paused,this.mode,allowLoad);
      if (!active) c.unload();
      this.nav.children[i].setAttribute('aria-pressed',String(selected));
      this.nav.children[i].classList.toggle('is-active',selected);
    });
    this.releasePlayback();
    const play=this.root.querySelector('[data-playback]');
    const needsClick=!this.requested && (mediaPolicy==='click' || reducedMotion.matches);
    play.textContent=needsClick?'Load & play':this.paused?'Play':'Pause'; play.setAttribute('aria-pressed',String(this.paused));
    this.root.querySelectorAll('[data-mode]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.mode===this.mode)));
    this.root.querySelector('[data-counter]').textContent=`${this.index+1}–${Math.min(this.index+this.perView(),this.cards.length)} / ${this.cards.length}`;
    if (this.select) this.select.value = String(this.selection ?? this.index);
  }
}
document.addEventListener('DOMContentLoaded',() => {
  const page=window.HOLO4D_PAGE;
  if (!page) return;
  const refreshNote=document.getElementById('media-refresh-note');
  if (refreshNote) refreshNote.hidden=!!page.sections.results?.every(e=>e.interleaved);
  const hero=Object.values(page.sections).flat().find(e => e.id===page.hero);
  const heroRoot=document.querySelector('[data-hero]');
  if (heroRoot && hero) new Gallery(heroRoot,[hero],true);
  document.querySelectorAll('[data-gallery]').forEach(root => {
    let entries=root.dataset.gallery === 'reshooting' ? [...(page.sections.davis || []), ...(page.sections.results || [])] : page.sections[root.dataset.gallery];
    if (root.dataset.orientation) entries=entries?.filter(entry => {
      const portrait=entry.portrait_horizontal || /^(Figure humanoid|Tesla humanoid)/.test(entry.scene);
      return root.dataset.orientation === (portrait ? 'portrait' : 'landscape');
    });
    if (entries?.length) new Gallery(root,entries);
  });
  const policy=document.querySelector('[data-media-policy]');
  policy.value=mediaPolicy;
  policy.addEventListener('change',()=>{
    mediaPolicy=policy.value;
    galleries.forEach(g=>{
      g.requested=false; g.paused=mediaPolicy==='click'||reducedMotion.matches;
      g.cards.forEach(c=>c.unload()); g.update();
    });
  });
  reducedMotion.addEventListener('change',()=>{
    galleries.forEach(g=>{
      if (reducedMotion.matches) { g.paused=true;g.requested=false;g.mode='clean';g.cards.forEach(c=>c.unload()); }
      g.update();
    });
  });
  document.addEventListener('visibilitychange',() => galleries.forEach(g => g.update()));
  document.addEventListener('fullscreenchange',() => galleries.forEach(g => g.update()));
  desktopQuery.addEventListener('change',() => galleries.forEach(g => g.move(g.index)));
  setInterval(() => galleries.filter(g => g.visible && !g.paused && !document.hidden).forEach(g => g.cards.filter(c => c.active).forEach(c => c.sync())),200);
  const observer=new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) document.querySelectorAll('.contents-sidebar a[href^="#"], .nav-links a[href^="#"]').forEach(a => {
      const current = a.hash === '#' + e.target.id;
      a.classList.toggle('current', current);
      if (current) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    }); });
  },{rootMargin:'-15% 0px -65% 0px'});
  document.querySelectorAll('section[id]').forEach(s => observer.observe(s));
  const backTop = document.querySelector('.back-to-top');
  const header = document.querySelector('.paper-header');
  if (backTop && header) new IntersectionObserver(([entry]) => {
    backTop.hidden = entry.isIntersecting || entry.boundingClientRect.top >= 0;
  }).observe(header);
  const copy=document.querySelector('[data-copy-bibtex]');
  copy?.addEventListener('click',async () => {
    try { await navigator.clipboard.writeText(document.getElementById('bibtex').innerText); copy.textContent='Copied'; }
    catch (_) { copy.textContent='Select and copy the citation below'; }
    setTimeout(() => { copy.textContent='Copy'; },1500);
  });
});
