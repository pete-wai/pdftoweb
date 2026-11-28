"""Convert the supplied 733-page January 2022 edition of SP 800-53A Rev. 5."""
from bisect import bisect_right
from collections import defaultdict
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import re

from bs4 import BeautifulSoup
from pdfminer.pdftypes import resolve1
from sp53_matter import restore_paragraphs, link_notes, figure_equivalents
import pdfplumber
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'nist-sp-800-53a-r5'
PDF = ROOT / f'public/sources/{SLUG}.pdf'
FIG = ROOT / 'public/figures' / SLUG
EVIDENCE = ROOT / 'evidence' / SLUG
TITLE = 'Assessing Security and Privacy Controls in Information Systems and Organizations'
SOURCE = 'https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53Ar5.pdf'
# Illustration boundaries in unrotated PDF points, exclusive of typeset captions.
CROPS = {24:(70,205,542,485),25:(70,164,542,469),26:(70,217,542,590),
         27:(70,178,542,521),28:(70,190,542,672),29:(70,291,542,505),
         30:(89,289,523,359),47:(69,108,747,477),731:(68,86,724,398)}
ALTS = ['Annotated AC-17 assessment procedure showing how objectives relate to the control.',
        'CM-04 impact analysis procedure with security and privacy objectives.',
        'CM-02 baseline configuration procedure showing assignment parameters.',
        'MP-07 media use procedure showing assignment and selection parameters.',
        'CA-03 information exchange procedure showing a selection with an embedded assignment.',
        'AC-17(01) monitoring and control assessment procedure.',
        'Assessment process from preparation and plan development through assessment and analysis.',
        'Pre-assessment, assessment, and post-assessment activities and their outputs.',
        'CP-03 contingency training objectives, assessment findings, and assessor comments.']


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def letters(text, font):
    italic = 'BoldItalic' in font
    return text.translate(str.maketrans({'\ue000':'ti','\ue001':'tt' if italic else 'tti',
        '\ue002':'ft','\ue003':'tti' if italic else 'tt','\ue004':'tf',
        'ﬀ':'ff','ﬁ':'fi','ﬂ':'fl','ﬃ':'ffi','ﬄ':'ffl'}))


def styled(value, font):
    value = escape(letters(value, font))
    if 'Italic' in font:
        value = f'<em>{value}</em>'
    if 'Bold' in font:
        value = f'<strong>{value}</strong>'
    return value


def table_html(label, rows, identifier, page):
    return (f'<figure class="table-figure" data-source-page="{page}"><div class="table-scroll" '
            f'tabindex="0" role="region" aria-labelledby="{identifier}"><table>'
            f'<caption id="{identifier}">{label}</caption>{rows}</table></div></figure>')


def catalog(doc):
    """Use the printed horizontal rules to keep every identifier beside its text."""
    out = []
    for page in range(51,695):
        pdf = doc[page-1]
        rules = set()
        for drawing in pdf.get_drawings():
            box = drawing['rect']
            if box.height < .01 and box.x0 < 300 < box.x1:
                rules.add(round(box.y0,1))
        rows = defaultdict(lambda: defaultdict(list))
        for block in pdf.get_text('dict',flags=3)['blocks']:
            for line in block['lines']:
                x,y,_,bottom = line['bbox']
                if x < 70 or y < 55 or y >= 714:
                    continue
                text = ''.join(styled(s['text'],s['font']) for s in line['spans'] if s['text'].strip() or s['text'])
                if not re.sub('<[^>]*>', '', text).strip():
                    continue
                row = bisect_right(sorted(rules),(y+bottom)/2)
                col = 0 if x<140 else 1 if x<225 else 2
                rows[row][col].append(text.strip())
        label = ''
        body = []
        def flush():
            if label:
                identifier = f'procedure-{page}-{len(out)}'
                out.append(table_html(label,''.join(body),identifier,page))
                body.clear()
        for cols in rows.values():
            cells = {k:' '.join(v) for k,v in cols.items()}
            if 0 in cells:
                flush()
                label = ''
                if 1 not in cells:
                    out.append(f'<h3 data-source-page="{page}">{cells[0]}</h3>')
                    continue
                label = ' '.join(cells.values())
            elif 2 in cells:
                body.append(f'<tr data-source-page="{page}"><th scope="row">{cells.get(1,"")}</th><td>{cells[2]}</td></tr>')
            else:
                body.append(f'<tr data-source-page="{page}"><td colspan="2">{cells[1]}</td></tr>')
        flush()
    return ''.join(out)


