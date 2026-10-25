# AdSense Pre-Approval Audit — October 26, 2026

**Audience:** Internal website owner and release engineer. **Status:** PRE-APPROVAL HOLD / NO ACCOUNT APPROVAL CLAIMED.
**Scope:** Public corporate root domain and all existing original English Insights/Intelligence pages; no publisher account changes, no speculative ads, no new content publication.

## Official policy baseline (checked 2026-10-26)

- Content should be original, valuable, complete and navigable: https://support.google.com/adsense/answer/7299563?hl=en
- AdSense site ownership is supported by the `google-adsense-account` HTML meta verification method; account/site review status is only authoritative in the connected AdSense Sites dashboard: https://support.google.com/adsense/answer/12169212?hl=en and https://support.google.com/adsense/answer/12170222?hl=en
- Privacy disclosures for Google advertising should explain third-party cookies, visits across sites and personalized-ads opt-out: https://support.google.com/adsense/answer/1348695?hl=en and https://support.google.com/publisherpolicies/answer/10437794?hl=en
- Google-certified IAB TCF CMP is needed for personalized ad service in EEA, UK and Switzerland: https://support.google.com/adsense/answer/13554116?hl=en
- Misrepresentation of publisher identity or unsupported affiliation/claims is restricted: https://support.google.com/adsense/answer/10502938?hl=en
- While review is pending, Google advises against removing and resubmitting the site: https://support.google.com/adsense/answer/12170222?hl=en

## Site-specific source evidence

**ESI-specific:** Root `energizeos.com`; existing production `privacy/index.html` already exists on main. Older Privacy Draft PR #33 is still explicitly HOLD and should not be merged. Separate GitHub ruleset protects `main` with zero required human approvals and mandatory `social-preview` and `verify-public-route` checks.

## Website checks and safe action already staged

- Existing independent English corporate pages and source-led original Intelligence editions are retained, with live HTTPS, page structure, responsive-browser, site navigation, archive, sitemap and primary-source gates covered by project CI.
- Official AdSense verification meta tag **is present in the website source**. Whether this exact publisher ID matches an **active account**, correct owner/payee and pending site submission remains account-side **NOT VERIFIED**.
- A publicly navigable English privacy notice already exists in the site build/source. Its detailed internal legal-fact review draft is separately marked unapproved; never merge the old draft PR merely to satisfy a checklist.
- This scoped PR clarifies **conditional future** Google third-party ad identifiers/cookies and Ads Settings opt-out in the published notice. It does not assert ad activation or legal approval. Site preflight tests ensure these disclosures stay present.
- Existing publication validation prevents internal 404s, missing first-party assets, non-English leakage, copied claims, duplicate references and unapproved/new broken source links.
- Existing website CI intentionally forbids insertion of speculative Google advertising scripts; an official account meta tag is not an ad-serving script.

## Owner-side factual / account gates — NOT CLOSED

1. Verify in the **existing** legitimate Google AdSense account: this site's root-domain row status (e.g. Getting ready / Needs attention / Ready), verified account identity, matching publisher ID, payee/legal entity, account/payout activation and Policy center messages. Owner has said a review request was submitted; that statement is not independently verified in the connected dashboard.
2. Finish the existing one-time internal privacy/legal facts review: actual website operator, providers that process technical logs and business-email content, cross-border transfers, correspondence retention practice, designated privacy-request handler, deployed third-party scripts/cookies and consent handling. The public notice must not claim unverified facts or overpromise privacy.
3. **Before serving ads, not as an invented pre-approval widget:** finalize required consent/CMP configuration in Google's Privacy & messaging or a certified CMP for applicable regions; publish final appropriate disclosure; match `ads.txt` to verified account ID if AdSense reports action needed. Do not guess publisher IDs or create an empty/incorrect ads.txt.
4. Substantiate public commercial scale/customer/certification claims from actual company records or qualify them without inventing numbers. Absence of evidence is **NOT** a finding that the statement is false; it is a verification gap.

## Sealing decision

- **Technical site quality:** good baseline, with targeted privacy disclosure improvement submitted under PR CI/deploy acceptance.
- **Google approval:** NOT VERIFIED. Google is the only authority for site status.
- **Full AdSense-ready project:** NOT CLOSED until the account-side and privacy-fact checks above are confirmed. No additional filler articles, guessed ads.txt, fake cookie banners, unapproved advertisements or duplicate Privacy draft publication.
- **Review cadence:** keep the approved sites stable; monitor GitHub live-validation failures, Google official policy updates, actual account messages and substantive original article freshness. React to specific failures, not speculative checklists.
