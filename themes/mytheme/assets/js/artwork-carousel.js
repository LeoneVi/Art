(function () {
  const galleries = document.querySelectorAll("[data-gallery]");
  galleries.forEach((gallery) => {
    const slides = Array.from(gallery.querySelectorAll(".artwork__slide"));
    if (slides.length < 2) return;

    const images = slides.map((slide) => slide.querySelector("img"));
    const imageLoads = new WeakMap();
    const prev = gallery.querySelector("[data-gallery-prev]");
    const next = gallery.querySelector("[data-gallery-next]");
    let current = 0;

    function loadImage(image, priority = "low") {
      if (!image) return Promise.resolve();

      const existingLoad = imageLoads.get(image);
      if (existingLoad) return existingLoad;

      const imageLoad = new Promise((resolve) => {
        if (image.complete && image.currentSrc) {
          resolve();
          return;
        }

        const finish = () => resolve();
        image.addEventListener("load", finish, { once: true });
        image.addEventListener("error", finish, { once: true });

        if (image.dataset.src) {
          image.fetchPriority = priority;
          image.src = image.dataset.src;
          delete image.dataset.src;
        }
      });

      imageLoads.set(image, imageLoad);
      return imageLoad;
    }

    async function preloadInOrder() {
      for (const image of images) {
        await loadImage(image);
      }
    }

    function show(index) {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        slide.classList.toggle("is-active", i === current);
      });

      loadImage(images[current], "high");
    }

    prev.addEventListener("click", () => show(current - 1));
    next.addEventListener("click", () => show(current + 1));

    preloadInOrder();
  });
})();
