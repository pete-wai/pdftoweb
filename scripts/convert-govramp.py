"""Report-specific GovRAMP RFC GR–2601 importer; never changes the NIST importer."""
from pathlib import Path
import hashlib, html, json, re
import pymupdf
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
SLUG='govramp-rfc-gr-2601'
PDF=ROOT/f'public/sources/{SLUG}.pdf'
OUT=ROOT/f'evidence/{SLUG}'
OUT.mkdir(exist_ok=True)
doc=pymupdf.open(PDF)
soup=BeautifulSoup('', 'html.parser')
headings=[]
def tag(name, text=None, **attrs):
 t=soup.new_tag(name,attrs=attrs)
 if text is not None:t.string=text
 return t
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def append_html(t,h):
 for n in list(BeautifulSoup(h,'html.parser').contents):t.append(n)
def lines(page):
 result=[]
 links=[l for l in page.get_links() if l.get('uri') or l.get('page',-1)>=0]
 for bi,b in enumerate(page.get_text('rawdict')['blocks']):
  if b['type']:continue
  for l in b['lines']:
   text=''.join(c['c'] for s in l['spans'] for c in s['chars'])
   if not text.strip():continue
   pieces=[]
   for s in l['spans']:
    runs=[]
    for c in s['chars']:
     r=pymupdf.Rect(c['bbox']);center=(r.tl+r.br)/2
     link=next((v for v in links if center in v['from']),None)
     href=(link.get('uri') or f'#pdf-page-{link["page"]+1}') if link else ''
     if runs and runs[-1][0]==href:runs[-1][1]+=c['c']
     else:runs.append([href,c['c']])
    value=''
    for href,txt in runs:
     txt=html.escape(txt)
     value+=f'<a href="{html.escape(href,quote=True)}">{txt}</a>' if href else txt
    if s['flags'] & 1:value=f'<sup>{value}</sup>'
    if 'Italic' in s['font']:value=f'<em>{value}</em>'
    if 'Bold' in s['font'] or 'Black' in s['font']:value=f'<strong>{value}</strong>'
    pieces.append(value)
   result.append(dict(text=text.strip(),html=''.join(pieces).strip(),bbox=l['bbox'],block=bi,size=max(s['size'] for s in l['spans'] if any(c['c'].strip() for c in s['chars']))))
 return result
all_lines=[lines(p) for p in doc]
(OUT/'source-pages.json').write_text(json.dumps([{'page':p.number+1,'text':p.get_text()} for p in doc],ensure_ascii=False,indent=2)+'\n')
# Exact facsimiles preserve every graphic, watermark, rule, printed page reference and layout.
for p in doc:
 target=ROOT/f'public/figures/{SLUG}/page-{p.number+1:02}.png'
 if not target.exists():p.get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False).save(target)
logo=ROOT/f'public/figures/{SLUG}/govramp-logo.png'
doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(49,48,238,100),alpha=False).save(logo)
cover=tag('div',**{'class':'source-publication','data-source-page':'1'})
cover.append(tag('img',src=f'/pdftoweb/figures/{SLUG}/govramp-logo.png',alt='GovRAMP',width='567',height='156',**{'class':'source-logo'}))
for text in ['November 2026','Request for Comments (RFC) GR – 2601','Proposed 20x Delta Assessment','info@govramp.org','9800 Crosspoint Boulevard, Indianapolis, Indiana 46256','https://govramp.org']:
 cover.append(tag('p',text))
soup.append(cover)
contents=tag('details',**{'class':'source-contents','data-source-page':'1'})
contents.append(tag('summary','Contents as printed'))
nav=tag('ul');contents.append(nav);soup.append(contents)
# Table cells are extracted by known, visually checked column bounds, not inferred reading order.
def cell(page,x0,y0,x1,y1):
 ls=[l for l in all_lines[page-1] if x0<=l['bbox'][0]<x1 and y0<=l['bbox'][1]<y1]
 chunks=[];last=None
 for l in ls:
  if last is None or l['bbox'][1]-last['bbox'][3]>4:chunks.append([])
  chunks[-1].append(l['text']);last=l
 return [' '.join(c) for c in chunks]
