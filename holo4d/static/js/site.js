document.addEventListener("DOMContentLoaded", () => {
  const examples = [
    ["Avocado slice", "Close crane above", "avocado-slice/close-crane-above"],
    ["Avocado slice", "Left front zoom", "avocado-slice/left-front-zoom"],
    ["Basketball", "Right to left", "basketball-four/right-left"],
    ["Basketball", "Shoulder out", "basketball-four/shoulder-out"],
    ["Bed shopping", "Dolly out", "bed-shopping/dolly-out"],
    ["Bed shopping", "Top arc", "bed-shopping/top-arc"],
    ["BMX bumps", "Crane follow zoom", "bmx-bumps/crane-follow-zoom"],
    ["BMX bumps", "Front follow", "bmx-bumps/front-follow"],
    ["Breakdance", "Crane, dolly and zoom", "breakdance/crane-dolly-zoom"],
    ["Breakdance", "Left to right", "breakdance/left-right"],
    ["Camel", "Three in and out", "camel/three-in-out"],
    ["Camel", "Zoom out", "camel/zoom-out"],
    ["Camera lens", "Crane zoom", "camera-lens/crane-zoom"],
    ["Camera lens", "Side full", "camera-lens/side-full"],
    ["Car roundabout", "Crane above", "car-roundabout/crane-above"],
    ["Car roundabout", "Front follow", "car-roundabout/front-follow"],
    ["Couch sit", "Crane below", "couch-sit/crane-below"],
    ["Couch sit", "Right-left zoom", "couch-sit/right-left-zoom"],
    ["Couple hug", "Crane above", "couple-hug/crane-above"],
    ["Couple hug", "Crane below zoom", "couple-hug/crane-below-zoom"]
  ];

  const mediaRoot = "static/videos/50step/";
  const carousel = document.querySelector("[data-carousel]");
  const track = document.querySelector("[data-carousel-track]");
  const currentLabel = document.querySelector("[data-carousel-current]");
  const totalLabel = document.querySelector("[data-carousel-total]");
  const progress = document.querySelector("[data-carousel-progress]");
  let currentIndex = 0;
  let carouselVisible = false;
  let pointerStart = null;

  const makeVideo = (filename, label, panelClass = "") => {
    const figure = document.createElement("figure");
    const caption = document.createElement("div");
    const video = document.createElement("video");

    if (panelClass) figure.classList.add(panelClass);
    caption.className = "video-label";
    caption.textContent = label;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "none";
    video.dataset.src = mediaRoot + filename;
    video.setAttribute("aria-label", label);

    figure.append(caption, video);
    return figure;
  };

  const renderSlides = () => {
    examples.forEach(([scene, trajectory, slug], index) => {
      const slide = document.createElement("article");
      const heading = document.createElement("header");
      const title = document.createElement("h3");
      const camera = document.createElement("p");
      const videos = document.createElement("div");

      slide.className = "result-slide";
      slide.dataset.slideIndex = String(index);
      slide.setAttribute("aria-hidden", index === 0 ? "false" : "true");
      heading.className = "slide-heading";
      title.textContent = scene;
      camera.textContent = "Target camera: " + trajectory;
      videos.className = "slide-videos";
      videos.append(
        makeVideo(`${slug}/source.mp4`, "Source video"),
        makeVideo(`${slug}/condition-placeholder.mp4`, "Condition (placeholder)", "condition-panel"),
        makeVideo(`${slug}/output.mp4`, "Holo4D output")
      );
      heading.append(title, camera);
      slide.append(heading, videos);
      track.append(slide);
    });
  };

  const modulo = (value, length) => ((value % length) + length) % length;

  const loadSlide = (index) => {
    const slide = track.children[modulo(index, examples.length)];
    slide.querySelectorAll("video").forEach((video) => {
      if (!video.src) {
        video.src = video.dataset.src;
        video.load();
      }
    });
  };

  const playCurrent = () => {
    Array.from(track.children).forEach((slide, index) => {
      slide.querySelectorAll("video").forEach((video) => {
        if (index === currentIndex && carouselVisible) {
          const promise = video.play();
          if (promise) promise.catch(() => {});
        } else {
          video.pause();
        }
      });
    });
  };

  const updateCarousel = (nextIndex) => {
    currentIndex = modulo(nextIndex, examples.length);
    track.style.transform = `translate3d(-${currentIndex * 100}%, 0, 0)`;

    Array.from(track.children).forEach((slide, index) => {
      slide.setAttribute("aria-hidden", index === currentIndex ? "false" : "true");
    });

    loadSlide(currentIndex);
    loadSlide(currentIndex - 1);
    loadSlide(currentIndex + 1);
    currentLabel.textContent = String(currentIndex + 1).padStart(2, "0");
    totalLabel.textContent = String(examples.length).padStart(2, "0");
    progress.style.width = `${((currentIndex + 1) / examples.length) * 100}%`;
    playCurrent();
  };

  const move = (direction) => updateCarousel(currentIndex + direction);

  renderSlides();
  document.querySelectorAll("[data-carousel-previous]").forEach((button) => {
    button.addEventListener("click", () => move(-1));
  });
  document.querySelectorAll("[data-carousel-next]").forEach((button) => {
    button.addEventListener("click", () => move(1));
  });

  carousel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      move(-1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      move(1);
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
        playCurrent();
      },
      { threshold: 0.25 }
    );
    observer.observe(carousel);
  } else {
    carouselVisible = true;
  }

  updateCarousel(0);

  const syncVideos = (videos) => {
    if (videos.length < 2 || videos.some((video) => video.readyState < 2)) return;
    const anchor = videos[0];
    videos.slice(1).forEach((video) => {
      if (Math.abs(anchor.currentTime - video.currentTime) > 0.12) {
        video.currentTime = anchor.currentTime;
      }
    });
  };

  window.setInterval(() => {
    const teaserVideos = Array.from(document.querySelectorAll("[data-sync-pair] video"));
    const currentVideos = Array.from(track.children[currentIndex].querySelectorAll("video"));
    syncVideos(teaserVideos);
    if (carouselVisible) syncVideos(currentVideos);
  }, 500);

  const copyButton = document.querySelector("[data-copy-bibtex]");
  const bibtex = document.getElementById("bibtex");
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
});
