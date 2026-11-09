"""Import the supplied resolution; retain wording, source pages and span emphasis."""
from pathlib import Path
import fitz, json, re, hashlib, html
ROOT=Path(__file__).resolve().parents[1]
SLUG='hegseth-articles-of-impeachment'
pdf=ROOT/f'public/sources/{SLUG}.pdf'
doc=fitz.open(pdf)
evidence=ROOT/'evidence'/SLUG
evidence.mkdir(exist_ok=True)
blocks=[]
source=[]
for pn,page in enumerate(doc,1):
 source.append({'page':pn,'text':page.get_text()})
 for b in page.get_text('dict')['blocks']:
  if 'lines' not in b or b['bbox'][1]>=725: continue
  spans=[s for l in b['lines'] for s in l['spans'] if s['text'].strip()]
  if not spans: continue
  text=' '.join(''.join(s['text'] for s in line['spans']).strip() for line in b['lines']).strip()
  if re.fullmatch(r'[. ]+',text):continue
  rendered=[]
  for line in b['lines']:
   parts=[]
   for s in line['spans']:
    t=html.escape(s['text'])
    if s['flags']&2:t=f'<em>{t}</em>'
    if s['flags']&16:t=f'<strong>{t}</strong>'
    parts.append(t)
   rendered.append(''.join(parts).strip())
  item={'page':pn,'pages':[pn],'text':text,'html':' '.join(rendered),'bbox':list(b['bbox'])}
  prev=blocks[-1] if blocks else None
  # Adjacent title lines and page-continuation paragraphs have no paragraph gap.
  near=prev and pn==prev['pages'][-1] and b['bbox'][1]-prev['bbox'][3]<5
  continuation=prev and pn>prev['pages'][-1] and not re.match(r'(ARTICLE |\([0-9A-Za-z]+\))',text) and not re.search(r'[.;:!?][”’"\']?$',prev['text']) and not prev['text'].startswith('ARTICLE ')
  if near or continuation:
   prev['text']+=' '+text;prev['html']+=' '+item['html'];prev['bbox']=item['bbox']
   if pn not in prev['pages']:prev['pages'].append(pn)
  else:blocks.append(item)
headings=[];output=[];stack=[]
def close_lists(depth=0):
 while len(stack)>depth:output.append('</li></ol>');stack.pop()
for i,b in enumerate(blocks):
 attrs=f'data-source-page="{b["page"]}" data-source-pages="{",".join(map(str,b["pages"]))}"'
 text=b['text'];content=b['html']
 if text.startswith('ARTICLE '):
  close_lists();roman=re.match(r'ARTICLE ([IVX]+)',text)[1];ident='article-'+roman.lower()
  headings.append({'id':ident,'text':text,'level':2});output.append(f'<h2 id="{ident}" {attrs}>{content}</h2>');continue
 marker=re.match(r'^\(([0-9]+|[A-Z]|[ivx]+)\)\s',text)
 if marker:
  label=marker[1];kind='1' if label.isdigit() else ('I' if label == 'I' else 'A' if label.isupper() else 'i')
  level={'1':1,'A':2,'i':3,'I':4}[kind]
  while stack and stack[-1][0]>level:close_lists(len(stack)-1)
  if stack and stack[-1][0]==level:output.append('</li>')
  else:output.append(f'<ol class="source-numbered" type="{kind}">');stack.append((level,kind))
  value=int(label) if kind=='1' else ord(label)-64 if kind=='A' else {'i':1,'ii':2,'iii':3,'iv':4,'v':5,'vi':6,'vii':7,'viii':8,'ix':9,'x':10}[label.lower()]
  # Keep literal source labels; suppress generated list markers.
  output.append(f'<li style="list-style-type:none" value="{value}" {attrs}>{content}')
 else:
  close_lists();output.append(f'<p {attrs}>{content}</p>')
close_lists()
report={'slug':SLUG,'title':'Impeaching Peter Brian Hegseth, Secretary of Defense, for high crimes and misdemeanors.','identifier':'H. RES. __ · 119th Congress','authors':['Mr. Massie (as identified in the supplied PDF)'],'date':'Undated','sourceUrl':f'/pdftoweb/sources/{SLUG}.pdf','sourceLabel':'User-supplied original PDF','sourceSha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pdfPath':f'/sources/{SLUG}.pdf','description':'User-supplied resolution containing eight articles of impeachment concerning Peter Brian Hegseth. The original PDF remains authoritative.','headings':headings,'html':'\n'.join(output)}
(ROOT/f'src/content/reports/{SLUG}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(evidence/'source-pages.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
(evidence/'block-map.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n')
print(len(blocks),'blocks;',len(headings),'articles')
