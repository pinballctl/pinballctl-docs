#!/usr/bin/env python3
"""Build screenshots from markdown directives.

Directive format in markdown:
<!-- pinballctl-shot {"url":"/login","output":"assets/screenshots/login.png"} -->
or on image tags:
<img src="/api/manual/assets/screenshots/login.png" data-source='{"url":"/login"}' ...>

Supported keys:
- url: Absolute URL or path (path is joined to domain)
- output: Output path (relative to docs root or absolute)
- domain: Optional per-shot domain override
- username/password: Optional per-shot login override
- login: true/false (when true, script performs a login step)
- with_frame: true/false (default true)
- full_page: true/false (default false; whole window/viewport capture)
- target: CSS selector for element-only capture (class or id)
- wait_for: CSS selector to wait for before capture
- dark_mode: true/false (emulate browser dark color scheme)
- dark_toggle: optional selector to click a UI dark-mode toggle
- click: click path; list of strings or step objects
  - string step: selector to click
  - object step:
    - action: click|wait|type|hover
    - selector: CSS selector or Playwright selector
    - value: value for type action
    - timeout_ms: optional wait timeout override
    - wait_for: optional selector to wait for after step
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
SHOT_RE = re.compile(r"<!--\s*pinballctl-shot\s*(\{.*?\})\s*-->", re.DOTALL)
IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r'([:@\w-]+)\s*=\s*(".*?"|\'.*?\'|[^\s>]+)', re.DOTALL)

DEFAULT_DOMAIN = "http://127.0.0.1:8888"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"
DEFAULT_TIMEOUT_MS = 10000
DEFAULT_VIEWPORT_WIDTH = 1440
DEFAULT_VIEWPORT_HEIGHT = 900


@dataclass
class ShotPlan:
    source: str
    line: int
    url: str
    next_url: str | None
    output: Path
    login: bool
    username: str | None
    password: str | None
    with_frame: bool
    full_page: bool
    target: str | None
    wait_for: str | None
    dark_mode: bool
    dark_toggle: str | None
    settle_ms: int
    highlight: list[dict[str, str]]
    click: list[Any]
    username_selector: str
    password_selector: str
    submit_selector: str
    raw: dict[str, Any]


def _line_number(text: str, start_idx: int) -> int:
    return text.count("\n", 0, start_idx) + 1


def _parse_tag_attrs(tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for key, value in ATTR_RE.findall(tag):
        v = value.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        attrs[key.lower()] = html.unescape(v)
    return attrs


def _output_from_img_src(src: str) -> str:
    clean = src.split("?", 1)[0].split("#", 1)[0]
    if clean.startswith("/api/manual/"):
        return clean[len("/api/manual/"):]
    if clean.startswith("./") or clean.startswith("../"):
        return clean
    if clean.startswith("/"):
        return clean[1:]
    return clean


def _parse_data_source(raw_value: str, source: str, line: int) -> dict[str, Any]:
    value = raw_value.strip()
    if not value:
        return {}
    if value.startswith("{"):
        try:
            parsed = json.loads(value)
        except Exception as exc:
            raise ValueError(f"Invalid data-source JSON in {source}:{line}: {exc}") from exc
        if not isinstance(parsed, dict):
            raise ValueError(f"data-source must decode to an object in {source}:{line}")
        return parsed
    return {"url": value}


def parse_directives(pages_root: Path, docs_root: Path) -> list[tuple[dict[str, Any], str, int]]:
    plans: list[tuple[dict[str, Any], str, int]] = []
    for md in sorted(pages_root.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        source = md.relative_to(docs_root).as_posix()

        for match in SHOT_RE.finditer(text):
            raw = match.group(1)
            line = _line_number(text, match.start())
            try:
                spec = json.loads(raw)
            except Exception as exc:
                raise ValueError(
                    f"Invalid JSON directive in {source}:{line}: {exc}"
                ) from exc
            plans.append((spec, source, line))

        for match in IMG_RE.finditer(text):
            line = _line_number(text, match.start())
            attrs = _parse_tag_attrs(match.group(0))
            if "data-source" not in attrs:
                continue

            spec = _parse_data_source(attrs.get("data-source", ""), source, line)
            if not spec:
                continue

            if "output" not in spec and attrs.get("src"):
                spec["output"] = _output_from_img_src(attrs["src"])

            plans.append((spec, source, line))
    return plans


def _normalize_output(path_str: str, docs_root: Path) -> Path:
    out = Path(path_str)
    if not out.is_absolute():
        out = docs_root / out
    return out


def _bool(spec: dict[str, Any], key: str, default: bool) -> bool:
    v = spec.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"1", "true", "yes", "on"}:
            return True
        if s in {"0", "false", "no", "off"}:
            return False
    raise ValueError(f"{key} must be a boolean")


def build_plan(
    spec: dict[str, Any],
    source: str,
    line: int,
    docs_root: Path,
    default_domain: str,
    default_username: str,
    default_password: str,
) -> ShotPlan:
    if "output" not in spec:
        raise ValueError(f"{source}:{line} missing required 'output'")
    if "url" not in spec:
        raise ValueError(f"{source}:{line} missing required 'url'")

    domain = str(spec.get("domain") or default_domain).rstrip("/")
    url_value = str(spec["url"]).strip()
    if not url_value:
        raise ValueError(f"{source}:{line} 'url' cannot be empty")
    def _resolve_url(raw_url: str) -> str:
        value = str(raw_url).strip()
        if value.startswith("http://") or value.startswith("https://"):
            return value
        if not value.startswith("/"):
            value = "/" + value
        return urljoin(domain + "/", value.lstrip("/"))

    url = _resolve_url(url_value)
    next_url_raw = spec.get("next_url")
    next_url = _resolve_url(str(next_url_raw)) if next_url_raw is not None else None

    login = _bool(spec, "login", False)
    with_frame = _bool(spec, "with_frame", True)
    full_page = _bool(spec, "full_page", False)
    dark_mode = _bool(spec, "dark_mode", False)

    username = spec.get("username")
    password = spec.get("password")
    username = str(username) if username is not None else default_username
    password = str(password) if password is not None else default_password

    target = spec.get("target")
    if target is not None:
        target = str(target)

    wait_for = spec.get("wait_for")
    if wait_for is not None:
        wait_for = str(wait_for)
    dark_toggle = spec.get("dark_toggle")
    if dark_toggle is not None:
        dark_toggle = str(dark_toggle)
    settle_ms = int(spec.get("settle_ms", 220))
    highlight_raw = spec.get("highlight", [])
    if isinstance(highlight_raw, dict):
        highlight_raw = [highlight_raw]
    if not isinstance(highlight_raw, list):
        raise ValueError(f"{source}:{line} 'highlight' must be an object or list")
    highlight: list[dict[str, str]] = []
    for i, entry in enumerate(highlight_raw, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"{source}:{line} highlight entry {i} must be an object")
        selector = entry.get("selector")
        if not selector:
            raise ValueError(f"{source}:{line} highlight entry {i} missing 'selector'")
        style = entry.get("style") or "border: 4px solid red;"
        highlight.append({"selector": str(selector), "style": str(style)})

    click = spec.get("click", [])
    if not isinstance(click, list):
        raise ValueError(f"{source}:{line} 'click' must be a list")

    return ShotPlan(
        source=source,
        line=line,
        url=url,
        next_url=next_url,
        output=_normalize_output(str(spec["output"]), docs_root),
        login=login,
        username=username,
        password=password,
        with_frame=with_frame,
        full_page=full_page,
        target=target,
        wait_for=wait_for,
        dark_mode=dark_mode,
        dark_toggle=dark_toggle,
        settle_ms=settle_ms,
        highlight=highlight,
        click=click,
        username_selector=str(spec.get("username_selector", "input[name='username']")),
        password_selector=str(spec.get("password_selector", "input[name='password']")),
        submit_selector=str(spec.get("submit_selector", "button[type='submit']")),
        raw=spec,
    )


def _first_visible_selector(page: Any, selectors: list[str], timeout_ms: int) -> str | None:
    for sel in selectors:
        try:
            page.wait_for_selector(sel, timeout=timeout_ms, state="visible")
            return sel
        except Exception:
            continue
    return None


def _run_login(page: Any, plan: ShotPlan, timeout_ms: int) -> None:
    user_sel = _first_visible_selector(
        page,
        [
            plan.username_selector,
            "#username",
            "input[type='text']",
            "input[name='user']",
        ],
        timeout_ms,
    )
    pass_sel = _first_visible_selector(
        page,
        [
            plan.password_selector,
            "#password",
            "input[type='password']",
            "input[name='pass']",
        ],
        timeout_ms,
    )
    if not user_sel or not pass_sel:
        raise RuntimeError("Login requested but could not find username/password fields")

    page.fill(user_sel, plan.username or "")
    page.fill(pass_sel, plan.password or "")

    try:
        page.click(plan.submit_selector, timeout=timeout_ms)
    except Exception:
        alt_submit = _first_visible_selector(
            page,
            [
                "button[type='submit']",
                "button:has-text('Sign in')",
                "button:has-text('Login')",
                "input[type='submit']",
            ],
            timeout_ms,
        )
        if not alt_submit:
            raise RuntimeError("Login requested but could not find submit button")
        page.click(alt_submit, timeout=timeout_ms)


def _run_click_steps(page: Any, plan: ShotPlan, timeout_ms: int) -> None:
    username_selectors = {
        plan.username_selector,
        "input[name='username']",
        'input[name="username"]',
        "#username",
        "input[name='user']",
        'input[name="user"]',
        "input[type='text']",
    }
    password_selectors = {
        plan.password_selector,
        "input[name='password']",
        'input[name="password"]',
        "#password",
        "input[name='pass']",
        'input[name="pass"]',
        "input[type='password']",
    }

    for idx, step in enumerate(plan.click, start=1):
        if isinstance(step, str):
            page.wait_for_selector(step, timeout=timeout_ms, state="visible")
            page.click(step, timeout=timeout_ms)
            continue

        if not isinstance(step, dict):
            raise ValueError(f"{plan.source}:{plan.line} click step {idx} must be string or object")

        action = str(step.get("action", "click")).strip().lower()
        selector = step.get("selector")
        local_timeout = int(step.get("timeout_ms", timeout_ms))

        if action == "click":
            if not selector:
                raise ValueError(
                    f"{plan.source}:{plan.line} click step {idx} missing 'selector'"
                )
            page.click(str(selector), timeout=local_timeout)
        elif action == "wait":
            wait_sel = step.get("wait_for") or selector
            if not wait_sel:
                raise ValueError(
                    f"{plan.source}:{plan.line} wait step {idx} needs 'wait_for' or 'selector'"
                )
            page.wait_for_selector(str(wait_sel), timeout=local_timeout)
        elif action == "type":
            if not selector:
                raise ValueError(
                    f"{plan.source}:{plan.line} type step {idx} missing 'selector'"
                )
            sel = str(selector)
            if "value" in step:
                fill_value = str(step["value"])
            elif sel in username_selectors:
                fill_value = str(plan.username or "")
            elif sel in password_selectors:
                fill_value = str(plan.password or "")
            else:
                raise ValueError(
                    f"{plan.source}:{plan.line} type step {idx} missing 'value'"
                )
            page.fill(sel, fill_value, timeout=local_timeout)
        elif action == "hover":
            if not selector:
                raise ValueError(
                    f"{plan.source}:{plan.line} hover step {idx} missing 'selector'"
                )
            page.hover(str(selector), timeout=local_timeout)
        else:
            raise ValueError(
                f"{plan.source}:{plan.line} click step {idx} has unsupported action '{action}'"
            )

        if step.get("wait_for") and action != "wait":
            page.wait_for_selector(str(step["wait_for"]), timeout=local_timeout)


def _capture(page: Any, plan: ShotPlan, timeout_ms: int) -> None:
    plan.output.parent.mkdir(parents=True, exist_ok=True)

    if plan.target:
        locator = page.locator(plan.target).first
        locator.wait_for(state="visible", timeout=timeout_ms)
        locator.screenshot(path=str(plan.output))
        return

    if plan.with_frame:
        page.screenshot(path=str(plan.output), full_page=plan.full_page)
        return

    page.screenshot(path=str(plan.output), full_page=False)


def _apply_highlight(page: Any, plan: ShotPlan) -> None:
    if not plan.highlight:
        return
    page.evaluate(
        """(items) => {
          for (const item of items) {
            const nodes = document.querySelectorAll(item.selector);
            nodes.forEach((el) => {
              const prev = el.getAttribute("style") || "";
              const next = prev ? `${prev}; ${item.style}` : item.style;
              el.setAttribute("style", next);
            });
          }
        }""",
        plan.highlight,
    )


def run_capture(plans: list[ShotPlan], timeout_ms: int, headed: bool, overwrite: bool = False) -> tuple[int, int]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(
            "Playwright is required for capture. Install it with '\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium'\n"
            f"Import error: {exc}",
            file=sys.stderr,
        )
        return (0, len(plans))

    ok = 0
    fail = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        try:
            for plan in plans:
                if plan.output.exists() and not overwrite:
                    print(f"SKIP {plan.source}:{plan.line} -> {plan.output} (already exists)")
                    continue
                context = browser.new_context(
                    viewport={"width": DEFAULT_VIEWPORT_WIDTH, "height": DEFAULT_VIEWPORT_HEIGHT}
                )
                page = context.new_page()
                try:
                    if plan.dark_mode:
                        page.emulate_media(color_scheme="dark")
                    page.goto(plan.url, wait_until="domcontentloaded", timeout=timeout_ms)
                    if plan.login:
                        _run_login(page, plan, timeout_ms)
                    if plan.dark_toggle:
                        page.click(plan.dark_toggle, timeout=timeout_ms)
                    _run_click_steps(page, plan, timeout_ms)
                    if plan.next_url:
                        page.goto(plan.next_url, wait_until="domcontentloaded", timeout=timeout_ms)
                    if plan.wait_for:
                        page.wait_for_selector(plan.wait_for, timeout=timeout_ms)
                    _apply_highlight(page, plan)
                    if plan.settle_ms > 0:
                        page.wait_for_timeout(plan.settle_ms)
                    _capture(page, plan, timeout_ms)
                    print(f"OK   {plan.source}:{plan.line} -> {plan.output}")
                    ok += 1
                except Exception as exc:
                    print(f"FAIL {plan.source}:{plan.line} -> {plan.output} ({exc})")
                    fail += 1
                finally:
                    page.close()
                    context.close()
        finally:
            browser.close()
    return (ok, fail)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build screenshots from markdown directives")
    parser.add_argument("--root", type=Path, default=ROOT, help="Docs root path")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="Default domain")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Default username")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Default password")
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS, help="Default timeout")
    parser.add_argument("--headed", action="store_true", help="Run browser with UI")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing image files")
    parser.add_argument("--dry-run", action="store_true", help="Print capture plan only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs_root = args.root.resolve()
    pages_root = docs_root / "pages"

    parsed = parse_directives(pages_root, docs_root)
    if not parsed:
        print("No screenshot directives found.")
        return

    plans: list[ShotPlan] = []
    for spec, source, line in parsed:
        plan = build_plan(
            spec=spec,
            source=source,
            line=line,
            docs_root=docs_root,
            default_domain=args.domain,
            default_username=args.username,
            default_password=args.password,
        )
        plans.append(plan)

    print(f"Found {len(plans)} screenshot directives")
    for plan in plans:
        target_label = plan.target or ("full-page" if plan.full_page else "window")
        if plan.login:
            print(
                f"WARN {plan.source}:{plan.line} uses legacy login=true; "
                "prefer explicit click/type steps."
            )
        print(
            f"PLAN {plan.source}:{plan.line} -> {plan.output} @ {plan.url} "
            f"target={target_label} login={plan.login} dark_mode={plan.dark_mode} "
            f"clicks={len(plan.click)}"
        )

    if args.dry_run:
        return

    ok, fail = run_capture(
        plans,
        timeout_ms=args.timeout_ms,
        headed=args.headed,
        overwrite=args.overwrite,
    )
    print(f"Completed: ok={ok} fail={fail}")
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
