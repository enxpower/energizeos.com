"""Validate the English-only ESI corporate Insights entry without external dependencies."""

from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HOMEPAGE = ROOT / "index.html"
INSIGHTS = ROOT / "insights" / "index.html"
SITEMAP = ROOT / "sitemap.xml"
CJK = re.compile(r"[\u3400-\u9fff]")


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.lang = None
        self.main_count = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        if tag == "a":
            self.links.append(attributes.get("href", ""))
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "main":
            self.main_count += 1


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    home = HOMEPAGE.read_text(encoding="utf-8")
    insights = INSIGHTS.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")
    for path, value in ((HOMEPAGE, home), (INSIGHTS, insights), (SITEMAP, sitemap)):
        check(CJK.search(value) is None, f"Non-English CJK text found: {path}")
    hp, ip = DocumentParser(), DocumentParser()
    hp.feed(home)
    ip.feed(insights)
    check(hp.lang == "en" and ip.lang == "en", "English HTML language declaration required")
    check("/insights/" in hp.links and "/" in ip.links, "Two-way corporate navigation required")
    check(ip.main_count == 1, "Insights requires one main landmark")
    check('href="https://energizeos.com/insights/"' in insights, "Canonical Insights URL missing")
    check('aria-current="page"' in insights, "Current navigation state missing")
    check("Required budget = fiber loss + connector loss + splice loss + reserved margin" in insights, "Original optical engineering explanation missing")
    check("10.0 dB" in insights and "20 km" in insights, "Illustrative optical link budget missing")
    check("adsbygoogle" not in insights.lower(), "Automated brief pages must remain ad-free by default")
    check("pagead2.googlesyndication" not in insights.lower(), "Unexpected advertising code")
    root = ET.fromstring(sitemap)
    urls = [el.text for el in root.findall(".//{*}loc")]
    check("https://energizeos.com/insights/" in urls, "Insights absent from sitemap")
    check("https://energizeos.com/" in urls, "Corporate homepage absent from sitemap")
    tools = (ROOT / "insights" / "tools" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "insights" / "assets" / "engineering-tools.js").read_text(encoding="utf-8")
    check(CJK.search(tools) is None and CJK.search(script) is None, "English-only tool pages and scripts required")
    check('<html lang="en">' in tools, "Tools HTML language missing")
    check('href="https://energizeos.com/insights/tools/"' in tools, "Tools canonical missing")
    check("https://energizeos.com/insights/tools/" in urls, "Tools absent from sitemap")
    check("/insights/tools/" in ip.links, "Insights must link to the engineering tools")
    check('id="optical-form"' in tools and 'id="dispatch-form"' in tools, "Two working forms are mandatory")
    check('src="/insights/assets/engineering-tools.js"' in tools, "Original calculation script is not linked")
    check("adsbygoogle" not in tools.lower(), "Do not insert ads into unchecked content")

    intelligence = (ROOT / "insights" / "intelligence" / "index.html").read_text(encoding="utf-8")
    check(CJK.search(intelligence) is None, "Intelligence must be English only")
    check('<html lang="en">' in intelligence, "Intelligence language declaration missing")
    check('href="https://energizeos.com/insights/intelligence/"' in intelligence, "Intelligence canonical missing")
    check("https://energizeos.com/insights/intelligence/" in urls, "Intelligence absent from sitemap")
    check("/insights/intelligence/" in ip.links, "Corporate Insights must link to intelligence")
    for series, value in (("PCU335921335921", "86.6"), ("PCU3359233592", "295.7"), ("IPN33592S", "71.3379")):
        check(series in intelligence and value in intelligence, f"Official-source evidence missing for {series}")
    check(intelligence.count("fred.stlouisfed.org/series/") == 3, "Three official source links required")
    check("June 2025" in intelligence and "August 2026" in intelligence, "Dated historical observations required")
    check("adsbygoogle" not in intelligence.lower(), "Unreviewed intelligence must not include ad-serving code")
    check("action_hint" not in intelligence and "recommended_action" not in intelligence, "Private BD content leaked")

    microgrid = (ROOT / "insights" / "microgrid-ai" / "index.html").read_text(encoding="utf-8")
    mp = DocumentParser()
    mp.feed(microgrid)
    check(mp.lang == "en" and mp.main_count == 1, "Microgrid architecture requires an English main landmark")
    check('href="https://energizeos.com/insights/microgrid-ai/"' in microgrid, "Microgrid canonical missing")
    check("https://energizeos.com/insights/microgrid-ai/" in urls, "Microgrid missing from sitemap")
    check("/insights/microgrid-ai/" in ip.links, "Microgrid research missing from Insights")
    check('viewBox="0 0 48 48"' in microgrid, "Corporate ESI brand mark is required")
    for term in ("L5", "L4", "L2", "CONTROL AUTHORIZATION BOUNDARY", "Deterministic energy management", "Site &amp; permissions"):
        check(term in microgrid, f"Microgrid architectural detail missing: {term}")
    check("not live API endpoints" in microgrid, "Do not imply an available customer API")
    check("adsbygoogle" not in microgrid.lower(), "Do not add ads in architectural reference")
    check(CJK.search(microgrid) is None, "Microgrid research must be English")
    check("copilot-ph2/" not in microgrid, "Paused Copilot must not be linked from public site")
    for href in mp.links:
        if href.startswith("#"):
            check(href[1:] in mp.ids, "Broken microgrid page anchor")

    for href in ip.links:
        check(not href.startswith("javascript:"), "Disallowed JavaScript hyperlink")
        if href.startswith("#"):
            check(href[1:] in ip.ids, f"Broken local anchor: {href}")
    print("ESI English Insights: document, navigation, SEO, original content and ad isolation PASS")


if __name__ == "__main__":
    main()
