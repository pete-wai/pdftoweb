"""Independent character-accounting check against PDF text, excluding documented layout regions."""
import json,re,collections
from pathlib import Path
import pymupdf
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
pdf=pymupdf.open(root/'public/sources/nist-ir-8547.pdf')
tables=json.loads((root/'evidence/tables.json').read_text())
source=''
for page in range(2,35):
 if page in [6,7]:continue
 for b in pdf[page-1].get_text('dict')['blocks']:
  if b['type']:continue
  y=b['bbox'][1]
  if page>2 and (y<65 or y>730):continue
  if page==2 and y<65:continue
  text=''.join(s['text'] for l in b['lines'] for s in l['spans'])
  if any(r['page']==page and r['y0']-2<=y<=r['y1'] for t in tables for r in t['regions']):continue
  if re.match(r'Table [1-8]\.',text.strip()):continue
  source+=text
report=json.loads((root/'src/content/reports/nist-ir-8547.json').read_text())
soup=BeautifulSoup(report['html'],'html.parser')
for node in soup.select('.table-figure,.source-contents,[data-pagefind-ignore],#publication-details,#footnotes'):node.decompose()
# List bullets become HTML list markers; footnote numbers become semantic list values.
for node in soup.select('.footnotes li'):node.insert(0,str(node.get('value')))
def chars(t):return collections.Counter(re.sub(r'[\s•]','',t))
a,b=chars(source),chars(soup.get_text())
missing=a-b;extra=b-a
print('Source characters',sum(a.values()),'output',sum(b.values()))
print('Missing',dict(missing),'extra',dict(extra))
assert not missing and not extra,'Prose differs from source character inventory'
