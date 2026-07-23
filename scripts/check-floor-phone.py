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
    assert h2_text == "On the supervisor's phone.", f"{path}: bad h2 {h2_text!r}"

    t0 = dismiss(page, "ack")
    t1 = page.locator("#floorTitle").inner_text()
    assert t1 != t0, f"{path}: ack did not advance"

    dismiss(page, "snooze")
    t2 = page.locator("#floorTitle").inner_text()
    assert t2 != t1, f"{path}: snooze did not advance"

    dismiss(page, "ack")
    page.wait_for_selector("#floorEnd:not([hidden])", timeout=3000)
    end = page.locator("#floorEnd strong").inner_text().strip()
    assert end == "Stamped Energy", f"{path}: end state {end!r}"
    assert not page.locator("#floorBubble").is_visible(), f"{path}: bubble still visible"

    # Desktop: status left, phone toward center-right; alarm wording
    page.set_viewport_size({"width": 1440, "height": 900})
    page.reload(wait_until="networkidle")
    go_to_slide(page, "scene-floor")
    layout = page.evaluate(
        """() => {
      const phone = document.getElementById('floorPhone');
      const rail = document.querySelector('#scene-floor .status-rail');
      const route = document.querySelector('#scene-floor .floor-route');
      const tag = document.getElementById('floorTag');
      const why = document.getElementById('floorWhy');
      if (!phone || !rail || !route) return null;
      const pr = phone.getBoundingClientRect();
      const rr = rail.getBoundingClientRect();
      const or_ = route.getBoundingClientRect();
      const items = Array.from(rail.querySelectorAll('.status-item'));
      const gaps = items.slice(0, -1).map((el, i) => items[i + 1].getBoundingClientRect().top - el.getBoundingClientRect().bottom);
      return {
        phoneLeft: pr.left,
        railRight: rr.right,
        routeLeft: or_.left,
        routeRight: or_.right,
        mid: window.innerWidth / 2,
        routes: document.querySelectorAll('#scene-floor .floor-route-card').length,
        tag: tag ? tag.textContent.trim() : '',
        why: why ? why.textContent.trim() : '',
        gaps,
        phoneRatio: pr.height ? pr.width / pr.height : 0,
      };
    }"""
    )
    assert layout and layout["railRight"] <= layout["phoneLeft"] + 8, f"{path}: status should be left of phone {layout}"
    assert layout["routeLeft"] < layout["phoneLeft"], f"{path}: route should be left of phone {layout}"
    assert layout["phoneLeft"] > layout["mid"] * 0.78, f"{path}: phone should sit on the right {layout}"
    assert all(g >= 12 for g in layout["gaps"]), f"{path}: status gaps too small {layout['gaps']}"
    assert layout["routes"] >= 3, f"{path}: expected route cards, got {layout['routes']}"
    assert layout["tag"].startswith("Alarm"), f"{path}: bad tag {layout['tag']!r}"
    assert layout["why"].startswith("Alarm:"), f"{path}: bad alarm line {layout['why']!r}"
    assert page.locator(".wa-compose").count() == 1, f"{path}: missing compose bar"
    assert page.locator(".phone-island").count() == 1, f"{path}: missing dynamic island"

    # Mobile phone: slight uniform scale, not vertically compressed
    page.set_viewport_size({"width": 390, "height": 844})
    page.reload(wait_until="networkidle")
    go_to_slide(page, "scene-floor")
    mobile_phone = page.evaluate(
        """() => {
      const phone = document.getElementById('floorPhone');
      const screen = phone && phone.querySelector('.phone__screen');
      if (!phone || !screen) return null;
      const pr = phone.getBoundingClientRect();
      const sr = screen.getBoundingClientRect();
      const cs = getComputedStyle(screen);
      return {
        phoneRatio: pr.height ? pr.width / pr.height : 0,
        screenRatio: sr.height ? sr.width / sr.height : 0,
        aspect: cs.aspectRatio,
        screenW: sr.width,
      };
    }"""
    )
    assert mobile_phone and 0.40 <= mobile_phone["phoneRatio"] <= 0.55, f"{path}: mobile phone squashed {mobile_phone}"
    assert mobile_phone["screenW"] >= 250, f"{path}: mobile phone scaled down too far {mobile_phone}"

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
