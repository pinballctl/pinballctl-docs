(function () {
  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function stripOrderPrefix(text) {
    const s = String(text || "").trim();
    return s.replace(/^\s*\d+\s*[-_. )]+\s*/i, "").trim() || s;
  }

  function menuTitleFor(slug, title) {
    return String(slug || "").toLowerCase() === "readme" ? "Home" : stripOrderPrefix(title || slug);
  }

  const BOOKMARKS_KEY = "pinballctl.docs.bookmarks.v1";
  const EXPANDED_KEY = "pinballctl.docs.expanded.v1";

  const state = {
    tree: [],
    pagesBySlug: new Map(),
    activeSlug: "",
    bookmarks: [],
    expanded: new Set(),
    searchTerm: "",
    lastResults: [],
  };

  function hashSlug() {
    const m = (window.location.hash || "").match(/doc=([^&]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function setHashSlug(slug) {
    const clean = encodeURIComponent(slug);
    if (window.location.hash !== `#doc=${clean}`) {
      window.location.hash = `doc=${clean}`;
    }
  }

  function loadState() {
    try {
      const b = JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || "[]");
      state.bookmarks = Array.isArray(b) ? b.filter((x) => x && x.slug) : [];
    } catch (_) {
      state.bookmarks = [];
    }
    try {
      const e = JSON.parse(localStorage.getItem(EXPANDED_KEY) || "[]");
      state.expanded = new Set(Array.isArray(e) ? e : []);
    } catch (_) {
      state.expanded = new Set();
    }
  }

  function persistBookmarks() {
    try {
      localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(state.bookmarks));
    } catch (_) {}
  }

  function persistExpanded() {
    try {
      localStorage.setItem(EXPANDED_KEY, JSON.stringify(Array.from(state.expanded)));
    } catch (_) {}
  }

  function isBookmarked(slug) {
    return state.bookmarks.some((b) => b.slug === slug);
  }

  function renderBookmarks() {
    const wrap = document.getElementById("docs-bookmarks-wrap");
    const el = document.getElementById("docs-bookmarks");
    if (!wrap || !el) return;

    if (!state.bookmarks.length) {
      wrap.classList.add("hidden");
      el.innerHTML = "";
      return;
    }
    wrap.classList.remove("hidden");
    el.innerHTML = state.bookmarks.map((b) => `
      <div class="docs-bookmark-item">
        <a href="#doc=${encodeURIComponent(b.slug)}" data-doc-slug="${esc(b.slug)}" class="docs-page-link${state.activeSlug === b.slug ? " active" : ""}">${esc(menuTitleFor(b.slug, b.title || b.slug))}</a>
        <button type="button" class="docs-bookmark-remove" data-bookmark-remove="${esc(b.slug)}" aria-label="Remove bookmark">x</button>
      </div>
    `).join("");
  }

  function refreshBookmarkToggle() {
    const btn = document.getElementById("docs-bookmark-toggle");
    if (!btn) return;
    const active = !!state.activeSlug && isBookmarked(state.activeSlug);
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
    btn.setAttribute("aria-label", active ? "Remove bookmark" : "Bookmark current page");
    btn.setAttribute("title", active ? "Remove bookmark" : "Bookmark current page");
  }

  function renderTreeNodes(nodes) {
    if (!Array.isArray(nodes) || !nodes.length) return "";
    return `<ul>${nodes.map((n) => {
      if (n.type === "folder") {
        const path = String(n.path || "");
        const open = state.expanded.has(path);
        return `<li class="docs-folder ${open ? "is-open" : ""}">
          <button type="button" class="docs-folder-toggle" data-folder-path="${esc(path)}" aria-expanded="${open ? "true" : "false"}">
            <span class="chev">${open ? "▾" : "▸"}</span>${esc(stripOrderPrefix(n.name || path))}
          </button>
          <div class="docs-folder-children ${open ? "" : "hidden"}">${renderTreeNodes(n.children || [])}</div>
        </li>`;
      }
      return `<li><a href="#doc=${encodeURIComponent(n.slug)}" data-doc-slug="${esc(n.slug)}" class="docs-page-link${state.activeSlug === n.slug ? " active" : ""}">${esc(menuTitleFor(n.slug, n.title || n.slug))}</a></li>`;
    }).join("")}</ul>`;
  }

  function renderTree() {
    const el = document.getElementById("docs-tree");
    if (!el) return;
    el.innerHTML = renderTreeNodes(state.tree);
  }

  function attachImageModal(articleEl) {
    const modal = document.getElementById("img-modal");
    const modalImg = modal?.querySelector(".img-modal__img");
    const closeBtn = modal?.querySelector(".img-modal__close");
    if (!modal || !modalImg) return;

    function close() {
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      modalImg.src = "";
    }

    closeBtn?.addEventListener("click", close);
    modal.addEventListener("click", (e) => {
      const t = e.target;
      if (!(t instanceof Element)) return;
      if (t === modal || t.classList.contains("img-modal__backdrop")) close();
    });

    articleEl.querySelectorAll("img").forEach((img) => {
      const src = img.getAttribute("src") || "";
      if (!src) return;
      img.classList.add("shot-click");
      img.addEventListener("click", () => {
        modalImg.src = src;
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
      });
    });
  }

  function renderArticle(slug) {
    const article = document.getElementById("docs-article");
    if (!article) return;
    const page = state.pagesBySlug.get(slug);
    if (!page) return;

    state.activeSlug = slug;
    article.innerHTML = page.html || `<h1>${esc(page.title || slug)}</h1><p>No content.</p>`;
    attachImageModal(article);

    article.querySelectorAll('a[href^="#doc="]').forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const h = a.getAttribute("href") || "";
        const s = (h.split("#doc=")[1] || "").trim();
        if (s) setHashSlug(decodeURIComponent(s));
      });
    });

    renderTree();
    renderBookmarks();
    refreshBookmarkToggle();
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  function scorePage(page, query) {
    const q = String(query || "").trim().toLowerCase();
    if (!q) return 0;
    const title = String(page.title || "").toLowerCase();
    const body = String(page.plain || "").toLowerCase();
    const excerpt = String(page.excerpt || "").toLowerCase();
    let s = 0;
    if (title.includes(q)) s += 100;
    if (body.includes(q)) s += 30;
    if (excerpt.includes(q)) s += 20;
    const tokens = q.match(/[a-z0-9][a-z0-9_-]*/g) || [];
    tokens.forEach((t) => {
      if (title.includes(t)) s += 22;
      if (body.includes(t)) s += 7;
    });
    return s;
  }

  function renderSearchResults(results) {
    const tree = document.getElementById("docs-tree");
    const resultsEl = document.getElementById("docs-search-results");
    const statusEl = document.getElementById("docs-search-status");
    if (!tree || !resultsEl || !statusEl) return;

    if (!state.searchTerm || state.searchTerm.length < 2) {
      tree.classList.remove("hidden");
      resultsEl.classList.add("hidden");
      resultsEl.innerHTML = "";
      statusEl.textContent = "";
      return;
    }

    tree.classList.add("hidden");
    resultsEl.classList.remove("hidden");
    statusEl.textContent = `${results.length} result${results.length === 1 ? "" : "s"}`;

    resultsEl.innerHTML = results.map((p) => `
      <a href="#doc=${encodeURIComponent(p.slug)}" data-doc-slug="${esc(p.slug)}" class="docs-search-result docs-page-link${state.activeSlug === p.slug ? " active" : ""}">
        <div class="docs-search-result-title">${esc(stripOrderPrefix(p.title || p.slug))}</div>
        <div class="docs-result-excerpt">${esc(p.excerpt || "")}</div>
      </a>
    `).join("");
  }

  function runSearch() {
    const query = state.searchTerm;
    if (!query || query.length < 2) {
      state.lastResults = [];
      renderSearchResults([]);
      return;
    }
    const scored = Array.from(state.pagesBySlug.values())
      .map((p) => ({ p, score: scorePage(p, query) }))
      .filter((x) => x.score > 0)
      .sort((a, b) => b.score - a.score || String(a.p.title).localeCompare(String(b.p.title)))
      .map((x) => x.p)
      .slice(0, 120);
    state.lastResults = scored;
    renderSearchResults(scored);
  }

  function wireEvents(defaultSlug) {
    document.addEventListener("click", (e) => {
      const target = e.target;
      if (!(target instanceof Element)) return;

      const remove = target.closest("[data-bookmark-remove]");
      if (remove) {
        e.preventDefault();
        const slug = remove.getAttribute("data-bookmark-remove") || "";
        state.bookmarks = state.bookmarks.filter((b) => b.slug !== slug);
        persistBookmarks();
        renderBookmarks();
        refreshBookmarkToggle();
        return;
      }

      const folder = target.closest("[data-folder-path]");
      if (folder) {
        e.preventDefault();
        const path = folder.getAttribute("data-folder-path") || "";
        if (state.expanded.has(path)) state.expanded.delete(path);
        else state.expanded.add(path);
        persistExpanded();
        renderTree();
        return;
      }

      const link = target.closest("[data-doc-slug]");
      if (link) {
        e.preventDefault();
        const slug = link.getAttribute("data-doc-slug") || "";
        if (slug) setHashSlug(slug);
      }
    });

    const bookmarkBtn = document.getElementById("docs-bookmark-toggle");
    bookmarkBtn?.addEventListener("click", () => {
      const slug = state.activeSlug;
      if (!slug) return;
      if (isBookmarked(slug)) {
        state.bookmarks = state.bookmarks.filter((b) => b.slug !== slug);
      } else {
        const page = state.pagesBySlug.get(slug);
        state.bookmarks.unshift({ slug, title: page?.title || slug });
      }
      persistBookmarks();
      renderBookmarks();
      refreshBookmarkToggle();
    });

    const searchEl = document.getElementById("docs-search");
    let t = null;
    searchEl?.addEventListener("input", () => {
      state.searchTerm = String(searchEl.value || "").trim();
      window.clearTimeout(t);
      t = window.setTimeout(runSearch, 120);
    });

    window.addEventListener("hashchange", () => {
      const slug = hashSlug() || defaultSlug;
      if (slug) renderArticle(slug);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        const modal = document.getElementById("img-modal");
        modal?.classList.remove("open");
      }
      const target = e.target;
      const inField = target instanceof Element && !!target.closest("input,textarea,select,[contenteditable='true']");
      if (!inField && e.key === "/") {
        e.preventDefault();
        searchEl?.focus();
        searchEl?.select();
      }
    });
  }

  function readInlineData() {
    const el = document.getElementById("site-data-inline");
    if (!el) return null;
    const raw = String(el.textContent || "").trim();
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function loadSiteData() {
    const inline = readInlineData();
    if (inline && typeof inline === "object") return inline;
    throw new Error("Missing inline docs data (#site-data-inline). Re-run build-docs.py.");
  }

  async function init() {
    loadState();

    const data = await loadSiteData();
    state.tree = Array.isArray(data.tree) ? data.tree : [];
    const pages = Array.isArray(data.pages) ? data.pages : [];
    pages.forEach((p) => state.pagesBySlug.set(String(p.slug || ""), p));

    renderTree();
    renderBookmarks();

    const defaultSlug = String(data.default_slug || pages[0]?.slug || "");
    wireEvents(defaultSlug);

    const slug = hashSlug() || defaultSlug;
    if (slug) renderArticle(slug);
  }

  document.addEventListener("DOMContentLoaded", init);
})();
