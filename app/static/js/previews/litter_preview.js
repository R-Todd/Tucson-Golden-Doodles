// app/static/js/previews/litter_preview.js

(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function setText(el, value, fallback) {
    if (!el) return;
    const v = (value || "").trim();
    el.textContent = v.length ? v : fallback;
  }

  function getSelectedText(selectEl) {
    if (!selectEl) return "";
    const opt = selectEl.options[selectEl.selectedIndex];
    return opt ? opt.text.trim() : "";
  }

  function formatDateToPretty(dateStr) {
    // DateField usually provides YYYY-MM-DD
    if (!dateStr) return "";
    const d = new Date(dateStr);
    if (Number.isNaN(d.getTime())) return "";
    return d.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
  }

  function updatePreview() {
    const breed = byId("breed_name")?.value || "";
    const expectedWeight = byId("expected_weight")?.value || "";
    const desc = byId("description")?.value || "";
    const birthRaw = byId("birth_date")?.value || "";

    const momName = getSelectedText(byId("mom_id"));
    const dadName = getSelectedText(byId("dad_id"));

    setText(byId("preview-title"), breed, "Litter");
    setText(byId("preview-breed"), breed, "—");
    setText(byId("preview-weight"), expectedWeight, "—");
    setText(byId("preview-desc"), desc, "Click below to explore the parents and puppies in this litter.");
    setText(byId("preview-born"), formatDateToPretty(birthRaw), "—");

    const bornPretty = formatDateToPretty(birthRaw);
    const parentsText = `${momName || "Mother: —"} & ${dadName || "Father: —"}${bornPretty ? " — Born on " + bornPretty : ""}`;
    setText(byId("preview-subtitle"), parentsText, "Mother: — & Father: —");

    // Image live preview from file input
    const fileInput = byId("image_upload");
    const imgEl = byId("preview-image");
    if (fileInput && imgEl && fileInput.files && fileInput.files[0]) {
      const file = fileInput.files[0];
      const url = URL.createObjectURL(file);
      imgEl.src = url;
    }
  }

  function wire() {
    const ids = ["breed_name", "expected_weight", "description", "birth_date", "mom_id", "dad_id", "image_upload"];
    ids.forEach((id) => {
      const el = byId(id);
      if (!el) return;
      el.addEventListener("input", updatePreview);
      el.addEventListener("change", updatePreview);
    });

    updatePreview();
  }

  document.addEventListener("DOMContentLoaded", wire);
})();