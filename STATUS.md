# Project Status: ClickBank Relationships

## Current State

- **Project Root:** `/Users/deanolmstead/Documents/Playground/heartwisecompare.com`
- **Status:** In progress; the latest relationship-guide comparison is published and live verification is complete
- **Kanban Board:** `clickbank-comparison`
- **Primary Hermes Project:** `relationship-program-comparison`

## Completed

- [x] Kept the physical-product site in `../worthadding.com`.
- [x] Moved the three ClickBank relationship comparison drafts into this repository.
- [x] Moved the ClickBank relationship image assets into this repository.
- [x] Documented the page inventory in `README.md`.

## Pending / To-Do

- [x] Rebuilt the root homepage as a distinct Heartwise Compare editorial index with a featured comparison and recent comparison list.
- [x] Kept each comparison as an independent page route linked from the homepage.
- [x] Browser-checked the homepage at desktop and 390px mobile widths; theme toggle and image loading verified.
- [x] Published the homepage update to `deanolmstead/heartwisecompare.com` and verified the live routes.
- [x] Replaced the ClickBank comparison hero still-life with an original adult-couple cafe image using cohesive, complementary styling; the other comparison pages retain different image subjects/scenes.
- [x] Confirmed the public Heartwise Compare brand and final domain; canonical public pages now use `index,follow` after explicit launch approval.
- [x] Normalized author, canonical, Open Graph, breadcrumb, and freshness metadata on the expanded His Secret Obsession comparison.
- [x] Rechecked current seller presentation, refund language, ClickBank offer metadata, direct-tracking availability, and generated-link redirects for all six represented offers.
- [x] Published approved product-specific affiliate links on all three comparison pages; every product CTA is tracked and direct source citations remain official product URLs.
- [x] Browser-checked the comparison pages at desktop and 390px mobile widths; product links, disclosures, image loading, no horizontal overflow, and `index,follow` verified.
- [x] Pushed the all-comparisons affiliate-link update to `deanolmstead/heartwisecompare.com` as commit `e8ca875` and verified the public pages after propagation.
- [x] Kept these comparisons as standalone pages within the dedicated Heartwise Compare public site.
- [x] Added a crawlability baseline with `robots.txt` and a canonical `sitemap.xml`, excluding the legacy redirect.
- [x] Built `women-relationship-books-language-of-desire-vs-make-him-worship-you/index.html` with an original couple hero image, situation-first verdict, comparison table, sources, FAQ, and tracked product CTAs.
- [x] Added the new comparison to the homepage latest-pages list and sitemap.
- [x] Built `devotion-system-vs-make-him-worship-you-relationship-guides/index.html` with an original couple hero image, package-clarity verdict, comparison table, sources, FAQ, and tracked product CTAs.
- [x] Browser-checked the new comparison at desktop and 390px mobile widths; image loading, no horizontal overflow, theme toggle, internal anchors, JSON-LD, and inline JavaScript passed.
- [x] Built `language-of-desire-vs-devotion-system-relationship-guides/index.html` with a new original couple hero image, intimacy-versus-package verdict, comparison table, sources, FAQ, and tracked product CTAs.
- [x] Added the Language of Desire vs The Devotion System comparison to the homepage latest-pages list and sitemap.
- [x] Published and publicly verified the matching Pinterest Pin on the Heartwise Compare board: `https://www.pinterest.com/pin/381820874681554561/`.
- [x] Built `ex-factor-2-0-vs-beat-the-breakup-relationship-guides/index.html` as a same-creator, opposite-goals breakup comparison with current package details, visible prices, original imagery, source links, FAQs, and tracked product CTAs.
- [x] Browser-checked, published, and publicly verified the Ex Factor 2.0 vs Beat the Breakup comparison, homepage entry, image, and sitemap URL.
- [x] Rebuilt the sitewide internal-link graph with concise product-specific anchors, topical related-comparison sections on every indexable comparison, and a complete comparison library on the About page; validated every target and mobile layout.
- [x] Added The Forever Woman vs The Obsession Method as a new comparison using two offers not represented on the site, with an original hero asset, official-source citations, audience-first verdict, FAQ, homepage entry, and sitemap entry.
- [x] Kept the new page on direct official seller URLs only; no new account-specific affiliate link was guessed or activated.

## Repository Boundaries

- `../worthadding.com` — Worth Adding physical-product comparison site and publishing pipeline.
- `../reusable-comparison-site-generator` — generic static comparison generator and validation infrastructure.
- This repository — ClickBank-derived relationship-program comparison drafts and reference material.

## Deployment State (2026-08-27)

- **Public site repository:** `deanolmstead/heartwisecompare.com`
- **Pages source:** `main` / root; legacy GitHub Pages build is built.
- **Custom domain:** `heartwisecompare.com`; canonical public pages use `index,follow`; the legacy HSO slug is retained only as a `noindex` redirect.
- **Registrar:** Porkbun; nameservers changed to Cloudflare's assigned `gabe.ns.cloudflare.com` and `lara.ns.cloudflare.com`.
- **Cloudflare web records:** apex A records use GitHub Pages' four documented IPs; `www` points to `deanolmstead.github.io`; obsolete wildcard parking record removed.
- **Preserved email records:** Porkbun MX, SPF, and ACME TXT records were read back unchanged.
- **Current deployment:** GitHub Pages serves `heartwisecompare.com` over HTTPS with the custom domain configured; the comparison pages use product-specific affiliate links and commission disclosures, canonical public pages are indexable, and `robots.txt`/`sitemap.xml` are deployed. The new comparison page, hero asset, homepage link, and sitemap entry returned HTTP 200 after the 5d97065 Pages deployment.

## Homepage Design System

- **Direction:** Editorial journal / comparison index; inspired by comparison-site browsing patterns without copying Worth Adding.
- **Type:** `DM Serif Display` for headings, `Manrope` for readable body and interface copy.
- **Palette:** Warm paper `#fbf7f2`, ink `#292222`, coral accent `#bd5c54`, muted sage support `#53796c`; dark mode uses `#211b1d` with soft ivory text and `#e18478` accent.
- **Structure:** Editorial intro, featured comparison spread, vertical recent-comparison list, and a three-point “details first” methodology section.
- **Interaction:** Sticky frosted header, scroll progress, eager local images, and persistent light/dark toggle using `heartwise-theme`.
- **Image rotation:** Comparison pages use distinct couple styling/appearance rather than reusing one couple across every hero; ClickBank uses a cafe-street scene with a cohesive, complementary couple.
- **Safety:** Canonical public pages are indexable; the legacy HSO URL is a `noindex` redirect; product links are disclosed; `sitemap.xml` excludes the legacy route; no signup integrations were added.