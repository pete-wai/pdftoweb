#!/usr/bin/env python3
"""Independently compare the four summary-table cells with PDF geometry.

Compares summary cells, figure crops, and the complete keyed catalog cell text
with source geometry. Ordered page text also accounts for unkeyed material.
"""
import json
from collections import defaultdict
from bisect import bisect_right
import re
import unicodedata
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'public/sources/nist-sp-800-53a-r5.pdf'
REPORT = ROOT / 'src/content/reports/nist-sp-800-53a-r5.json'
# Physical page, divider x, horizontal row boundaries. Coordinates are independently
# read from the PDF's drawn table boxes, not from the conversion's text.
TABLES = [
    (30, 153, (470.38, 501.0, 525.9, 550.8, 652.1)),
    (34, 171, (198.7, 235.7, 248.4, 273.4, 361.33)),
    (41, 149.6, (366.64, 405.5, 442.6, 479.5, 529.81)),
    (44, 149.6, (94.12, 135.5, 160.3, 185.4, 252.26)),
]

def canonical(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s).replace('•', ''))

def clip_text(page, rect):
    return page.get_text('text', clip=fitz.Rect(*rect), sort=True)

def main():
    report = json.loads(REPORT.read_text())
    soup = BeautifulSoup(report['html'], 'html.parser')
    tables = [soup.select_one(f'table[data-source-page="{page}"]') for page, _, _ in TABLES]
    if any(table is None for table in tables):
        raise SystemExit(f'Expected four semantic summary tables; found {len(tables)}')
    doc = fitz.open(PDF)
    for index, ((pageno, divider, ys), table) in enumerate(zip(TABLES, tables), 1):
        rows = table.find_all('tr')
        if len(rows) != 4:
            raise AssertionError(f'Table {index}: expected 4 rows, got {len(rows)}')
        for rownum, (row, y0, y1) in enumerate(zip(rows, ys, ys[1:]), 1):
            cells = row.find_all(['th', 'td'], recursive=False)
            if len(cells) != 2:
                raise AssertionError(f'Table {index} row {rownum}: expected 2 cells, got {len(cells)}')
            assert [cell.name for cell in cells] == ['th', 'td'] and cells[0].get('scope') == 'row', f'Table {index} row {rownum}: incorrect cell semantics'
            for col, (cell, x0, x1) in enumerate(zip(cells, (90, divider), (divider, 523)), 1):
                actual = canonical(cell.get_text(' '))
                expected = canonical(clip_text(doc[pageno - 1], (x0, y0 + .2, x1, y1 - .2)))
                if actual != expected:
                    raise AssertionError(f'Table {index} row {rownum} cell {col}:\nPDF: {expected}\nHTML: {actual}')
    print('Four summary tables: all 32 cells match the corresponding PDF regions.')
    check_figures(doc, soup)
    check_keyed_rows(doc, soup)


def check_figures(doc, soup):
    # Independently checked image boundaries, in physical PDF coordinates.
    regions = [(24,(70,205,542,485)), (25,(70,164,542,469)),
               (26,(70,217,542,590)), (27,(70,178,542,521)),
               (28,(70,190,542,672)), (29,(70,291,542,505)),
               (30,(89,289,523,359)), (47,(69,108,747,477)),
               (731,(68,86,724,398))]
    figures = soup.select('figure img')
    for index, (page, rect) in enumerate(regions, 1):
        path = ROOT / f'public/figures/nist-sp-800-53a-r5/figure-{index}.png'
        expected = doc[page-1].get_pixmap(matrix=fitz.Matrix(2,2), clip=fitz.Rect(rect))
        actual = fitz.Pixmap(str(path))
        assert (actual.width, actual.height, actual.n, actual.samples) == (expected.width, expected.height, expected.n, expected.samples), f'Figure {index} differs from source render'
        assert sum(img.get('src', '').endswith(f'/figure-{index}.png') for img in figures) == 1, f'Figure {index} missing or duplicated'
    for figure in soup.select('figure:has(img)'):
        detail = figure.select_one('details')
        assert detail and not any(c in detail.get_text() for c in '�Ɵƫ'), 'Figure text missing or contains extraction errors'
    seven = soup.select_one('figure[data-source-page="30"] details').get_text(' ', strip=True)
    for label in ('Prepare for Security and Privacy Control Assessments', 'Develop Security and Privacy Assessment Plans', 'Conduct Security and Privacy Control Assessments', 'Analyze Assessment Report Results'):
        assert label in seven
    nine = soup.select_one('figure[data-source-page="731"] details table')
    assert nine and len(nine.select('tr')) == 10
    assert [row.find_all('td', recursive=False)[1].get_text(strip=True) for row in nine.select('tr')[1:]] == list('SSSOSOSSO')
    print('Nine figure crops match source pixels; transcripts and findings structure are present.')


