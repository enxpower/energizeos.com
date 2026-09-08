# VERIFIED WORKING STATE

Project: `enxpower/energizeos.com`

## Objective
Give `https://energizeos.com/` one accurate, non-blank, brand-controlled sharing preview across Open Graph, X/Twitter, and Apple share surfaces.

## Verified Current State
- Production is served from `enxpower/energizeos.com` `main` through GitHub Pages.
- Production HTML currently names `assets/og-image.png`; the 1200×630 image has large blank areas and non-primary white square treatments.
- X/Twitter has only `twitter:card`; title, description, image, and alt fields are absent.
- Organization JSON-LD incorrectly uses the landscape sharing card as its `logo`.
- No open Issue or PR overlaps this repair as of 2026-09-08.

## Completed
- VWS governance structure exists.
- Replacement 1200×630 sharing card rendered and visually inspected with the approved mark geometry, palette, and readable content.
- Square 512×512 organization logo and 180×180 Apple touch icon rendered from the approved primary SVG mark.
- Local social-preview contract, asset dimensions, pinned asset hashes, workflow YAML, Python syntax, and diff whitespace checks pass.

## Remaining
- Review, merge, deploy through GitHub Pages, and verify the live HTML and asset URLs.

## Constraints / Do Not Touch
- Action does not equal completion.
- Current system/tool evidence outranks old docs, chats, memory, or inference.
- Follow repository-specific governance and safety rules.
- Do not change homepage layout, copy, links, or product claims.
- Do not redraw or reinterpret the approved Energize 2×2 mark geometry or colors.

## Evidence
- GitHub default-branch head before work: `5c09f7797984e60b31e3ac6f404edfc952173ab5`.
- Live `https://energizeos.com/` HTTP 200 and metadata inspected on 2026-09-08.
- Live `assets/og-image.png` matches the repository file and approved VI source hash but is visually unsuitable as a sharing card.
- Local validation: `python scripts/validate_social_preview.py` → `social preview contract: OK`.
- Rendered asset SHA-256: `190f4ec8ebc28c9a2ccc919521a250b03b258019c34f6b91a2b10f01df576576`.

## Success Criteria
- Correct primary Energize mark and readable company/site identity in a 1200×630 PNG.
- Complete Open Graph and X/Twitter metadata use a new cache-busting image URL.
- Apple touch and structured-data logo references use square, brand-correct assets.
- Automated validation passes on the reviewed revision.
- Production HTML and every referenced asset return HTTP 200 and match the merged revision.

## Next Action
Create the review branch and PR, observe required checks, merge, and verify production.

## Operating Rule
**Action → Observation → Verification → State Update**. Keep this file concise and current; history belongs elsewhere.
