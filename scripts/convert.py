"""Reproduce the NIST IR 8547 reading edition from the pinned source PDF.
Layout-specific extraction is intentionally explicit; new reports require their own review.
"""
from pathlib import Path
import hashlib, html, json, re
import pymupdf
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)
ROOT=Path(__file__).resolve().parents[1]
pdf=ROOT/'public/sources/nist-ir-8547.pdf'
doc=pymupdf.open(pdf)
tables=json.loads((ROOT/'evidence/tables.json').read_text())
BASE='/pdftoweb'
headings=[]; records=[]; notes=[]; audit=[]
def plain(h):return BeautifulSoup(h,'html.parser').get_text()
def norm(s):return re.sub(r'\s+',' ',s).strip()
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def combine(parts):
 out=''
 for part in parts:
  if not plain(part).strip():continue
  out+=('' if not out or plain(out).rstrip().endswith('-') else ' ')+part.strip()
 return out

def line_html(line, page, foot=False):
 out=''
 for s in line['spans']:
  t=s['text']; safe=html.escape(t)
  if not t.strip():out+=safe;continue
  # Body footnote marker is smaller than surrounding text, but unflagged in this PDF.
  if not foot and page==18 and t=='1' and s['size']<9:
   safe='<sup><a id="fnref-1" href="#fn-1" aria-label="Footnote 1">1</a></sup>'
  elif s['flags']&1:safe=f'<sup>{safe}</sup>'
  elif 'Italic' in s['font']:safe=f'<em>{safe}</em>'
  elif 'Bold' in s['font']:safe=f'<strong>{safe}</strong>'
  out+=safe
 return out.strip()

def heading(text, page, level=2):
 ident=slug(text)
 headings.append({'id':ident,'text':text,'level':level})
 return {'tag':f'h{level}','html':html.escape(text),'page':page,'id':ident}

# Cover 1 repeats cover 2. Keep the complete second cover in a modest front-matter section.
records.append(heading('Publication details',2))
for page in range(2,35):
 if page in (6,7):continue # replaced below by linked, faithful original navigation
 pg=doc[page-1]
 blocks=[b for b in pg.get_text('dict')['blocks'] if b['type']==0]
 blocks.sort(key=lambda b:(round(b['bbox'][1],1),b['bbox'][0]))
 events=[]
 for b in blocks:
  y=b['bbox'][1]
  if page>2 and (y<65 or y>730):continue
  if page==2 and y<65:continue
  raw=combine([html.escape(''.join(s['text'] for s in l['spans'])) for l in b['lines']])
  if not raw.strip():continue
  if any(r['page']==page and r['y0']-2<=y<=r['y1'] for t in tables for r in t['regions']):continue
  if re.match(r'Table [1-8]\.',plain(raw)):continue
  # Physical footnotes become endnotes with return links.
  is_note=page in (18,23,25) and y>670 and max(s['size'] for l in b['lines'] for s in l['spans'])<9
  if is_note:
   txt=combine([line_html(l,page,True) for l in b['lines']]); num=plain(txt).strip()[0]
   txt=re.sub(r'^'+num+r'\s*','',txt)
   notes.append({'number':num,'html':txt,'page':page});audit.append({'page':page,'kind':'footnote','source':plain(raw),'output':num+' '+plain(txt)})
   continue
  lines=b['lines']
  first=norm(''.join(s['text'] for s in lines[0]['spans']))
  # Split metadata and glossary labels from their body text.
  if (page==3 or page>=32) and all('Bold' in s['font'] for s in lines[0]['spans'] if s['text'].strip()) and len(lines)>1:
   groups=[]
   for line in lines:
    spans=[sp for sp in line['spans'] if sp['text'].strip()]
    if not spans:continue
    if all('Bold' in sp['font'] for sp in spans):groups.append([line]);groups.append([])
    else:
     if not groups:groups.append([])
     groups[-1].append(line)
   groups=[g for g in groups if g]
  else:groups=[lines]
  for group in groups:
   text=combine([line_html(l,page) for l in group]); ptext=norm(plain(text))
   if page==2 or (page==3 and (ptext.startswith('David Cooper:') or ptext.startswith('pqc-transition@'))):
    text='<br/>'.join(line_html(l,page) for l in group if plain(line_html(l,page)).strip())
   if not ptext:continue
   firstsp=[s for s in group[0]['spans'] if s['text'].strip()]
   allbold=all('Bold' in s['font'] for s in firstsp)
   tag='p';ident=None
   m=re.match(r'^(\d+(?:\.\d+)*\.)\s',ptext)
   if (m and allbold) or ptext in ['Abstract','Keywords','Reports on Computer Systems Technology','Patent Disclosure Notice','References','Appendix A. Glossary']:
    level=min(4,m[1].count('.')+1) if m else 2
    ev=heading(ptext,page,level)
   elif page>=32 and allbold:
    ev={'tag':'dt','html':text,'page':page}
   elif page>=32:ev={'tag':'dd','html':text,'page':page}
   elif page==3 and allbold and len(group)==1 and ptext!='All comments are subject to release under the Freedom of Information Act (FOIA).':
    ev=heading(ptext,page,3)
   else:
    if ptext.startswith('•'):
     text=re.sub(r'^(?:<[^>]+>)*•\s*','',text);tag='li'
    ev={'tag':tag,'html':text,'page':page}
   ev.update(y=group[0]['bbox'][1],bottom=group[-1]['bbox'][3])
   events.append(ev)
   audit.append({'page':page,'kind':'block','source':norm(combine([html.escape(''.join(s['text'] for s in l['spans'])) for l in group])),'output':plain(text)})
 for t in tables:
  if t['regions'][0]['page']==page:events.append({'tag':'table','table':t,'page':page,'y':t['regions'][0]['y0']-15,'bottom':t['regions'][0]['y1']})
 events.sort(key=lambda e:e['y'])
 records.extend(events)