def source_text(value, font):
    # The embedded source font maps private-use codepoints to these ligatures;
    # bold italic uses a different mapping for two glyphs.
    italic = 'BoldItalic' in font
    return value.translate(str.maketrans({'\ue000':'ti', '\ue001':'tt' if italic else 'tti',
        '\ue002':'ft', '\ue003':'tti' if italic else 'tt', '\ue004':'tf'}))


def check_keyed_rows(doc, soup):
    by_page = defaultdict(lambda: defaultdict(list))
    page_text = defaultdict(list)
    page_rows = defaultdict(list)
    for element in soup.select('h3[data-source-page], figure[data-source-page]:has(table)'):
        page = int(element['data-source-page'])
        page_text[page].append(element.get_text())
        if element.name == 'h3':
            page_rows[page].append(canonical(element.get_text()))
        else:
            page_rows[page].extend(canonical(item.get_text()) for item in element.select('caption,tr'))
    for row in soup.select('tr[data-source-page]'):
        head, cell = row.find('th', recursive=False), row.find('td', recursive=False)
        if head and cell:
            by_page[int(row['data-source-page'])][canonical(head.get_text())].append(canonical(cell.get_text()))
    count = 0
    for page in range(51, 695):
        pdf = doc[page-1]
        lines = []
        for block in pdf.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                x, y, _, bottom = line['bbox']
                value = ''.join(source_text(span['text'], span['font']) for span in line['spans'])
                lines.append((x, y, (y+bottom)/2, value))
        # Compare every character on the page in order, including control headers,
        # withdrawn notices, unkeyed rows, and continuations. Whitespace and
        # compatibility ligatures normalize; content is not corrected.
        source = canonical(''.join(value for x, y, _, value in lines if x > 70 and 55 < y < 714))
        result = canonical(''.join(page_text[page]))
        assert source == result, f'Catalog page {page}: ordered source text differs from HTML'
        # Rule coordinates define row boundaries independently of find_tables(),
        # which merges many individual source rows into one inferred row.
        rules = sorted(set(d['rect'].y0 for d in pdf.get_drawings()
                           if d['rect'].height < .01 and d['rect'].x0 < 300 < d['rect'].x1))
        groups = defaultdict(list)
        for x, top, center, text in lines:
            if x >= 70 and 55 <= top < 714:
                groups[bisect_right([round(rule, 1) for rule in rules], center)].append(text)
        source_rows = [canonical(''.join(parts)) for parts in groups.values() if canonical(''.join(parts))]
        html_rows = [row for row in page_rows[page] if row]
        assert source_rows == html_rows, f'Catalog page {page}: row boundaries or text differ'
        for x, _, y, key in lines:
            key = canonical(key)
            if not (140 < x < 225 and re.fullmatch(r'[A-Z]{2}-\d\d\S*', key)):
                continue
            if not any(xx > 225 and abs(yy-y) < 1 for xx, _, yy, _ in lines):
                continue
            top = max((rule for rule in rules if rule < y), default=0)
            bottom = min((rule for rule in rules if rule > y), default=714)
            value = canonical(''.join(text for xx, _, yy, text in lines if 225 < xx < 530 and top < yy < bottom))
            if value not in by_page[page].get(key, []):
                raise AssertionError(f'Catalog page {page}: complete cell for {key} differs from source')
            count += 1
    assert count == 7104, f'Unexpected catalog keyed row count: {count}'
    print(f'{count} complete keyed catalog cells and every source row across 644 catalog pages match.')

if __name__ == '__main__':
    main()
