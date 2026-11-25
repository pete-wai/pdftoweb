"""Import the CSA draft using its column geometry and PDF link annotations."""
import hashlib
import json
import re
from html import escape
from itertools import groupby
from pathlib import Path

from bs4 import BeautifulSoup
import fitz
from artex_tables import tables

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'public/sources/cisos-artex.pdf'
doc = fitz.open(source)
title = 'The Third Wave: ARTEX and Agentic Offensive Frameworks (AOFs)'
sections = {}
html = []


def page_lines(number):
    page = doc[number - 1]
    links = [(link['from'], link['uri']) for link in page.get_links()
             if link.get('uri', '').startswith(('https://', 'http://', 'mailto:'))]
    result = []
    for block in page.get_text('rawdict', flags=fitz.TEXTFLAGS_TEXT)['blocks']:
        for line in block['lines']:
            x, y, *_ = line['bbox']
            if y > 735:
                continue
            characters = []
            for span in line['spans']:
                for char in span['chars']:
                    rect = fitz.Rect(char['bbox'])
                    center = (rect.tl + rect.br) / 2
                    url = next((uri for box, uri in links if center in box), '')
                    characters.append((url, char['c']))
            parts = []
            for url, chars in groupby(characters, key=lambda c: c[0]):
                value = escape(''.join(ch for _, ch in chars))
                if value.strip() and url:
                    value = f'<a href="{escape(url, quote=True)}">{value}</a>'
                parts.append(value)
            value = ''.join(parts).strip()
            if value:
                result.append((x, y, value, block['number']))
    return result


def join(lines):
    value = ''
    for line in lines:
        separator = '' if value.endswith('-') else ' '
        value += separator + line
    return ' '.join(value.split())


def append(tag, value, n, attrs=''):
    html.append(f'<{tag} data-source-page="{n}" {attrs}>{value}</{tag}>')


def paragraphs(n, lines):
    groups = []
    last = None
    for x, y, value, block in sorted(lines, key=lambda r: (r[0] >= 302, round(r[1], 1), r[0])):
        # The three numbered discs in the executive summary sit next to their paragraphs.
        if n == 6 and value in ('1', '2', '3'):
            continue
        if last is None or block != last[3] or abs(y-last[1]) > 22 or (
            n == 7 and ((x < 302 and round(y) in (449, 591)) or (x >= 302 and round(y) in (98, 271)))) or (
            n == 6 and round(y) == 627 and x > 302):
            groups.append([])
        groups[-1].append(value)
        last = x, y, value, block
    return [join(g) for g in groups]


def restore_continuation(groups, prefix):
    index = next(i for i, value in enumerate(groups) if value.startswith(prefix))
    groups[index-1:index+1] = [join(groups[index-1:index+1])]


def normalize_links(value, n):
    # Link rectangles cover individual printed lines. Reassemble the label and
    # restore the whole first glyph where the PDF rectangle clips its edge.
    while re.search(r'</a>\s*<a ',value):
        merged = re.sub(r'(<a href="([^"]+)">[^<]*?)\s*</a>\s*<a href="\2">',r'\1 ',value)
        if value == merged:
            break
        value = merged
    if n in (25,26) and '<a ' in value:
        node = BeautifulSoup(value, 'html.parser')
        url = node.a['href']
        before, _, after = value.rpartition('</a>')
        label = BeautifulSoup(before,'html.parser').get_text().strip()
        label = ' '.join(label.split()).replace('AI- orchestrated','AI-orchestrated').replace('Post- Mortem','Post-Mortem')
        value = f'<a href="{escape(url,quote=True)}">{escape(label)}</a>' + after
    if n == 4:
        value = value.replace('alliance.o</a>rg','alliance.org</a>')
    return value


