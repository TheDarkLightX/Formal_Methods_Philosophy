(() => {
  const selector = ".fp-diagram";
  const diagrams = Array.from(document.querySelectorAll(selector));
  if (!diagrams.length) return;

  let active = null;
  let lastFocus = null;

  const close = () => {
    if (!active) return;
    active.remove();
    active = null;
    document.body.classList.remove("fp-modal-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
    lastFocus = null;
  };

  const open = (sourceEl) => {
    close();
    lastFocus = document.activeElement;
    document.body.classList.add("fp-modal-open");

    const overlay = document.createElement("div");
    overlay.className = "fp-lightbox";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Diagram viewer");

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "fp-lightbox-close";
    closeBtn.textContent = "Close";
    closeBtn.addEventListener("click", close);

    const inner = document.createElement("div");
    inner.className = "fp-lightbox-inner";

    const clone = sourceEl.cloneNode(true);
    clone.removeAttribute("width");
    clone.removeAttribute("height");
    inner.appendChild(clone);

    overlay.appendChild(closeBtn);
    overlay.appendChild(inner);

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) close();
    });

    const onKey = (e) => {
      if (e.key === "Escape") close();
    };

    document.addEventListener("keydown", onKey, { once: true });

    document.body.appendChild(overlay);
    active = overlay;
    closeBtn.focus();
  };

  diagrams.forEach((diagram) => {
    diagram.classList.add("fp-zoomable");
    diagram.addEventListener("click", () => open(diagram));
    diagram.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        open(diagram);
      }
    });
    diagram.setAttribute("tabindex", "0");
    diagram.setAttribute("role", "button");
    diagram.setAttribute("aria-label", "Open diagram");
  });
})();

