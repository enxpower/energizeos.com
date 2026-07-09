# Decision Log

## Active Decisions

- Decision: Initial Project Context Pack added.
  Reason: Future AI coding sessions need a reliable project baseline instead of relying on chat history.
  Impact: Future sessions should read `CLAUDE.md` and docs files before making changes.

- Decision: This repository remains a static official website.
  Reason: Inspection found `README.md`, `index.html`, and `CNAME`, with no root `package.json`.
  Impact: Future work must not add a build system, framework, dependency, or package file unless explicitly approved.

- Decision: The canonical public domain is `energizeos.com`.
  Reason: The root `CNAME` file contains `energizeos.com`, and `index.html` uses `https://energizeos.com/` in canonical and social metadata.
  Impact: Do not change domain routing, canonical URLs, or public routes without explicit approval.

- Decision: EnergizeOS visual identity governs the public surface.
  Reason: The site is the official EnergizeOS website for Energize Solutions Inc.
  Impact: Future UI work must preserve a light, bright, industrial, serious, and premium EnergizeOS presentation.

- Decision: Public messaging must stay technical and delivery-focused.
  Reason: The site positions EnergizeOS around control systems, BESS, power equipment delivery, interconnection compliance, and commissioning responsibility.
  Impact: Future copy must not drift into generic SaaS, vague AI, or unsupported marketing claims.
