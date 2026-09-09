from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from datetime import date
from pathlib import Path
from string import Template
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Tuple

BASE_URL = "https://heartwisecompare.com"
ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "templates" / "comparison.html"
REQUIRED_TOP_LEVEL = {
    "slug", "audience", "published", "modified", "title", "seo_title", "description",
    "eyebrow", "h1", "dek", "hero_image", "hero_alt", "verdict", "products",
    "decision_cards", "buyer_checks", "faqs", "related",
}
REQUIRED_PRODUCT = {
    "name", "creator", "price", "format", "best_for", "checkout", "guarantee",
    "affiliate_url", "official_url", "official_label", "summary", "features", "limits",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def validate_comparison(data: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL - set(data))
    if missing:
        raise ValueError(f"missing comparison fields: {', '.join(missing)}")
    if data["audience"].strip().lower() != "women":
        raise ValueError("Heartwise page-factory comparisons must target women")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
        raise ValueError("slug must be lowercase kebab-case")
    date.fromisoformat(data["published"])
    date.fromisoformat(data["modified"])
    if len(data["products"]) != 2:
        raise ValueError("exactly two products are required")
    names = []
    for index, product in enumerate(data["products"], 1):
        product_missing = sorted(REQUIRED_PRODUCT - set(product))
        if product_missing:
            raise ValueError(f"product {index} missing fields: {', '.join(product_missing)}")
        names.append(product["name"].strip().lower())
        if "hop.clickbank.net" not in product["affiliate_url"]:
            raise ValueError(f"product {index} affiliate_url must be a generated ClickBank HopLink")
        if not product["official_url"].startswith("https://"):
            raise ValueError(f"product {index} official_url must use https")
    if names[0] == names[1]:
        raise ValueError("products must be distinct")
    if len(data["decision_cards"]) < 3:
        raise ValueError("at least three decision cards are required")
    if len(data["faqs"]) < 2:
        raise ValueError("at least two FAQs are required")
    if len(data["related"]) < 2:
        raise ValueError("at least two related comparisons are required")


def json_script(payload: Mapping[str, Any]) -> str:
    return '<script type="application/ld+json">\n' + json.dumps(payload, indent=2, ensure_ascii=False).replace("</", "<\\/") + "\n</script>"


def render_page(data: Mapping[str, Any], template_path: Path | None = None) -> str:
    validate_comparison(data)
    product_a, product_b = data["products"]
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
            {"@type": "ListItem", "position": 2, "name": "Comparisons", "item": f"{BASE_URL}/#recent"},
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
    hero_actions = "".join(
        f'<a class="button primary" href="{esc(product["affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">Visit {esc(product["name"])} <span aria-hidden="true">↗</span></a>'
        for product in data["products"]
    )
    decision_cards = "".join(
        f'<article class="card"><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></article>'
        for item in data["decision_cards"]
    )
    product_headers = "".join(f'<th scope="col">{esc(product["name"])}</th>' for product in data["products"])
    rows = [
        ("Listed price", "price"), ("Format", "format"), ("Best fit", "best_for"),
        ("Checkout note", "checkout"), ("Refund language", "guarantee"),
    ]
    comparison_rows = "".join(
        f'<tr><th scope="row">{esc(label)}</th>' + "".join(f'<td>{esc(product[key])}</td>' for product in data["products"]) + "</tr>"
        for label, key in rows
    )
    product_cards = "".join(render_product_card(product) for product in data["products"])
    buyer_checks = "".join(f'<div class="check-item"><span aria-hidden="true">✓</span><p>{esc(item)}</p></div>' for item in data["buyer_checks"])
    source_cards = "".join(
        f'<article class="product-card"><div><div class="kicker">{esc(product["name"])}</div><h3>{esc(product["official_label"])}</h3><p>Confirm the current package, price, and checkout terms directly with the seller.</p></div><a class="button secondary" href="{esc(product["official_url"])}" target="_blank" rel="noopener noreferrer">Open official source <span aria-hidden="true">↗</span></a></article>'
        for product in data["products"]
    )
    related_cards = "".join(
        f'<article class="card"><h3><a href="../{esc(item["slug"])}/">{esc(item["title"])}</a></h3><p>{esc(item["description"])}</p></article>'
        for item in data["related"]
    )
    faqs = "".join(
        f'<details class="faq-item"><summary>{esc(item["question"])}<span aria-hidden="true">+</span></summary><div class="faq-body"><p>{esc(item["answer"])}</p></div></details>'
        for item in data["faqs"]
    )
    values = {
        "SEO_TITLE": esc(data["seo_title"]), "DESCRIPTION": esc(data["description"]), "CANONICAL": canonical,
        "OG_IMAGE": f"{BASE_URL}/{esc(data['slug'])}/{esc(data['hero_image'])}",
        "SCHEMAS": "\n".join((json_script(article), json_script(breadcrumb), json_script(faq))),
        "TITLE": esc(data["title"]), "EYEBROW": esc(data["eyebrow"]), "H1": esc(data["h1"]), "DEK": esc(data["dek"]),
        "PUBLISHED": esc(data["published"]), "PUBLISHED_DISPLAY": display_date(data["published"]),
        "MODIFIED": esc(data["modified"]), "MODIFIED_DISPLAY": display_date(data["modified"]),
        "HERO_ACTIONS": hero_actions, "HERO_IMAGE": esc(data["hero_image"]), "HERO_ALT": esc(data["hero_alt"]),
        "VERDICT": esc(data["verdict"]), "DECISION_CARDS": decision_cards, "PRODUCT_HEADERS": product_headers,
        "COMPARISON_ROWS": comparison_rows, "PRODUCT_CARDS": product_cards, "BUYER_CHECKS": buyer_checks,
        "SOURCE_CARDS": source_cards, "RELATED_CARDS": related_cards, "FAQS": faqs,
    }
    template = (template_path or TEMPLATE_PATH).read_text(encoding="utf-8")
    return Template(template).substitute(values)


def render_product_card(product: Mapping[str, Any]) -> str:
    features = "".join(f"<li>{esc(item)}</li>" for item in product["features"])
    limits = "".join(f"<li>{esc(item)}</li>" for item in product["limits"])
    return (
        f'<article class="product-card"><div><div class="kicker">{esc(product["format"])}</div><h3>{esc(product["name"])}</h3>'
        f'<p>{esc(product["summary"])}</p><p><strong>By:</strong> {esc(product["creator"])}</p>'
        f'<h4>What the seller lists</h4><ul>{features}</ul><h4>Limits to keep in view</h4><ul>{limits}</ul></div>'
        f'<div class="product-meta"><strong>{esc(product["price"])}</strong><span>{esc(product["checkout"])}</span></div>'
        f'<a class="button primary" href="{esc(product["affiliate_url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">Visit {esc(product["name"])} <span aria-hidden="true">↗</span></a></article>'
    )


def _replace_website_schema(home: str, data: Mapping[str, Any]) -> str:
    pattern = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)
    for match in pattern.finditer(home):
        try:
            payload = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        schema_type = payload.get("@type")
        if schema_type not in {"WebSite", "CollectionPage"}:
            continue
        entry = (
            {
                "@type": "WebPage", "name": data["title"],
                "url": f"{BASE_URL}/{data['slug']}/", "description": data["description"],
                "datePublished": data["published"],
            }
            if schema_type == "WebSite"
            else {"@type": "Article", "url": f"{BASE_URL}/{data['slug']}/", "headline": data["title"]}
        )
        parts = [part for part in payload.get("hasPart", []) if part.get("url") != entry["url"]]
        parts.insert(0, entry)
        payload["hasPart"] = (
            sorted(parts, key=lambda item: item.get("datePublished", ""), reverse=True)
            if schema_type == "WebSite"
            else parts
        )
        replacement = match.group(1) + "\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n" + match.group(3)
        return home[:match.start()] + replacement + home[match.end():]
    raise ValueError("homepage CollectionPage/WebSite JSON-LD not found")


