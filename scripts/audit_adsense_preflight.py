#!/usr/bin/env python3
"""Audit published English corporate pages for AdSense technical preflight readiness.

This is a technical quality gate, not Google policy, privacy, or account approval.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


CJK = re.compile(r"[\u3400-\u9fff]")
CANONICAL_REL = "canonical"


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title_depth = 0
        self.titles = []
        self.description = []
        self.canonicals = []
        self.anchors = []
        self.asset_refs = []
        self.ids = set()
        self.footer_depth = 0
        self.footer_contact_links = 0

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "html":
            self.lang = attr.get("lang")
        if tag == "title":
            self.title_depth += 1
        if tag == "meta" and attr.get("name", "").lower() == "description":
            self.description.append(attr.get("content", ""))
        if tag == "link" and CANONICAL_REL in attr.get("rel", "").lower().split():
            self.canonicals.append(attr.get("href", ""))
        if tag == "footer":
            self.footer_depth += 1
        if attr.get("id"):
            self.ids.add(attr["id"])
        if tag in ("img", "script", "source", "video") and attr.get("src"):
            self.asset_refs.append(attr["src"])
        if tag == "video" and attr.get("poster"):
            self.asset_refs.append(attr["poster"])
        if tag == "link" and any(v in (attr.get("rel") or "").lower().split() for v in ("stylesheet", "icon", "preload", "modulepreload")) and attr.get("href"):
            self.asset_refs.append(attr["href"])
        if tag == "a":
            href = attr.get("href", "")
            self.anchors.append(href)
            if self.footer_depth and urlsplit(href).path == "/contact/":
                self.footer_contact_links += 1

    def handle_endtag(self, tag):
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag == "footer" and self.footer_depth:
            self.footer_depth -= 1

    def handle_data(self, value):
        if self.title_depth:
            self.titles.append(value.strip())


def expected_url(host, relative):
    if relative == "index.html":
        return "https://" + host + "/"
    assert relative.endswith("/index.html")
    return "https://" + host + "/" + relative[:-10]


def page_for_path(root, path):
    if path in ("", "/"):
        return root / "index.html"
    clean = path.lstrip("/")
    if clean.endswith("/"):
        return root / clean / "index.html"
    return root / clean


def audit(root, host):
    if not root.is_dir():
        raise ValueError("Published website root does not exist")
    if not (root / "sitemap.xml").is_file():
        raise ValueError("Public XML sitemap missing")
    pages = sorted(root.rglob("*.html"))
    pages = [p for p in pages if not any(part in {"node_modules", ".git", ".github", "build", "dist"} for part in p.relative_to(root).parts)]
    if not pages:
        raise ValueError("No published HTML pages available")
    problems = []
    parsed = {}
    for page in pages:
        rel = page.relative_to(root).as_posix()
        html = page.read_text(encoding="utf-8")
        doc = Page()
        doc.feed(html)
        parsed[rel] = doc
        url = expected_url(host, rel)
        if doc.lang != "en":
            problems.append(rel + ": not declared English")
        if CJK.search(html):
            problems.append(rel + ": contains Chinese-language characters")
        if len(doc.canonicals) != 1 or doc.canonicals[0] != url:
            problems.append(rel + ": incorrect or duplicated canonical URL")
        if len(doc.description) != 1 or not (40 <= len(doc.description[0].strip()) <= 320):
            problems.append(rel + ": missing or invalid description")
        if len(doc.titles) < 1 or not any(doc.titles):
            problems.append(rel + ": missing page title")
        if rel == "privacy/index.html":
            # Google requires clear partner-cookie disclosures and a visible opt-out path.
            if "https://adssettings.google.com/" not in doc.anchors:
                problems.append(rel + ": Google advertising personalization opt-out link missing")
            if "https://policies.google.com/technologies/partner-sites" not in doc.anchors:
                problems.append(rel + ": Google partner-site data-use disclosure link missing")
            if "If Google advertising is enabled" not in html:
                problems.append(rel + ": future advertising data-use disclosure missing")
        if doc.footer_contact_links != 1:
            problems.append(rel + ": corporate footer must contain exactly one Contact link")
        if "adsbygoogle" in html.lower() or "pagead2.googlesyndication.com" in html.lower():
            problems.append(rel + ": no publisher authorization for inserted ad scripts")
    tree = ET.parse(root / "sitemap.xml")
    listed = [el.text for el in tree.findall(".//{*}url/{*}loc")]
    if not listed or len(listed) != len(set(listed)):
        problems.append("sitemap.xml: empty or duplicate public URL inventory")
    site_urls = {expected_url(host, rel) for rel in parsed}
    if set(listed) != site_urls:
        missing = sorted(site_urls - set(listed))
        excess = sorted(set(listed) - site_urls)
        problems.append("sitemap.xml: missing=" + str(missing) + " not_in_site=" + str(excess))
    checked_links = 0
    for rel, doc in parsed.items():
        base = expected_url(host, rel)
        for href in doc.anchors:
            if not href:
                problems.append(rel + ": empty anchor URL")
                continue
            if href.startswith(("mailto:", "tel:")):
                continue
            url = urlsplit(href)
            if url.scheme and url.scheme not in ("http", "https"):
                problems.append(rel + ": unsafe link scheme")
                continue
            if url.netloc and url.netloc.lower() != host.lower():
                continue
            if not url.netloc and url.scheme:
                problems.append(rel + ": malformed local link")
                continue
            if href.startswith("#"):
                target_path = urlsplit(base).path
            elif href.startswith("/"):
                target_path = url.path
            elif url.netloc:
                target_path = url.path
            else:
                target_path = urlsplit(base).path.rsplit("/", 1)[0] + "/" + url.path
            target = page_for_path(root, unquote(target_path))
            checked_links += 1
            if not target.exists():
                problems.append(rel + ": broken first-party link: " + href)
                continue
            if url.fragment and target.name == "index.html":
                target_rel = target.relative_to(root).as_posix()
                other = parsed.get(target_rel)
                if other and unquote(url.fragment) not in other.ids:
                    problems.append(rel + ": missing target anchor: " + href)
    checked_assets = 0
    for rel, doc in parsed.items():
        for href in doc.asset_refs:
            if href.startswith(("data:", "blob:")):
                continue
            parsed_url = urlsplit(href)
            if parsed_url.scheme not in ("", "https", "http"):
                problems.append(rel + ": unsupported media scheme: " + href)
                continue
            if parsed_url.hostname and parsed_url.hostname.lower() != host.lower():
                continue
            if not parsed_url.path and parsed_url.hostname:
                problems.append(rel + ": missing asset path: " + href)
                continue
            from urllib.parse import urljoin
            address = urlsplit(urljoin(expected_url(host, rel), href))
            if address.hostname and address.hostname.lower() != host.lower():
                continue
            target = (root / unquote(address.path).lstrip("/")).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                problems.append(rel + ": missing first-party asset: " + href)
            checked_assets += 1
    if problems:
        for problem in sorted(set(problems)):
            print("ADSENSE_TECHNICAL_PREFLIGHT=FAIL " + problem)
        raise SystemExit(1)
    print("ADSENSE_TECHNICAL_PREFLIGHT=PASS pages=%d internal_links=%d assets=%d domain=%s" % (len(pages), checked_links, checked_assets, host))
    print("AD_ACCOUNT_PRIVACY_AND_PROVIDER_APPROVAL=NOT_VERIFIED")


def self_test():
    assert expected_url("example.com", "index.html") == "https://example.com/"
    assert expected_url("example.com", "contact/index.html") == "https://example.com/contact/"
    p = Page()
    p.feed('<html lang="en"><head><title>Example</title><link rel="canonical" href="https://example.com/"></head><body><footer><a href="/contact/">Contact</a></footer><section id="case"></section></body></html>')
    assert p.lang == "en" and p.footer_contact_links == 1
    assert p.canonicals == ["https://example.com/"] and "case" in p.ids
    assets = Page()
    assets.feed('<img src="/assets/example.svg"><script src="/assets/core.js"></script><link rel="stylesheet" href="/assets/base.css">')
    assert assets.asset_refs == ["/assets/example.svg", "/assets/core.js", "/assets/base.css"]
    print("ADSENSE_TECHNICAL_PREFLIGHT_SELF_TEST=PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?")
    parser.add_argument("--domain")
    parser.add_argument("--self-test", action="store_true")
    options = parser.parse_args()
    if options.self_test:
        self_test()
    else:
        if not options.root or not options.domain:
            parser.error("A published HTML directory and the official root domain are required")
        audit(Path(options.root), options.domain)
