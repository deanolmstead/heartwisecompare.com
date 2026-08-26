# Project Status: ClickBank Relationships

## Current State

- **Project Root:** `/Users/deanolmstead/Documents/Playground/relationship-program-comparison`
- **Status:** In progress; Heartwise Compare homepage is now an editorial comparison index
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
- [ ] Confirm the public brand and final domain before changing any page from `noindex`.
- [ ] Normalize inherited Worth Adding canonical/author metadata on the expanded His Secret Obsession draft after the public identity is approved.
- [ ] Recheck current seller format, refund, support, and affiliate-link terms.
- [ ] Browser-check desktop and mobile output for every comparison page.
- [x] Kept these comparisons as standalone pages within the dedicated Heartwise Compare public site.

## Repository Boundaries

- `../worthadding.com` — Worth Adding physical-product comparison site and publishing pipeline.
- `../reusable-comparison-site-generator` — generic static comparison generator and validation infrastructure.
- This repository — ClickBank-derived relationship-program comparison drafts and reference material.

## Deployment State (2026-08-25)

- **Public site repository:** `deanolmstead/heartwisecompare.com`
- **Pages source:** `main` / root; legacy GitHub Pages build is built.
- **Custom domain:** `heartwisecompare.com`; the deployed artifact remains `noindex,follow`.
- **Registrar:** Porkbun; nameservers changed to Cloudflare's assigned `gabe.ns.cloudflare.com` and `lara.ns.cloudflare.com`.
- **Cloudflare web records:** apex A records use GitHub Pages' four documented IPs; `www` points to `deanolmstead.github.io`; obsolete wildcard parking record removed.
- **Preserved email records:** Porkbun MX, SPF, and ACME TXT records were read back unchanged.
- **Current deployment:** GitHub Pages serves `heartwisecompare.com` over HTTPS with the custom domain configured; homepage update is ready for publish verification.

## Homepage Design System

- **Direction:** Editorial journal / comparison index; inspired by comparison-site browsing patterns without copying Worth Adding.
- **Type:** `DM Serif Display` for headings, `Manrope` for readable body and interface copy.
- **Palette:** Warm paper `#fbf7f2`, ink `#292222`, coral accent `#bd5c54`, muted sage support `#53796c`; dark mode uses `#211b1d` with soft ivory text and `#e18478` accent.
- **Structure:** Editorial intro, featured comparison spread, vertical recent-comparison list, and a three-point “details first” methodology section.
- **Interaction:** Sticky frosted header, scroll progress, eager local images, and persistent light/dark toggle using `heartwise-theme`.
- **Image rotation:** Comparison pages use distinct couple styling/appearance rather than reusing one couple across every hero; ClickBank uses a cafe-street scene with a cohesive, complementary couple.
- **Safety:** Root homepage remains `noindex,follow`; no affiliate tracking links or signup integrations were added.