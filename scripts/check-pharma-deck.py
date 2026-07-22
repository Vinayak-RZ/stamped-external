#!/usr/bin/env python3
"""Full pharma deck professionalism gate — desktop + mobile, every slide."""
from __future__ import annotations

import http.server
import socketserver
import threading
from functools import partial
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/tmp/pharma-deck-audit")
DECK = "demo-decks/pharma/index.html"

EXPECTED_MATH = [
    "Load management",
    "HVAC & chillers",
    "Utilities & idle loads",
    "Tariff & intensity",
    "Early warnings",
]

EXPECTED_ORDER_PREFIX = [
    "scene-title",
    "scene-hook",
    "scene-math",
    "scene-what",
    "scene-prescription",
    "scene-floor",
    "scene-verify",
]


def start_server() -> tuple[socketserver.TCPServer, str]:
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def visible_slides(page) -> list[str]:
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('.slide'))
          .filter((s) => getComputedStyle(s).display !== 'none')
          .map((s) => s.id)"""
    )


def go_to(page, slide_id: str) -> None:
    page.evaluate(
        """(slideId) => {
      const slides = Array.from(document.querySelectorAll('.slide')).filter(
        (s) => getComputedStyle(s).display !== 'none'
      );
      const idx = slides.findIndex((s) => s.id === slideId);
      if (idx < 0) throw new Error('missing ' + slideId);
      const dots = document.querySelectorAll('#dots .dots__dot');
      if (dots[idx]) dots[idx].click();
      else slides.forEach((s, i) => s.classList.toggle('active', i === idx));
    }""",
        slide_id,
    )
    page.wait_for_selector(f"#{slide_id}.active", timeout=5000)


def audit_viewport(page, base: str, label: str, width: int, height: int) -> list[str]:
    issues: list[str] = []
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{base}/{DECK}", wait_until="networkidle")

    slides = visible_slides(page)
    if not slides:
        return [f"{label}: no visible slides"]
    if slides[: len(EXPECTED_ORDER_PREFIX)] != EXPECTED_ORDER_PREFIX:
        issues.append(f"{label}: order={slides[:8]} expected prefix={EXPECTED_ORDER_PREFIX}")
    if "scene-gap" in slides:
        issues.append(f"{label}: scene-gap should be merged away")

    hero = page.evaluate(
        """() => {
      const img = document.getElementById('heroPhotoImg');
      if (!img) return {ok:false, reason:'no hero'};
      return {
        ok: img.complete && img.naturalWidth > 0,
        src: img.currentSrc || img.src,
        nw: img.naturalWidth,
      };
    }"""
    )
    if not hero.get("ok"):
        issues.append(f"{label}: hero image failed {hero}")

    for sid in slides:
        go_to(page, sid)
        page.wait_for_timeout(750)
        page.screenshot(path=str(OUT / f"{label}_{sid}.png"))

        report = page.evaluate(
            """(slideId) => {
      const slide = document.getElementById(slideId);
      const vw = window.innerWidth;
      const problems = [];
      slide.querySelectorAll('h1,h2,h3,p,li,td,th,button,a,.chip,.lede,.eyebrow').forEach((el) => {
        const t = (el.textContent || '').trim();
        if (!t) return;
        const r = el.getBoundingClientRect();
        if (r.width < 2 || r.height < 2) return;
        if (getComputedStyle(el).visibility === 'hidden') return;
        if (r.right > vw + 2) problems.push('overflow:' + el.tagName + ':' + t.slice(0, 48));
      });
      if (slideId === 'scene-verify') {
        slide.querySelectorAll('.ledger-table td, .ledger-table th').forEach((el) => {
          const cs = getComputedStyle(el);
          if (cs.wordBreak !== 'normal') problems.push('ledger-word-break:' + cs.wordBreak);
        });
      }
      if (slideId === 'scene-math') {
        return {
          problems,
          mathTitles: Array.from(slide.querySelectorAll('.waste-card h3')).map((h) => h.textContent.trim()),
        };
      }
      if (slideId === 'scene-offer') {
        const cal = slide.querySelector('.ask-cal a');
        return {
          problems,
          cta: cal ? cal.textContent.trim() : null,
          href: cal ? cal.getAttribute('href') : null,
          day60: /Day 60/.test(slide.textContent || ''),
          pay: /pay-as-you-save/i.test(slide.textContent || ''),
          founders: Array.from(slide.querySelectorAll('.founders a')).map((a) => ({
            text: a.textContent.trim(),
            href: a.getAttribute('href'),
          })),
        };
      }
      if (slideId === 'scene-floor') {
        const h2 = slide.querySelector('h2');
        const phone = document.getElementById('floorPhone');
        const rail = slide.querySelector('.status-rail');
        const statusbar = slide.querySelector('.phone-statusbar');
        const rect = phone ? phone.getBoundingClientRect() : null;
        const railRect = rail ? rail.getBoundingClientRect() : null;
        const tag = slide.querySelector('#floorTag');
        return {
          problems,
          h2Visible: !!(h2 && getComputedStyle(h2).display !== 'none' && h2.getBoundingClientRect().height > 0),
          rxCount: Array.isArray(window.__FLOOR_RX__) ? window.__FLOOR_RX__.length : 0,
          hasStatusbar: !!statusbar,
          phoneRightOfRail: !!(rect && railRect && rect.left >= railRect.right - 8),
          hasCompose: !!slide.querySelector('.wa-compose'),
          hasIsland: !!slide.querySelector('.phone-island'),
          hasRouteCards: slide.querySelectorAll('.floor-route-card').length >= 3,
          alarmTag: tag ? tag.textContent.trim() : '',
        };
      }
      return {problems};
    }""",
            sid,
        )
        for p in report.get("problems") or []:
            issues.append(f"{label}/{sid}: {p}")

        if sid == "scene-math" and report.get("mathTitles") != EXPECTED_MATH:
            issues.append(f"{label}/scene-math: titles={report.get('mathTitles')}")

        if sid == "scene-offer":
            if report.get("cta") != "Book a meet":
                issues.append(f"{label}/scene-offer: CTA={report.get('cta')!r}")
            if "calendly.com/stamped-energy" not in (report.get("href") or ""):
                issues.append(f"{label}/scene-offer: bad calendly href")
            if not report.get("day60"):
                issues.append(f"{label}/scene-offer: missing Day 60")
            if not report.get("pay"):
                issues.append(f"{label}/scene-offer: missing pay-as-you-save")
            founders = report.get("founders") or []
            hrefs = {f.get("href") for f in founders}
            if "https://in.linkedin.com/in/vinayak-rz" not in hrefs:
                issues.append(f"{label}/scene-offer: missing Vinayak LinkedIn")
            if "https://in.linkedin.com/in/utso" not in hrefs:
                issues.append(f"{label}/scene-offer: missing Utso LinkedIn")

        if sid == "scene-floor":
            if width > 720 and not report.get("phoneRightOfRail"):
                issues.append(f"{label}/scene-floor: phone should sit right of status rail")
            if width > 720 and not report.get("hasRouteCards"):
                issues.append(f"{label}/scene-floor: missing alarm/prescription route cards")
            if not report.get("hasStatusbar"):
                issues.append(f"{label}/scene-floor: missing realistic status bar")
            if not report.get("hasCompose"):
                issues.append(f"{label}/scene-floor: missing compose bar")
            if not report.get("hasIsland"):
                issues.append(f"{label}/scene-floor: missing dynamic island")
            if not str(report.get("alarmTag") or "").startswith("Alarm"):
                issues.append(f"{label}/scene-floor: expected Alarm tag, got {report.get('alarmTag')!r}")
            if width <= 720:
                if not report.get("h2Visible"):
                    issues.append(f"{label}/scene-floor: h2 not visible")
                if report.get("rxCount") != 3:
                    issues.append(f"{label}/scene-floor: rxCount={report.get('rxCount')}")

    if width <= 720:
        go_to(page, "scene-floor")
        t0 = page.locator("#floorTitle").inner_text()
        page.locator("#floorAck").click()
        page.wait_for_timeout(400)
        if page.locator("#floorTitle").inner_text() == t0:
            issues.append(f"{label}: floor ack did not advance")
        page.locator("#floorSnooze").click()
        page.wait_for_timeout(400)
        page.locator("#floorAck").click()
        page.wait_for_timeout(400)
        if not page.locator("#floorEnd").is_visible():
            issues.append(f"{label}: floor end state not shown")

    return issues


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    httpd, base = start_server()
    all_issues: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            desk = browser.new_page()
            all_issues += audit_viewport(desk, base, "desktop", 1440, 900)
            mob = browser.new_page()
            all_issues += audit_viewport(mob, base, "mobile", 390, 844)
            browser.close()
    finally:
        httpd.shutdown()

    if all_issues:
        print("ISSUES:")
        for i in all_issues:
            print(" -", i)
        raise SystemExit(1)
    print("PHARMA_DECK_AUDIT_PASSED")
    print(f"screenshots: {OUT}")


if __name__ == "__main__":
    main()
