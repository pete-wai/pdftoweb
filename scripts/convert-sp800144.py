"""Import NIST SP 800-144 using its ordered PDF structure tree and marked content."""
from collections import defaultdict
from hashlib import sha256
from html import escape
from itertools import groupby
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
from pdfminer.pdftypes import resolve1
import pdfplumber
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'nist-sp-800-144'
PDF = ROOT / f'public/sources/{SLUG}.pdf'
EVIDENCE = ROOT / 'evidence' / SLUG
FIGURES = ROOT / 'public/figures' / SLUG
TITLE = 'Guidelines on Security and Privacy in Public Cloud Computing'
SOURCE = 'https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-144.pdf'


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


class TaggedSource:
    def __init__(self, source):
        self.pages = {}
        self.runs = defaultdict(list)
        for page in source.pages:
            self.pages[page.page_obj.pageid] = page.page_number
            for char in page.chars:
                if char['mcid'] is None:
                    continue
                self.runs[page.page_number, char['mcid']].append(
                    (char['fontname'], round(char['size']), char['text']))
            page.close()

    def render(self, node, page=1, note=False):
        node = resolve1(node)
        if isinstance(node, list):
            return ''.join(self.render(child, page, note) for child in node)
        if isinstance(node, int):
            parts = []
            for (font, size), chars in groupby(self.runs[page, node], key=lambda c: c[:2]):
                value = escape(''.join(c[2] for c in chars))
                if 'Webdings' in font or 'Wingdings' in font:
                    continue
                if value.strip().isdigit() and ((note and size == 5) or
                        (not note and page < 63 and ((size == 8 and 'Times' in font) or
                         (page == 23 and size == 6 and font == 'Helvetica')))):
                    value = f'<sup>{value}</sup>'
                if 'Italic' in font:
                    value = f'<em>{value}</em>'
                if 'Bold' in font:
                    value = f'<strong>{value}</strong>'
                parts.append(value)
            return ''.join(parts)
        if not isinstance(node, dict):
            return ''
        if 'Pg' in node:
            page = self.pages[node['Pg'].objid]
        if 'MCID' in node:
            return self.render(node['MCID'], page, note)
        kind = getattr(node.get('S'), 'name', '')
        if kind == 'Figure':
            return f'<figure data-source-page="{page}"><img src="/pdftoweb/figures/{SLUG}/page-{page}.png"></figure>'
        body = self.render(node.get('K'), page, note or kind == 'Footnote')
        if not re.sub('<[^>]+>', '', body).strip() and '<img' not in body:
            return ''
        if kind == 'Link':
            kids = resolve1(node.get('K'))
            for k in kids if isinstance(kids, list) else [kids]:
                obj = resolve1(k)
                if isinstance(obj, dict) and 'Obj' in obj:
                    action = resolve1(resolve1(obj['Obj']).get('A', {}))
                    uri = resolve1(action.get('URI', b'')).decode('latin1')
                    if uri.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                        return f'<a href="{escape(uri, quote=True)}">{body}</a>'
        tag = {'H1':'h2', 'H2':'h3', 'P':'p', 'L':'ul', 'LI':'li',
               'Table':'table', 'TR':'tr', 'TD':'td', 'TH':'th', 'Footnote':'aside',
               'TOC':'nav', 'TOCI':'div'}.get(kind)
        return f'<{tag} data-source-page="{page}">{body}</{tag}>' if tag else body


