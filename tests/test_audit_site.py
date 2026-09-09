import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_site import audit_site


class AuditSiteTests(unittest.TestCase):
    def valid_page(self, title, canonical, body, robots="index,follow"):
        return f'''<!doctype html><html><head><title>{title}</title><meta name="description" content="Useful description"><meta name="robots" content="{robots}"><link rel="canonical" href="{canonical}"><script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article"}}</script></head><body><h1>{title}</h1>{body}</body></html>'''

    def make_valid_site(self, root: Path):
        (root / "about").mkdir(parents=True)
        (root / "alpha").mkdir()
        (root / "beta").mkdir()
        (root / "favicon.png").write_bytes(b"png")
        (root / "index.html").write_text(self.valid_page("Home", "https://heartwisecompare.com/", '<a href="about/">About</a><a href="alpha/">Alpha</a><a href="beta/">Beta</a>'), encoding="utf-8")
        (root / "about" / "index.html").write_text(self.valid_page("About", "https://heartwisecompare.com/about/", '<a href="../">Home</a><a href="../alpha/">Alpha</a><a href="../beta/">Beta</a>'), encoding="utf-8")
        (root / "alpha" / "index.html").write_text(self.valid_page("Alpha", "https://heartwisecompare.com/alpha/", '<a href="../">Home</a><a href="../about/">About</a><a href="../beta/">Beta</a><a href="https://abc.hop.clickbank.net" rel="sponsored nofollow noopener noreferrer">Buy</a>'), encoding="utf-8")
        (root / "beta" / "index.html").write_text(self.valid_page("Beta", "https://heartwisecompare.com/beta/", '<a href="../">Home</a><a href="../about/">About</a><a href="../alpha/">Alpha</a>'), encoding="utf-8")
        (root / "sitemap.xml").write_text('''<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://heartwisecompare.com/</loc></url><url><loc>https://heartwisecompare.com/about/</loc></url><url><loc>https://heartwisecompare.com/alpha/</loc></url><url><loc>https://heartwisecompare.com/beta/</loc></url></urlset>''', encoding="utf-8")

    def test_valid_site_passes_all_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_valid_site(root)
            report = audit_site(root, min_inbound=2)
            self.assertTrue(report["ok"], report)
            self.assertEqual(report["broken_internal_links_or_assets"], [])
            self.assertEqual(report["seo_structure_errors"], [])
            self.assertEqual(report["affiliate_rel_errors"], [])
            self.assertEqual(report["missing_from_sitemap"], [])
            self.assertEqual(report["weak_inbound_routes"], [])

    def test_broken_link_and_sitemap_mismatch_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_valid_site(root)
            alpha = root / "alpha" / "index.html"
            alpha.write_text(alpha.read_text(encoding="utf-8").replace('../beta/', '../missing/'), encoding="utf-8")
            sitemap = root / "sitemap.xml"
            sitemap.write_text(sitemap.read_text(encoding="utf-8").replace('<url><loc>https://heartwisecompare.com/beta/</loc></url>', ''), encoding="utf-8")
            report = audit_site(root, min_inbound=1)
            self.assertFalse(report["ok"])
            self.assertTrue(report["broken_internal_links_or_assets"])
            self.assertIn("/beta/", report["missing_from_sitemap"])

    def test_malformed_json_ld_and_unsafe_affiliate_rel_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_valid_site(root)
            alpha = root / "alpha" / "index.html"
            html = alpha.read_text(encoding="utf-8").replace('{"@context":"https://schema.org","@type":"Article"}', '{broken').replace('rel="sponsored nofollow noopener noreferrer"', 'rel="nofollow"')
            alpha.write_text(html, encoding="utf-8")
            report = audit_site(root, min_inbound=1)
            self.assertFalse(report["ok"])
            self.assertTrue(any(item["issue"] == "invalid JSON-LD" for item in report["seo_structure_errors"]))
            self.assertTrue(report["affiliate_rel_errors"])


if __name__ == "__main__":
    unittest.main()
