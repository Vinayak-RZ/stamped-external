#!/usr/bin/env python3
"""Playwright gate: floor title, interactive phone, verify ledger wrapping."""
from __future__ import annotations

import http.server
import socketserver
import threading
from functools import partial
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def start_server() -> tuple[socketserver.TCPServer, str]:
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, f"http://127.0.0.1:{port}"


def go_to_slide(page, slide_id: str) -> None:
    page.evaluate(
        """(slideId) => {
      const slides = Array.from(document.querySelectorAll('.slide')).filter(
        (s) => getComputedStyle(s).display !== 'none'
      );
      const idx = slides.findIndex((s) => s.id === slideId);
      if (idx < 0) throw new Error(slideId + ' missing');
      const dots = document.querySelectorAll('#dots .dots__dot');
      if (dots[idx]) dots[idx].click();
      else slides.forEach((s, i) => s.classList.toggle('active', i === idx));
    }""",
        slide_id,
    )
    page.wait_for_selector(f"#{slide_id}.active", timeout=5000)


def dismiss(page, how: str) -> str:
    before = page.locator("#floorTitle").inner_text()
    if how == "snooze":
        page.locator("#floorSnooze").click()
    else:
        page.locator("#floorAck").click()
    page.wait_for_timeout(400)
    return before


def check_deck(page, base: str, path: str) -> None:
    page.goto(f"{base}/{path}", wait_until="networkidle")
    page.set_viewport_size({"width": 390, "height": 844})

    go_to_slide(page, "scene-floor")

    h2 = page.locator("#scene-floor h2")
    assert h2.is_visible(), f"{path}: floor h2 not visible on mobile"
    h2_text = h2.inner_text().strip()
    assert h2_text == "The action reaches the floor.", f"{path}: bad h2 {h2_text!r}"

    t0 = dismiss(page, "ack")
    t1 = page.locator("#floorTitle").inner_text()
    assert t1 != t0, f"{path}: ack did not advance"

    dismiss(page, "snooze")
    t2 = page.locator("#floorTitle").inner_text()
    assert t2 != t1, f"{path}: snooze did not advance"

    dismiss(page, "ack")
    page.wait_for_selector("#floorEnd:not([hidden])", timeout=3000)
    end = page.locator("#floorEnd").inner_text().strip()
    assert end == "Stamped Energy", f"{path}: end state {end!r}"
    assert not page.locator("#floorBubble").is_visible(), f"{path}: bubble still visible"

    go_to_slide(page, "scene-verify")
    cells = page.evaluate(
        """() => Array.from(document.querySelectorAll(
          '#scene-verify .ledger-table th, #scene-verify .ledger-table td'
        )).map((el) => {
          const cs = getComputedStyle(el);
          return {
            text: el.textContent.trim(),
            wordBreak: cs.wordBreak,
            overflowWrap: cs.overflowWrap,
          };
        })"""
    )
    for c in cells:
        assert c["wordBreak"] == "normal", f"{path}: word-break={c['wordBreak']} for {c['text']!r}"
        assert c["overflowWrap"] != "anywhere", f"{path}: overflow-wrap=anywhere for {c['text']!r}"

    print(f"OK {path}")


def main() -> None:
    httpd, base = start_server()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            check_deck(page, base, "demo-decks/pharma/index.html")
            check_deck(page, base, "demo-decks/cement.html")
            browser.close()
        print("ALL_CHECKS_PASSED")
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
