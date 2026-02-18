#!/usr/bin/env python3
"""Build a static docs site from markdown pages.

Source of truth:
- pages/**/*.md
- assets/**

Generated:
- index.html
- site-data.json
"""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

try:
    import markdown as _markdown  # type: ignore
except Exception:
    _markdown = None

_ORDERED_NAME_RE = re.compile(r"^\s*(\d+)\s*[-_. )]+\s*(.*)$")


def _ordered_name(raw: str) -> tuple[int, str]:
    text = str(raw or "").strip()
    match = _ORDERED_NAME_RE.match(text)
    if not match:
        clean = text.replace("-", " ").replace("_", " ").strip()
        return (10_000, clean or text)
    order = int(match.group(1))
    tail = (match.group(2) or "").strip()
    clean = tail.replace("-", " ").replace("_", " ").strip() or text
    return (order, clean)


def _title_from_markdown(md_path: Path) -> str:
    stem = _ordered_name(md_path.stem)[1].title()
    try:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("# "):
                heading = _ordered_name(s[2:].strip())[1]
                return heading or stem
    except Exception:
        return stem
    return stem


def _slug_for(md_path: Path, root: Path) -> str:
    return md_path.relative_to(root).with_suffix("").as_posix()


def _scan_pages(root: Path) -> list[dict]:
    pages = []
    if not root.exists():
        return pages
    for md_path in sorted(root.rglob("*.md")):
        slug = _slug_for(md_path, root)
        pages.append(
            {
                "slug": slug,
                "path": md_path.relative_to(root).as_posix(),
                "title": _title_from_markdown(md_path),
                "order": _ordered_name(md_path.stem)[0],
                "md_path": md_path,
            }
        )
    return pages


def _insert_node(tree: dict, rel_parts: list[str], page: dict) -> None:
    node = tree
    for part in rel_parts[:-1]:
        children = node.setdefault("children", {})
        part_order, part_name = _ordered_name(part)
        node = children.setdefault(
            part,
            {
                "type": "folder",
                "name": part_name.title(),
                "order": part_order,
                "children": {},
            },
        )
    file_nodes = node.setdefault("pages", [])
    file_nodes.append(
        {
            "type": "page",
            "title": page["title"],
            "slug": page["slug"],
            "order": page.get("order", 10_000),
        }
    )


def _normalize_tree(node: dict, path_prefix: str = "") -> list[dict]:
    def _page_sort_key(page: dict) -> tuple[int, int, str]:
        slug = str(page.get("slug", "")).strip("/").lower()
        leaf = slug.split("/")[-1] if slug else ""
        is_overview = leaf in ("readme", "index")
        order = int(page.get("order", 10_000))
        title = str(page.get("title", "")).lower()
        return (0 if is_overview else 1, order, title)

    pages = sorted(node.get("pages", []), key=_page_sort_key)

    folders = []

    def _folder_sort_key(item: tuple[str, dict]) -> tuple[int, str]:
        key, child = item
        return (int(child.get("order", 10_000)), key.lower())

    for key, child in sorted(node.get("children", {}).items(), key=_folder_sort_key):
        child_path = f"{path_prefix}/{key}".strip("/")
        folders.append(
            {
                "type": "folder",
                "name": child.get("name", key),
                "path": child_path,
                "children": _normalize_tree(child, child_path),
            }
        )
    return pages + folders


