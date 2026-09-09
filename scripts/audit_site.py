#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Mapping, Optional, Set
from urllib.parse import urljoin, urlparse

BASE_URL = "https://heartwisecompare.com"
REQUIRED_AFFILIATE_REL = {"sponsored", "nofollow", "noopener", "noreferrer"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_count = 0
        self.h1_count = 0
        self.description_count = 0
        self.canonicals: List[str] = []
        self.robots: List[str] = []
        self.references: List[Dict[str, str]] = []
        self.affiliate_links: List[Dict[str, str]] = []
        self.json_ld: List[str] = []
        self._in_json_ld = False
        self._json_chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        values = {str(key).lower(): str(value or "") for key, value in attrs}
        if tag == "title":
            self.title_count += 1
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and values.get("name", "").lower() == "description":
            self.description_count += 1
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots.append(values.get("content", ""))
        if tag == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonicals.append(values.get("href", ""))
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_chunks = []
        for attr in ("href", "src"):
            if values.get(attr):
                self.references.append({"tag": tag, "url": values[attr], "rel": values.get("rel", "")})
        href = values.get("href", "")
        if tag == "a" and "hop.clickbank.net" in urlparse(href).netloc.lower():
            self.affiliate_links.append({"url": href, "rel": values.get("rel", "")})

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_chunks).strip())
            self._in_json_ld = False
            self._json_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_chunks.append(data)


def route_for(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    if relative == Path("index.html"):
        return "/"
    if relative.name == "index.html":
        return "/" + relative.parent.as_posix().strip("/") + "/"
    return "/" + relative.as_posix()


def local_target(raw_url: str, source: Path, root: Path) -> Optional[Path]:
    if raw_url.startswith(("mailto:", "tel:", "javascript:", "data:", "#")):
        return None
    parsed = urlparse(raw_url)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc.lower() not in {"heartwisecompare.com", "www.heartwisecompare.com"}:
        return None
    path = parsed.path
    if not path:
        return None
    candidate = (root / path.lstrip("/")).resolve() if path.startswith("/") or parsed.netloc else (source.parent / path).resolve()
    if str(candidate).endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def sitemap_routes(root: Path) -> Set[str]:
    tree = ET.parse(root / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    routes = set()
    for node in tree.findall("s:url/s:loc", namespace):
        if node.text:
            routes.add(urlparse(node.text.strip()).path or "/")
    return routes


def audit_site(root: Path, min_inbound: int = 2) -> Dict[str, Any]:
    root = Path(root).resolve()
    pages: Dict[Path, PageParser] = {}
    indexable: Dict[Path, PageParser] = {}
    for path in sorted(root.rglob("*.html")):
        if any(part in {".git", "tests", "templates"} for part in path.relative_to(root).parts):
            continue
        parsed = parse_page(path)
        pages[path] = parsed
        if not any("noindex" in value.lower() for value in parsed.robots):
            indexable[path] = parsed

    broken: List[Dict[str, str]] = []
    seo_errors: List[Dict[str, str]] = []
    affiliate_errors: List[Dict[str, str]] = []
    inbound: DefaultDict[str, Set[str]] = defaultdict(set)
    route_to_path = {route_for(path, root): path for path in indexable}

    for path, parsed in indexable.items():
        source_route = route_for(path, root)
        expected_canonical = BASE_URL + source_route
        counts = {
            "title": parsed.title_count,
            "h1": parsed.h1_count,
            "description": parsed.description_count,
            "canonical": len(parsed.canonicals),
        }
        for field, count in counts.items():
            if count != 1:
                seo_errors.append({"source": source_route, "issue": f"expected one {field}, found {count}"})
        if len(parsed.canonicals) == 1 and parsed.canonicals[0] != expected_canonical:
            seo_errors.append({"source": source_route, "issue": f"canonical mismatch: {parsed.canonicals[0]}"})
        for raw in parsed.json_ld:
            try:
                json.loads(raw)
            except json.JSONDecodeError:
                seo_errors.append({"source": source_route, "issue": "invalid JSON-LD"})
        if not parsed.json_ld:
            seo_errors.append({"source": source_route, "issue": "missing JSON-LD"})
        for affiliate in parsed.affiliate_links:
            rel = set(affiliate["rel"].lower().split())
            missing = sorted(REQUIRED_AFFILIATE_REL - rel)
            if missing:
                affiliate_errors.append({"source": source_route, "url": affiliate["url"], "missing": " ".join(missing)})
        for reference in parsed.references:
            target = local_target(reference["url"], path, root)
            if target is None:
                continue
            target_route = route_for(target, root) if target.name == "index.html" else "/" + target.relative_to(root).as_posix()
            if not target.exists():
                broken.append({"source": source_route, "url": reference["url"], "resolved": target_route})
                continue
            if target.name == "index.html" and target in indexable and target_route != source_route:
                inbound[target_route].add(source_route)

    sitemap = sitemap_routes(root)
    indexable_routes = set(route_to_path)
    missing_from_sitemap = sorted(indexable_routes - sitemap)
    extra_in_sitemap = sorted(sitemap - indexable_routes)
    weak_inbound = []
    for route in sorted(indexable_routes - {"/", "/about/"}):
        count = len(inbound[route])
        if count < min_inbound:
            weak_inbound.append({"route": route, "count": count, "minimum": min_inbound})

    report: Dict[str, Any] = {
        "html_files": len(pages),
        "indexable_routes": len(indexable_routes),
        "broken_internal_links_or_assets": broken,
        "seo_structure_errors": seo_errors,
        "affiliate_rel_errors": affiliate_errors,
        "missing_from_sitemap": missing_from_sitemap,
        "extra_in_sitemap": extra_in_sitemap,
        "weak_inbound_routes": weak_inbound,
        "inbound_counts": {route: len(inbound[route]) for route in sorted(indexable_routes)},
    }
    report["ok"] = not any((broken, seo_errors, affiliate_errors, missing_from_sitemap, extra_in_sitemap, weak_inbound))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Heartwise static SEO, links, assets, sitemap coverage, and affiliate attributes.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--min-inbound", type=int, default=2)
    args = parser.parse_args()
    report = audit_site(args.root, args.min_inbound)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
