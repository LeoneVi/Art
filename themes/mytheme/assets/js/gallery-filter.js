/**
 * Gallery filter — search + medium/tag filtering against the feed grid.
 * No framework: reads data-title / data-medium / data-tags attributes
 * that feed.html renders onto each .gallery-feed__item.
 */
(function () {
  const grid = document.getElementById("gallery-feed-grid");
  const bar = document.getElementById("gallery-filter-bar");
  if (!grid || !bar) return;

  const searchInput = document.getElementById("gallery-search");
  const items = Array.from(grid.querySelectorAll(".gallery-feed__item"));

  const state = { search: "", medium: "all", tag: "all" };

  function applyFilters() {
    items.forEach((item) => {
      const title = item.dataset.title || "";
      const medium = item.dataset.medium || "";
      const tags = (item.dataset.tags || "").split(",");

      const matchesSearch = title.includes(state.search);
      const matchesMedium = state.medium === "all" || medium === state.medium;
      const matchesTag = state.tag === "all" || tags.includes(state.tag);

      item.classList.toggle(
        "gallery-feed__item--hidden",
        !(matchesSearch && matchesMedium && matchesTag)
      );
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.search = e.target.value.trim().toLowerCase();
      applyFilters();
    });
  }

  bar.querySelectorAll("[data-filter-type]").forEach((group) => {
    const type = group.dataset.filterType; // "medium" or "tag"

    group.querySelectorAll(".filter-bar__button").forEach((btn) => {
      btn.addEventListener("click", () => {
        group
          .querySelectorAll(".filter-bar__button")
          .forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");

        state[type] = btn.dataset.value;
        applyFilters();
      });
    });
  });
})();