def _plain_text_from_markdown(md: str) -> str:
    text = md.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"```[\s\S]*?```", " ", text)
    # Remove raw HTML blocks/tags from preview/search text (for example inline <img ...>).
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"^\s*\[[^\]]+\]:\s+\S+.*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"\b[\w./-]+\.md\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"(\*\*|__|\*|_)", "", text)
    text = re.sub(r"[\[\]\(\)]", " ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}\d+[.)]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_excerpt(content: str, query: str = "") -> str:
    plain = _plain_text_from_markdown(content)
    if not plain:
        return ""
    if not query:
        lead = plain[:220]
        if len(lead) < len(plain):
            cut = lead.rfind(" ")
            if cut > 100:
                lead = lead[:cut]
            lead = f"{lead.strip()}..."
        return lead.strip()

    q = (query or "").strip().lower()
    low = plain.lower()
    i = low.find(q)
    if i < 0:
        return _extract_excerpt(content, "")
    start = max(0, i - 90)
    end = min(len(plain), i + max(70, len(q)) + 90)
    if start > 0:
        ws = plain.rfind(" ", 0, start)
        if ws > 0:
            start = ws + 1
    if end < len(plain):
        ws = plain.find(" ", end)
        if ws > 0:
            end = ws
    snippet = plain[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(plain):
        snippet = f"{snippet}..."
    return snippet


def _safe_resolve(base: Path, rel_path: str) -> Path | None:
    try:
        resolved = (base / rel_path).resolve()
    except Exception:
        return None
    try:
        resolved.relative_to(base)
    except Exception:
        return None
    return resolved


def _rewrite_links(html_text: str, doc_md: Path, pages_root: Path, assets_root: Path) -> str:
    doc_dir = doc_md.parent

    def _replace(match: re.Match) -> str:
        attr = match.group(1)
        url = (match.group(2) or "").strip()
        if not url:
            return match.group(0)

        if url.startswith("/api/manual/assets/"):
            rel = url.removeprefix("/api/manual/assets/")
            return f'{attr}="./assets/{html.escape(rel, quote=True)}"'

        if url.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return match.group(0)

        if url.startswith("/"):
            return match.group(0)

        target = _safe_resolve(doc_dir, url)
        if target is None:
            return match.group(0)

        if target.suffix.lower() == ".md" and target.exists():
            slug = _slug_for(target, pages_root)
            return f'{attr}="#doc={html.escape(slug)}"'

        if target.exists() and target.is_file():
            if target.is_relative_to(assets_root):
                rel = target.relative_to(assets_root).as_posix()
                return f'{attr}="./assets/{quote(rel, safe="/")}"'
            try:
                rel_page = target.relative_to(pages_root).as_posix()
                return f'{attr}="./pages/{quote(rel_page, safe="/")}"'
            except Exception:
                return match.group(0)

        return match.group(0)

    rewritten = re.sub(r'(href|src)="([^"]+)"', _replace, html_text)
    # Strip screenshot build directives from compiled output.
    rewritten = re.sub(
        r"""\sdata-source\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)""",
        "",
        rewritten,
        flags=re.IGNORECASE,
    )
    return rewritten


def _render_markdown(md_text: str, md_path: Path, pages_root: Path, assets_root: Path) -> str:
    if _markdown is not None:
        rendered = _markdown.markdown(md_text, extensions=["fenced_code", "tables", "toc"])
        return _rewrite_links(rendered, md_path, pages_root, assets_root)

    def _inline(s: str) -> str:
        out = html.escape(s)
        out = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", out)
        out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
        out = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", out)
        out = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            lambda m: f'<img alt="{html.escape(m.group(1), quote=True)}" src="{html.escape(m.group(2), quote=True)}">',
            out,
        )
        out = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
            out,
        )
        return out

    lines = md_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    paragraph: list[str] = []
    in_ul = False
    in_ol = False
    in_code = False
    code_lines: list[str] = []
    in_raw_html = False
    raw_html_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{_inline(' '.join(paragraph).strip())}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            flush_paragraph()
            close_list()
            if not in_code:
                in_code = True
                code_lines = []
            else:
                out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                in_code = False
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        if in_raw_html:
            raw_html_lines.append(line)
            if ">" in line:
                flush_paragraph()
                close_list()
                out.append("\n".join(raw_html_lines))
                in_raw_html = False
                raw_html_lines = []
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2).strip())}</h{level}>")
            continue

        bullet = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bullet:
            flush_paragraph()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_inline(bullet.group(1).strip())}</li>")
            continue

        ordered = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if ordered:
            flush_paragraph()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{_inline(ordered.group(1).strip())}</li>")
            continue

        if line.strip().startswith("<") and line.strip().endswith(">"):
            flush_paragraph()
            close_list()
            out.append(line)
            continue

        if line.strip().startswith("<") and not line.strip().endswith(">"):
            in_raw_html = True
            raw_html_lines = [line]
            continue

        paragraph.append(line.strip())

    if in_code:
        out.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    if in_raw_html and raw_html_lines:
        out.append("\n".join(raw_html_lines))
    flush_paragraph()
    close_list()
    return _rewrite_links("".join(out), md_path, pages_root, assets_root)


