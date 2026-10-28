"""Verify approved content, semantic structure, deployment paths, and local links."""
from pathlib import Path
import hashlib,json,subprocess,sys
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'evidence/approved-content.json').read_text())
for name,digest in manifest.items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,f'Approved source changed: {name}; re-review before updating baseline'
subprocess.run([sys.executable,str(ROOT/'scripts/check-source.py')],check=True)
for file in (ROOT/'src/content/reports').glob('*.json'):
 report=json.loads(file.read_text());soup=BeautifulSoup(report['html'],'html.parser')
 required=['slug','title','identifier','authors','date','sourceUrl','sourceSha256','pdfPath','description','headings','html']
 assert all(k in report for k in required),file
 assert (ROOT/'public'/report['pdfPath'].lstrip('/')).is_file()
 ids=[n['id'] for n in soup.select('[id]')];assert len(ids)==len(set(ids)),'Duplicate IDs'
 for node in soup.select('[headers]'):
  assert all(i in ids for i in node['headers']),'Missing table header'
 for a in soup.select('a[href^="#"]'):
  assert a['href'][1:] in ids,f'Broken anchor {a["href"]}'
 if report['slug']=='nist-ir-8547':
  assert len(soup.select('table'))==8
  assert len(soup.select('dl dt'))==35
  assert len(soup.select('.footnotes li'))==4
  assert len(soup.select('.reference-label'))==31
  assert len(soup.select('.source-contents')[1].select('a'))==8
 # Exact rendered content equality ensures build transformations cannot silently lose text.
 built=ROOT/'dist/reports'/report['slug']/'index.html'
 if built.exists():
  actual=BeautifulSoup(built.read_text(),'html.parser').select_one('.report-prose')
  normalize=lambda s:''.join(s.get_text().split())
  assert normalize(actual)==normalize(soup),'Built report differs from approved content'
if (ROOT/'dist').exists():
 for file in (ROOT/'dist').rglob('*.html'):
  soup=BeautifulSoup(file.read_text(),'html.parser')
  ids=[n['id'] for n in soup.select('[id]')];assert len(ids)==len(set(ids)),f'Duplicate built IDs: {file}'
  for node in soup.select('[href],[src]'):
   raw=node.get('href',node.get('src'));url=urlsplit(raw)
   if url.scheme or url.netloc or raw.startswith('data:'):continue
   path=unquote(url.path)
   if path.startswith('/'):
    assert path.startswith('/pdftoweb/'),f'Broken deployment base {raw}'
    target=ROOT/'dist'/path.removeprefix('/pdftoweb/')
   else:target=file.parent/path if path else file
   if target.is_dir():target=target/'index.html'
   assert target.exists(),f'Broken local link {raw} in {file}'
   if url.fragment and target.suffix=='.html':
    dest=BeautifulSoup(target.read_text(),'html.parser')
    assert dest.find(id=unquote(url.fragment)),f'Broken fragment {raw}'
print('PASS: approved source/content hashes, source inventory, tables, glossary, references, footnotes, build text and local links.')