class Matter:
    """Word’s logical structure retains inline links, footnotes, and multi-page tables."""
    def __init__(self, source):
        self.pages = {}
        self.content = {}
        for page in source.pages:
            n = page.page_number
            self.pages[page.page_obj.pageid] = n
            if 51 <= n <= 694:
                continue
            chunks = defaultdict(list)
            for char in page.chars:
                if char['mcid'] is not None:
                    chunks[char['mcid']].append(char)
            for key, chars in chunks.items():
                runs = []
                last = None
                for char in chars:
                    font = char['fontname']
                    if char['text'].isdigit() and (6.3 < char['size'] < 7.2 or
                            (n == 33 and 7.9 < char['size'] < 8.1)):
                        font += '|sup'
                    if last and not last['text'].isspace() and not char['text'].isspace():
                        if (abs(char['top']-last['top']) > max(5,char['size']*.7)
                            or char['x0']-last['x1'] > char['size']*.19):
                            runs.append(('',' '))
                    if runs and runs[-1][0]==font:
                        runs[-1] = (font,runs[-1][1]+char['text'])
                    else:
                        runs.append((font,char['text']))
                    last = char
                self.content[n,key]=''.join(f'<sup>{v}</sup>' if f.endswith('|sup') else styled(v,f) for f,v in runs)
            page.close()

    def render(self,node,page=1):
        node=resolve1(node)
        if isinstance(node,int):
            value=self.content.get((page,node),'')
            return (f'<pdf-run page="{page}">{value}</pdf-run>' if value else ''),page
        if isinstance(node,list):
            children=[self.render(c,page) for c in node]
            return ''.join(v for v,_ in children),next((p for v,p in children if v.strip()),page)
        if not isinstance(node,dict):
            return '',page
        if 'Pg' in node:
            page=self.pages[node['Pg'].objid]
        if 'MCID' in node:
            return self.render(node['MCID'],page)
        kind=getattr(node.get('S'),'name','')
        if kind=='Figure' and page in CROPS:
            index=list(CROPS).index(page)
            return (f'<figure data-source-page="{page}"><img loading="lazy" alt="{ALTS[index]}" '
                    f'src="/pdftoweb/figures/{SLUG}/figure-{index+1}.png"></figure>'),page
        body,start=self.render(node.get('K'),page)
        if not re.sub('<[^>]+>','',body).strip() and '<img' not in body:
            return '',start
        if kind=='Link':
            kids=resolve1(node.get('K'))
            for child in kids if isinstance(kids,list) else [kids]:
                obj=resolve1(child)
                if isinstance(obj,dict) and 'Obj' in obj:
                    action=resolve1(resolve1(obj['Obj']).get('A',{}))
                    dest=resolve1(action.get('D',[]))
                    if isinstance(dest,list) and dest and getattr(dest[0],'objid',None) in self.pages:
                        return f'<a href="#pdf-page-{self.pages[dest[0].objid]}">{body}</a>',start
                    uri=resolve1(action.get('URI',b'')).decode('latin1')
                    if uri.startswith(('https://','http://','mailto:')):
                        return f'<a href="{escape(uri,quote=True)}">{body}</a>',start
        tag={'P':'p','H1':'h2','H2':'h3','H3':'h4','H4':'h5','Footnote':'aside',
             'Table':'table','TR':'tr','TH':'th','TD':'td','L':'ul','LI':'li',
             'TOCI':'p','TOC':'nav'}.get(kind)
        if tag:
            attrs=f' data-source-page="{start}"'
            if kind in ('TH','TD'):
                props=resolve1(node.get('A',{}))
                for prop in props if isinstance(props,list) else [props]:
                    if isinstance(prop,dict):
                        for key in ('ColSpan','RowSpan'):
                            if key in prop:
                                attrs+=f' {key.lower()}="{prop[key]}"'
            return f'<{tag}{attrs}>{body}</{tag}>',start
        return body,start


