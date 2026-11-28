#!/usr/bin/env python3
"""Independent PDF line-fragment and source-page coverage audit for 53A.

This checks fragment presence, not complete order or cell associations.
"""
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unicodedata
import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'public/sources/nist-sp-800-53a-r5.pdf'
REPORT = ROOT / 'src/content/reports/nist-sp-800-53a-r5.json'
FURNITURE = re.compile(r'^(?:NIST SP 800-53A[, ]+REV\. 5|ASSESSING SECURITY AND PRIVACY CONTROLS IN INFORMATION SYSTEMS AND ORGANIZATIONS|This publica(?:tion|on) is available free of charge from:.*|Reference produced from open data|h(?:tt|)ps://github\.com/usnistgov/oscal-content|CHAPTER (?:ONE|TWO|THREE|FOUR)|APPENDIX [A-F]|PAGE \d+|[ivxlcdm]+|_+)$', re.I)
CROPS = {24:(70,205,542,485), 25:(70,164,542,469), 26:(70,217,542,590),
         27:(70,178,542,521), 28:(70,190,542,672), 29:(70,291,542,505),
         30:(89,289,523,359), 47:(69,108,747,477), 731:(68,86,724,398)}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.pages = defaultdict(list)
        self.stack = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        page = attrs.get('data-source-page', self.stack[-1][1] if self.stack else None)
        hidden = (tag in ('script', 'style') or 'data-pagefind-ignore' in attrs or
                  (tag == 'details' and any(x[0] == 'figure' for x in self.stack)) or
                  (self.stack[-1][2] if self.stack else False))
        if tag not in VOID:
            self.stack.append((tag, page, hidden))
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        if self.stack and self.stack[-1][2]:
            return
        self.parts.append(data)
        if self.stack and self.stack[-1][1]:
            self.pages[self.stack[-1][1]].append(data)

def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s)).replace('\u00ad', '').replace('•', '')

def span_text(span):
    bold_italic = 'bolditalic' in span['font'].lower().replace('-', '')
    glyphs = {'\ue000': 'ti', '\ue001': 'tt' if bold_italic else 'tti',
              '\ue002': 'ft', '\ue003': 'tti' if bold_italic else 'tt', '\ue004': 'tf'}
    return span['text'].translate(str.maketrans(glyphs))

def source_lines(page, page_number):
    crop = fitz.Rect(CROPS[page_number]) if page_number in CROPS else None
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            if crop and crop.contains(fitz.Rect(line['bbox'])):
                continue
            text = ''.join(span_text(span) for span in line['spans']).strip()
            if page_number == 11:
                text = re.sub(r'\.{3,}', '', text)
            yield text

def check_page_inventory(page, number, rendered):
    # Physical layout boundaries exclude vertical running notices, footers and headers.
    bounds = fitz.Rect(CROPS[number]) if number in CROPS else None
    source = []
    for block in page.get_text('dict', flags=3)['blocks']:
        for line in block['lines']:
            box = fitz.Rect(line['bbox'])
            if number >= 4 and (box.x0 < 55 or box.y0 < 54 or
                               box.y0 > (551 if page.rect.width > 700 else 729)):
                continue
            if bounds and bounds.contains(box):
                continue
            source.extend(span_text(s) for s in line['spans'])
    original = ''.join(source)
    if number == 11:
        original = re.sub(r'\.{2,}', '', original)
    assert Counter(norm(original)) == Counter(rendered), f'Character inventory on physical page {number}'


def check_note_position(page, ref, number):
    # Compare the call's immediate neighbours to the actual printed superscript line.
    parent = ref.find_parent(['p', 'li', 'th', 'td'])
    ref.string = '§'
    context = norm(parent.get_text())
    ref.string = str(number)
    for block in page.get_text('dict', flags=3)['blocks']:
        for line in block['lines']:
            spans = line['spans']
            for i, span in enumerate(spans):
                if span['text'].strip() != str(number) or not 5.3 < span['size'] < 8.1:
                    continue
                before = norm(''.join(s['text'] for s in spans[:i]))[-18:]
                after = norm(''.join(s['text'] for s in spans[i+1:]))[:18]
                if (before or after) and before + '§' + after in context:
                    return
    raise AssertionError(f'Footnote {number} is displaced')


def main():
    if not REPORT.exists():
        print(f'Conversion not present: {REPORT}', file=sys.stderr)
        return 2
    html = json.loads(REPORT.read_text())['html']
    soup = BeautifulSoup(html, 'html.parser')
    note_errors = []
    for number in range(1, 66):
        refs = soup.find_all(id=f'note-ref-{number}')
        notes = soup.find_all(id=f'note-{number}')
        if len(refs) != 1 or len(notes) != 1:
            note_errors.append(f'{number}: expected one reference and one note')
            continue
        parent = refs[0].find_parent(attrs={'data-source-page': True})
        if not parent or parent['data-source-page'] != notes[0].get('data-source-page'):
            note_errors.append(f'{number}: source page mismatch')
        if refs[0].get('href') != f'#note-{number}' or not notes[0].find('a', href=f'#note-ref-{number}'):
            note_errors.append(f'{number}: missing reciprocal link')
    p = Text()
    p.feed(html)
    rendered = norm(''.join(p.parts))
    pages = {str(k): norm(''.join(v)) for k, v in p.pages.items()}
    missing = []
    misplaced = []
    checked = [0, 0, 0]
    with fitz.open(PDF) as doc:
        for number in range(1, 66):
            ref = soup.find(id=f'note-ref-{number}')
            source_page = ref.find_parent(attrs={'data-source-page': True})['data-source-page']
            check_note_position(doc[int(source_page)-1], ref, number)
        for number, (page_number, box) in enumerate(CROPS.items(), 1):
            expected = doc[page_number-1].get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(box), alpha=False)
            image = fitz.Pixmap(str(ROOT / f'public/figures/nist-sp-800-53a-r5/figure-{number}.png'))
            if (expected.width, expected.height, expected.samples) != (image.width, image.height, image.samples):
                raise ValueError(f'Figure {number} does not match the source crop')
        for index, page in enumerate(doc):
            section = 0 if index < 50 else 1 if index < 694 else 2
            if section != 1:
                check_page_inventory(page, index + 1, pages[str(index+1)])
            nearby = ''.join(pages.get(str(n), '') for n in range(max(1, index), index+3))
            for line in source_lines(page, index + 1):
                if FURNITURE.match(line) or len(norm(line)) < 20:
                    continue
                checked[section] += 1
                item = (index + 1, line)
                if norm(line) not in rendered:
                    missing.append(item)
                elif norm(line) not in nearby:
                    misplaced.append(item)
    print('Checked source line fragments (front/body, catalog, appendices):', checked)
    print('Missing fragments:', len(missing))
    for page, line in missing[:200]:
        print(f'{page}: {line}')
    print('Present globally but absent from page or adjacent pages:', len(misplaced))
    for page, line in misplaced[:100]:
        print(f'{page}: {line}')
    print('Footnote pair errors:', len(note_errors))
    for error in note_errors:
        print(error)
    return bool(missing or misplaced or note_errors)

if __name__ == '__main__':
    sys.exit(main())
