"""Independent ordered prose and cell comparisons against the retained GovRAMP PDF."""
from pathlib import Path
import hashlib,json,re
import pymupdf
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SLUG='govramp-rfc-gr-2601'
report=json.loads((ROOT/f'src/content/reports/{SLUG}.json').read_text())
source=ROOT/'public'/report['pdfPath'].lstrip('/')
assert hashlib.sha256(source.read_bytes()).hexdigest()==report['sourceSha256']
doc=pymupdf.open(source)
soup=BeautifulSoup(report['html'],'html.parser')
normalize=lambda t:re.sub(r'\s+','',t)
expected=[]
for pn in range(2,18):
 if pn==8:continue
 for block in doc[pn-1].get_text('dict')['blocks']:
  if block['type']:continue
  for line in block['lines']:
   y=line['bbox'][1]
   if (pn==7 and y>=449) or (pn==9 and 349<=y<468):continue
   text=''.join(s['text'] for s in line['spans']).strip()
   text=re.sub(r'^(?:[•▪\uf06f]\s*|o\s+|\d+\.\s+)','',text)
   expected.append(text)
prose=BeautifulSoup(str(soup),'html.parser')
for n in prose.select('.source-publication,.source-contents,.source-facsimiles,.table-figure'):n.decompose()
a,b=normalize(''.join(expected)),normalize(prose.get_text())
assert a==b,'GovRAMP prose differs in wording or order from original PDF'
# Independent rectangular extraction of each cell; whitespace and line wrapping only.
tables=soup.select('table');assert len(tables)==2
for ri,(pn,y0,y1) in enumerate([(7,476,660),(8,62,599)]):
 cells=tables[0].select('tbody tr')[ri].find_all(['th','td'],recursive=False)
 for ci,(x0,x1) in enumerate([(49,109),(109,313),(313,516)]):
  text=doc[pn-1].get_textbox(pymupdf.Rect(x0,y0,x1,y1))
  assert normalize(text)==normalize(cells[ci].get_text()),f'GovRAMP KSI cell mismatch {pn}/{ci}'
extracted=doc[8].find_tables().tables[0].extract()
for row,actual in zip(extracted,tables[1].select('tr'),strict=True):
 assert [normalize(v) for v in row]==[normalize(v.get_text()) for v in actual.find_all(['th','td'],recursive=False)]
assert [li.get('value') for li in soup.select('ol > li')]==[str(i) for i in range(1,5)]+['1','2']+[str(i) for i in range(1,10)]
assert len(soup.select('.source-contents li'))==23
assert len(soup.select('.source-facsimiles img'))==17
assert len(soup.select('.source-logo'))==1
for n in soup.select('img'):
 assert n.get('alt') and n.get('width') and n.get('height')
 assert (ROOT/'public'/n['src'].removeprefix('/pdftoweb/')).exists()
# Every original URI annotation is represented; destinations are not fetched or rewritten.
links={a['href'] for a in soup.select('a[href]')}
for p in doc:
 for link in p.get_links():
  if link.get('uri'):assert link['uri'] in links,f'Missing source URI {link["uri"]}'
print(f'PASS: GovRAMP ordered prose ({len(a)} characters), every table cell, source links, list numbering and 17 page images.')