tables=[{'id':'ksi-mapping','caption':'Part A – Aligns 20x KSIs and NIST Guidance (FedRAMP .json Mapping)','pages':[7,8], 'headers':['20x KSI ID','GR KSI Guidance','GR Assessment Objectives'],'rows':[]}]
for pn,y0,y1 in [(7,476,660),(8,62,599)]:
 row=[cell(pn,*bounds) for bounds in [(49,y0,109,y1),(109,y0,313,y1),(313,y0,516,y1)]]
 row[0]=[''.join(row[0][0].split())]
 tables[0]['rows'].append({'page':pn,'cells':row})
tables.append({'id':'outstanding-controls','caption':'GovRAMP Verified Status (Moderate Impact Level)','pages':[9], 'headers':['GovRAMP Verified Status (Moderate Impact Level)','# of Controls Not Mapped to a KSI','# of Controls > or = 41.772','# of Controls < 41.772'], 'rows':[{'page':9,'cells':[[v] for v in row]} for row in [['Core','7','4','3'],['Ready','17','4','3'],['Authorized','120','24','96']]]})
(OUT/'tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n')
def add_table(data):
 f=tag('figure',**{'class':'table-figure','data-source-page':str(data['pages'][0])})
 cap=tag('figcaption',data['caption'],id=data['id']+'-caption',**{'data-pagefind-ignore':''});f.append(cap)
 scroll=tag('div',**{'class':'table-scroll','tabindex':'0','role':'region','aria-labelledby':cap['id']});f.append(scroll)
 t=tag('table');scroll.append(t)
 thead=tag('thead');tr=tag('tr');thead.append(tr);t.append(thead)
 for i,h in enumerate(data['headers']):tr.append(tag('th',h,scope='col',id=f'{data["id"]}-col-{i}'))
 body=tag('tbody');t.append(body)
 for ri,row in enumerate(data['rows']):
  tr=tag('tr',**{'data-source-page':str(row['page'])});body.append(tr)
  for ci,paras in enumerate(row['cells']):
   td=tag('th' if ci==0 else 'td',**({'scope':'row','id':f'{data["id"]}-row-{ri}'} if ci==0 else {'headers':f'{data["id"]}-row-{ri} {data["id"]}-col-{ci}'}))
   for para in paras:td.append(tag('p',para))
   tr.append(td)
 soup.append(f)
# Reading-order line grouping recovers paragraphs across extraction blocks and pages.
current=None;previous=None;stack=[];mapping=[]
for pn,ls in enumerate(all_lines[1:],2):
 anchor=tag('span',id=f'pdf-page-{pn}',**{'data-pagefind-ignore':''});soup.append(anchor)
 for l in ls:
  x,y,_,bottom=l['bbox']
  if pn==7 and y>=449:
   if not soup.find(id='ksi-mapping-caption'):add_table(tables[0])
   current=None;previous=None;stack=[];continue
  if pn==8:continue
  if pn==9 and 349<=y<468:
   if not soup.find(id='outstanding-controls-caption'):add_table(tables[1])
   current=None;previous=None;stack=[];continue
  txt=l['text'];h=l['html'];level=2 if l['size']>=18 else 3 if l['size']>=14 else None
  # Multi-line Part B heading.
  if level:
   if current and current.name==f'h{level}' and previous and previous['page']==pn and y-previous['bbox'][3]<4:
    append_html(current,' '+h);headings[-1]['text']+=' '+txt
   else:
    current=tag(f'h{level}',id=slug(txt),**{'data-source-page':str(pn)});append_html(current,h);soup.append(current)
    headings.append({'id':current['id'],'text':txt,'level':level})
   stack=[]
  else:
   marker=re.match(r'^(?:([•▪\uf06f]\s*|o\s+)|(\d+)\.\s+)',txt)
   if marker:
    # Remove only the marker from formatted HTML, retaining all substantive characters.
    fragment=BeautifulSoup(h,'html.parser');remaining=marker.end()
    for node in list(fragment.find_all(string=True)):
     if remaining:
      take=min(len(str(node)),remaining);node.replace_with(str(node)[take:]);remaining-=take
    h=str(fragment)
    kind='ol' if marker.group(2) else 'ul'
    while stack and (x<stack[-1][0]-3 or (abs(x-stack[-1][0])<3 and kind!=stack[-1][1].name)):stack.pop()
    if not stack or x>stack[-1][0]+3:
     ul=tag(kind)
     if stack and stack[-1][2] is not None:stack[-1][2].append(ul)
     else:soup.append(ul)
     stack.append([x,ul,None])
    current=tag('li',**{'data-source-page':str(pn)})
    if marker.group(2):current['value']=marker.group(2)
    append_html(current,h);stack[-1][1].append(current);stack[-1][2]=current
   else:
    adjacent=previous and ((previous['page']==pn and y-previous['bbox'][3]<5) or (previous['page']==pn-1 and (txt[0].islower() or txt.startswith('Simultaneously,'))))
    same_indent=not stack or x>=stack[-1][0]+12
    if current and current.name in ['p','li'] and adjacent and same_indent:
     append_html(current,' '+h)
    else:
     current=tag('p',**{'data-source-page':str(pn)});append_html(current,h)
     if stack and x>=stack[-1][0]+12 and pn in [10,11,12]:stack[-1][2].append(current)
     else:soup.append(current);stack=[]
  mapping.append({'page':pn,'bbox':list(l['bbox']),'text':txt})
  previous={**l,'page':pn}
