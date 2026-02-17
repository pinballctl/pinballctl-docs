#!/usr/bin/env python3
"""Parse screenshot directives from markdown pages and print capture plan.

Directive format in markdown:
<!-- pinballctl-shot {"url":"http://raspberrypi.local:8888/login","click":["text=Sign in"],"wait_for":"#dashboard","output":"assets/screenshots/dashboard.png"} -->

This script currently validates and prints planned captures.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
SHOT_RE = re.compile(r"<!--\s*pinballctl-shot\s*(\{.*?\})\s*-->", re.DOTALL)


def parse_directives() -> list[dict]:
    plans: list[dict] = []
    for md in sorted(PAGES.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for match in SHOT_RE.finditer(text):
            raw = match.group(1)
            try:
                spec = json.loads(raw)
            except Exception as exc:
                raise ValueError(f"Invalid JSON directive in {md}: {exc}") from exc
            spec["source"] = md.relative_to(ROOT).as_posix()
            plans.append(spec)
    return plans


def main() -> None:
    plans = parse_directives()
    if not plans:
        print("No screenshot directives found.")
        return
    print(f"Found {len(plans)} screenshot directives:")
    for i, plan in enumerate(plans, start=1):
        print(f"{i}. {plan.get('source')} -> {plan.get('output', '<missing output>')} @ {plan.get('url', '<missing url>')}")


if __name__ == "__main__":
    main()
