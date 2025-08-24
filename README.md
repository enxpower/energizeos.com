# EnergizeOS Site (UTF-8 + i18n)

Production-ready static site. No build tools. Deploy anywhere that serves static files.

## Structure
- `/index.html` (EN/中文 toggle persists)
- `/assets/style.css`, `/assets/script.js`
- `/products/*`, `/resources/*`, `/legal/*`, `about.html`, `careers.html`, `contact.html`
- `.nojekyll` to disable Jekyll on GitHub Pages
- `CNAME` -> `enxpower.com` (edit if you use another domain)
- `robots.txt`, `sitemap.xml`

## Deploy to GitHub Pages (root-domain repo)
1. Push this folder to your repo root (e.g., `enxpower/energizeos.com`).
2. Settings → Pages → Source: `main`.
3. Custom domain: `enxpower.com` (then **Enforce HTTPS**).
4. DNS A records (root): `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
   And `CNAME www -> enxpower.com`.

## Notes
- All files are UTF-8 **without BOM** and include `<meta charset="utf-8">` (plus an http-equiv fallback).
- Asset URLs are **relative** so the site also works under preview paths.
- You can force the language via querystring `?lang=zh` or `?lang=en`.
