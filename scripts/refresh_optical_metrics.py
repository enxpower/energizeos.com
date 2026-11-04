#!/usr/bin/env python3
"""Refresh only three preselected official numeric series; never generate prose."""
import argparse
import csv
from datetime import date
from hashlib import sha256
from html import escape
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
START, END = '<!-- OPTICAL METRICS START -->', '<!-- OPTICAL METRICS END -->'
SERIES = {
    'PCU335921335921': ('Fiber optic cable manufacturing PPI', 'U.S. Bureau of Labor Statistics producer-price series, distributed by FRED. The last published period may be old; it is not a current supplier quotation.'),
    'PCU3359233592': ('Communication and energy wire/cable PPI', 'A broader U.S. Bureau of Labor Statistics manufacturing price-pressure proxy. Product mix and contract terms differ from an individual optical cable order.'),
    'IPN33592S': ('Wire/cable industrial production', 'Federal Reserve seasonally adjusted physical-output index, base 2017 = 100. It is not a price, installed-network-capacity or available-inventory measure.'),
}


def parse_csv(series, body):
    if series not in SERIES:
        raise ValueError('Unapproved series')
    reader = csv.DictReader(io.StringIO(body.decode('utf-8-sig')))
    if reader.fieldnames != ['observation_date', series]:
        raise ValueError('Official CSV schema/series mismatch')
    seen, observations = set(), []
    for row in reader:
        period = date.fromisoformat(row['observation_date'])
        if period.day != 1 or period > date.today() or period in seen:
            raise ValueError('Duplicate, future or nonmonthly period')
        seen.add(period)
        if row[series] in ('', '.'):
            continue
        value = float(row[series])
        if not math.isfinite(value) or not 0 < value < 1000000:
            raise ValueError('Invalid index value')
        observations.append((period, value))
    if not observations:
        raise ValueError('No usable observations')
    period, value = max(observations)
    return {'series': series, 'period': period.isoformat(), 'value': value,
            'source_url': 'https://fred.stlouisfed.org/series/' + series,
            'source_sha256': sha256(body).hexdigest()}


def download(series):
    if series not in SERIES:
        raise ValueError('Unapproved source')
    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + series
    request = Request(url, headers={'User-Agent': 'EnergizeOS-Official-Numeric-Series/1.0'})
    with urlopen(request, timeout=20) as response:
        target = urlsplit(response.geturl())
        if response.status != 200 or target.scheme != 'https' or target.hostname != 'fred.stlouisfed.org':
            raise ValueError('Unexpected official source response')
        body = response.read(2000001)
    if len(body) > 2000000:
        raise ValueError('Oversized source')
    return body


def render(rows):
    cards = []
    for row in rows:
        title, boundary = SERIES[row['series']]
        period = date.fromisoformat(row['period']).strftime('%B %Y')
        cards.append('<article class="indicator-card" data-series="' + row['series'] + '">'
                     '<p class="source-id">' + row['series'] + '</p><h3>' + escape(title) + '</h3>'
                     '<div class="indicator-value">' + format(row['value'], '.10g') + ' <span>index</span></div>'
                     '<div class="indicator-date">' + period + ' · latest available source period</div>'
                     '<p>' + escape(boundary) + '</p><a href="' + row['source_url'] + '" target="_blank" rel="noopener noreferrer">Verify the official source series</a></article>')
    return START + '<div class="indicator-grid">' + ''.join(cards) + '</div><p><a href="/insights/intelligence/data.json" download>Download the dated numeric observations (JSON)</a></p>' + END


def validate_dataset(dataset):
    if set(dataset) != {'schema_version', 'metrics'} or dataset['schema_version'] != 1:
        raise ValueError('Unexpected public dataset fields')
    rows = dataset['metrics']
    if not isinstance(rows, list) or len(rows) != len(SERIES) or {x['series'] for x in rows} != set(SERIES):
        raise ValueError('Published series inventory invalid')
    for row in rows:
        if set(row) != {'series', 'period', 'value', 'source_url', 'source_sha256'}:
            raise ValueError('Unexpected public metric fields')
        period = date.fromisoformat(row['period'])
        if period.day != 1 or period > date.today():
            raise ValueError('Invalid public observation period')
        if type(row['value']) not in (int, float) or not math.isfinite(row['value']) or not 0 < row['value'] < 1000000:
            raise ValueError('Invalid public index value')
        if row['source_url'] != 'https://fred.stlouisfed.org/series/' + row['series'] or not re.fullmatch('[0-9a-f]{64}', row['source_sha256']):
            raise ValueError('Published provenance invalid')
    return dataset


def refresh(root=ROOT, *, fetch=download):
    rows = [parse_csv(series, fetch(series)) for series in SERIES]
    dataset = validate_dataset({'schema_version': 1, 'metrics': rows})
    target = root / 'insights/intelligence/data.json'
    page = root / 'insights/intelligence/index.html'
    old = validate_dataset(json.loads(target.read_text())) if target.exists() else None
    if old:
        previous = {row['series']: row for row in old['metrics']}
        if set(previous) != set(SERIES):
            raise ValueError('Previous series inventory mismatch')
        if any(row['period'] < previous[row['series']]['period'] for row in rows):
            raise ValueError('Reject source period rollback')
    html = page.read_text()
    pattern = re.escape(START) + r'.*?' + re.escape(END) if START in html else r'<div class="indicator-grid">.*?</article>\s*</div>'
    updated, count = re.subn(pattern, lambda match: render(rows), html, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Expected numeric publication slot missing')
    if old == dataset and html == updated:
        return False
    # All remote sources and page shape pass before either public file is staged.
    staged = []
    for path, content in [(target, json.dumps(dataset, indent=2) + '\n'), (page, updated)]:
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_text(content)
        staged.append((tmp, path))
    for tmp, path in staged:
        tmp.replace(path)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if args.refresh:
        changed = refresh()
        print('OPTICAL_NUMERIC_REFRESH=' + ('UPDATED' if changed else 'UNCHANGED'))
    else:
        dataset = validate_dataset(json.loads((ROOT / 'insights/intelligence/data.json').read_text()))
        html = (ROOT / 'insights/intelligence/index.html').read_text()
        if render(dataset['metrics']) not in html:
            raise ValueError('Published numbers do not match the dataset')
        print('OPTICAL_NUMERIC_PUBLICATION=PASS')


if __name__ == '__main__':
    main()
