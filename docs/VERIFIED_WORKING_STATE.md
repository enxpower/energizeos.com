# VERIFIED WORKING STATE

Project: `enxpower/energizeos.com`
Workstream: AdSense readiness — Issue #5
Checkpoint: 2026-10-25 (GitHub source and policy audit; not a deployed-feature acceptance)
Progress pointer: **G0 IN PROGRESS / G1 IN PROGRESS / G2–G4 NOT STARTED / G5 EXTERNAL**

## Objective
Deliver a premium English-only ESI corporate website with a useful, original `/insights/` center and tools, fully unattended regular operations within Google's publisher policies, and a separately verifiable organization AdSense application.

## Verified Current State
- `enxpower/energizeos.com` is the current official static website repository. It includes the approved logo assets, social-preview validation, sitemap and robots rules.
- `enxpower/docs-energize-v2/intel` contains the optical-market intelligence packages, including W43 dated 2026-10-19. Publication workflow success is not a current live-route test.
- The website repository tree has no `/insights/` directory at this checkpoint, and there were no open website PRs at the checkpoint.
- `docs-energize-v2` contains other independent products and unrelated open pull requests; this work must not modify those unrelated directories.
- The 2026-10-25 AdSense governing Issue is #5. A scoped `agent/adsense-g0-control-plane` branch exists.

## Completed
- Read and mapped the actual website and intelligence repository responsibilities from connected GitHub.
- Independently located authoritative Issue #5 and the relevant source/automation boundaries.
- Governance PR #6 was squash-merged into `main` as `2f3e832e8918adbc3c32026a7f46eca5526b46cd`; local Six Rules are now on the default branch.
- The G1 feature branch contains an English-only Insights page, two-way corporate links, a sitemap addition and a validator integrated with existing social-preview CI; these changes are not deployed or live-verified.

## Remaining
- G0 [IN PROGRESS] — verify current public Pages route, rollback, legacy optical URL, English and policy/claim inventory.
- G1 [IN PROGRESS] — create premium English-only `/insights/` focused on EMS and a distinct ESI-only optical channel.
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
- Direct GitHub branch, tree, workflow and file reads from 2026-10-25. No unverified browser-live claim is used as completion evidence.

## Success Criteria
1. All active corporate and research outputs English only; business topics and brand ownership correct.
2. High-quality, responsive `/insights/`, useful original calculators, source/methodology disclosures and robust safety gates work on live public URLs.
3. Regular intelligence publishing and site updates run unattended with reliable fail-closed quality checks and no disallowed automatic advertising.
4. Google publisher/privacy and technical site-ownership requirements are independently verified; the distinct organization account is eligible.
5. Actual Google site-approval decision is observed. Never represent a pre-submission checklist as Google approval.

## Next Action
Review exact G1 diff and independent CI, verify optical calculations and responsive layout, and establish safe live routing/rollback before considering any merge or deployment.

## Operating Rule
**Action → Observation → Verification → State Update**. Report the actual G0–G5 gate, observable output, blocker, and exact next action. Avoid fictional percentages and progress from code changes alone. Historical releases remain accessible in Git history; this file represents the current active workstream only.
