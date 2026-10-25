#!/usr/bin/env python3
"""Admit reviewed English editions and render static, immutable article routes."""
import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = '/insights/intelligence/'
CJK = re.compile(r'[\u3400-\u9fff]')
SLUG = re.compile(r'^20\d{2}-(?:w(?:0[1-9]|[1-4]\d|5[0-3])|reference-\d{2})$')
START, END = '<!-- EDITIONS START -->', '<!-- EDITIONS END -->'


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(issue):
    payload = {k: v for k, v in issue.items() if k != 'approval'}
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def validate_issue(x, config):
    require(isinstance(x, dict), 'Issue must be an object')
    require(x.get('schema_version') == 1 and x.get('language') == 'en', 'English issue schema required')
    require(bool(SLUG.fullmatch(x.get('issue', ''))), 'Invalid local issue slug')
    encoded = json.dumps(x, ensure_ascii=False)
    require(not CJK.search(encoded) and not re.search(r'\$\{|%%[A-Z_]+%%|\{\{', encoded), 'Non-English or template content')
    require(bool(re.fullmatch(r'20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', x.get('published_at', ''))), 'Canonical UTC publication timestamp required')
    try:
        published = datetime.fromisoformat(x['published_at'].replace('Z', '+00:00'))
        require(published.tzinfo is not None and published <= datetime.now(timezone.utc), 'Future or undated publication')
        approval = x['approval']
        reviewed = date.fromisoformat(approval['reviewed_on'])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('Valid publication and review dates required') from error
    if '-w' in x['issue']:
        require(published.date().isocalendar()[:2] == (int(x['issue'][:4]), int(x['issue'][-2:])), 'Issue week and actual publication date disagree')
    require(reviewed <= published.date() and reviewed <= date.today(), 'Invalid review date')
    require(approval.get('status') == 'approved' and bool(approval.get('reviewer')) and approval.get('content_sha256') == digest(x), 'Missing approval or edited approved content')
    for key in ('headline', 'label', 'summary', 'briefing'):
        require(isinstance(x.get(key), str) and bool(x[key].strip()), 'Missing editorial field: ' + key)
    require(60 <= len(x['summary']) <= 400 and len(x['briefing'].split()) >= 40, 'Insufficient executive briefing')
    for key in ('sources', 'developments', 'takeaways', 'uncertainties', 'watchlist'):
        require(isinstance(x.get(key), list) and bool(x[key]), 'Missing editorial section: ' + key)
    require(3 <= len(x['developments']) <= 5 and 3 <= len(x['sources']) <= 12, 'Three to five substantive developments and primary sources required')
    source_ids = set()
    for source in x['sources']:
        require(isinstance(source, dict), 'Invalid source')
        url = urlsplit(source.get('url', ''))
        require(url.scheme == 'https' and url.hostname in config['allowed_source_hosts'] and not url.username and not url.fragment, 'Unapproved primary source')
        require(source.get('kind') == 'primary' and source.get('id') not in source_ids, 'Duplicate or secondary evidence')
        for key in ('id', 'title', 'publisher', 'verified_fact'):
            require(isinstance(source.get(key), str) and bool(source[key]), 'Incomplete source metadata')
        try:
            verified = date.fromisoformat(source['verified_on'])
            source_day = date.fromisoformat(source['published_on'])
        except (KeyError, ValueError) as error:
            raise ValueError('Source dates missing') from error
        require(source_day <= verified <= reviewed, 'Unverified or future source')
        source_ids.add(source['id'])
    for development in x['developments']:
        require(isinstance(development, dict), 'Invalid development')
        for key in ('headline', 'status', 'fact', 'why_it_matters', 'implications', 'uncertainty'):
            require(isinstance(development.get(key), str) and bool(development[key]), 'Incomplete development: ' + key)
        require(len(development['fact'].split()) >= 30 and len(development['implications'].split()) >= 30, 'Thin development')
        require(bool(development.get('sources')) and set(development['sources']) <= source_ids, 'Untraceable development')
    for key in ('takeaways', 'uncertainties', 'watchlist'):
        require(all(isinstance(v, str) and len(v.split()) >= 5 for v in x[key]), 'Empty editorial list')
    return x


