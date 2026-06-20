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

  document.addEventListener("DOMContentLoaded", function () {
    mount("speakers-grid",   window.PHYSAI_SPEAKERS   || [], false);
    mount("organizers-grid", window.PHYSAI_ORGANIZERS || [], true);
  });
})();
