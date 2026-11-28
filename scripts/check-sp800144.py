"""Independently account for printed text on each physical SP 800-144 page."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT/'src/content/reports/nist-sp-800-144.json').read_text())
pdf = ROOT/'public'/report['pdfPath'].lstrip('/')
assert sha256(pdf.read_bytes()).hexdigest() == report['sourceSha256']
body = BeautifulSoup(report['html'], 'html.parser')
assert len(body.select('table')) == 5 and len(body.select('dl dt')) == 33
for number in range(1, 28):
    assert body.find(id=f'note-ref-{number}')['href'] == f'#note-{number}'
    assert body.find(id=f'note-{number}').find('a')['href'] == f'#note-ref-{number}'
for caption in body.select('caption[data-pagefind-ignore]'):
    caption.decompose()
pages = defaultdict(list)
for text in body.find_all(string=True):
    ancestor = text.find_parent(attrs={'data-source-page': True})
    if ancestor:
        pages[int(ancestor['data-source-page'])].append(text)

def characters(value):
    # Native list markers replace the two printed bullet shapes.
    return Counter(re.sub(r'[\s\uf03c\uf0a7▪]', '', value))

with pymupdf.open(pdf) as doc:
    for n, page in enumerate(doc, 1):
        text = ''.join(s['text'] for b in page.get_text('dict', flags=3)['blocks']
                       for line in b['lines'] if line['bbox'][1] < 730 for s in line['spans'])
        if n == 5:
            text = re.sub(r'\.{2,}', '', text)
        if n == 46:
            text = text.replace('Areas', '', 1).replace('Recommendations', '', 1)
        assert characters(text) == characters(''.join(pages[n])), f'Page {n} text differs'
print('SP 800-144: all 80 page inventories, five tables, 33 acronym pairs, and 27 footnotes passed.')