# Restore extraction-fragmented prose: only visually confirmed continuations.
for i in range(len(records)-1,0,-1):
 cur,prev=records[i],records[i-1]
 if cur['tag']==prev['tag']=='p' and ((cur['page']!=prev['page'] and cur['page'] in [9,18,19,21,25]) or (cur['page']==26 and plain(cur['html']).startswith('SP80052]'))):
  prev['html']=combine([prev['html'],cur['html']]);prev['endPage']=cur['page'];records.pop(i)

# References consist of hanging labels and text, sometimes spanning a physical page.
start=next(i for i,r in enumerate(records) if r.get('id')=='references')+1
end=next(i for i,r in enumerate(records) if r.get('id')=='appendix-a-glossary')
reftext=combine([r['html'] for r in records[start:end]])
# Reference labels are unformatted and occur at the start of each entry.
refs=re.split(r'(\[(?:EO|FIPS|SP|NCCOE|NIST|NSM|OMB|PQC|RFC)[A-Z0-9-]*\])',reftext)
# Instead split using PDF left-column labels, not bracket citations in prose.
labels=[]
for p in range(28,32):
 for b in doc[p-1].get_text('dict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   t=norm(''.join(s['text'] for s in l['spans']))
   if l['bbox'][0]<80 and re.fullmatch(r'\[[A-Z0-9-]+\]',t):labels.append(t)
pattern='('+'|'.join(re.escape(x) for x in labels)+')'
parts=re.split(pattern,reftext)
refrecords=[]
for i in range(1,len(parts),2):
 label=parts[i];content=parts[i+1].strip()
 refrecords.append({'tag':'p','html':f'<span class="reference-label">{label}</span> '+content,'page':28,'id':'ref-'+label[1:-1].lower()})
records[start:end]=refrecords

# Source navigation retains the printed TOC's differing title for section 4.
bodyhead=[h for h in headings if re.match(r'^\d+\.',h['text']) or h['text'] in ['References','Appendix A. Glossary']]
nav='<details class="source-contents"><summary>Table of Contents</summary><ol>'
for h in bodyhead:
 label=h['text'] if h['text']!='4. PQC Standards Transition Timeline' else '4. Toward a PQC Standards Transition Timeline'
 nav+=f'<li class="level-{h["level"]}"><a href="#{h["id"]}">{html.escape(label)}</a></li>'
nav+='</ol></details><details class="source-contents"><summary>List of Tables</summary><ol>'
for t in tables:nav+=f'<li><a href="#table-{t["number"]}">{html.escape(t["caption"])}</a></li>'
nav+='</ol></details>'
index=next(i for i,r in enumerate(records) if r.get('id')=='1-introduction')
records.insert(index,{'tag':'raw','html':nav,'page':6})

def linkify(h):
 soup=BeautifulSoup(h,'html.parser')
 for node in list(soup.find_all(string=True)):
  if node.parent.name in ('a','script','style'):continue
  t=str(node)
  # References are clickable without changing their visible labels.
  pattern=r'https?://[^\s<>]+|\[(?:'+'|'.join(re.escape(x[1:-1]) for x in labels)+r')\]'
  out=[];pos=0
  for m in re.finditer(pattern,t):
   out.append(html.escape(t[pos:m.start()]));label=m[0]
   href=label if label.startswith('http') else '#ref-'+label[1:-1].lower()
   out.append(f'<a href="{html.escape(href,quote=True)}">{html.escape(label)}</a>');pos=m.end()
  if out:
   out.append(html.escape(t[pos:]));node.replace_with(BeautifulSoup(''.join(out),'html.parser'))
 return str(soup)

def render_table(t):
 n=t['number'];s=f'<figure class="table-figure" id="table-{n}" data-source-page="{t["regions"][0]["page"]}"><div class="table-scroll" role="region" tabindex="0" aria-labelledby="table-caption-{n}"><table><caption id="table-caption-{n}">{html.escape(t["caption"])}</caption><thead><tr>'
 for i,c in enumerate(t['headers']):s+=f'<th scope="col" id="t{n}-col-{i}">{c}</th>'
 s+='</tr></thead><tbody>'
 family=None
 for ri,row in enumerate(t['rows']):
  s+='<tr>'
  for ci,cell in enumerate(row):
   if cell is None:continue
   val=cell['text'] if isinstance(cell,dict) else cell
   span=cell.get('rowspan',1) if isinstance(cell,dict) else 1
   if ci==0:
    family=f't{n}-family-{ri}';s+=f'<th id="{family}" scope="{"rowgroup" if span>1 else "row"}" rowspan="{span}">{val}</th>'
   else:s+=f'<td headers="t{n}-col-{ci} {family}">{val}</td>'
  s+='</tr>'
 return s+'</tbody></table></div></figure>'

out=[];group=None
for r in records:
 tag=r['tag'];newgroup='ul' if tag=='li' else 'dl' if tag in ('dt','dd') else None
 if group!=newgroup:
  if group:out.append(f'</{group}>')
  if newgroup:out.append(f'<{newgroup}>')
  group=newgroup
 if tag=='table':out.append(render_table(r['table']));continue
 if tag=='raw':out.append(r['html']);continue
 ident=f' id="{r["id"]}"' if r.get('id') else ''
 content=r['html']
 if tag.startswith('h'):
  content+=f' <a class="source-page" data-pagefind-ignore href="{BASE}/sources/nist-ir-8547.pdf#page={r["page"]}" aria-label="View source PDF page {r["page"]}">↗</a>'
 out.append(f'<{tag}{ident} data-source-page="{r["page"]}">{content}</{tag}>')
if group:out.append(f'</{group}>')
out.append('<section class="footnotes" aria-labelledby="footnotes"><h2 id="footnotes">Footnotes</h2><ol>')
for note in notes:
 n=note['number'];out.append(f'<li id="fn-{n}" value="{n}" data-source-page="{note["page"]}">{note["html"]} <a data-pagefind-ignore href="#fnref-{n}" aria-label="Return to footnote {n} reference">↩</a></li>')
out.append('</ol></section>')
headings.append({'id':'footnotes','text':'Footnotes','level':2})
result={'slug':'nist-ir-8547','title':'Transition to Post-Quantum Cryptography Standards','identifier':'NIST IR 8547','authors':['Dustin Moody','Ray Perlner','Andrew Regenscheid','Angela Robinson','David Cooper'],'date':'October 2026','sourceUrl':'https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf','pdfPath':'/sources/nist-ir-8547.pdf','sourceSha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'description':'NIST’s approach to transitioning from quantum-vulnerable cryptographic algorithms to post-quantum standards.','headings':headings,'html':linkify('\n'.join(out))}
(ROOT/'src/content/reports/nist-ir-8547.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'evidence/block-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(ROOT/'evidence/source-pages.json').write_text(json.dumps([{'page':i+1,'text':p.get_text()} for i,p in enumerate(doc)],ensure_ascii=False,indent=2)+'\n')
print(f'Converted {len(records)} blocks, {len(headings)} headings, {len(tables)} tables, {len(notes)} footnotes, {len(refrecords)} references.')
