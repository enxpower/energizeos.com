# VERIFIED WORKING STATE

Project: `enxpower/energizeos.com`

## Objective
Give `https://energizeos.com/` one accurate, non-blank, brand-controlled sharing preview across Open Graph, X/Twitter, and Apple share surfaces.

## Verified Current State
- Production is served from `enxpower/energizeos.com` `main` through GitHub Pages.
- Production HTML names the cache-busting `assets/og-image-v2.png` and exposes complete Open Graph and X/Twitter metadata.
- Production Apple touch icon and Organization JSON-LD use square, brand-correct assets.
- No open Issue or PR overlaps this repair as of 2026-09-08.

## Completed
- VWS governance structure exists.
- Replacement 1200×630 sharing card rendered and visually inspected with the approved mark geometry, palette, and readable content.
- Square 512×512 organization logo and 180×180 Apple touch icon rendered from the approved primary SVG mark.
- Local social-preview contract, asset dimensions, pinned asset hashes, workflow YAML, Python syntax, and diff whitespace checks pass.
- PR #2 passed `Validate site`, was squash-merged as `590ba0f5312984a4ffaec88de535954abb1bf0cb`, and GitHub Pages published that revision.
- Live homepage and all three referenced PNG assets returned HTTP 200; content types, dimensions, metadata, and SHA-256 values match the merged revision.

## Remaining
- No unresolved engineering item for this repair.
- Previously created messages may retain their old embedded preview; verify with a newly shared URL because client-side message caches are outside the site deployment.

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
- PR: `https://github.com/enxpower/energizeos.com/pull/2`; check run `34181380899` concluded `success`.
- Live social card: HTTP 200, `image/png`, 1200×630, SHA-256 `190f4ec8ebc28c9a2ccc919521a250b03b258019c34f6b91a2b10f01df576576`.
- Live brand icon: HTTP 200, `image/png`, 512×512, SHA-256 `b04af3fbbd945690364378549baf94331becab69e6b735292ca7fe4808436a7d`.
- Live Apple touch icon: HTTP 200, `image/png`, 180×180, SHA-256 `51be05c24d8885bbbd155eaabe4ec28594d323a8df20f72b24137edb2fa0ba3b`.

## Success Criteria
- Correct primary Energize mark and readable company/site identity in a 1200×630 PNG.
- Complete Open Graph and X/Twitter metadata use a new cache-busting image URL.
- Apple touch and structured-data logo references use square, brand-correct assets.
- Automated validation passes on the reviewed revision.
- Production HTML and every referenced asset return HTTP 200 and match the merged revision.

## Next Action
Share `https://energizeos.com/` in a new message to confirm the receiving app refreshes its own cached presentation.

## Operating Rule
**Action → Observation → Verification → State Update**. Keep this file concise and current; history belongs elsewhere.
