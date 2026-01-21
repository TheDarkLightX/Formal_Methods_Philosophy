(() => {
  const doc = document.querySelector("[data-fp-doc]");
  const toc = document.querySelector("[data-fp-toc]");
  const progress = document.querySelector("[data-fp-progress-bar]");

  if (!doc) {
    if (progress) progress.style.width = "0%";
    return;
  }

  const content = doc.querySelector(".fp-doc-content") || doc;

  const slugify = (text) =>
    text
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .slice(0, 64);

  const headings = Array.from(content.querySelectorAll("h2, h3")).filter(
    (h) => h.textContent && h.textContent.trim().length > 0,
  );

  const ensureId = (heading) => {
    if (heading.id) return heading.id;
    const base = slugify(heading.textContent);
    if (!base) return "";

    let id = base;
    let n = 2;
    while (document.getElementById(id)) {
      id = `${base}-${n}`;
      n += 1;
    }

    heading.id = id;
    return id;
  };

  const addAnchor = (heading, id) => {
    if (heading.querySelector(".fp-heading-anchor")) return;
    const a = document.createElement("a");
    a.className = "fp-heading-anchor";
    a.href = `#${id}`;
    a.setAttribute("aria-label", "Link to this section");
    a.textContent = "#";
    heading.appendChild(a);
  };

  if (toc) {
    toc.innerHTML = "";

    const list = document.createElement("div");
    list.className = "fp-toc-list";

    headings.forEach((heading) => {
      const id = ensureId(heading);
      if (!id) return;
      addAnchor(heading, id);

      const a = document.createElement("a");
      a.className = "fp-toc-link";
      a.href = `#${id}`;
      a.textContent = heading.textContent.trim();
      a.dataset.fpTocTarget = id;
      a.dataset.fpTocLevel = heading.tagName.toLowerCase();
      list.appendChild(a);
    });

    toc.appendChild(list);
  }

  const updateActiveToc = () => {
    if (!toc) return;
    const scrollY = window.scrollY || window.pageYOffset || 0;
    const offset = 120;

    let activeId = null;
    for (const heading of headings) {
      const id = heading.id;
      if (!id) continue;
      const top = heading.getBoundingClientRect().top + scrollY;
      if (top - offset <= scrollY) activeId = id;
      else break;
    }

    toc.querySelectorAll(".fp-toc-link").forEach((a) => {
      a.classList.toggle("is-active", a.dataset.fpTocTarget === activeId);
    });
  };

  const updateProgress = () => {
    if (!progress) return;

    const docRect = content.getBoundingClientRect();
    const scrollTop = window.scrollY || window.pageYOffset || 0;
    const docTop = scrollTop + docRect.top;
    const docHeight = Math.max(1, content.scrollHeight);
    const viewport = window.innerHeight || 1;
    const maxScroll = Math.max(1, docTop + docHeight - viewport);
    const pct = Math.min(1, Math.max(0, scrollTop / maxScroll));

    progress.style.width = `${Math.round(pct * 100)}%`;
  };

  let raf = null;
  const onScroll = () => {
    if (raf) return;
    raf = window.requestAnimationFrame(() => {
      raf = null;
      updateActiveToc();
      updateProgress();
    });
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);

  onScroll();
})();