def _upsert_home_row(home: str, data: Mapping[str, Any]) -> str:
    section_match = re.search(r'(<section\b[^>]*id=["\']recent["\'][^>]*>)(.*?)(</section>)', home, re.I | re.S)
    if not section_match:
        raise ValueError("homepage #recent section not found")
    section = section_match.group(2)
    list_match = re.search(r'(<div\b[^>]*class=["\'][^"\']*post-list[^"\']*["\'][^>]*>)(.*)(</div>\s*)$', section, re.I | re.S)
    if not list_match:
        raise ValueError("homepage post-list not found")
    row_pattern = re.compile(r'<a\b[^>]*class=["\'][^"\']*post-row[^"\']*["\'][^>]*>.*?</a>', re.I | re.S)
    rows = row_pattern.findall(list_match.group(2))
    target = f'{data["slug"]}/'
    rows = [row for row in rows if not re.search(rf'href=["\'](?:\./)?{re.escape(target)}["\']', row)]
    row = (
        f'<a class="post-row" href="{esc(data["slug"])}/"><div><time datetime="{esc(data["published"])}">{display_date(data["published"])}</time>'
        f'<h3>{esc(data["title"])}</h3><p>{esc(data["description"])}</p></div><span>Read comparison →</span></a>'
    )
    rows.append(row)

    def row_date(item: str) -> str:
        match = re.search(r'<time\b[^>]*datetime=["\']([^"\']+)', item)
        return match.group(1) if match else ""

    rows.sort(key=row_date, reverse=True)
    body = "\n        " + "\n        ".join(rows) + "\n      "
    new_list = list_match.group(1) + body + list_match.group(3)
    new_section = section[:list_match.start()] + new_list + section[list_match.end():]
    return home[:section_match.start(2)] + new_section + home[section_match.end(2):]


