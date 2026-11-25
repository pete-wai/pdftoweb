"""Independently compare the reading edition's ordered prose with PDF glyph lines."""

from collections import defaultdict
import json
from pathlib import Path
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup
import fitz


root = Path(__file__).resolve().parents[2]
report = json.loads((root / "src/content/reports/cisos-artex.json").read_text())
pdf = fitz.open(root / "public/sources/cisos-artex.pdf")


def lines(page, *, x0=0, x1=612, y0=0, y1=737):
    result = []
    for block in pdf[page - 1].get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            x, y, _, _ = line["bbox"]
            if x0 <= x < x1 and y0 <= y < y1:
                text = "".join(span["text"] for span in line["spans"]).strip()
                result.append((y, x, text))
    return [text for _, _, text in sorted(result)]


def columns(page):
    return lines(page, x1=315) + lines(page, x0=315)


expected = {
    1: lines(1, y1=337) + lines(1, y0=400) + lines(1, y0=337, y1=400),
    4: lines(4, y0=500),
    5: lines(5),
    6: [text for text in columns(6) if text not in ("1", "2", "3")],
    7: [text if text != "Hardened Defenses" else "1. Hardened Defenses" for text in columns(7)],
    9: lines(9, y1=100),
    15: lines(15, y1=150),
    18: lines(18, y1=110),
}
for n in (8, 10, 11, 12, 13, 14, 21, 22, 23, 24, 25, 26):
    expected[n] = columns(n)

# Read each legend row as label followed by definition.
for y0, y1 in ((150, 206), (206, 265), (265, 326), (326, 381)):
    expected[15] += lines(15, x1=95, y0=y0, y1=y1) + lines(15, x0=95, y0=y0, y1=y1)
expected[15] += lines(15, y0=381, y1=470)

doc = BeautifulSoup(report["html"], "html.parser")
for summary in doc.find_all("summary", string="Attribution"):
    summary.decompose()
for table in doc.find_all("table"):
    if table.caption:
        table.replace_with(table.caption.extract())
    else:
        table.decompose()

pages = defaultdict(list)


def collect(node):
    page = node.get("data-source-page")
    if page:
        pages[int(page)].append(node.get_text())
    else:
        for child in node.find_all(recursive=False):
            collect(child)


for element in doc.find_all(recursive=False):
    collect(element)
pages[1].insert(1, report["title"])


def source_words(glyph_lines):
    text = "\n".join(glyph_lines)
    text = re.sub(r"(?<=-)\n *", "", text)
    # Extraction may infer a space at the colored link/punctuation seam.
    text = re.sub(r"\s+([.,])", r"\1", text)
    return text.split()


for page, glyph_lines in sorted(expected.items()):
    source_tokens = source_words(glyph_lines)
    html_tokens = "\n".join(pages[page]).split()
    if page == 18:
        # Table 2's caption has separate title and paragraph nodes.
        html_tokens = doc.find(id="controls-list-caption").parent.get_text(" ").split()
    assert source_tokens == html_tokens, f"Ordered prose differs on PDF page {page}"

for page in expected:
    source_links = {
        unquote(link["uri"])
        for link in pdf[page - 1].get_links()
        if "uri" in link and (page != 4 or link["from"].y0 >= 500)
    }
    html_links = {
        unquote(link["href"])
        for link in doc.find_all("a", href=True)
        if (parent := link.find_parent(attrs={"data-source-page": True}))
        and parent["data-source-page"] == str(page)
        and not link["href"].startswith("#")
    }
    assert source_links == html_links, f"Link destinations differ on PDF page {page}"

citations = doc.find_all("li", attrs={"data-source-page": ["25", "26"]})
assert len(citations) == 28
assert sum(len(citation.find_all("a")) for citation in citations) == 26
assert all(len(citation.find_all("a")) <= 1 for citation in citations)
assert not report["authors"]

total = sum(len(source_words(glyph_lines)) for glyph_lines in expected.values())
print(f"Verified {total:,} ordered prose tokens on {len(expected)} pages and 28 citations.")
