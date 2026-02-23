// app/static/js/gallery_lightbox.js
(function () {
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () {
    const modalEl = document.getElementById("galleryLightbox");
    const imgEl = document.getElementById("galleryLightboxImg");
    const titleEl = document.getElementById("galleryLightboxTitle");

    if (!modalEl || !imgEl) return;

    const modal = new bootstrap.Modal(modalEl);

    const links = Array.from(document.querySelectorAll('a[data-gallery="site-gallery"]'));
    if (!links.length) return;

    const prevBtn = modalEl.querySelector(".gallery-prev");
    const nextBtn = modalEl.querySelector(".gallery-next");

    let currentIndex = 0;

    function openAt(index) {
      if (index < 0) index = links.length - 1;
      if (index >= links.length) index = 0;

      currentIndex = index;

      const a = links[currentIndex];
      const fullSrc = a.getAttribute("href");
      const caption = a.getAttribute("data-title") || "Gallery";

      imgEl.src = fullSrc;
      imgEl.alt = caption;
      if (titleEl) titleEl.textContent = caption;

      modal.show();
    }

    function openFromLink(a) {
      const idx = links.indexOf(a);
      openAt(idx >= 0 ? idx : 0);
    }

    // Intercept clicks on thumbnails
    links.forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        openFromLink(a);
      });
    });

    // Next/Prev buttons
    if (prevBtn) prevBtn.addEventListener("click", () => openAt(currentIndex - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => openAt(currentIndex + 1));

    // Keyboard support when modal is open
    function onKeyDown(e) {
      // Only act if modal is visible
      if (!modalEl.classList.contains("show")) return;

      if (e.key === "ArrowLeft") openAt(currentIndex - 1);
      if (e.key === "ArrowRight") openAt(currentIndex + 1);
      if (e.key === "Escape") modal.hide();
    }
    document.addEventListener("keydown", onKeyDown);

    // Cleanup on close
    modalEl.addEventListener("hidden.bs.modal", () => {
      imgEl.src = "";
      imgEl.alt = "";
      if (titleEl) titleEl.textContent = "Gallery";
    });
  });
})();