def load_issues(root=ROOT):
    folder = root / 'content/intelligence'
    config = json.loads((folder / 'config.json').read_text())
    manifest = json.loads((folder / 'manifest.json').read_text())
    require(manifest.get('schema_version') == 1 and manifest.get('language') == 'en', 'Manifest must be English')
    slugs = manifest.get('issues', [])
    require(isinstance(slugs, list) and bool(slugs) and len(slugs) == len(set(slugs)), 'Empty or duplicate edition manifest')
    require(all(isinstance(s, str) and SLUG.fullmatch(s) for s in slugs), 'Unsafe issue path')
    issues = [validate_issue(json.loads((folder / 'issues' / (slug + '.json')).read_text()), config) for slug in slugs]
    require(all(x['issue'] == slug for x, slug in zip(issues, slugs)), 'Manifest and article identity mismatch')
    require(len({x['published_at'] for x in issues}) == len(issues), 'Ambiguous publication ordering')
    return sorted(issues, key=lambda x: x['published_at'], reverse=True)


def check_tracked_output(root):
    pending = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'insights', 'sitemap.xml'], cwd=root, text=True)
    require(not pending.strip(), 'Generated publication output is untracked: ' + pending.strip())


def check_route_inventory(site_root, issues):
    allowed = {x['issue'] for x in issues}
    folder = site_root / 'insights/intelligence'
    for child in folder.iterdir() if folder.exists() else []:
        if child.is_dir() and re.match(r'^20\d{2}-(?:w|reference-)', child.name):
            require(child.name in allowed, 'Unreviewed public edition route: ' + child.name)


def check_history(current, previous):
    now = {x['issue']: digest(x) for x in current}
    for x in previous:
        require(now.get(x['issue']) == digest(x), 'Published history cannot be deleted or overwritten: ' + x['issue'])


def check_git_history(root, ref):
    def old_file(path):
        r = subprocess.run(['git', 'show', ref + ':' + path], cwd=root, text=True, capture_output=True)
        return json.loads(r.stdout) if r.returncode == 0 else None
    manifest = old_file('content/intelligence/manifest.json')
    if manifest:
        previous = []
        for slug in manifest['issues']:
            x = old_file('content/intelligence/issues/' + slug + '.json')
            require(x is not None, 'Historical source missing from baseline')
            previous.append(x)
        check_history(load_issues(root), previous)


def e(value):
    return escape(str(value), quote=True)


def issue_url(x):
    return BASE + x['issue'] + '/'


def when(x):
    return datetime.fromisoformat(x['published_at'].replace('Z', '+00:00')).strftime('%B %d, %Y').replace(' 0', ' ')


def bullets(values):
    return '<ul>' + ''.join('<li>' + e(v) + '</li>' for v in values) + '</ul>'


def meta(x):
    return '<span class="edition-meta">' + e(x['label']) + ' <span aria-hidden="true">/</span> <time datetime="' + e(x['published_at']) + '">' + when(x) + '</time></span>'