# Cover contents retain the source's printed numbers; navigation targets actual headings.
for l in all_lines[0]:
 m=re.match(r'^(.*?)\s*\.{2,}\s*(\d+)$',l['text'])
 if not m:continue
 title,num=m.groups();target=next((v['id'] for v in headings if v['text']==title),None)
 if target is None:
  # Smaller appendix headings are still valid navigation destinations.
  p=next(p for p in soup.find_all('p') if p.get_text().strip()==title)
  p['id']=slug(title);target=p['id']
 li=tag('li');li.append(tag('a',title,href='#'+target));li.append(' '+num);nav.append(li)
cover.insert(0,tag('span',id='pdf-page-1'))
# Supplementary source images never replace or interrupt the continuous reading text.
section=tag('section',**{'class':'source-facsimiles','data-pagefind-ignore':''})
section.append(tag('h2','Original page layouts',id='original-page-layouts'))
section.append(tag('p','Expand any page to view all original graphics, branding, and printed layout. The reading text above is searchable and reflows with your text size.'))
for pn in range(1,18):
 detail=tag('details');detail.append(tag('summary',f'Original PDF · page {pn}'))
 figure=tag('figure');detail.append(figure)
 figure.append(tag('img',src=f'/pdftoweb/figures/{SLUG}/page-{pn:02}.png',alt=f'Original PDF page {pn}, preserving the source graphics and layout; its text is transcribed above.',loading='lazy',width='1224',height='1584'))
 a=tag('a',f'Open PDF page {pn}',href=f'/pdftoweb/sources/{SLUG}.pdf#page={pn}');figure.append(a)
 section.append(detail)
soup.append(section)
# Whitespace-only link fragments are extraction artifacts, not useful focus targets.
for a in list(soup.select('a')):
 if not a.get_text().strip():a.unwrap()
report={'slug':SLUG,'title':'Request for Comments (RFC) GR – 2601','identifier':'GovRAMP RFC GR – 2601','authors':['GovRAMP'],'date':'November 2026','sourceUrl':f'/pdftoweb/sources/{SLUG}.pdf','sourceLabel':'GovRAMP source PDF','sourceSha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'pdfPath':f'/sources/{SLUG}.pdf','description':'Proposed 20x Delta Assessment. GovRAMP’s request for stakeholder comments, with assessment mappings, response instructions, and the rationale for the proposed approach.','headings':headings+[{'id':'original-page-layouts','text':'Original page layouts','level':2}],'html':str(soup)}
(ROOT/f'src/content/reports/{SLUG}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(OUT/'block-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
print(f'Imported {len(doc)} pages, {len(tables)} tables, {len(headings)} headings.')
