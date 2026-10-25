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

    for href in ip.links:
        check(not href.startswith("javascript:"), "Disallowed JavaScript hyperlink")
        if href.startswith("#"):
            check(href[1:] in ip.ids, f"Broken local anchor: {href}")
    print("ESI English Insights: document, navigation, SEO, original content and ad isolation PASS")


if __name__ == "__main__":
    main()