def cards(issues, config, archive=False):
    latest = issues[0]
    previous = issues[1] if len(issues) > 1 else None
    bits = [START, '<section class="edition-hub" aria-label="' + e(config['title']) + '"><div class="edition-wrap">',
            '<div class="edition-top"><p class="edition-kicker">' + e(config['brand']) + ' / North America</p><span>Weekly intelligence · Source-led analysis</span></div>',
            '<div class="edition-heading"><h2>Latest Intelligence</h2><a href="' + BASE + 'archive/">Browse All Editions <span aria-hidden="true">↗</span></a></div>',
            '<div class="edition-grid"><article class="edition-current"><p class="edition-kicker">Current Edition</p>', meta(latest),
            '<h3><a href="' + issue_url(latest) + '">' + e(latest['headline']) + '</a></h3><p>' + e(latest['summary']) + '</p>',
            '<div class="edition-tags">' + ''.join('<span>' + e(x['status']) + '</span>' for x in latest['developments']) + '</div>',
            '<a class="edition-button" href="' + issue_url(latest) + '">Read the full edition <span aria-hidden="true">→</span></a></article>',
            '<div class="edition-side"><article class="edition-previous"><p class="edition-kicker">Previous Edition</p>']
    if previous:
        bits += [meta(previous), '<h3><a href="' + issue_url(previous) + '">' + e(previous['headline']) + '</a></h3><p>' + e(previous['summary']) + '</p><a href="' + issue_url(previous) + '">Read previous edition →</a>']
    else:
        bits += ['<h3>The first edition</h3><p>This series has just launched. Future editions will retain this article in the archive.</p>']
    bits += ['</article><aside class="edition-watch"><p class="edition-kicker">Next Week’s Watchlist</p>', bullets(latest['watchlist']),
             '<p class="edition-note">Monitoring priorities, not predictions. New editions depend on verified evidence.</p></aside></div></div>']
    if archive:
        bits += ['<div class="edition-archive" id="archive"><h2>All Editions</h2>']
        years = sorted({x['published_at'][:4] for x in issues}, reverse=True)
        for year in years:
            bits += ['<h3 class="edition-year">' + year + '</h3><div class="edition-archive-list">']
            for x in issues:
                if x['published_at'].startswith(year):
                    bits += ['<article>', meta(x), '<h3><a href="' + issue_url(x) + '">' + e(x['headline']) + '</a></h3><p>' + e(x['summary']) + '</p><a href="' + issue_url(x) + '">Full article →</a></article>']
            bits += ['</div>']
        bits += ['</div>']
    bits += ['<p class="edition-policy">Independent English research. Publication dates and source dates are separate. Analysis is informational and does not establish project approval, supplier performance or a binding offer.</p></div></section>', END]
    return ''.join(bits)


def article(x, issues, config):
    sources = {s['id']: (n + 1, s) for n, s in enumerate(x['sources'])}
    bits = ['<article class="edition-article"><header class="edition-article-head"><div class="edition-wrap"><a class="edition-back" href="' + BASE + '">← ' + e(config['title']) + '</a>', meta(x),
            '<h1>' + e(x['headline']) + '</h1><p class="edition-deck">' + e(x['summary']) + '</p><p class="edition-byline">' + e(config['brand']) + ' · Research &amp; Engineering</p></div></header>',
            '<div class="edition-body"><nav class="edition-toc" aria-label="In this edition"><a href="#briefing">Executive briefing</a><a href="#developments">Key developments</a><a href="#implications">Implications</a><a href="#watchlist">Watchlist</a><a href="#sources">Sources</a></nav>',
            '<section id="briefing"><p class="edition-kicker">The Briefing</p><h2>Executive briefing</h2><p>' + e(x['briefing']) + '</p></section><section id="developments"><h2>Key developments</h2>']
    for n, dev in enumerate(x['developments'], 1):
        refs = ' '.join('<a class="edition-ref" href="#source-' + e(sid) + '">[' + str(sources[sid][0]) + ']</a>' for sid in dev['sources'])
        bits += ['<section class="edition-development"><p class="edition-kicker">' + str(n).zfill(2) + ' / ' + e(dev['status']) + '</p><h3>' + e(dev['headline']) + '</h3><p>' + e(dev['fact']) + ' ' + refs + '</p>',
                 '<h4>Why it matters</h4><p>' + e(dev['why_it_matters']) + '</p><h4>Engineering &amp; commercial implications</h4><p>' + e(dev['implications']) + '</p><div class="edition-uncertain"><h4>What remains uncertain</h4><p>' + e(dev['uncertainty']) + '</p></div></section>']
    bits += ['</section><section id="implications"><h2>Decisions to carry forward</h2>', bullets(x['takeaways']), '</section><section><h2>What remains uncertain</h2>', bullets(x['uncertainties']),
             '</section><section id="watchlist" class="edition-watch"><h2>Next Week’s Watchlist</h2>', bullets(x['watchlist']), '<p class="edition-note">These are questions for the next review, not statements about future outcomes.</p></section>',
             '<section id="sources"><h2>Primary source references</h2><ol class="edition-sources">']
    for s in x['sources']:
        source_date = s.get('date_label', s['published_on'])
        bits += ['<li id="source-' + e(s['id']) + '"><a href="' + e(s['url']) + '" rel="noopener noreferrer">' + e(s['title']) + '</a><p>' + e(s['publisher']) + ' · Source date: ' + e(source_date) + ' · Verified: ' + e(s['verified_on']) + '</p></li>']
    bits += ['</ol></section><p class="edition-policy">Facts are attributed to the cited sources. Sections labelled analysis are our interpretation. This publication is informational; project decisions require current technical, contractual and regulatory evidence.</p><nav class="edition-pagination" aria-label="Edition navigation">']
    index = next(n for n, v in enumerate(issues) if v['issue'] == x['issue'])
    if index + 1 < len(issues):
        older = issues[index + 1]
        bits += ['<a href="' + issue_url(older) + '">← Previous: ' + e(older['label']) + '</a>']
    if index > 0:
        newer = issues[index - 1]
        bits += ['<a href="' + issue_url(newer) + '">Next: ' + e(newer['label']) + ' →</a>']
    bits += ['<a href="' + BASE + 'archive/">Browse All Editions</a></nav></div></article>']
    return ''.join(bits)


