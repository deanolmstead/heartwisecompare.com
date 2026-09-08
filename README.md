# Relationship Program Comparison

Standalone working repo for comparing online relationship programs and other digital self-help products.

## Existing comparison pages

- `index.html` — **His Secret Obsession vs The Devotion System** reference specimen
- `clickbank-his-secret-obsession-vs-devotion-system/index.html` — expanded comparison draft
- `ex-factor-2-0-vs-text-chemistry-relationship-programs/index.html` — breakup/texting comparison draft
- `mend-the-marriage-vs-beat-the-breakup-relationship-guides/index.html` — marriage/breakup comparison draft
- `women-relationship-books-language-of-desire-vs-make-him-worship-you/index.html` — intimacy/relationship communication comparison
- `forever-woman-vs-obsession-method-relationship-guides/index.html` — women-focused commitment guide vs men-focused attraction guide
- `relationship-rewrite-vs-avoidant-recovery-relationship-guides/index.html` — reconnection-oriented method vs avoidant-relationship recovery program
- `save-the-marriage-vs-thats-not-how-men-work-relationship-guides/index.html` — marriage-repair system vs dating-and-relationship guide
- `300-creative-dates-vs-modern-relationships-for-women/index.html` — practical date-ideas collection vs standards-and-boundaries course
- `woman-men-adore-vs-infatuation-scripts/index.html` — women-focused five-module framework vs multimedia script package, with recurring-offer checks
- `inside-the-male-mind-vs-carlos-cavallo-womens-dating-relationships/index.html` — women-focused dating-guide comparison
- `devotion-system-vs-make-him-worship-you-relationship-guides/index.html` — package-clarity/relationship communication comparison
- `language-of-desire-vs-devotion-system-relationship-guides/index.html` — intimacy-focus/multimedia-package comparison
- `ex-factor-2-0-vs-beat-the-breakup-relationship-guides/index.html` — reconnection/moving-forward breakup comparison
- `images/relationship-programs-comparison.webp` / `.png` — reference image assets
- `images/clickbank-couple-cafe.webp` — expanded comparison hero asset with a cohesive, distinct adult couple

These ClickBank-derived relationship pages belong to this repository and are **not part of the `worthadding.com` repository or its physical-product comparison pipeline**. The reusable generator is maintained separately at `../reusable-comparison-site-generator`.

## Comparison-page template

`comparison-template.css` is the canonical shared visual contract for every indexable comparison route. New pages must link it after page-specific styles and inherit its navigation, 1120px content shell, Inter/Georgia typography, OKLCH palette, hero grid, rounded cards, source strip, table overflow treatment, and responsive mobile header. The homepage and About page retain their separate site-level layouts; `clickbank-his-secret-obsession-vs-devotion-system/` remains a noindex redirect.

## Hermes Agent field guide

- `hermes-agent-guide/index.html` — standalone interactive digital guide based on the current verified Hermes setup.
- `hermes-agent-guide/guide.md` — editable Markdown source.
- `hermes-agent-guide/sources.md` — official documentation and live setup evidence.
- `hermes-agent-guide/STATUS.md` — scope and verification notes.

## Current status

- The public Heartwise Compare pages are indexable editorial comparisons with visible disclosures.
- Product CTAs use verified tracked destinations; official seller pages remain listed as editorial sources.
- No dummy checkout credentials, newsletter credentials, or Worth Adding analytics are included.
- The Save The Marriage System vs That's Not How Men Work comparison is published from `main`, linked on the homepage, and included in the sitemap, with verified account-specific product links and official seller-page sources.
- The 300 Creative Dates vs Modern Relationships for Women comparison is prepared with verified account-specific product links, official seller-page sources, and a page-specific hero asset.
- The Forever Woman vs The Obsession Method comparison uses official seller URLs only, with no account-specific affiliate links.

## Local preview

```bash
python3 -m http.server 8766
```

Then open:

```text
http://127.0.0.1:8766/
```

## Source pages used for the current comparison

- https://hissecretobsession.com/
- https://www.devotionsystem.com/video/welcome.php
- https://hewillworshiptwo.com/

The current Devotion System and Make Him Worship You pages were checked on August 31, 2026. Re-check current pricing, deliverables, refund terms, vendor details, and approved affiliate-link construction before publishing or monetizing the page.
