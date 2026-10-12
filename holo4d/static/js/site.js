document.addEventListener("DOMContentLoaded", () => {
  const examples = Array.isArray(window.HOLO4D_EXAMPLES)
    ? window.HOLO4D_EXAMPLES
    : [];
  const mediaRoot = "static/videos/cowtracker/";
  const desktopQuery = window.matchMedia("(min-width: 761px)");
  const carousel = document.querySelector("[data-carousel]");
  const track = document.querySelector("[data-carousel-track]");
  const thumbnailNav = document.querySelector("[data-thumbnail-nav]");
  const playbackButton = document.querySelector("[data-carousel-playback]");
  let currentIndex = 0;
  let carouselVisible = false;
  let galleryPaused = false;
  let pointerStart = null;
  let unloadTimer = null;
  let lastSlidesPerView = desktopQuery.matches ? 2 : 1;

  const modulo = (value, length) => ((value % length) + length) % length;
  const getSlidesPerView = () => (desktopQuery.matches ? 2 : 1);

  const getVisibleIndexes = () => {
    const count = getSlidesPerView();
    return Array.from(
      { length: Math.min(count, examples.length - currentIndex) },
      (_, offset) => currentIndex + offset
    );
  };

  const makeVideo = (filename, label, className) => {
    const video = document.createElement("video");
    video.className = className;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "none";
    video.dataset.src = mediaRoot + filename;
    video.setAttribute("aria-label", label);
    return video;
  };

  const makeBlendVisual = (example) => {
    const figure = document.createElement("figure");
    const stage = document.createElement("div");
    const state = document.createElement("div");
    const cleanState = document.createElement("span");
    const overlayState = document.createElement("span");
    const caption = document.createElement("figcaption");
    const clean = makeVideo(
      `${example.path}/clean.mp4`,
      `${example.scene}, clean source-condition-synthesis visualization`,
      "blend-layer blend-clean"
    );
    const overlay = makeVideo(
      `${example.path}/overlay.mp4`,
      `${example.scene}, source-condition-synthesis visualization with 3D track overlay`,
      "blend-layer blend-overlay"
    );

    figure.className = "blend-visual";
    stage.className = "blend-stage";
    stage.dataset.syncPair = "";
    stage.style.setProperty("--slide-aspect", String(example.aspect || 1.0863));
    stage.style.setProperty(
      "--blend-cycle",
      `${Math.max(Number(example.duration || 3.0625) * 2, 6).toFixed(3)}s`
    );
    state.className = "blend-state";
    state.setAttribute("aria-hidden", "true");
    cleanState.className = "blend-state-clean";
    cleanState.textContent = "Clean";
    overlayState.className = "blend-state-overlay";
    overlayState.textContent = "3D tracks";
    caption.textContent = "Source · Condition · Holo4D synthesis";

    state.append(cleanState, overlayState);
    stage.append(clean, overlay, state);
    figure.append(stage, caption);
    return figure;
  };

  const renderSlides = () => {
    examples.forEach((example, index) => {
      const slide = document.createElement("article");
      const heading = document.createElement("header");
      const title = document.createElement("h3");
      const camera = document.createElement("p");

      slide.className = "result-slide";
      slide.dataset.slideIndex = String(index);
      slide.setAttribute("aria-hidden", "true");
      heading.className = "slide-heading";
      title.textContent = example.scene;
      camera.textContent = "Target camera: " + example.camera;
      heading.append(title, camera);
      slide.append(heading, makeBlendVisual(example));
      track.append(slide);
    });
  };

  const loadSlide = (index) => {
    const slide = track.children[index];
    if (!slide) return;
    slide.querySelectorAll("video").forEach((video) => {
      if (!video.hasAttribute("src")) {
        video.src = video.dataset.src;
        video.load();
      }
    });
  };

  const unloadHiddenSlides = () => {
    const visible = new Set(getVisibleIndexes());
    Array.from(track.children).forEach((slide, index) => {
      if (visible.has(index)) return;
      slide.querySelectorAll("video").forEach((video) => {
        video.pause();
        if (video.hasAttribute("src")) {
          video.removeAttribute("src");
          video.load();
        }
      });
    });
  };

  const updatePlaybackButton = () => {
    if (!playbackButton) return;
    playbackButton.textContent = galleryPaused ? "Play visible videos" : "Pause visible videos";
    playbackButton.setAttribute("aria-pressed", String(galleryPaused));
    carousel.classList.toggle("is-paused", galleryPaused);
  };

  const playVisible = () => {
    const visible = new Set(getVisibleIndexes());
    Array.from(track.children).forEach((slide, index) => {
      const isVisible = visible.has(index);
      const isActive = isVisible && carouselVisible;
      const shouldPlay = isActive && !galleryPaused;
      slide.classList.toggle("is-active", isActive);
      slide.setAttribute("aria-hidden", String(!isVisible));
      slide.querySelectorAll("video").forEach((video) => {
        if (shouldPlay) {
          const promise = video.play();
          if (promise) promise.catch(() => {});
        } else {
          video.pause();
        }
      });
    });
  };

  const loadThumbnail = (image) => {
    if (!image || image.hasAttribute("src")) return;
    image.src = image.dataset.src;
  };

  const renderThumbnails = () => {
    if (!thumbnailNav) return;
    examples.forEach((example, index) => {
      const button = document.createElement("button");
      const image = document.createElement("img");
      const label = document.createElement("span");
      button.className = "thumbnail-button";
      button.type = "button";
      button.dataset.thumbnailIndex = String(index);
      button.setAttribute("aria-label", `Show ${example.scene}, ${example.camera}`);
      image.alt = "";
      image.decoding = "async";
      image.dataset.src = `${mediaRoot}${example.path}/thumb.jpg`;
      label.textContent = `${example.scene} · ${example.camera}`;
      button.append(image, label);
      button.addEventListener("click", () => updateCarousel(index));
      thumbnailNav.append(button);
    });

    const images = Array.from(thumbnailNav.querySelectorAll("img[data-src]"));
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            loadThumbnail(entry.target);
            observer.unobserve(entry.target);
          });
        },
        { root: thumbnailNav, rootMargin: "0px 320px" }
      );
      images.forEach((image) => observer.observe(image));
    } else {
      images.forEach(loadThumbnail);
    }
  };

  const updateThumbnails = () => {
    if (!thumbnailNav) return;
    const visible = new Set(getVisibleIndexes());
    const buttons = Array.from(thumbnailNav.children);
    buttons.forEach((button, index) => {
      const active = visible.has(index);
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    const anchor = buttons[currentIndex];
    if (anchor) {
      loadThumbnail(anchor.querySelector("img"));
      const left = anchor.offsetLeft - (thumbnailNav.clientWidth - anchor.offsetWidth) / 2;
      thumbnailNav.scrollTo({ left: Math.max(0, left), behavior: "smooth" });
    }
  };

  const normalizeStartIndex = (requestedIndex) => {
    const perView = getSlidesPerView();
    const pageCount = Math.ceil(examples.length / perView);
    const page = modulo(Math.floor(requestedIndex / perView), pageCount);
    return page * perView;
  };

  const updateCarousel = (requestedIndex) => {
    currentIndex = normalizeStartIndex(requestedIndex);
    const stepPercent = 100 / getSlidesPerView();
    track.style.transform = `translate3d(-${currentIndex * stepPercent}%, 0, 0)`;

    getVisibleIndexes().forEach(loadSlide);
    updateThumbnails();
    playVisible();

    window.clearTimeout(unloadTimer);
    unloadTimer = window.setTimeout(unloadHiddenSlides, 600);
  };

  const setupCarousel = () => {
    if (!carousel || !track || examples.length === 0) return;
    const move = (direction) => {
      updateCarousel(currentIndex + direction * getSlidesPerView());
    };

    renderSlides();
    renderThumbnails();
    document.querySelectorAll("[data-carousel-previous]").forEach((button) => {
      button.addEventListener("click", () => move(-1));
    });
    document.querySelectorAll("[data-carousel-next]").forEach((button) => {
      button.addEventListener("click", () => move(1));
    });
    if (playbackButton) {
      playbackButton.addEventListener("click", () => {
        galleryPaused = !galleryPaused;
        updatePlaybackButton();
        playVisible();
      });
    }

    carousel.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        move(-1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        move(1);
      }
      if (
        (event.key === " " || event.key === "Spacebar") &&
        event.target === carousel
      ) {
        event.preventDefault();
        galleryPaused = !galleryPaused;
        updatePlaybackButton();
        playVisible();
      }
    });

    carousel.addEventListener("pointerdown", (event) => {
      pointerStart = event.clientX;
    });
    carousel.addEventListener("pointerup", (event) => {
      if (pointerStart === null) return;
      const distance = event.clientX - pointerStart;
      pointerStart = null;
      if (Math.abs(distance) > 45) move(distance > 0 ? -1 : 1);
    });
    carousel.addEventListener("pointercancel", () => {
      pointerStart = null;
    });

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          carouselVisible = entry.isIntersecting;
          playVisible();
        },
        { threshold: 0.15 }
      );
      observer.observe(carousel);
    } else {
      carouselVisible = true;
    }

    window.addEventListener("resize", () => {
      const nextSlidesPerView = getSlidesPerView();
      if (nextSlidesPerView === lastSlidesPerView) return;
      lastSlidesPerView = nextSlidesPerView;
      track.style.transition = "none";
      updateCarousel(currentIndex);
      track.getBoundingClientRect();
      track.style.transition = "";
    });

    updatePlaybackButton();
    updateCarousel(0);
  };

  const setupTeaserPlayback = () => {
    const teaser = document.querySelector(".teaser-blend");
    const button = document.querySelector("[data-teaser-playback]");
    if (!teaser || !button) return;
    const videos = Array.from(teaser.querySelectorAll("video"));
    let paused = false;

    button.addEventListener("click", () => {
      paused = !paused;
      teaser.classList.toggle("is-paused", paused);
      button.setAttribute("aria-pressed", String(paused));
      button.textContent = paused ? "Play teaser" : "Pause teaser";
      videos.forEach((video) => {
        if (paused) {
          video.pause();
        } else {
          const promise = video.play();
          if (promise) promise.catch(() => {});
        }
      });
    });
  };

  setupCarousel();
  setupTeaserPlayback();

  const syncVideos = (videos) => {
    if (videos.length < 2 || videos.some((video) => video.readyState < 2)) return;
    const anchor = videos[0];
    videos.slice(1).forEach((video) => {
      if (Math.abs(anchor.currentTime - video.currentTime) > 0.08) {
        video.currentTime = anchor.currentTime;
      }
    });
  };

  window.setInterval(() => {
    const teaserVideos = Array.from(document.querySelectorAll(".teaser [data-sync-pair] video"));
    syncVideos(teaserVideos);
    if (carouselVisible && track && track.children.length) {
      getVisibleIndexes().forEach((index) => {
        syncVideos(Array.from(track.children[index].querySelectorAll("video")));
      });
    }
  }, 250);

  const copyButton = document.querySelector("[data-copy-bibtex]");
  const bibtex = document.getElementById("bibtex");
  if (copyButton && bibtex) {
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(bibtex.innerText);
        copyButton.textContent = "Copied";
      } catch (_error) {
        const range = document.createRange();
        const selection = window.getSelection();
        range.selectNodeContents(bibtex);
        selection.removeAllRanges();
        selection.addRange(range);
        copyButton.textContent = "Selected";
      }
      window.setTimeout(() => {
        copyButton.textContent = "Copy";
      }, 1500);
    });
  }
});