def _build_tree(pages: list[dict]) -> list[dict]:
    raw_tree: dict = {"children": {}, "pages": []}
    for page in pages:
        rel = Path(page["path"])
        _insert_node(raw_tree, list(rel.parts), page)
    return _normalize_tree(raw_tree)


def _render_index_html(embedded_data_json: str, updated_label: str, title: str = "Pinball CTL Docs") -> str:
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{html.escape(title)}</title>
  <meta name=\"description\" content=\"Pinball CTL documentation site.\">
  <link rel=\"stylesheet\" href=\"./assets/css/style.css\">
  <link rel=\"stylesheet\" href=\"./assets/css/docs.css\">
</head>
<body>
  <header class=\"site-header\">
    <a class=\"brand\" href=\"#doc=README\" aria-label=\"Pinball CTL docs home\">
      <span class=\"brand-dot\" aria-hidden=\"true\"></span>
      <span>Pinball CTL Docs</span>
    </a>
    <button class=\"menu-toggle\" type=\"button\" aria-expanded=\"false\" aria-label=\"Toggle navigation\">
      <span></span><span></span><span></span>
    </button>
    <nav class=\"site-nav\" aria-label=\"Main navigation\">
      <span class=\"docs-updated\">Updated {html.escape(updated_label)}</span>
      <a href=\"https://pinballctl.com\" class=\"nav-link website-link\">
        <svg class=\"website-link__icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" focusable=\"false\">
          <path d=\"M3 12h18M12 3a16 16 0 0 1 0 18M12 3a16 16 0 0 0 0 18M4.5 7.5h15M4.5 16.5h15\"/>
        </svg>
        <span>Pinball CTL Website</span>
      </a>
    </nav>
  </header>

  <main id=\"top\" class=\"docs-shell\">
    <section class=\"section\">
      <p class=\"kicker hero-kicker\">Documentation</p>
      <h1>Pinball CTL Documentation</h1>
      <p class=\"lead\">Find setup guides, feature walkthroughs, and troubleshooting help for Pinball CTL.</p>

      <div class=\"docs-toolbar\">
        <button id=\"docs-sidebar-toggle\" class=\"docs-sidebar-toggle\" type=\"button\" aria-expanded=\"false\" aria-controls=\"docs-sidebar\">Docs Menu</button>
        <input type=\"search\" id=\"docs-search\" data-docs-search=\"desktop\" class=\"docs-search-input docs-search-desktop\" placeholder=\"Search docs...\" />
        <span id=\"docs-search-status\" data-docs-search-status=\"desktop\" class=\"docs-search-status docs-search-status-desktop\"></span>
      </div>

      <div class=\"docs-layout\">
        <aside id=\"docs-sidebar\" class=\"docs-sidebar\">
          <div class=\"docs-sidebar-head\">
            <span class=\"docs-sidebar-title\">Docs Menu</span>
            <button id=\"docs-sidebar-close\" class=\"docs-sidebar-close\" type=\"button\" aria-label=\"Close docs menu\">Close</button>
          </div>
          <div class=\"docs-sidebar-search\">
            <input type=\"search\" id=\"docs-search-mobile\" data-docs-search=\"mobile\" class=\"docs-search-input\" placeholder=\"Search docs...\" />
            <span id=\"docs-search-status-mobile\" data-docs-search-status=\"mobile\" class=\"docs-search-status\"></span>
          </div>
          <div id=\"docs-bookmarks-wrap\" class=\"docs-bookmarks-wrap hidden\">
            <div class=\"docs-bookmarks-title\">Bookmarks</div>
            <div id=\"docs-bookmarks\" class=\"docs-bookmarks\"></div>
          </div>
          <div id=\"docs-tree\" class=\"docs-tree\"></div>
          <div id=\"docs-search-results\" class=\"docs-search-results hidden\"></div>
        </aside>

        <article class=\"docs-content\">
          <button id=\"docs-bookmark-toggle\" class=\"docs-bookmark-toggle docs-bookmark-toggle-card\" type=\"button\" aria-pressed=\"false\" aria-label=\"Bookmark current page\" title=\"Bookmark current page\">
            <svg class=\"docs-bookmark-icon\" viewBox=\"0 0 24 24\" aria-hidden=\"true\" focusable=\"false\">
              <path d=\"M7 3h10a1 1 0 0 1 1 1v17l-6-3.8L6 21V4a1 1 0 0 1 1-1z\"></path>
            </svg>
          </button>
          <div class=\"doc-panel\" id=\"docs-article\"></div>
        </article>
      </div>
    </section>
  </main>

  <footer class=\"site-footer\">
    <div class=\"site-footer__inner\">
      <p class=\"site-footer__copy\">&copy; 2026 Pinball CTL. All rights reserved.</p>
      <nav class=\"site-footer__nav\" aria-label=\"Footer links\">
        <a href=\"https://www.pinballctl.com/privacy.html\" target=\"_blank\" rel=\"noopener noreferrer\">Privacy</a>
        <a href=\"https://www.pinballctl.com/terms.html\" target=\"_blank\" rel=\"noopener noreferrer\">Terms</a>
        <a href=\"https://www.pinballctl.com/contact.html\" target=\"_blank\" rel=\"noopener noreferrer\">Contact</a>
      </nav>
    </div>
  </footer>

  <div id=\"img-modal\" class=\"img-modal\" aria-hidden=\"true\" role=\"dialog\" aria-label=\"Screenshot preview\">
    <div class=\"img-modal__backdrop\"></div>
    <div class=\"img-modal__body\">
      <button class=\"img-modal__close\" aria-label=\"Close preview\">Close</button>
      <img src=\"\" alt=\"Screenshot preview\" class=\"img-modal__img\">
    </div>
  </div>

  <script id=\"site-data-inline\" type=\"application/json\">{embedded_data_json}</script>\n  <script src=\"./assets/js/main.js\"></script>
