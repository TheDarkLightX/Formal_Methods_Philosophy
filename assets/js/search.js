(() => {
  const input = document.querySelector("[data-fp-search-input]");
  const resultsRoot = document.querySelector("[data-fp-search-results]");
  const hint = document.querySelector("[data-fp-search-hint]");

  if (!input || !resultsRoot) return;

  const normalize = (value) =>
    value
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();

  const limit = 8;
  let pages = null;
  let inflight = null;

  const render = (items, query) => {
    resultsRoot.innerHTML = "";

    if (!query) {
      if (hint) hint.textContent = "Tip: try “counterexample”, “invariant”, or “state machine”.";
      return;
    }

    if (!items.length) {
      if (hint) hint.textContent = "No matches. Try fewer words.";
      return;
    }

    if (hint) hint.textContent = `Showing ${Math.min(items.length, limit)} result(s).`;

    items.slice(0, limit).forEach((item) => {
      const a = document.createElement("a");
      a.className = "fp-search-result";
      a.href = item.url;

      const title = document.createElement("div");
      title.className = "fp-search-result-title";
      title.textContent = item.title;
      a.appendChild(title);

      if (item.snippet) {
        const snippet = document.createElement("div");
        snippet.className = "fp-search-result-snippet";
        snippet.textContent = item.snippet;
        a.appendChild(snippet);
      }

      resultsRoot.appendChild(a);
    });
  };

  const score = (page, query) => {
    let s = 0;
    if (page.title.includes(query)) s += 8;
    if (page.content.includes(query)) s += 3;
    page.tags?.forEach((t) => {
      if (t.includes(query)) s += 2;
    });
    return s;
  };

  const snippetOf = (content, query) => {
    const contentSingleLine = content.replace(/\s+/g, " ").trim();
    const idx = contentSingleLine.toLowerCase().indexOf(query);
    if (idx < 0) return "";
    const start = Math.max(0, idx - 60);
    const end = Math.min(contentSingleLine.length, idx + 140);
    return contentSingleLine.slice(start, end).trim();
  };

  const getPages = async () => {
    if (pages) return pages;
    if (inflight) return inflight;

    const searchUrl = window.FP_SEARCH_URL || "/search.json";

    inflight = fetch(searchUrl)
      .then((r) => r.json())
      .then((data) => {
        pages = data.map((p) => ({
          title: normalize(p.title || ""),
          url: p.url,
          tags: (p.tags || []).map(normalize),
          content: normalize(p.content || ""),
          rawTitle: p.title || "",
          rawContent: p.content || "",
        }));
        return pages;
      })
      .catch(() => {
        pages = [];
        return pages;
      })
      .finally(() => {
        inflight = null;
      });

    return inflight;
  };

  const onInput = async () => {
    const queryRaw = input.value || "";
    const query = normalize(queryRaw);
    const all = await getPages();

    if (!query) {
      render([], "");
      return;
    }

    const scored = all
      .map((p) => ({
        url: p.url,
        title: p.rawTitle,
        snippet: snippetOf(p.rawContent, query),
        score: score(p, query),
      }))
      .filter((x) => x.score > 0)
      .sort((a, b) => b.score - a.score);

    render(scored, query);
  };

  input.addEventListener("input", () => {
    onInput();
  });

  render([], "");
})();
