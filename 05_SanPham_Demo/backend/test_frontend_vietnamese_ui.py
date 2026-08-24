"""Static check: forbidden English UI phrases must not appear as rendered
text in the frontend. Scoped to visible HTML text nodes and JS source with
comments stripped, so it does not fail on DOM ids, variable names, API
paths, canonical algorithm names, or source comments (all of which
legitimately stay in English)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

FORBIDDEN = [
    "Control Room", "Live Simulation", "Compare Policies", "Long Horizon",
    "Run History", "Why This Driver", "Service Rate", "Assigned", "Declined",
    "Infeasible", "Pickup ETA", "Demand / Supply", "Mean Income",
    "Bottom 10%", "Top 10%", "Verified Replay", "New Run", "Save Run",
    "Checking backend", "No data", "No run selected",
]


def _html_visible_text(html: str) -> str:
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def _js_without_comments(js: str) -> str:
    js = re.sub(r"//[^\n]*", " ", js)
    return re.sub(r"/\*.*?\*/", " ", js, flags=re.S)


def _find_forbidden(text: str) -> list[tuple[str, str]]:
    hits = []
    for phrase in FORBIDDEN:
        for m in re.finditer(re.escape(phrase), text):
            start, end = m.start(), m.end()
            before = text[start - 1] if start > 0 else " "
            after = text[end] if end < len(text) else " "
            if before.isalpha() or after.isalpha():
                continue  # part of a larger identifier (camelCase, etc.)
            hits.append((phrase, text[max(0, start - 40):end + 40]))
    return hits


@pytest.mark.parametrize("filename,extractor", [
    ("index.html", _html_visible_text),
    ("app.js", _js_without_comments),
])
def test_no_forbidden_english_ui_phrases(filename, extractor):
    text = extractor((FRONTEND_DIR / filename).read_text(encoding="utf-8"))
    hits = _find_forbidden(text)
    assert not hits, f"English UI leakage in {filename}: {hits}"
