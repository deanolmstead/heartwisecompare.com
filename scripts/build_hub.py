#!/usr/bin/env python3
"""Build a Heartwise Compare hub (topic guide) page from data/hubs/<slug>.json.

Usage:
    python3 scripts/build_hub.py data/hubs/<slug>.json [--check]

Builds <slug>/index.html from templates/hub.html and upserts the sitemap entry.
Homepage hub cards are hand-maintained (see index.html #guides section).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from string import Template
from typing import Any, Dict, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page_factory import (  # noqa: E402
    BASE_URL,
    _upsert_sitemap,
    display_date,
    esc,
    json_script,
)

ROOT = Path(__file__).resolve().parents[1]
HUB_TEMPLATE_PATH = ROOT / "templates" / "hub.html"
REQUIRED_TOP_LEVEL = {
    "slug", "audience", "published", "modified", "title", "seo_title", "description",
    "eyebrow", "h1", "dek", "hero_image", "hero_alt", "verdict",
    "products", "methodology", "faqs", "related",
}
REQUIRED_PRODUCT = {
    "name", "creator", "format", "best_for", "affiliate_url",
    "summary", "facts", "vs_slug", "vs_title",
}


def validate_hub(data: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing:
        raise ValueError(f"missing hub fields: {', '.join(missing)}")
    if data["audience"].strip().lower() != "women":
        raise ValueError("Heartwise hub pages must target women")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
        raise ValueError("slug must be lowercase kebab-case")
    date.fromisoformat(data["published"])
    date.fromisoformat(data["modified"])
    if len(data["seo_title"]) > 60:
        raise ValueError(f"seo_title too long ({len(data['seo_title'])} chars, max 60)")
    if len(data["description"]) > 160:
        raise ValueError(f"description too long ({len(data['description'])} chars, max 160)")
    if len(data["products"]) < 3:
        raise ValueError("at least three ranked products are required")
    names = set()
    for index, product in enumerate(data["products"], 1):
        product_missing = sorted(REQUIRED_PRODUCT - set(product))
        if product_missing:
            raise ValueError(f"product {index} missing fields: {', '.join(product_missing)}")
        key = product["name"].strip().lower()
        if key in names:
            raise ValueError(f"duplicate product: {product['name']}")
        names.add(key)
        if "hop.clickbank.net" not in product["affiliate_url"]:
            raise ValueError(f"product {index} affiliate_url must be a generated ClickBank HopLink")
        if not product["facts"]:
            raise ValueError(f"product {index} needs at least one package fact")
    if len(data["methodology"]) < 2:
        raise ValueError("at least two methodology cards are required")
    if len(data["faqs"]) < 2:
        raise ValueError("at least two FAQs are required")
    if len(data["related"]) < 2:
        raise ValueError("at least two related comparisons are required")


def render_ranked_card(rank: int, product: Mapping[str, Any]) -> str:
    facts = "".join(f"<li>{esc(item)}</li>" for item in product["facts"])
    return (
        f'<article class="product-card"><div>'
        f'<span class="rank-num" aria-hidden="true">{rank}</span>'
        f'<div class="kicker">Best for: {esc(product["best_for"])}</div>'
        f'<h3>{esc(product["name"])}</h3>'
        f'<p>{esc(product["summary"])}</p><p><strong>By:</strong> {esc(product["creator"])}</p>'
        f'<h4>Package highlights</h4><ul>{facts}</ul></div>'
        f'<div class="hub-card-actions">'
        f'<a class="button primary" href="{esc(product["affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">See {esc(product["name"])} <span aria-hidden="true">↗</span></a>'
        f'<a class="button secondary" href="../{esc(product["vs_slug"])}/">Read the comparison <span aria-hidden="true">→</span></a>'
        f'</div></article>'
    )


def render_hub(data: Mapping[str, Any], template_path: Path | None = None) -> str:
    validate_hub(data)
    canonical = f"{BASE_URL}/{data['slug']}/"
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": data["title"],
        "description": data["description"],
        "datePublished": data["published"],
        "dateModified": data["modified"],
        "mainEntityOfPage": canonical,
        "author": {"@type": "Person", "name": "Jordan Wells"},
        "publisher": {"@type": "Organization", "name": "Heartwise Compare", "url": f"{BASE_URL}/"},
        "image": f"{BASE_URL}/{data['slug']}/{data['hero_image']}",
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{BASE_URL}/#guides"},
            {"@type": "ListItem", "position": 3, "name": data["title"], "item": canonical},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": item["question"], "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}}
            for item in data["faqs"]
        ],
    }
    top_two = data["products"][:2]
    hero_actions = (
        f'<a class="button primary" href="{esc(top_two[0]["affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">See the top pick: {esc(top_two[0]["name"])} <span aria-hidden="true">↗</span></a>'
        f'<a class="button secondary" href="#ranking-title">Compare all {len(data["products"])} <span aria-hidden="true">↓</span></a>'
    )
    ranked_cards = "".join(render_ranked_card(rank, product) for rank, product in enumerate(data["products"], 1))
    table_rows = "".join(
        f'<tr><th scope="row">{rank}</th><td><a href="../{esc(product["vs_slug"])}/">{esc(product["name"])}</a></td>'
        f'<td>{esc(product["best_for"])}</td><td>{esc(product["format"])}</td></tr>'
        for rank, product in enumerate(data["products"], 1)
    )
    methodology_cards = "".join(
        f'<article class="card decision-card"><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></article>'
        for item in data["methodology"]
    )
    related_cards = "".join(
        f'<article class="card"><h3><a href="../{esc(item["slug"])}/">{esc(item["title"])}</a></h3><p>{esc(item["description"])}</p></article>'
        for item in data["related"]
    )
    faqs = "".join(
        f'<details class="faq-item"{" open" if index == 0 else ""}><summary>{esc(item["question"])}</summary><div class="faq-body"><p>{esc(item["answer"])}</p></div></details>'
        for index, item in enumerate(data["faqs"])
    )
    final_actions = "".join(
        f'<a class="button primary" href="{esc(product["affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">See {esc(product["name"])} <span aria-hidden="true">↗</span></a>'
        for product in top_two
    )
    values = {
        "SEO_TITLE": esc(data["seo_title"]), "DESCRIPTION": esc(data["description"]), "CANONICAL": canonical,
        "OG_IMAGE": f"{BASE_URL}/{esc(data['slug'])}/{esc(data['hero_image'])}",
        "SCHEMAS": "\n".join((json_script(article), json_script(breadcrumb), json_script(faq))),
        "TITLE": esc(data["title"]), "EYEBROW": esc(data["eyebrow"]), "H1": esc(data["h1"]), "DEK": esc(data["dek"]),
        "PUBLISHED": esc(data["published"]), "PUBLISHED_DISPLAY": display_date(data["published"]),
        "MODIFIED": esc(data["modified"]), "MODIFIED_DISPLAY": display_date(data["modified"]),
        "HERO_ACTIONS": hero_actions, "HERO_IMAGE": esc(data["hero_image"]), "HERO_ALT": esc(data["hero_alt"]),
        "VERDICT": esc(data["verdict"]), "RANKED_CARDS": ranked_cards, "TABLE_ROWS": table_rows,
        "METHODOLOGY_CARDS": methodology_cards, "RELATED_CARDS": related_cards, "FAQS": faqs,
        "FINAL_ACTIONS": final_actions,
    }
    template = (template_path or HUB_TEMPLATE_PATH).read_text(encoding="utf-8")
    return Template(template).substitute(values)


def build_hub(root: Path, data: Mapping[str, Any], check: bool = False) -> bool:
    validate_hub(data)
    root = Path(root)
    output = root / data["slug"] / "index.html"
    hero = root / data["slug"] / data["hero_image"]
    if not hero.exists():
        raise ValueError(f"hero image missing: {hero}")
    desired: Dict[Path, str] = {output: render_hub(data, root / "templates" / "hub.html" if (root / "templates" / "hub.html").exists() else HUB_TEMPLATE_PATH)}
    sitemap_path = root / "sitemap.xml"
    desired[sitemap_path] = _upsert_sitemap(sitemap_path.read_text(encoding="utf-8"), data)
    changed = any(not path.exists() or path.read_text(encoding="utf-8") != content for path, content in desired.items())
    if check:
        return changed
    for path, content in desired.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return changed


def load_hub_data(path: Path) -> Dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    validate_hub(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Heartwise hub page from its JSON data.")
    parser.add_argument("json_path", type=Path)
    parser.add_argument("--check", action="store_true", help="exit 1 if the built page or sitemap would change")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    data = load_hub_data(args.json_path)
    changed = build_hub(args.root, data, check=args.check)
    if args.check:
        print("DRIFT" if changed else "CLEAN")
        return 1 if changed else 0
    print("built" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
