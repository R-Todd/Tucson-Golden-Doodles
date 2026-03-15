// app/static/js/reviews_modal.js
(function () {
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () {
    const triggers = Array.from(document.querySelectorAll(".rv-open"));
    if (!triggers.length) return;

    if (typeof bootstrap === "undefined") return;

    // Hide "View full review" when the card text does not overflow the clamp.
    // We intentionally scope the check to the nearest blockquote <p> for each trigger.
    function updateReviewLinkVisibility() {
      triggers.forEach((btn) => {
        const card = btn.closest(".card");
        if (!card) return;

        const p = card.querySelector("blockquote p");
        if (!p) return;

        // Some browsers report fractional values; use a small tolerance.
        const isOverflowing = (p.scrollHeight - p.clientHeight) > 2;

        // If the text isn't overflowing the 3-line clamp, hide the link.
        btn.style.display = isOverflowing ? "" : "none";
      });
    }

    const reviewModalEl = document.getElementById("reviewViewerModal");
    const lightboxEl = document.getElementById("reviewLightbox");
    if (!reviewModalEl || !lightboxEl) return;

    const reviewModal = new bootstrap.Modal(reviewModalEl);
    const lightboxModal = new bootstrap.Modal(lightboxEl);

    const rvTitle = document.getElementById("rvTitle");
    const rvText = document.getElementById("rvText");
    const rvFilmstrip = document.getElementById("rvFilmstrip");
    const rvPrev = document.getElementById("rvPrev");
    const rvNext = document.getElementById("rvNext");
    const rvIndex = document.getElementById("rvIndex");

    const lbImg = document.getElementById("reviewLightboxImg");
    const lbTitle = document.getElementById("reviewLightboxTitle");
    const lbPrev = lightboxEl.querySelector(".gallery-prev");
    const lbNext = lightboxEl.querySelector(".gallery-next");

    const reviews = triggers.map((btn) => {
      let text = "";
      let images = [];
      try {
        text = JSON.parse(btn.dataset.reviewText || '""');
      } catch (e) {
        text = btn.dataset.reviewText || "";
      }
      try {
        images = JSON.parse(btn.dataset.reviewImages || "[]");
      } catch (e) {
        images = [];
      }

      return {
        author: btn.dataset.reviewAuthor || "Review",
        text,
        images,
      };
    });

    // Run once after DOM is ready, and again after resize (responsive line wrapping can change overflow).
    updateReviewLinkVisibility();
    window.addEventListener("resize", updateReviewLinkVisibility);

    let currentReviewIndex = 0;
    let currentImageIndex = 0;

    function clampIndex(i, len) {
      if (!len) return 0;
      if (i < 0) return len - 1;
      if (i >= len) return 0;
      return i;
    }

    function renderFilmstrip(images) {
      rvFilmstrip.innerHTML = "";
      if (!images || !images.length) return;

      images.forEach((src, idx) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn p-0 border-0 bg-transparent";
        btn.style.flex = "0 0 auto";

        const img = document.createElement("img");
        img.src = src;
        img.alt = "Review photo " + (idx + 1);
        img.loading = "lazy";
        img.style.height = "64px";
        img.style.width = "64px";
        img.style.objectFit = "cover";
        img.style.borderRadius = "10px";
        img.style.border = "1px solid rgba(0,0,0,0.08)";

        btn.appendChild(img);

        btn.addEventListener("click", function () {
          openLightbox(idx);
        });

        rvFilmstrip.appendChild(btn);
      });
    }

    function showReview(index) {
      currentReviewIndex = clampIndex(index, reviews.length);
      const r = reviews[currentReviewIndex];

      if (rvTitle) rvTitle.textContent = r.author;
      if (rvText) rvText.textContent = r.text;
      if (rvIndex) rvIndex.textContent = (currentReviewIndex + 1) + " of " + reviews.length;

      renderFilmstrip(r.images);
    }

    function openLightbox(imageIndex) {
      const r = reviews[currentReviewIndex];
      if (!r.images || !r.images.length) return;

      currentImageIndex = clampIndex(imageIndex, r.images.length);

      const src = r.images[currentImageIndex];
      if (lbImg) {
        lbImg.src = src;
        lbImg.alt = "Review photo " + (currentImageIndex + 1);
      }

      if (lbTitle) lbTitle.textContent = r.author + " — Photos";

      lightboxModal.show();
    }

    function lightboxStep(delta) {
      const r = reviews[currentReviewIndex];
      if (!r.images || !r.images.length) return;
      openLightbox(currentImageIndex + delta);
    }

    // Wire card triggers
    triggers.forEach((btn, idx) => {
      btn.addEventListener("click", function () {
        showReview(idx);
        reviewModal.show();
      });
    });

    // Review prev/next
    if (rvPrev) rvPrev.addEventListener("click", () => showReview(currentReviewIndex - 1));
    if (rvNext) rvNext.addEventListener("click", () => showReview(currentReviewIndex + 1));

    // Lightbox prev/next (gallery-style buttons)
    if (lbPrev) lbPrev.addEventListener("click", () => lightboxStep(-1));
    if (lbNext) lbNext.addEventListener("click", () => lightboxStep(1));

    // Keyboard support
    document.addEventListener("keydown", function (e) {
      // Review modal navigation
      if (reviewModalEl.classList.contains("show")) {
        if (e.key === "ArrowLeft") showReview(currentReviewIndex - 1);
        if (e.key === "ArrowRight") showReview(currentReviewIndex + 1);
      }

      // Lightbox navigation
      if (lightboxEl.classList.contains("show")) {
        if (e.key === "ArrowLeft") lightboxStep(-1);
        if (e.key === "ArrowRight") lightboxStep(1);
      }
    });

    // Cleanup on close
    lightboxEl.addEventListener("hidden.bs.modal", function () {
      if (lbImg) {
        lbImg.src = "";
        lbImg.alt = "";
      }
      if (lbTitle) lbTitle.textContent = "Review Photos";
    });
  });
})();