def set_metadata(html, title, description, canonical, x=None, config=None):
    html = re.sub(r'<title>.*?</title>', '<title>' + e(title) + '</title>', html, count=1, flags=re.S)
    replacements = [('name="description"', description), ('property="og:title"', title), ('property="og:description"', description), ('property="og:url"', canonical)]
    for attribute, value in replacements:
        html = re.sub(r'<meta ' + attribute + r' content="[^"]*"\s*/?>', '<meta ' + attribute + ' content="' + e(value) + '">', html)
    html = re.sub(r'<link rel="canonical" href="[^"]*"\s*/?>', '<link rel="canonical" href="' + e(canonical) + '">', html)
    if x:
        html = html.replace('property="og:type" content="website"', 'property="og:type" content="article"')
        schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': x['headline'], 'description': x['summary'], 'datePublished': x['published_at'], 'dateModified': x['published_at'], 'inLanguage': 'en', 'mainEntityOfPage': canonical, 'author': {'@type': 'Organization', 'name': config['brand']}, 'publisher': {'@type': 'Organization', 'name': config['brand']}, 'citation': [s['url'] for s in x['sources']]}
        html = html.replace('</head>', '<script type="application/ld+json">' + json.dumps(schema).replace('<', '\\u003c') + '</script></head>')
    return html


def shell(template, body, title, description, canonical, x=None, config=None):
    html = re.sub(r'<main(?:\s[^>]*)?>.*?</main>', '<main>' + body + '</main>', template, count=1, flags=re.S)
    return set_metadata(html, title, description, canonical, x, config)


