import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.page_factory import build_comparison, render_page, validate_comparison


class PageFactoryTests(unittest.TestCase):
    def sample(self):
        return {
            "slug": "alpha-vs-beta",
            "audience": "women",
            "published": "2026-09-08",
            "modified": "2026-09-08",
            "title": "Alpha vs Beta",
            "seo_title": "Alpha vs Beta | Heartwise Compare",
            "description": "A practical comparison of Alpha and Beta for women.",
            "eyebrow": "Women-focused relationship guides",
            "h1": "A workbook vs a video course.",
            "dek": "Choose the learning format that fits your situation.",
            "hero_image": "images/hero.png",
            "hero_alt": "A woman comparing two relationship guides",
            "verdict": "Start with Alpha for structured reflection; choose Beta for guided lessons.",
            "products": [
                {
                    "name": "Alpha",
                    "creator": "Author A",
                    "price": "$47",
                    "format": "Five-module workbook",
                    "best_for": "Structured reflection",
                    "checkout": "Optional club renews monthly unless declined.",
                    "guarantee": "Seller states 60 days.",
                    "affiliate_url": "https://alpha.example.hop.clickbank.net",
                    "official_url": "https://alpha.example/product",
                    "official_label": "Official Alpha presentation",
                    "summary": "A sequenced written framework.",
                    "features": ["Five modules", "Written exercises"],
                    "limits": ["Seller claims are not guaranteed outcomes."],
                },
                {
                    "name": "Beta",
                    "creator": "Author B",
                    "price": "$49",
                    "format": "Video, audio, and ebook",
                    "best_for": "Multimedia learning",
                    "checkout": "Optional series renews monthly unless declined.",
                    "guarantee": "Seller states 60 days.",
                    "affiliate_url": "https://beta.example.hop.clickbank.net",
                    "official_url": "https://beta.example/product",
                    "official_label": "Official Beta presentation",
                    "summary": "A multimedia lesson package.",
                    "features": ["Video lessons", "Audio files"],
                    "limits": ["Scripts cannot control another person's response."],
                },
            ],
            "decision_cards": [
                {"title": "Choose Alpha when", "body": "You prefer a workbook."},
                {"title": "Choose Beta when", "body": "You prefer multimedia."},
                {"title": "Pause when", "body": "You expect guaranteed commitment."},
            ],
            "buyer_checks": ["Confirm the one-time price.", "Decline recurring add-ons you do not want."],
            "faqs": [
                {"question": "Which format is simpler?", "answer": "Alpha is the simpler written package."},
                {"question": "Are results guaranteed?", "answer": "No. Neither guide can control another person."},
            ],
            "related": [
                {"slug": "related-one", "title": "Related One", "description": "A nearby comparison."},
                {"slug": "related-two", "title": "Related Two", "description": "Another comparison."},
            ],
        }

    def make_site(self, root: Path):
        (root / "about").mkdir(parents=True)
        (root / "related-one").mkdir()
        (root / "related-two").mkdir()
        (root / "images").mkdir()
        (root / "comparison-template.css").write_text("body{}", encoding="utf-8")
        (root / "favicon.png").write_bytes(b"png")
        homepage_schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Heartwise Compare",
            "url": "https://heartwisecompare.com/",
            "hasPart": [],
        }
        (root / "index.html").write_text(
            '<html><head><script id="website-schema" type="application/ld+json">'
            + json.dumps(homepage_schema)
            + '</script></head><body><section id="recent"><div class="post-list">'
            + '<a class="post-row" href="old/"><div><time datetime="2026-09-01">September 1, 2026</time><h3>Old</h3><p>Old page.</p></div></a>'
            + '</div></section></body></html>',
            encoding="utf-8",
        )
        (root / "about" / "index.html").write_text(
            '<section aria-labelledby="links-title"><div class="card-grid">'
            '<article class="card"><h3><a href="../old/">Old</a></h3><p>Old page.</p></article>'
            '</div></section>',
            encoding="utf-8",
        )
        related_html = (
            '<section aria-labelledby="related-title"><div class="card-grid">'
            '<article class="card"><h3><a href="../old/">Old</a></h3><p>Old page.</p></article>'
            '</div></section>'
        )
        (root / "related-one" / "index.html").write_text(related_html, encoding="utf-8")
        (root / "related-two" / "index.html").write_text(related_html, encoding="utf-8")
        (root / "sitemap.xml").write_text(
            '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>https://heartwisecompare.com/</loc><lastmod>2026-09-01</lastmod></url>'
            '<url><loc>https://heartwisecompare.com/about/</loc><lastmod>2026-09-01</lastmod></url>'
            '</urlset>',
            encoding="utf-8",
        )
        page_dir = root / "alpha-vs-beta" / "images"
        page_dir.mkdir(parents=True)
        (page_dir / "hero.png").write_bytes(b"png")

    def test_validation_rejects_non_women_audience(self):
        data = self.sample()
        data["audience"] = "men"
        with self.assertRaisesRegex(ValueError, "women"):
            validate_comparison(data)

    def test_render_is_escaped_and_contains_required_seo_contract(self):
        data = self.sample()
        data["dek"] = 'Readable <script>alert("x")</script>'
        html = render_page(data)
        self.assertIn("Readable &lt;script&gt;", html)
        self.assertNotIn("<script>alert", html)
        self.assertIn('href="../comparison-template.css', html)
        self.assertIn('rel="sponsored nofollow noopener noreferrer"', html)
        self.assertIn('https://heartwisecompare.com/alpha-vs-beta/', html)
        self.assertIn('"@type": "FAQPage"', html)

    def test_shared_stylesheet_keeps_check_markers_with_their_text(self):
        root = Path(__file__).resolve().parents[1]
        css = (root / "comparison-template.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.check-item\s*\{[^}]*display:\s*grid")
        self.assertRegex(css, r"\.check-item\s*\{[^}]*grid-template-columns:\s*[^;]*")
        self.assertRegex(css, r"\.check-item p\s*\{[^}]*margin:\s*0")

    def test_shared_stylesheet_spaces_factory_faq_items(self):
        root = Path(__file__).resolve().parents[1]
        css = (root / "comparison-template.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.faq-list\s*\{[^}]*display:\s*grid")
        self.assertRegex(css, r"\.faq-list\s*\{[^}]*gap:\s*10px")

    def test_build_updates_every_discovery_surface_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_site(root)
            data = self.sample()
            changed = build_comparison(root, data)
            self.assertTrue(changed)
            page = (root / "alpha-vs-beta" / "index.html").read_text(encoding="utf-8")
            home = (root / "index.html").read_text(encoding="utf-8")
            about = (root / "about" / "index.html").read_text(encoding="utf-8")
            sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")
            related = (root / "related-one" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Alpha vs Beta", page)
            self.assertLess(home.index("alpha-vs-beta"), home.index('href="old/"'))
            self.assertIn('"url": "https://heartwisecompare.com/alpha-vs-beta/"', home)
            self.assertIn("../alpha-vs-beta/", about)
            self.assertIn("https://heartwisecompare.com/alpha-vs-beta/", sitemap)
            self.assertIn("../alpha-vs-beta/", related)
            first = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertFalse(build_comparison(root, data))
            second = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(first, second)

    def test_check_mode_reports_drift_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_site(root)
            data = self.sample()
            drift = build_comparison(root, data, check=True)
            self.assertTrue(drift)
            self.assertFalse((root / "alpha-vs-beta" / "index.html").exists())

    def test_cli_build_then_check_reports_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_site(root)
            (root / "templates").mkdir()
            source_template = Path(__file__).resolve().parents[1] / "templates" / "comparison.html"
            (root / "templates" / "comparison.html").write_text(source_template.read_text(encoding="utf-8"), encoding="utf-8")
            data_path = root / "comparison.json"
            data_path.write_text(json.dumps(self.sample()), encoding="utf-8")
            cli = Path(__file__).resolve().parents[1] / "scripts" / "build_comparison.py"
            built = subprocess.run([sys.executable, str(cli), str(data_path), "--root", str(root)], text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertIn("updated", built.stdout)
            checked = subprocess.run([sys.executable, str(cli), str(data_path), "--root", str(root), "--check"], text=True, capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("clean", checked.stdout)


if __name__ == "__main__":
    unittest.main()
