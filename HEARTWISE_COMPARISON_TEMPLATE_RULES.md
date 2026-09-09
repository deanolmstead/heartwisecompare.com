# Heartwise Compare: Comparison-Page Template Rules

These rules are the guardrail for Hermes and any other agent editing a Heartwise Compare comparison page. The goal is to extend the established site, not invent a new page design for each product pair.

## Source of truth

Use these files in this order:

1. `templates/comparison.html` is the canonical section order and markup contract.
2. `comparison-template.css` is the canonical visual and responsive contract.
3. `scripts/page_factory.py` is the only supported renderer for structured comparison pages.
4. `data/comparisons/<slug>.json` contains page content and source evidence.
5. `his-secret-obsession-vs-devotion-system/index.html` is the visual reference when checking whether the page still belongs to the site.

Do not hand-design a generated route from scratch. Do not create a route-specific CSS fork when a shared template or shared class can solve the problem.

## Required page structure

Keep this sequence unless the user explicitly requests a structural change:

1. Breadcrumb
2. Hero with product-name H1, dek, byline, product CTAs, disclosure, and one decisive image
3. Three-cell source strip
4. Short-answer verdict panel
5. Decision guide with three situation-first cards and a CTA row
6. Side-by-side table and a CTA row directly below it
7. Package details with two product cards
8. Safety/limitations note
9. Buyer checklist
10. Primary evidence cards linking to official seller pages
11. Related comparisons
12. Final CTA panel
13. FAQ accordion
14. Footer

Every section must have one clear job. Do not add decorative card grids, invented testimonials, urgency banners, popups, or unrelated upsells.

## Naming and copy

- The page title and H1 use the actual product names, for example `The Woman Men Adore vs Infatuation Scripts`.
- Never replace product names with abstract packaging copy such as “A five-module guide vs a multimedia script library.”
- Lead with format, package transparency, practical fit, and limitations.
- Clearly separate seller claims from verifiable package details.
- Never promise attraction, commitment, reconciliation, control, or a guaranteed reaction.
- Keep safety language visible when a product uses manipulative relationship claims or touches coercion, abuse, stalking, crisis, or serious distress.
- Keep body copy readable and plain. Avoid hype, fake social proof, fake testimonials, and invented credentials.

## Price policy

Prices and currency amounts must never appear on the public comparison page.

- It is acceptable to retain `price` fields in the JSON for internal source auditing.
- The renderer must not output a price row, price badge, currency amount, or pricing amount in checkout notes, FAQs, checklists, source copy, or CTA copy.
- Refer visitors to the current seller page for the live offer and checkout terms.
- Before delivery, search the generated HTML for currency amounts and the label `Listed price`.

## CTA and link rules

- Keep product CTAs visible in the hero, after the decision guide, below the comparison table, and in the final CTA panel.
- Product CTAs use the verified tracked HopLink from the JSON.
- Official evidence cards use the direct official seller URL, not the affiliate link.
- Product links must include `target="_blank"` and `rel="sponsored nofollow noopener noreferrer"`.
- Source links must include `target="_blank"` and `rel="noopener noreferrer"`.
- Use `.hero-actions` and `.cta-actions`; preserve their wrapping and `gap` rules so buttons never touch.
- CTA text should identify the product, such as `Visit The Woman Men Adore` or `Review Infatuation Scripts`.

## Visual contract

- Use the shared warm editorial system: Bodoni Moda display type, Manrope body/interface type, tinted paper neutrals, muted berry accent, and the existing dark-mode tokens.
- Reuse the existing `page-shell`, `section`, `section-head`, `product-card`, `table-wrap`, `faq-list`, `final-cta`, and `footer-inner` classes.
- The hero is a two-column editorial layout on desktop and a single-column stack on smaller screens.
- Cards and tables use neutral borders, controlled radii, and restrained shadows. Do not introduce colored side stripes, gradient text, glass cards, or generic SaaS panels.
- The footer spans the viewport, but `.footer-inner` stays inside `var(--content)` and stacks cleanly on mobile.
- FAQ rows use the custom accordion treatment: no browser disclosure triangle, a full-width summary row, and plus/minus indicators. The first answer is open by default.

## Responsive requirements

- Desktop content is constrained by `--content` and centered.
- Two- and three-column sections collapse to one column at the shared breakpoints.
- Hero, product, and CTA buttons wrap without collision; on narrow screens, important button groups become full width.
- Tables may scroll inside `.table-wrap`, but the page itself must never create horizontal overflow.
- Check the route at both a wide desktop viewport and approximately 390px mobile width.

## Editing workflow

1. Inspect the canonical template, shared CSS, JSON data, and the established reference page before editing.
2. Make content changes in the JSON and structural/style changes in the template or shared CSS.
3. Never edit generated `index.html` by hand as the final source.
4. Rebuild the route:

   ```bash
   python3 scripts/build_comparison.py data/comparisons/<slug>.json
   ```

5. Run the checks:

   ```bash
   python3 scripts/build_comparison.py data/comparisons/<slug>.json --check
   python3 scripts/audit_site.py --min-inbound 2
   python3 -m unittest discover -s tests -v
   ```

6. Browser-check the rebuilt route at desktop and mobile widths. Inspect the full page, open and close the FAQ, test the theme toggle, and confirm the footer, CTA groups, image, table, and cards do not clip.
7. Search the generated HTML for `$`, currency amounts, `Listed price`, broken relative links, and unexpected horizontal overflow before declaring the page complete.

## Agent stop conditions

Stop and ask for direction when a requested change would:

- Replace the canonical section sequence
- Remove disclosures or safety limitations
- Expose prices on the public page
- Swap an official source URL for an unverified destination
- Add claims, testimonials, guarantees, or checkout facts that are not in the source data
- Require a new visual direction instead of a template-consistent repair

### Short instruction for Hermes

> Treat `templates/comparison.html` and `comparison-template.css` as the Heartwise Compare contract. Extend the established editorial comparison layout; do not invent a new page shell. Keep actual product names in the H1, never render prices, keep product CTAs and official source links distinct, preserve footer containment and responsive wrapping, and run the factory, audit, unit tests, and desktop/mobile visual QA before stopping.