def emit_prose(n, groups):
    list_tag = None
    for value in groups:
        value = normalize_links(value,n)
        if n == 7 and value == 'Hardened Defenses':
            value = '1. ' + value
        tag = 'p'
        attrs = ''
        if re.match(r'^[IVX]+\. ', value):
            anchor = 'section-' + value.split('.')[0].lower()
            sections[anchor] = value
            tag, attrs = 'h2', f'id="{anchor}"'
        elif n == 7 and (value == 'CISO Action Items' or re.match(r'^[1-4]\. ', value)):
            tag = 'h3'
        elif n in (12,13,14,21) and (value.endswith(':') or (len(value)<70 and value[-1] not in '.?"')):
            tag = 'h3'
        if tag == 'h3' and n in (12,13,14,21) and value not in (
                'New measures from the community:', 'New risks:', 'Expectations and considerations:',
                'The message for the board:', 'Decisions the board needs to make:', 'Questions the board should ask:'):
            tag = 'h4'
        kind = None
        if n == 12 and value.startswith(('Community contributors report','Faster patching','Vulnerability hunting')):
            kind = 'ul'
        if n in (22,25,26) and tag == 'p' or n == 6 and value.startswith(('Check Point Research','SentinelOne counts')) or n == 24 and value.startswith(('Teams that','Deception slowed','Partial cleanup')):
            kind = 'ul'
        if n == 6 and value.startswith(('Traditional human-in','CISOs must be granted','Organizations must be willing')):
            kind = 'ol'
        if kind != list_tag:
            if list_tag:
                html.append(f'</{list_tag}>')
            if kind:
                html.append(f'<{kind}>')
            list_tag = kind
        if n == 11 and tag == 'p' and not value.startswith('<a '):
            value = re.sub(r'^([^.,:]+[.:,])',r'<strong>\1</strong>',value)
        if (n == 7 and value.startswith('CISOs must immediately')) or (
                n == 24 and value.startswith('Keep in mind')) or (n == 6 and value == 'Critical summary:'):
            value = f'<strong>{value}</strong>'
        if n == 21 and tag == 'p' and '?' in value:
            value = f'<em>{value}</em>'
        append('li' if kind else tag, value, n, attrs)
    if list_tag:
        html.append(f'</{list_tag}>')


table_html = tables(doc)
for n in [1,4,5,6,7,8,9,10,11,12,13,14,15,18,21,22,23,24,25,26]:
    html.append(f'<span id="pdf-page-{n}"></span>')
    lines = page_lines(n)
    if n == 1:
        lines = [r for r in lines if not (130 < r[1] < 300 or 335 < r[1] < 400)]
    if n == 1:
        # Keep collective source attribution available on demand. Individual
        # author biographies and contributor rosters stay in the original PDF.
        byline = join([r[2] for r in page_lines(n) if 335 < r[1] < 400])
    if n == 4:
        lines = [r for r in lines if r[1] > 510]
    if n == 5:
        entries = sorted([r for r in lines if 100 < r[1] and r[0] < 100],key=lambda r:r[1])
        numbers = sorted([r for r in lines if r[0]>550],key=lambda r:r[1])
        html.append('<details class="source-contents" data-source-page="5"><summary>Table of Contents</summary><ol>')
        for entry, page in zip(entries,numbers,strict=True):
            label = entry[2]
            html.append(f'<li><a href="#section-{label.split(".")[0].lower()}">{label}</a> {page[2]}</li>')
        html.append('</ol></details>')
        continue
    if n == 9:
        lines = [r for r in lines if r[1]<115]
    if n == 18:
        lines = [r for r in lines if 55<r[1]<110]
    if n == 15:
        emit_prose(n, paragraphs(n, [r for r in lines if r[1]<130]))
        append('h3','SEVERITY:',n)
        html.append('<dl data-source-page="15">')
        for low, high in [(150,200),(200,255),(255,313),(313,380)]:
            band=[r for r in lines if low<r[1]<high]
            append('dt',join([r[2] for r in band if r[0]<90]),n)
            append('dd',join([r[2] for r in sorted(band,key=lambda r:r[1]) if r[0]>90]),n)
        html.append('</dl>')
        lines = [r for r in lines if 390<r[1]<430]
    groups = paragraphs(n,lines)
    if n==6:
        restore_continuation(groups,'business operations')
    if n==12:
        restore_continuation(groups,'systems that have')
    if n==13:
        restore_continuation(groups,'concentrate keys')
    if n == 18:
        # Keep the introductory note immediately after its caption title.
        table = BeautifulSoup(table_html[n], 'html.parser')
        caption = table.caption
        label = table.new_tag('span', id=caption.attrs.pop('id'))
        label.string = caption.string.extract()
        caption.append(label)
        note = table.new_tag('p', attrs={'data-source-page': '18'})
        note.string = groups.pop()
        caption.append(note)
        table_html[n] = str(table)
    emit_prose(n,groups)
    if n == 1:
        html.append(f'<details data-pagefind-ignore data-source-page="1"><summary>Attribution</summary><p>{byline}</p></details>')
    if n in table_html:
        html.append(table_html[n])

report = dict(slug='cisos-artex',title=title,identifier='Expedited Strategy Briefing',authors=[],
              date='24 November 2026',sourceUrl='https://cloudsecurityalliance.org/artifacts/aof/',
              sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),pdfPath='/sources/cisos-artex.pdf',
              description='A draft briefing on agentic cyberattacks, with a risk register, defensive controls, and decisions for boards.',
              headings=[dict(id=k,text=v,level=2) for k,v in sections.items()],html='\n'.join(html))
(ROOT/'src/content/reports/cisos-artex.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
