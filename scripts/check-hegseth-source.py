"""Compare the full ordered source text independently of importer block grouping."""
from pathlib import Path
import fitz,json,re,hashlib
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
slug='hegseth-articles-of-impeachment'
pdf=ROOT/f'public/sources/{slug}.pdf'
r=json.loads((ROOT/f'src/content/reports/{slug}.json').read_text())
soup=BeautifulSoup(r['html'],'html.parser')
source=[]
for p in fitz.open(pdf):
 for line in p.get_text('text',clip=fitz.Rect(0,0,p.rect.width,725)).splitlines():
  if not re.fullmatch(r'[.\s]*',line):source.append(line)
normalize=lambda t:''.join(t.split())
expected=normalize(' '.join(source));actual=normalize(soup.get_text(' '))
assert expected==actual,'Ordered source text differs'
assert ' '.join(source).split()==soup.get_text().split(), 'Source word spacing differs'
assert len(soup.select('h2'))==8
assert r['sourceSha256']==hashlib.sha256(pdf.read_bytes()).hexdigest()
assert {int(p) for el in soup.select('[data-source-pages]') for p in el['data-source-pages'].split(',')}==set(range(1,35))
source_labels=re.findall(r'\(([0-9]+|[A-Z]|[ivx]+)\)\s', ' '.join(source))
html_labels=re.findall(r'\(([0-9]+|[A-Z]|[ivx]+)\)\s',soup.get_text(' '))
assert source_labels==html_labels
labels=[re.match(r'^\(([^)]+)\)',li.get_text().strip())[1] for li in soup.select('li')]
expected_labels=[m[1] for line in source if (m:=re.match(r'^\(([0-9]{1,2}|[A-Z]|[ivx]+)\)\s*',line))]
assert labels==expected_labels, 'Clause list labels differ'
assert len(labels)==77
roman_child=next(li for li in soup.select('li') if li.get_text().startswith('(I)'))
assert roman_child.parent['type']=='I' and roman_child['value']=='1'
assert roman_child.parent.parent.name=='li' and roman_child.parent.parent.get_text().startswith('(i)')
assert not soup.select('table'), 'New tables need independent cell checks'
print(f'PASS: Hegseth ordered source text ({len(expected):,} characters), eight articles, all 34 page mappings and source checksum.')
