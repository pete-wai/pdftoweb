"""Physical reading-order repairs for the Word-authored portions of SP 800-53A."""
import re
from html import escape
from bs4 import BeautifulSoup
import pymupdf


def fragment(value):
    return list(BeautifulSoup(value,'html.parser').contents)


def restore_paragraphs(soup, doc, styled):
    # In these paragraphs Word attached marked-content runs after the footnote
    # annotation rather than at the printed callout. Read the complete printed block.
    starts = {10:['SP 800-53A is a companion'],23:['The appropriate depth and coverage'],
              37:['Assessors note which security'],39:['The assessment procedures in Chapter 4'],
              48:['This chapter provides a catalog'],732:['Ongoing security and privacy assessment']}
    def line_html(line):
        parts=[]
        for s in line['spans']:
            v=styled(s['text'],s['font'])
            if s['text'].strip().isdigit() and 5.4<s['size']<7.2:
                v=f'<sup>{s["text"].strip()}</sup>'
            parts.append(v)
        return ''.join(parts).strip()
    for page, prefixes in starts.items():
        blocks=doc[page-1].get_text('dict',flags=3)['blocks']
        for prefix in prefixes:
            target=next(p for p in soup.select(f'p[data-source-page="{page}"]') if p.get_text().startswith(prefix))
            lines=next(b['lines'] for b in blocks if ''.join(s['text'] for s in b['lines'][0]['spans']).startswith(prefix))
            target.clear()
            target.extend(fragment(' '.join(line_html(l) for l in lines)))

    previous=next(n for n in soup.select('li[data-source-page="13"]') if 'privacy risk assessment' in n.get_text())
    previous.string=previous.get_text().split('• The security and privacy controls')[0].rstrip()
    first=next(n for n in soup.select('li[data-source-page="14"]') if 'assurance requirements' in n.get_text())
    li=soup.new_tag('li',attrs={'data-source-page':'14'})
    lines=next(b['lines'] for b in doc[13].get_text('dict',flags=3)['blocks'] if 70<b['bbox'][1]<75 and b['bbox'][0]>95)
    li.extend(fragment(' '.join(line_html(l) for l in lines[1:4])))
    first.insert_before(li)


def link_notes(soup):
    notes=soup.new_tag('section',attrs={'class':'footnotes','aria-label':'Footnotes'})
    last=None
    for aside in soup.select('aside'):
        for p in list(aside.select('p')):
            match=re.match(r'\s*(\d+)\s*',p.get_text())
            if match:
                n=match[1]
                p['id']='note-'+n
                first=p.find(string=lambda t:t and t.strip())
                assert first.strip().startswith(n)
                back=soup.new_tag('a',href='#note-ref-'+n,attrs={'aria-label':'Return to footnote '+n+' in text'})
                back.string=n
                first.insert_before(back)
                first.replace_with(first.lstrip()[len(n):])
                last=p
                notes.append(p.extract())
            else:
                assert last is not None
                p.name='span'
                last.append(' ')
                last.append(p.extract())
        aside.decompose()
    for sup in soup.select('sup'):
        num=sup.get_text(strip=True)
        if notes.find(id='note-'+num):
            a=soup.new_tag('a',id='note-ref-'+num,href='#note-'+num)
            sup.wrap(a)
    soup.append(notes)