def _upsert_about(about: str, data: Mapping[str, Any]) -> str:
    section_match = re.search(r'<section\b[^>]*aria-labelledby=["\']links-title["\'][^>]*>.*?</section>', about, re.I | re.S)
    if not section_match:
        raise ValueError("About comparison library not found")
    section = section_match.group(0)
    grid_match = re.search(r'(<div\b[^>]*class=["\'][^"\']*card-grid[^"\']*["\'][^>]*>)(.*)(</div>\s*</section>)', section, re.I | re.S)
    if not grid_match:
        raise ValueError("About comparison card grid not found")
    card_pattern = re.compile(r'<article\b[^>]*class=["\'][^"\']*card[^"\']*["\'][^>]*>.*?</article>', re.I | re.S)
    cards = card_pattern.findall(grid_match.group(2))
    needle = f'../{data["slug"]}/'
    cards = [card for card in cards if needle not in card]
    cards.insert(0, f'<article class="card"><h3><a href="{needle}">{esc(data["title"])}</a></h3><p>{esc(data["description"])}</p></article>')
    new_section = section[:grid_match.start(2)] + "".join(cards) + section[grid_match.end(2):]
    return about[:section_match.start()] + new_section + about[section_match.end():]


def _upsert_related(page: str, data: Mapping[str, Any]) -> str:
    if f'../{data["slug"]}/' in page:
        return page
    section_match = re.search(r'<section\b[^>]*aria-labelledby=["\']related-title["\'][^>]*>.*?</section>', page, re.I | re.S)
    if not section_match:
        raise ValueError("related-comparison section not found")
    section = section_match.group(0)
    grid_match = re.search(r'(<div\b[^>]*class=["\'][^"\']*card-grid[^"\']*["\'][^>]*>)(.*)(</div>\s*</section>)', section, re.I | re.S)
    if not grid_match:
        raise ValueError("related card grid not found")
    card = f'<article class="card"><h3><a href="../{esc(data["slug"])}/">{esc(data["title"])}</a></h3><p>{esc(data["description"])}</p></article>'
    new_section = section[:grid_match.end(1)] + grid_match.group(2) + card + section[grid_match.start(3):]
    return page[:section_match.start()] + new_section + page[section_match.end():]


def _upsert_sitemap(xml: str, data: Mapping[str, Any]) -> str:
    url = f"{BASE_URL}/{data['slug']}/"
    block = f"  <url><loc>{url}</loc><lastmod>{data['modified']}</lastmod></url>"
    existing = re.compile(rf'[ \t]*<url><loc>{re.escape(url)}</loc><lastmod>[^<]+</lastmod></url>')
    if existing.search(xml):
        return existing.sub(block, xml, count=1)
    separator = "" if xml[:xml.index("</urlset>")].endswith("\n") else "\n"
    return xml.replace("</urlset>", separator + block + "\n</urlset>")


def build_comparison(root: Path, data: Mapping[str, Any], check: bool = False) -> bool:
    validate_comparison(data)
    root = Path(root)
    output = root / data["slug"] / "index.html"
    hero = root / data["slug"] / data["hero_image"]
    if not hero.exists():
        raise ValueError(f"hero image missing: {hero}")
    desired: Dict[Path, str] = {output: render_page(data, root / "templates" / "comparison.html" if (root / "templates" / "comparison.html").exists() else TEMPLATE_PATH)}
    home_path = root / "index.html"
    home = home_path.read_text(encoding="utf-8")
    desired[home_path] = _upsert_home_row(_replace_website_schema(home, data), data)
    about_path = root / "about" / "index.html"
    desired[about_path] = _upsert_about(about_path.read_text(encoding="utf-8"), data)
    sitemap_path = root / "sitemap.xml"
    desired[sitemap_path] = _upsert_sitemap(sitemap_path.read_text(encoding="utf-8"), data)
    for related in data["related"]:
        path = root / related["slug"] / "index.html"
        if not path.exists():
            raise ValueError(f"related page missing: {related['slug']}")
        desired[path] = _upsert_related(path.read_text(encoding="utf-8"), data)
    changed = any(not path.exists() or path.read_text(encoding="utf-8") != content for path, content in desired.items())
    if check:
        return changed
    for path, content in desired.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return changed


def load_data(path: Path) -> Dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    validate_comparison(data)
    return data
