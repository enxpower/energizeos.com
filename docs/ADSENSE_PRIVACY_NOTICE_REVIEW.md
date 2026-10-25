# Website Privacy Notice — Review Draft

**STATUS: INTERNAL REVIEW ONLY / NOT APPROVED FOR PUBLICATION**
**Website:** https://energizeos.com/
**Company presented on website:** Energize Solutions Inc.
**Draft date:** 2026-10-25
**Proposed privacy contact:** info@energizeos.com (website-listed mailbox; delivery and privacy-request assignment NOT yet verified)
**Source of technical scope:** current `main` website HTML, scripts and published Sitemap, inspected 2026-10-25.

> This is proposed English notice language for counsel/authorized company review, not a statement that the data practices or legal basis below have already been verified. Do not deploy this file as `/privacy/` or represent it as effective until each open fact is confirmed. No advertising or analytics integration is authorized by this document.

## Proposed Public Notice — Conditional Draft

### 1. Scope and website operator

This notice would apply to the public corporate website at https://energizeos.com/, operated by Energize Solutions Inc., including its public Insights and engineering research pages. The website describes EMS software, microgrid intelligence architecture, original engineering calculators and optical market research. Separately operated websites and external services may have their own privacy practices.

### 2. Information people provide

If you contact us at info@energizeos.com, the information you choose to include—such as your name, organization, contact details, engineering questions and project context—may be used to read and respond to your inquiry and manage relevant business correspondence. The website's inspected public pages currently provide an email link rather than a built-in contact form.

**VERIFY BEFORE PUBLICATION:** actual receiving mailbox, receiving legal entity, email provider and sub-processors, international transfers, administrative access, business-retention practices, and whether contact information is used for anything beyond responding to inquiries.

### 3. Hosting, security and technical data

The website is currently deployed as a static public website using its existing GitHub-based publishing workflow. Hosting, DNS, network and security providers may process technical information associated with a visit, such as requests, IP addresses, device/browser characteristics, timestamps or error events, according to the actual deployed infrastructure and provider configuration.

**VERIFY BEFORE PUBLICATION:** whether specific access logs are created, which provider controls them, log content and retention, CDN/DNS protections, exact international hosting locations and applicable data processing terms. Do not claim that logs are never stored.

### 4. Cookies and similar technologies

A current review of the website's first-party HTML, source scripts and existing engineering tools did not identify a deployed Google AdSense advertising script, Google Analytics tag or website marketing pixel. This is a limited code inspection rather than a guarantee about every third-party resource or linked destination.

**VERIFY BEFORE PUBLICATION:** any externally injected scripts, proxy-level analytics, first-party cookies, browser storage, customer-support widgets or separate deployed subsites.

### 5. Google advertising, if later enabled

If the website is approved to display Google advertising, Google and its advertising partners may use cookies and other technologies for ad delivery, measurement and, where legally permitted, personalized advertising, including information about visits to this and other websites. The live notice must explain relevant third-party vendors and link to <https://adssettings.google.com/> for Google advertising preferences, with any other required choices and disclosures.

Before serving relevant ads in the EEA, UK or Switzerland, implement the appropriate Google-certified, IAB TCF-integrated consent management platform where Google requires it and complete any other applicable legal requirements. Consent settings must reflect the actual deployment, not a decorative banner.

**NOT CURRENTLY ACTIVE:** No Google publisher ID, advertising script, approval, certified CMP implementation or advertising cookie use has been verified for this site.

### 6. External links

The website may link to independently operated documentation at https://docs.energizeos.com/, relevant primary-source research, and affiliated or external business websites such as https://agim.ca/. A link does not establish common data processing or identical privacy terms. Review each provider's notice before describing its actual practices.

### 7. Sharing, safeguarding and retention

A final notice must accurately describe whether personal information is disclosed to service providers, affiliated companies or other recipients; what safeguards apply; the purposes and legal grounds where required; and how long records are retained.

**NOT READY FOR PUBLICATION:** the actual providers, retention periods, international transfers, requests for erasure, and any applicable exceptions have not been independently verified.

### 8. Your choices and contact

A completed notice should tell visitors how to seek access, correction, deletion, objection or withdrawal of consent where applicable, and how to contact the responsible organization. Proposed point of contact: info@energizeos.com.

**VERIFY BEFORE PUBLICATION:** responsible privacy person/team, actual request process and relevant territorial rights, as informed by legal review.

### 9. Updates

The final notice should state an accurate effective date and be updated when the actual website's technologies, operators or practices materially change. A source-code commit date alone does not establish legal effectiveness.

## Required Verification Matrix

| Required fact | Observed state | Verification owner | Gate |
|---|---|---|---|
| Public corporate identity | Energize Solutions Inc. named in website content | Legal/company records | OPEN |
| Privacy mailbox | info@energizeos.com included in public Contact and schema | Business email administrator | OPEN: delivery + request handling |
| Online contact forms | No built-in form identified in reviewed public pages | Website/production inspection | PARTIAL |
| AdSense publisher script or ID | Not found in reviewed source | Actual AdSense account holder | OPEN |
| Analytics/pixels and injected tags | Not found in reviewed source | DNS/CDN/hosting administrator | OPEN |
| Website logs, providers, retention | Not established by HTML audit | Hosting/DNS administrator | OPEN |
| Email processing, purpose, retention | Not established by HTML audit | Mail administrator + company | OPEN |
| Third-party docs/privacy | docs.energizeos.com is a distinct linked site | Separate documentation owner | OPEN |
| EEA/UK/CH CMP selection | Not configured/verified | Publisher account holder + counsel | OPEN before covered ads |
| Corporate performance/certifications | Some public claims lack independent evidence | Business records owner | OPEN, tracked in Issue #15 |

## Google Authoritative References

- AdSense privacy policy and advertising-cookie disclosures: https://support.google.com/adsense/answer/1348695?hl=en
- Certified CMP and TCF requirements: https://support.google.com/adsense/answer/13554116?hl=en
- Website ownership connection and review: https://support.google.com/adsense/answer/7584263?hl=en
- Site URL scope: https://support.google.com/adsense/answer/2784438?hl=en

## Implementation Instruction After Factual Approval

Only after the factual/legal review is resolved: publish a concise, brand-matched `/privacy/` page within the existing static website; add exactly one Privacy link to sitewide footer/navigation and Sitemap; verify public-policy text matches actual infrastructure; run sitewide canonical/link/English gates, 390/768/1440 Chromium, Pages deployment and independent HTTPS smoke. Do not enable Google ad technology, publish guessed publisher IDs or add an uncertified CMP as part of that change.