def figure_equivalents(soup, doc, crops, styled):
    for n, (page, bounds) in enumerate(crops.items(),1):
        fig=soup.select_one(f'figure[data-source-page="{page}"]:has(img)')
        details=soup.new_tag('details',attrs={'data-source-page':str(page)})
        summary=soup.new_tag('summary')
        summary.string='Figure text'
        details.append(summary)
        pdf=doc[page-1]
        if n==7:
            # The four labels are part of the raster image.
            values=['Prepare for Security and Privacy Control Assessments', 'Develop Security and Privacy Assessment Plans', 'Conduct Security and Privacy Control Assessments', 'Analyze Assessment Report Results']
            entries=['<p>'+escape(v)+'</p>' for v in values]
        elif n==8:
            # Group text by the printed swimlanes and stages. Editorial explanations
            # in brackets describe arrows, which have no textual representation.
            entries=["""<p>Pre-Assessment → Assessment → Post-Assessment</p>
<p>Prepare for Security and Privacy Control Assessments → Develop Security and Privacy Assessment Plans → Conduct Security and Privacy Control Assessments → Analyze Assessment Report Results</p>
<h4>Organization — Prepare for Security and Privacy Control Assessments</h4><p>Approved Security and Privacy Plans</p><ul><li>Implement controls</li><li>Notify key organizational officials of impending assessment</li><li>Establish communications channels among stakeholders</li><li>Identify and allocate resources; assemble assessment team</li><li>Establish scope and key milestones</li><li>Assemble artifacts for assessment</li></ul>
<h4>Assessor / Assessment Team — Prepare for Security and Privacy Control Assessments</h4><ul><li>Establish organizational points of contact</li><li>Understand organization’s mission, functions, and business processes</li><li>Understand system structure/architecture</li><li>Understand selected controls for assessment and relevant NIST standards and guidelines</li></ul>
<h4>Assessor / Assessment Team — Develop Security and Privacy Assessment Plans</h4><ul><li>Develop assessment plan based on security and privacy plans<ul><li>Select assessment methods and objects</li><li>Tailor procedures for organization and system</li></ul></li><li>Identify schedule and milestones</li><li>Obtain artifacts for assessment</li></ul><p>Assessment Plan(s)</p>
<h4>Organization — Develop Security and Privacy Assessment Plans</h4><ul><li>Ensure assessment plan is appropriately tailored</li><li>Involve senior leadership</li><li>Balance schedule, performance, and cost</li><li>Approve assessment plan</li></ul>
<h4>Assessor / Assessment Team — Conduct Security and Privacy Control Assessments</h4><ul><li>Implement assessment plan(s)</li><li>Execute assessment procedures to achieve assessment objectives</li><li>Produce assessment findings</li><li>Recommend specific remediation actions</li><li>Produce initial (draft) and final assessment report(s)</li></ul><p>1. Initial draft report<br>2. Final report with organizational annotations</p><p>Assessment Report(s)</p>
<h4>Organization — Analyze Assessment Report Results</h4><ul><li>Review assessor findings and assess the risk of weaknesses and deficiencies</li><li>Determine appropriate response actions</li><li>Develop/update Plans of Action and Milestones</li><li>Update Security and Privacy Plans (and Risk Assessment)</li></ul><p>Authorization Package: Assessment Report(s); Plans of Action and Milestones; Updated Security and Privacy Plans.</p>
<h4>Assessor / Assessment Team — Analyze Assessment Report Results</h4><ul><li>Consult with organizational officials regarding control effectiveness</li></ul>
<p>[The arrows connect the approved security and privacy plans to the organization and assessor preparation activities; connect the two preparation activities to each other; carry the assessor’s preparation into plan development; connect the assessment plan with its development and organizational approval; carry the approved plan into the conduct of assessments; and connect assessment reporting, organizational analysis, the authorization package, and consultation about control effectiveness.]</p>"""]
        elif n==9:
            tab=pdf.find_tables().tables[0]
            entries=['<div class="table-scroll" role="region" tabindex="0" aria-label="Figure 9 findings"><table><caption>CP-03 CONTINGENCY TRAINING</caption>']
            for i,row in enumerate(tab.rows[1:-1]):
                vals=[]
                for cell in row.cells:
                    if cell:
                        text=pdf.get_textbox(cell).replace('Ɵ','ti').replace('�','ti')
                        vals.append(escape(' '.join(text.split())))
                if i==0:
                    entries.append('<tr><th colspan="2" scope="colgroup">'+vals[0]+'</th>'+''.join('<th scope="col">'+v+'</th>' for v in vals[1:])+'</tr>')
                else:
                    entries.append('<tr><th scope="row">'+vals[0]+'</th>'+''.join('<td>'+v+'</td>' for v in vals[1:])+'</tr>')
            entries.append('</table></div>')
        else:
            entries=[]
            for b in pdf.get_text('dict')['blocks']:
                lines=[]
                for line in b['lines']:
                    x,y,x1,y1=line['bbox']
                    if not (bounds[0] <= x and x1 <= bounds[2]+1 and bounds[1]-1 <= (y+y1)/2 < bounds[3]):
                        continue
                    v=''.join(styled(s['text'],s['font']) for s in line['spans']).strip()
                    if v:
                        lines.append(v)
                if lines:
                    entries.append('<p>'+' '.join(lines).replace('Ɵ','ti').replace('ƫ','tti')+'</p>')
        details.extend(fragment(''.join(entries)))
        fig.append(details)