def generate():
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    FIG.mkdir(parents=True,exist_ok=True)
    with pymupdf.open(PDF) as doc:
        save(EVIDENCE/'source-pages.json',[p.get_text() for p in doc])
        for idx,(page,clip) in enumerate(CROPS.items(),1):
            doc[page-1].get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(clip)).save(FIG/f'figure-{idx}.png')
        controls=catalog(doc)
    with pdfplumber.open(PDF) as src:
        html,_=Matter(src).render(src.doc.catalog['StructTreeRoot'])
    soup=BeautifulSoup(html,'html.parser')
    for run in soup.select('pdf-run'):
        physical=run['page']
        block=run.find_parent(attrs={'data-source-page':True})
        if block and physical!=block['data-source-page']:
            run.name='span'
            run.attrs={'data-source-page':physical}
        else:
            run.unwrap()
    with pymupdf.open(PDF) as doc:
        restore_paragraphs(soup,doc,styled)
        fix_matter(soup)
        link_notes(soup)
        # Physical breaks inside single paragraphs, checked on both adjoining pages.
        for page in (15,16,18,19,20,21,22,26,34,36,37,39,40,41,42,43,46,49,
                     720,721,723,725,733):
            continuation=soup.find(attrs={'data-source-page':str(page)},recursive=False)
            previous=continuation.find_previous_sibling()
            assert continuation.name=='p' and previous.name=='p'
            continuation.name='span'
            previous.append(' ')
            previous.append(continuation.extract())
        figure_equivalents(soup,doc,CROPS,styled)
    ref=soup.find(string=lambda s:s and s.strip()=='REFERENCES' and s.parent.find_parent(attrs={'data-source-page':'695'}))
    if not ref:
        ref=soup.find('h2',attrs={'data-source-page':'695'})
    else:
        ref=ref.find_parent('h2')
    ref.insert_before('CATALOG_PLACEHOLDER')
    html=str(soup).replace('CATALOG_PLACEHOLDER',controls)
    # Only section-level headings go in the global reader navigation.
    def heading(match):
        level=int(match[1])
        label=BeautifulSoup(match[3],'html.parser').get_text(' ',strip=True)
        key=re.sub('[^a-z0-9]+','-',label.lower()).strip('-')
        if key in used:
            key+=f'-{len(headings)}'
        used.add(key)
        headings.append(dict(id=key,level=level,text=label))
        return f'<h{level}{match[2]} id="{key}">{match[3]}</h{level}>'
    used=set()
    headings=[]
    html=re.sub(r'<h([23])([^>]*)>(.*?)</h\1>',heading,html,flags=re.S)
    soup=BeautifulSoup(html,'html.parser')
    for entry in soup.nav.select('p'):
        label,num=re.split(r'\.{2,}', ' '.join(entry.get_text().split()), maxsplit=1)
        digits=re.match(r'^(\d+\.\d+)\b',label)
        family=re.match(r'^(CHAPTER \w+|APPENDIX [A-F])\b',label)
        if digits:
            h=next(h for h in headings if h['text'].split()[0]==digits[1])
        elif family:
            h=next(h for h in headings if h['text'].upper()==family[1])
        else:
            h=next(h for h in headings if h['text'].upper()==label.strip().upper())
        a=soup.new_tag('a',href='#'+h['id'])
        a.string=label.strip()+' '+num.strip()
        entry.clear()
        entry.append(a)
    # Destinations in the PDF use physical pages, including multi-page table rows.
    seen=set()
    for node in soup.select('[data-source-page]'):
        page=node['data-source-page']
        if page not in seen:
            seen.add(page)
            anchor=soup.new_tag('span',id='pdf-page-'+page)
            if node.name in ('table','tr','th','td'):
                (node.select_one('p') or node.find(['th','td']) or node).insert(0,anchor)
            else:
                node.insert(0,anchor)
    assert len(seen)==733
    html=str(soup)
    save(ROOT/f'src/content/reports/{SLUG}.json',dict(slug=SLUG,title=TITLE,
         identifier='NIST SP 800-53A Rev. 5',authors=['Joint Task Force'],date='January 2022',
         sourceUrl=SOURCE,sourceSha256=sha256(PDF.read_bytes()).hexdigest(),pdfPath=f'/sources/{SLUG}.pdf',
         description='Assessment objectives, methods, and procedures for the security and privacy controls in NIST SP 800-53 Revision 5.',
         headings=headings,html=html))


