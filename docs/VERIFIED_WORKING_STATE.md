# VERIFIED WORKING STATE

Project: `enxpower/energizeos.com`
Workstream: AdSense readiness — Issue #5
Checkpoint: 2026-10-25 (G1 production route verified by independent HTTP smoke; G0/G2–G5 remain open)
Progress pointer: **G0 IN PROGRESS / G1 VERIFIED COMPLETE / G2–G4 NOT STARTED / G5 EXTERNAL**

## Objective
Deliver a premium English-only ESI corporate website with a useful, original `/insights/` center and tools, fully unattended regular operations within Google's publisher policies, and a separately verifiable organization AdSense application.

## Verified Current State
- `enxpower/energizeos.com` is the current official static website repository. It includes the approved logo assets, social-preview validation, sitemap and robots rules.
- `enxpower/docs-energize-v2/intel` contains the optical-market intelligence packages, including W43 dated 2026-10-19. Publication workflow success is not a current live-route test.
- The current website default branch now contains `insights/index.html`, a homepage Insights link, sitemap entry, and English/content/SEO validation.
- `docs-energize-v2` contains other independent products and unrelated open pull requests; this work must not modify those unrelated directories.
- The 2026-10-25 AdSense governing Issue is #5. A scoped `agent/adsense-g0-control-plane` branch exists.

## Completed
- Read and mapped the actual website and intelligence repository responsibilities from connected GitHub.
- Independently located authoritative Issue #5 and the relevant source/automation boundaries.
- Governance PR #6 was squash-merged into `main` as `2f3e832e8918adbc3c32026a7f46eca5526b46cd`; local Six Rules are now on the default branch.
- G1 feature PR #7 merged as `227eeac8913ce7ea8b1dd86d8de803f7d8de421a`. Existing social-preview tests, new static content checks and real Chromium tests all passed; screenshots at 390/768/1440 px were visually inspected.
- GitHub Pages build and deployment run #40168309514 reported SUCCESS for the merged revision. This does not prove external HTTPS content availability.

- G1 LIVE VERIFIED: independent GitHub Actions run #40168516915 successfully fetched `https://energizeos.com/insights/` over HTTPS and verified HTTP 200, resolved URL, canonical URL, English HTML and the expected original engineering content. Production publication and site quality were separately supported by Pages success and reviewed Chromium screenshots. This completes G1 only, not broader AdSense acceptance.

## Remaining
- G0 [IN PROGRESS] — complete legacy optical-route checks, English history inventory, corporate claim audit and rollback documentation.

- G2 [NOT STARTED] — implement independently tested optical link budget and EMS engineering tools.
- G3 [NOT STARTED] — integrate limited public-safe English intelligence without exposing internal BD action hints and with ad-free defaults on automated reports.
- G4 [NOT STARTED] — test privacy/CMP/ads.txt prerequisites, SEO, accessibility, mobile and live browser flows.
- G5 [GOOGLE EXTERNAL GATE] — separate ESI organization AdSense eligibility, verification, review and observed decision.

## Constraints / Do Not Touch
- All active implementation and public copy, comments, HTML, tests, metadata, automated email and new research must be English; preserve history for audit.
- Maintain established EnergizeOS corporate brand/VI, EMS primary positioning, and optical intelligence only under ESI.
- Never alter independent `docs-energize-v2` products, deployment, commercial confidences, secrets or publisher cadence as collateral work.
- Automated, uncurated new reports default to ad-free; ads must never imply Google policy approval.
- No unauthorized new public customer claim, billing or account action.

## Evidence
- Authoritative issue: https://github.com/enxpower/energizeos.com/issues/5
- Source repository: https://github.com/enxpower/energizeos.com
- Group policies: `enxpower/group-governance/docs/GLOBAL_OBJECTIVE_LOCK.md`, `docs/AI_DELIVERY_CONTRACT.md`, `docs/STANDING_ENGINEERING_AUTHORITY.md`.
- G1 merged SHA `227eeac8913ce7ea8b1dd86d8de803f7d8de421a`, GitHub Actions deployment/Pages run #40168309514 reported SUCCESS, and pre-merge Chromium screenshots were reviewed. Public URL `https://energizeos.com/insights/` is still pending independent content response.

## Success Criteria
1. All active corporate and research outputs English only; business topics and brand ownership correct.
2. High-quality, responsive `/insights/`, useful original calculators, source/methodology disclosures and robust safety gates work on live public URLs.
3. Regular intelligence publishing and site updates run unattended with reliable fail-closed quality checks and no disallowed automatic advertising.
4. Google publisher/privacy and technical site-ownership requirements are independently verified; the distinct organization account is eligible.
5. Actual Google site-approval decision is observed. Never represent a pre-submission checklist as Google approval.

## Next Action
Prioritize G2 original optical link-budget and EMS engineering calculators; in parallel verify legacy optical public-route ownership and G4 privacy/Google account requirements.

## Operating Rule
**Action → Observation → Verification → State Update**. Report the actual G0–G5 gate, observable output, blocker, and exact next action. Avoid fictional percentages and progress from code changes alone. Historical releases remain accessible in Git history; this file represents the current active workstream only.
