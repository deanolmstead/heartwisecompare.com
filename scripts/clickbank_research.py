#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping
from urllib.parse import urlparse

DEFAULT_ENDPOINT = "http://127.0.0.1:9223"
MARKETPLACE_FRAGMENT = "/master/dashboard/affiliate-marketplace"
WOMEN_MARKERS = ("for women", "women's list", "women’s list", "women-focused", "female audience", "woman men adore")
MEN_MARKERS = ("for men", "men's traffic", "men’s traffic", "male offer", "male audience")
MIXED_MARKERS = ("for men and women", "for women and men", "men / women", "men and women", "women and men")
DEFAULT_CATEGORIES = frozenset({"Self-Help/Dating Guides", "Self-Help/Marriage & Relationships"})


def classify_audience(title: str, description: str) -> str:
    text = f"{title} {description}".casefold()
    if any(marker in text for marker in MIXED_MARKERS):
        return "mixed"
    if any(marker in text for marker in WOMEN_MARKERS):
        return "women"
    if any(marker in text for marker in MEN_MARKERS):
        return "men"
    return "unknown"


def _product_name_variants(title: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", title).strip().casefold()
    if not normalized:
        return []
    variants = {normalized, re.split(r"\s+by\s+", normalized, maxsplit=1)[0]}
    marketing = {"affiliate", "commission", "converter", "high", "lists", "new", "offer", "program"}
    for segment in re.split(r"\s+(?:-|\|)\s+", normalized):
        words = set(re.findall(r"[a-z0-9']+", segment))
        if len(words) >= 2 and not (words & marketing):
            variants.add(segment)
    return sorted((variant for variant in variants if len(variant) >= 8), key=len, reverse=True)


def product_is_already_used(root: Path, title: str) -> bool:
    variants = _product_name_variants(title)
    if not variants:
        return False
    for path in Path(root).rglob("*.html"):
        if any(part in {".git", "tests", "templates"} for part in path.parts):
            continue
        content = re.sub(r"\s+", " ", path.read_text(encoding="utf-8", errors="ignore")).casefold()
        if any(variant in content for variant in variants):
            return True
    return False


def filter_candidates(
    candidates: Iterable[Mapping[str, Any]],
    root: Path,
    audience: str = "women",
    allowed_categories: Iterable[str] = DEFAULT_CATEGORIES,
) -> List[Dict[str, Any]]:
    result = []
    seen = set()
    allowed = set(allowed_categories)
    for raw in candidates:
        title = str(raw.get("title", "")).strip()
        if not title or title.casefold() in seen:
            continue
        if classify_audience(title, str(raw.get("description", ""))) != audience:
            continue
        if str(raw.get("category", "")) not in allowed:
            continue
        if bool(raw.get("approval_required")) or not raw.get("sales_url"):
            continue
        if product_is_already_used(root, title):
            continue
        seen.add(title.casefold())
        result.append({
            "title": title,
            "category": str(raw.get("category", "")),
            "description": str(raw.get("description", "")),
            "approval_required": False,
            "sales_url": str(raw.get("sales_url", "")),
            "affiliate_page_url": str(raw.get("affiliate_page_url", "")),
            "audience": audience,
        })
    return result


def choose_offer_button_index(title: str, card_texts: Iterable[str]) -> int:
    needle = re.sub(r"\s+", " ", title).strip().casefold()
    matches = [
        (index, len(text))
        for index, text in enumerate(card_texts)
        if needle and needle in re.sub(r"\s+", " ", text).casefold()
    ]
    if not matches:
        raise ValueError(f"offer not found: {title}")
    return min(matches, key=lambda item: item[1])[0]


def _marketplace_page(browser: Any) -> Any:
    pages = [page for context in browser.contexts for page in context.pages]
    for page in pages:
        if MARKETPLACE_FRAGMENT in page.url:
            return page
    for page in pages:
        if "accounts.clickbank.com/master/dashboard" in page.url:
            page.goto(
                "https://accounts.clickbank.com/master/dashboard/affiliate-marketplace",
                wait_until="domcontentloaded",
            )
            return page
    raise RuntimeError(
        "authenticated ClickBank dashboard/Marketplace tab not found; sign in to the dedicated CDP profile first"
    )


def _extract_visible_cards(page: Any) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    buttons = page.get_by_text("Get Affiliate Link", exact=True)
    for index in range(buttons.count()):
        button = buttons.nth(index)
        chosen = None
        for level in range(2, 8):
            ancestor = button.locator("xpath=" + "/.." * level)
            try:
                text = ancestor.inner_text(timeout=1500)
            except Exception:
                continue
            if "View Sales Page" in text and "Description" in text and len(text) < 3000:
                chosen = ancestor
                break
        if chosen is None:
            continue
        text = chosen.inner_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title = lines[0] if lines else ""
        category = next((line for line in lines[1:5] if "/" in line), "")
        description = ""
        if "Description" in lines:
            start = lines.index("Description") + 1
            end = lines.index("Get Affiliate Link") if "Get Affiliate Link" in lines else len(lines)
            description = " ".join(lines[start:end])
        links = {item["text"].strip(): item["href"] for item in chosen.locator("a").evaluate_all("els => els.map(a => ({text:a.innerText,href:a.href}))")}
        cards.append({
            "title": title,
            "category": category,
            "description": description,
            "approval_required": "Approval Required" in text,
            "affiliate_page_url": links.get("View Affiliate Page", ""),
            "sales_url": links.get("View Sales Page", ""),
        })
    return cards


def discover(endpoint: str, query: str, root: Path, audience: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Playwright is required for authenticated ClickBank discovery") from exc
    collected: List[Dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(endpoint)
        page = _marketplace_page(browser)
        search = page.locator('input[role="combobox"]').first
        search.fill(query)
        search.press("Enter")
        page.wait_for_timeout(2200)
        for _ in range(max_pages):
            collected.extend(_extract_visible_cards(page))
            next_button = page.get_by_label("Go to next page")
            if not next_button.count() or next_button.first.is_disabled():
                break
            next_button.first.click()
            page.wait_for_timeout(1800)
    return filter_candidates(collected, root, audience)


def generate_link(endpoint: str, title: str, affiliate_nickname: str, private_output: Path) -> Dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Playwright is required for ClickBank link generation") from exc
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(endpoint)
        page = _marketplace_page(browser)
        while page.locator('[role="dialog"]').count():
            page.locator('[role="dialog"]').last.locator('button[aria-label="close"]').first.click()
        search = page.locator('input[role="combobox"]').first
        search.fill(title)
        search.press("Enter")
        page.wait_for_timeout(1800)
        buttons = page.get_by_text("Get Affiliate Link", exact=True)
        cards = []
        card_texts = []
        for index in range(buttons.count()):
            button = buttons.nth(index)
            chosen = None
            chosen_text = ""
            for level in range(2, 8):
                candidate = button.locator("xpath=" + "/.." * level)
                try:
                    text = candidate.inner_text(timeout=1200)
                except Exception:
                    continue
                if "Description" in text and "Get Affiliate Link" in text and "View Sales Page" in text:
                    chosen = candidate
                    chosen_text = text
                    break
            if chosen is not None:
                cards.append((button, chosen))
                card_texts.append(chosen_text)
        if not cards:
            raise RuntimeError("offer card controls not found")
        try:
            match_index = choose_offer_button_index(title, card_texts)
        except ValueError as exc:
            raise RuntimeError(str(exc)) from exc
        button, card = cards[match_index]
        if "Approval Required" in card_texts[match_index]:
            raise RuntimeError("offer requires approval; no link was generated")
        button.click()
        dialog = page.locator('[role="dialog"]').last
        dialog.locator("input").first.fill(affiliate_nickname)
        page.wait_for_timeout(500)
        option = page.get_by_role("option", name=affiliate_nickname, exact=True)
        try:
            option.wait_for(state="visible", timeout=5000)
        except Exception:
            raise RuntimeError("affiliate nickname was not offered by ClickBank")
        option.click()
        dialog.locator('button:has-text("Continue")').click(force=True)
        page.wait_for_timeout(900)
        dialog.locator('button:has-text("Copy")').last.click()
        page.context.grant_permissions(["clipboard-read", "clipboard-write"], origin="https://accounts.clickbank.com")
        link = page.evaluate("navigator.clipboard.readText()")
        if "hop.clickbank.net" not in urlparse(link).netloc:
            raise RuntimeError("ClickBank did not return an encrypted HopLink")
        private_output = Path(private_output)
        private_output.parent.mkdir(parents=True, exist_ok=True)
        private_output.write_text(link + "\n", encoding="utf-8")
        os.chmod(private_output, 0o600)
        verifier = page.context.new_page()
        response = verifier.goto(link, wait_until="domcontentloaded", timeout=30000)
        result = {
            "title": title,
            "status": response.status if response else None,
            "final_host": urlparse(verifier.url).netloc,
            "final_path": urlparse(verifier.url).path,
            "page_title": verifier.title(),
            "private_output": str(private_output),
        }
        verifier.close()
        dialog.locator('button[aria-label="close"]').first.click()
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover new ClickBank offers in Dean's authenticated CDP profile without exposing account data.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--query", default="women")
    parser.add_argument("--audience", choices=("women", "men"), default="women")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--generate-link", metavar="EXACT_TITLE")
    parser.add_argument("--affiliate-nickname")
    parser.add_argument("--private-output", type=Path)
    args = parser.parse_args()

    if args.generate_link:
        if not args.affiliate_nickname or not args.private_output:
            parser.error("--generate-link requires --affiliate-nickname and --private-output")
        result: Any = generate_link(args.endpoint, args.generate_link, args.affiliate_nickname, args.private_output)
    else:
        result = discover(args.endpoint, args.query, args.root, args.audience, args.max_pages)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