def fix_matter(soup):
    for li in soup.select('li'):
        marker=li.find(string=lambda t:t.strip())
        if marker and marker.lstrip().startswith('•'):
            marker.replace_with(marker.lstrip()[1:].lstrip())
    for p in soup.select('p p, p aside, p table, p ul, p figure'):
        parent=p.find_parent('p')
        if parent:
            parent.name='div'
    for h in soup.select('h2,h3'):
        if len(h.get_text())>300:
            h.name='p'
    for p in soup.select('p'):
        if p.get_text(strip=True) in ('Executive Summary','Table of Contents','Acknowledgments'):
            p.name='h2'
    for table in soup.select('table'):
        page=int(table['data-source-page'])
        previous=table.find_previous(['p','h2'])
        caption=soup.new_tag('caption',id=f'table-{page}')
        if previous and previous.get_text(strip=True).upper().startswith('TABLE '):
            caption.extend(list(previous.contents))
            previous.decompose()
        else:
            caption['data-pagefind-ignore']=''
            caption.string={5:'Acknowledgments',695:'References',700:'Glossary',716:'Acronyms',
                            719:'Examine',722:'Interview',724:'Test'}.get(page,'Assessment method')
        table.insert(0,caption)
        for index,row in enumerate(table.select('tr')):
            cells=row.find_all(['td','th'],recursive=False)
            if page==5:
                group=0 if index<6 else 6 if index<12 else 12
                for col,cell in enumerate(cells):
                    if index==group:
                        cell.name='th'
                        cell['id']=f'credits-{index}-{col}'
                        cell['scope']='colgroup'
                        cell['colspan']='4' if group==12 else '2'
                    else:
                        cell.name='td'
                        cell['headers']=f'credits-{group}-{0 if group==12 else col}'
                        if group!=12:
                            cell['colspan']='2'
                continue
            if page in (30,34,41,44,719,722,724) and len(cells)==2:
                cells[1].name='td'
            if cells and cells[0].get_text(strip=True):
                cells[0].name='th'
                cells[0]['scope']='row'
        region=soup.new_tag('div',attrs={'class':'table-scroll','tabindex':'0','role':'region','aria-labelledby':caption['id']})
        table.wrap(region).wrap(soup.new_tag('figure',attrs={'class':'table-figure'}))
    for fig in soup.select('figure:has(img)'):
        pg=fig['data-source-page']
        cap=next((p for p in soup.select(f'p[data-source-page="{pg}"]') if re.match(r'FIGURE\s+\d+[.:]',p.get_text(strip=True))),None)
        if cap:
            cap.name='figcaption'
            fig.append(cap.extract())


if __name__=='__main__':
    generate()