def render(root, site_root):
    issues = load_issues(root)
    config = json.loads((root / 'content/intelligence/config.json').read_text())
    check_route_inventory(site_root, issues)
    domain = 'https://' + config['domain']
    css = (root / 'content/intelligence/publication.css').read_text()
    public = site_root / 'insights/intelligence'
    template = (public / 'index.html').read_text()
    template = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', template, flags=re.S)
    style = '<style id="edition-styles">' + css + '</style>'
    template = re.sub(r'<style id="edition-styles">.*?</style>', '', template, flags=re.S).replace('</head>', style + '</head>')
    hub = cards(issues, config, archive=True)
    reference_link = '<p><a href="/insights/intelligence/history/">Historical Market Indicators →</a></p>' if config['kind'] == 'energy' else ''
    index = re.sub(r'<section class="(?:hero|edition-masthead)">.*?</section>', '<section class="edition-masthead"><div class="edition-wrap"><p class="edition-kicker">' + e(config['brand']) + ' / North America</p><h1>' + e(config['title']) + '</h1><p>Independent industry intelligence for engineering, procurement and project delivery.</p>' + reference_link + '</div></section>' + hub, template, count=1, flags=re.S)
    require(index != template, 'Expected Intelligence hero missing')
    (public / 'index.html').write_text(index)
    home = site_root / 'insights/index.html'
    homepage = home.read_text()
    if START in homepage:
        homepage = re.sub(re.escape(START) + r'.*?' + re.escape(END), cards(issues, config), homepage, count=1, flags=re.S)
    else:
        homepage, count = re.subn(r'<section[^>]+aria-labelledby="weekly-intelligence-title".*?</section>', cards(issues, config), homepage, count=1, flags=re.S)
        require(count == 1, 'Expected Insights publication slot missing')
    homepage = re.sub(r'<style id="edition-styles">.*?</style>', '', homepage, flags=re.S).replace('</head>', style + '</head>')
    home.write_text(homepage)
    for x in issues:
        folder = public / x['issue']; folder.mkdir(parents=True, exist_ok=True)
        (folder / 'index.html').write_text(shell(template, article(x, issues, config), x['headline'] + ' | ' + config['brand'], x['summary'], domain + issue_url(x), x, config))
    archive = public / 'archive'; archive.mkdir(exist_ok=True)
    (archive / 'index.html').write_text(shell(template, '<section class="edition-masthead"><div class="edition-wrap"><p class="edition-kicker">The Publication Archive</p><h1>' + e(config['title']) + ' / All Editions</h1><p>Every edition retains its original publication date and primary references.</p></div></section>' + hub, config['title'] + ' Archive | ' + config['brand'], 'Browse complete, dated English editions with executive briefings, engineering interpretation, watchlists and primary source references.', domain + BASE + 'archive/'))
    public_manifest = {'schema_version': 1, 'language': 'en', 'issues': [{k: x[k] for k in ('issue', 'label', 'headline', 'summary', 'published_at')} | {'url': issue_url(x)} for x in issues]}
    (public / 'issues.json').write_text(json.dumps(public_manifest, indent=2, ensure_ascii=False) + '\n')
    sitemap = site_root / 'sitemap.xml'
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    tree = ET.fromstring(sitemap.read_text())
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    for url in list(tree):
        loc = url.find(ns + 'loc')
        if loc is not None and loc.text and (re.search(r'/20\d{2}-(?:w\d{2}|reference-\d{2})/', loc.text) or loc.text == domain + BASE + 'archive/'):
            tree.remove(url)
    for route, changed in [(issue_url(x), x['published_at'][:10]) for x in issues] + [(BASE + 'archive/', issues[0]['published_at'][:10])]:
        item = ET.SubElement(tree, ns + 'url')
        ET.SubElement(item, ns + 'loc').text = domain + route
        ET.SubElement(item, ns + 'lastmod').text = changed
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding='unicode') + '\n')
    print('ENGLISH_EDITIONS_RENDERED=' + str(len(issues)) + ' latest=' + issues[0]['issue'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', type=Path)
    parser.add_argument('--baseline')
    parser.add_argument('--check-tracked', action='store_true')
    args = parser.parse_args()
    issues = load_issues()
    if args.baseline:
        check_git_history(ROOT, args.baseline)
    if args.render:
        render(ROOT, args.render)
    if args.check_tracked:
        check_tracked_output(ROOT)
    print('REVIEWED_ENGLISH_MANIFEST=PASS issues=' + str(len(issues)))


if __name__ == '__main__':
    main()