def convert():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(PDF) as doc:
        write_json(EVIDENCE / 'source-pages.json', [p.get_text() for p in doc])
        for n in [1, 15]:
            page = doc[n-1]
            ref = page.get_images()[0][0]
            pix = pymupdf.Pixmap(doc, ref)
            if pix.colorspace.name not in ('DeviceRGB', 'DeviceGray'):
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            pix.save(FIGURES / f'page-{n}.png')
    with pdfplumber.open(PDF) as source:
        html = TaggedSource(source).render(source.doc.catalog['StructTreeRoot'])
    soup = BeautifulSoup(html, 'html.parser')
    def tag(name, **attrs):
        return soup.new_tag(name, attrs=attrs)
    def words(n):
        return ' '.join(n.get_text().split())
    for img, alt in zip(soup.select('img'), ['National Institute of Standards and Technology',
            'Five layers from facility and hardware through virtualized infrastructure and platform architecture to application. Provider control increases from IaaS to PaaS to SaaS, while consumer control decreases.'], strict=True):
        img['alt'] = alt
    fig = soup.select('figure')[1]
    caption = fig.find_next('p')
    assert words(caption).startswith('Figure 1:')
    caption.name = 'figcaption'
    fig.append(caption.extract())
    headings = []
    for p in soup.find_all('p'):
        if words(p) in ('Reports on Computer Systems Technology', 'Abstract', 'Acknowledgements'):
            p.name = 'h2'
    for h in soup.select('h2,h3'):
        label = words(h)
        anchor = re.sub('[^a-z0-9]+', '-', label.lower()).strip('-')
        h['id'] = anchor
        headings.append(dict(id=anchor, text=label, level=int(h.name[1])))
    entries = soup.nav.find_all('div', recursive=False)
    entries[0].name = 'summary'
    soup.nav.name = 'details'
    details = entries[0].parent
    details['class'] = 'source-contents'
    for entry, h in zip(entries[1:], headings[-35:], strict=True):
        label, numeral = re.split(r'\.{2,}', words(entry))
        link = tag('a', href='#' + h['id'])
        link.string = label.strip() + ' ' + numeral.strip()
        entry.clear()
        entry.append(link)

    tables = soup.select('table')
    for row in tables[2].select('tr')[1:]:
        tables[1].append(row.extract())
    tables[2].decompose()
    for table in soup.select('table'):
        page = int(table['data-source-page'])
        prior = table.find_previous_sibling('p')
        if page in (45, 52, 61):
            cap = prior.extract()
            cap.name = 'caption'
        else:
            cap = tag('caption', **{'data-pagefind-ignore':''})
            cap.string = 'Publication and title' if page == 10 else 'Online Resources'
        cap['id'] = f'table-caption-{page}'
        table.insert(0, cap)
        region = tag('div', **{'class':'table-scroll','role':'region','tabindex':'0','aria-labelledby':cap['id']})
        table.wrap(region).wrap(tag('figure', **{'class':'table-figure'}))
        for i, row in enumerate(table.select('tr')):
            for j, cell in enumerate(row.find_all(['td','th'], recursive=False)):
                if i == 0 or j == 0:
                    cell.name = 'th'
                    cell['scope'] = 'row' if i else 'col'

    notes = tag('section', **{'class':'footnotes','aria-label':'Footnotes'})
    for aside in soup.select('aside'):
        for p in list(aside.select('p')):
            mark = p.find('sup')
            if mark:
                num = words(mark)
                p['id'] = 'note-' + num
                link = tag('a', href='#note-ref-' + num, **{'aria-label':f'Return to footnote {num} in text'})
                mark.wrap(link)
            notes.append(p.extract())
        aside.decompose()
    for sup in soup.select('sup'):
        num = words(sup)
        if notes.find(id='note-' + num):
            sup.wrap(tag('a', href='#note-' + num, id='note-ref-' + num))
    soup.append(notes)
    postprocess(soup)
    report = dict(slug=SLUG, title=TITLE, identifier='NIST SP 800-144',
                  authors=['Wayne Jansen','Timothy Grance'], date='December 2011', sourceUrl=SOURCE,
                  sourceSha256=sha256(PDF.read_bytes()).hexdigest(), pdfPath=f'/sources/{SLUG}.pdf',
                  description='NIST’s December 2011 guidance on security and privacy when outsourcing data, applications, and infrastructure to public clouds.',
                  headings=headings, html='\n'.join(str(n) for n in soup.contents))
    write_json(ROOT / f'src/content/reports/{SLUG}.json', report)


def postprocess(soup):
    cover = soup.find('p', attrs={'data-source-page':'1'})
    assert ''.join(cover.stripped_strings).replace(' ', '') == TITLE.replace(' ', '')
    cover.string = TITLE
    soup.select_one('#note-2 sup').parent.insert_after(' ')

    # Word split paragraphs and list items into separate tags at physical page breaks.
    continued = (8, 9, 10, 18, 20, 21, 22, 25, 26, 28, 29, 30, 31, 32, 34, 35,
                 36, 37, 39, 40, 41, 42, 44, 48, 50, 51, 55, 57, 58, 59, 61, 75)
    for page in continued:
        right = soup.find(attrs={'data-source-page': str(page)}, recursive=False)
        left = right.find_previous_sibling()
        source = right.li if right.name == 'ul' else right
        dest = left.find_all('li')[-1] if left.name == 'ul' else left
        assert dest.name == source.name and dest.name in ('li', 'p')
        fragment = soup.new_tag('span', attrs={'data-source-page':str(page)})
        fragment.extend(list(source.contents))
        dest.append(fragment)
        source.decompose()
        if right.name == 'ul' and not right.li:
            right.decompose()

    # In the visual front matter the commercial notice precedes the publication line.
    notice = soup.find(string=re.compile('Certain commercial entities'))
    line = soup.find(string=re.compile('National Institute of Standards and Technology Special Publication 800-144'))
    line.find_parent('p').insert_before(notice.find_parent('p').extract())

    for p in soup.select('p[data-source-page="79"]'):
        term = p.find('strong')
        assert term
        previous = p.find_previous_sibling()
        if previous.name != 'dl':
            previous = soup.new_tag('dl', attrs={'data-source-page':'79'})
            p.insert_before(previous)
        term.name = 'dt'
        previous.append(term.extract())
        p.name = 'dd'
        previous.append(p.extract())

    for p in soup.find_all('p', recursive=False):
        if p.get_text().lstrip().startswith('▪'):
            p.name = 'li'
            first = p.find(string=True)
            first.replace_with(first.lstrip().removeprefix('▪').lstrip())
            p.wrap(soup.new_tag('ul', attrs={'data-source-page':p['data-source-page']}))
    for ul in list(soup.find_all('ul', recursive=False)):
        previous = ul.find_previous_sibling()
        if previous and previous.name == 'ul':
            previous.extend(list(ul.contents))
            ul.decompose()

    # Keep reference keys verbatim, including the source’s suffixes and case.
    targets = {}
    for p in soup.find_all('p', recursive=False):
        if 63 <= int(p['data-source-page']) <= 78:
            match = re.match(r'\[([^\]]+)\]', p.get_text())
            if match:
                key = match[1]
                p['id'] = 'reference-' + key
                targets[key] = p['id']
    for node in list(soup.find_all(string=re.compile(r'\[[^\]]+\]'))):
        if node.find_parent('a') or node.find_parent(id=re.compile('^reference-')):
            continue
        segments = re.split(r'(\[[^\]]+\])', str(node))
        for i, segment in enumerate(segments):
            if i % 2 and segment[1:-1] in targets:
                a = soup.new_tag('a', href='#' + targets[segment[1:-1]])
                a.string = segment
                node.insert_before(a)
            else:
                node.insert_before(segment)
        node.extract()


if __name__ == '__main__':
    convert()