</body>
</html>
"""


def build(root: Path, website_root: Path | None = None) -> None:
    pages_root = root / "pages"
    assets_root = root / "assets"
    out_html = root / "index.html"
    out_data = root / "site-data.json"
    css_dir = root / "assets" / "css"
    js_dir = root / "assets" / "js"
    out_style = css_dir / "style.css"
    out_docs_css = css_dir / "docs.css"
    out_main_js = js_dir / "main.js"

    if not pages_root.exists():
        raise FileNotFoundError(f"pages directory not found: {pages_root}")
    if not assets_root.exists():
        raise FileNotFoundError(f"assets directory not found: {assets_root}")

    css_dir.mkdir(parents=True, exist_ok=True)
    js_dir.mkdir(parents=True, exist_ok=True)

    if website_root is not None:
        website_style = website_root / "style.css"
        if website_style.exists():
            out_style.write_text(website_style.read_text(encoding="utf-8"), encoding="utf-8")

    if not out_docs_css.exists():
        raise FileNotFoundError(f"docs.css missing: {out_docs_css}")
    if not out_main_js.exists():
        raise FileNotFoundError(f"main.js missing: {out_main_js}")

    pages = _scan_pages(pages_root)
    if not pages:
        raise RuntimeError("No markdown files found under pages/")

    for page in pages:
        md_text = page["md_path"].read_text(encoding="utf-8")
        page["html"] = _render_markdown(md_text, page["md_path"], pages_root, assets_root)
        page["plain"] = _plain_text_from_markdown(md_text)
        page["excerpt"] = _extract_excerpt(md_text)
        page.pop("md_path", None)

    tree = _build_tree(pages)
    default = next((p for p in pages if p["slug"] == "README"), None)
    if default is None:
        default = next((p for p in pages if p["slug"].split("/")[-1].lower() == "readme"), None)
    default_slug = (default or pages[0])["slug"]

    build_now = datetime.now(timezone.utc)
    payload = {
        "generated_at": build_now.isoformat(),
        "default_slug": default_slug,
        "tree": tree,
        "pages": pages,
    }

    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    out_data.write_text(payload_json, encoding="utf-8")
    updated_label = build_now.strftime("%Y-%m-%d %H:%M UTC")
    out_html.write_text(_render_index_html(payload_json, updated_label), encoding="utf-8")

    print(f"Built {out_html}")
    print(f"Built {out_data} ({len(pages)} pages)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static docs site from markdown pages.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--website-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "pinballctl-website",
        help="Website repo root used to copy style.css for matching layout",
    )
    args = parser.parse_args()

    website_root = args.website_root if args.website_root.exists() else None
    build(args.root.resolve(), website_root=website_root)


if __name__ == "__main__":
    main()
