(function () {
  const galleries = document.querySelectorAll("[data-gallery]");
  galleries.forEach((gallery) => {
    const slides = Array.from(gallery.querySelectorAll(".artwork__slide"));
    if (slides.length < 2) return;

    const prev = gallery.querySelector("[data-gallery-prev]");
    const next = gallery.querySelector("[data-gallery-next]");
    let current = 0;

    function show(index) {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        slide.classList.toggle("is-active", i === current);
      });
    }

    prev.addEventListener("click", () => show(current - 1));
    next.addEventListener("click", () => show(current + 1));
  });
})();
