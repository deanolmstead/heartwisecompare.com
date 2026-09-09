# Heartwise Page Factory Implementation Plan

> **For Hermes:** Implement this plan directly with strict RED-GREEN-REFACTOR cycles.

**Goal:** Turn verified comparison research into a complete static Heartwise page while automatically maintaining discovery, sitemap, reciprocal links, and SEO validation.

**Architecture:** Use dependency-free Python 3.9 scripts so GitHub Pages remains plain static HTML. A structured JSON comparison record feeds a shared HTML renderer. Integration helpers update only the current comparison’s homepage, About, sitemap, and reciprocal-link records; the permanent auditor independently crawls the resulting site. The ClickBank helper attaches read-only to the authenticated CDP marketplace and exports sanitized shortlist evidence; link generation remains an explicit flag.

**Tech Stack:** Python 3.9 standard library, `unittest`, static HTML/CSS, optional Playwright for authenticated ClickBank discovery.

---

### Task 1: Define page-factory behavior with failing tests

**Files:**
- Create: `tests/test_page_factory.py`
- Create: `tests/fixtures/site/`

Test schema validation, deterministic rendering, women-only audience enforcement, homepage ordering, About discovery, sitemap inclusion, reciprocal links, idempotency, and check-mode drift detection. Run `python3 -m unittest tests.test_page_factory -v` and confirm expected import failure.

### Task 2: Implement the structured renderer

**Files:**
- Create: `scripts/page_factory.py`
- Create: `templates/comparison.html`

Implement schema validation and escaped deterministic section rendering. Run the focused tests until green.

### Task 3: Implement integration updates

**Files:**
- Modify: `scripts/page_factory.py`
- Create: `scripts/build_comparison.py`

Implement idempotent page writing plus homepage, About, sitemap, and reciprocal-related-link updates. Add `--check` drift mode. Run all page-factory tests.

### Task 4: Add permanent SEO auditing with tests

**Files:**
- Create: `tests/test_audit_site.py`
- Create: `scripts/audit_site.py`

First write failing tests for broken links, sitemap mismatch, malformed metadata/schema, unsafe affiliate rels, and weak inbound links. Implement the auditor and run the complete suite.

### Task 5: Add authenticated ClickBank shortlist helper

**Files:**
- Create: `tests/test_clickbank_research.py`
- Create: `scripts/clickbank_research.py`

Test pure title/audience/existing-product filters first. Implement a sanitized Playwright/CDP CLI that defaults to read-only discovery and requires an explicit option before opening link-generation dialogs. Smoke-test discovery against the live authenticated marketplace without persisting credentials or account identifiers.

### Task 6: Adopt the factory for the latest live comparison

**Files:**
- Create: `data/comparisons/woman-men-adore-vs-infatuation-scripts.json`
- Regenerate: `woman-men-adore-vs-infatuation-scripts/index.html`
- Modify: `index.html`, `about/index.html`, `sitemap.xml`, selected reciprocal pages

Represent the existing women-focused comparison as structured data, rebuild it, verify idempotency, and confirm no content/SEO regressions.

### Task 7: Automate CI and document usage

**Files:**
- Create: `.github/workflows/site-quality.yml`
- Modify: `README.md`
- Modify: `STATUS.md`

Run unit tests, page-factory drift checks, and the SEO auditor on every push. Document research, build, audit, and deployment commands.

### Task 8: Final verification and deployment

Run all unit tests, compile checks, factory check mode, permanent SEO audit, local HTTP crawl, desktop/mobile browser QA, and git diff checks. Commit, push, verify GitHub Actions, verify the live page and live link graph, then update the stale shared-memory repository record with provenance.
