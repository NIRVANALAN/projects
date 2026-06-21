(function () {
  function initials(name) {
    return name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(s => s.replace(/[^\p{L}]/gu, "").charAt(0).toUpperCase())
      .join("");
  }

  function renderPerson(p, includeRole) {
    const wrap = document.createElement("article");
    wrap.className = "person";

    const photo = document.createElement("div");
    photo.className = "photo";

    if (p.photo) {
      const img = document.createElement("img");
      img.alt = p.name;
      img.loading = "lazy";
      img.src = p.photo;
      img.onerror = () => {
        photo.classList.add("placeholder");
        photo.setAttribute("data-initials", initials(p.name));
        img.remove();
      };
      photo.appendChild(img);
    } else {
      photo.classList.add("placeholder");
      photo.setAttribute("data-initials", initials(p.name));
    }
    wrap.appendChild(photo);

    const name = document.createElement("h4");
    name.textContent = p.name;
    wrap.appendChild(name);

    const aff = document.createElement("p");
    aff.className = "aff";
    aff.textContent = includeRole && p.role ? `${p.role} · ${p.aff}` : p.aff;
    wrap.appendChild(aff);

    if (p.url) {
      const a = document.createElement("a");
      a.className = "weblink";
      a.href = p.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = "Website →";
      wrap.appendChild(a);
    }

    return wrap;
  }

  function mount(id, people, includeRole) {
    const el = document.getElementById(id);
    if (!el) return;
    const frag = document.createDocumentFragment();
    people.forEach(p => frag.appendChild(renderPerson(p, includeRole)));
    el.appendChild(frag);
  }

  // Hero point cloud: a slowly rotating, depth-shaded sphere of points in the brand
  // colors — reads as a "3D reconstruction" of the physical world. No video asset needed.
  function initHeroCloud() {
    const canvas = document.getElementById("hero-cloud");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const COLORS = ["#1c4cff", "#7b3dff", "#ff5b3a"];
    const N = 170;
    const pts = [];
    for (let i = 0; i < N; i++) {
      const theta = 2 * Math.PI * Math.random();
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 0.78 + Math.random() * 0.22; // sphere shell + jitter
      pts.push({
        x: r * Math.sin(phi) * Math.cos(theta),
        y: r * Math.cos(phi),
        z: r * Math.sin(phi) * Math.sin(theta),
        c: COLORS[(Math.random() * COLORS.length) | 0],
      });
    }

    let w = 0, h = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      const rect = canvas.parentElement.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener("resize", resize);

    let ang = 0, raf = 0;
    function frame() {
      ctx.clearRect(0, 0, w, h);
      const narrow = w < 720;
      const cx = w * (narrow ? 0.5 : 0.72);
      const cy = h * 0.44;
      const R = Math.min(w, h) * (narrow ? 0.34 : 0.42);
      const cosA = Math.cos(ang), sinA = Math.sin(ang);
      const proj = [];
      for (let i = 0; i < N; i++) {
        const p = pts[i];
        const xr = p.x * cosA - p.z * sinA;
        const zr = p.x * sinA + p.z * cosA;
        const persp = 1 / (1.9 - zr); // zr in ~[-1,1]
        proj.push({ sx: cx + xr * R * persp, sy: cy + p.y * R * persp, d: zr, persp, c: p.c });
      }
      proj.sort((a, b) => a.d - b.d); // far first, near drawn on top
      for (let j = 0; j < proj.length; j++) {
        const q = proj[j];
        const depth = (q.d + 1) / 2; // 0 far .. 1 near
        ctx.globalAlpha = 0.1 + depth * 0.32;
        ctx.fillStyle = q.c;
        ctx.beginPath();
        ctx.arc(q.sx, q.sy, (0.7 + depth * 1.9) * q.persp, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      ang += 0.0016;
      if (!reduce) raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) cancelAnimationFrame(raf);
      else if (!reduce) raf = requestAnimationFrame(frame);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    mount("speakers-grid",   window.PHYSAI_SPEAKERS   || [], false);
    mount("organizers-grid", window.PHYSAI_ORGANIZERS || [], true);
    initHeroCloud();
  });
})();
