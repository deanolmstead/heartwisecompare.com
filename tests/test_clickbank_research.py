import tempfile
import unittest
from pathlib import Path

from scripts.clickbank_research import (
    _marketplace_page,
    choose_offer_button_index,
    classify_audience,
    filter_candidates,
    product_is_already_used,
)


class ClickBankResearchTests(unittest.TestCase):
    def test_offer_button_selection_uses_the_matching_card(self):
        cards = [
            "Other Product Get Affiliate Link",
            "Secrets of Flirting With Men Self-Help/Dating Guides Get Affiliate Link",
            "Another Product Get Affiliate Link",
        ]
        self.assertEqual(choose_offer_button_index("Secrets of Flirting With Men", cards), 1)

    def test_dashboard_session_navigates_to_marketplace(self):
        class FakePage:
            def __init__(self):
                self.url = "https://accounts.clickbank.com/master/dashboard.html"
                self.visited = []

            def goto(self, url, wait_until=None):
                self.visited.append((url, wait_until))
                self.url = url

        class FakeContext:
            def __init__(self, page):
                self.pages = [page]

        class FakeBrowser:
            def __init__(self, page):
                self.contexts = [FakeContext(page)]

        page = FakePage()
        result = _marketplace_page(FakeBrowser(page))
        self.assertIs(result, page)
        self.assertIn("affiliate-marketplace", page.visited[0][0])

    def test_audience_classification_prefers_explicit_women_language(self):
        self.assertEqual(classify_audience("The Woman Men Adore", "For women's lists and women seeking relationships"), "women")
        self.assertEqual(classify_audience("900 Seductive Texts", "Male offer for men's traffic"), "men")
        self.assertEqual(classify_audience("Relationship products", "Courses for men and women"), "mixed")
        self.assertEqual(classify_audience("General communication course", "Relationship lessons"), "unknown")

    def test_existing_product_inventory_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text(
                "<h1>Infatuation Scripts vs Modern Relationships for Women</h1>"
                "<p>That's Not How Men Work</p>",
                encoding="utf-8",
            )
            self.assertTrue(product_is_already_used(root, "infatuation scripts"))
            self.assertTrue(product_is_already_used(root, "New High Converter for Women's Lists - Infatuation Scripts"))
            self.assertTrue(product_is_already_used(root, "Modern Relationships for Women by Full-Wisdom"))
            self.assertTrue(product_is_already_used(root, "That's Not How Men Work - NEW Offer for Women"))
            self.assertFalse(product_is_already_used(root, "The Woman Men Adore"))

    def test_filter_keeps_only_new_women_offers_without_approval(self):
        candidates = [
            {"title": "The Woman Men Adore", "category": "Self-Help/Dating Guides", "description": "For women's lists", "approval_required": False, "sales_url": "https://example.com"},
            {"title": "900 Seductive Texts", "category": "Self-Help/Dating Guides", "description": "Male offer for men", "approval_required": False, "sales_url": "https://example.com"},
            {"title": "Private Women Course", "category": "Self-Help/Dating Guides", "description": "For women", "approval_required": True, "sales_url": "https://example.com"},
            {"title": "His Secret Obsession", "category": "Self-Help/Marriage & Relationships", "description": "For women", "approval_required": False, "sales_url": "https://example.com"},
            {"title": "Women in Business", "category": "E-business & E-marketing/Consulting", "description": "For women entrepreneurs", "approval_required": False, "sales_url": "https://example.com"},
            {"title": "Relationship Products", "category": "Self-Help/Marriage & Relationships", "description": "For men and women", "approval_required": False, "sales_url": "https://example.com"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("His Secret Obsession", encoding="utf-8")
            result = filter_candidates(candidates, root, audience="women")
            self.assertEqual([item["title"] for item in result], ["The Woman Men Adore"])
            self.assertNotIn("contact", result[0])


if __name__ == "__main__":
    unittest.main()
