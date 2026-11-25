"""Compare the reading edition's tables cell by cell with the retained ARTEX PDF."""
import json
import re
from pathlib import Path

import pymupdf
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SLUG = "cisos-artex"

# Boundaries measured from the rendered PDF, in points. The first narrow
# column contains the circled source row numerals. Severity icons are paths.
TOP_RISKS = [(9, (164, 357, 552, 686), (28, 56, 165, 327, 475, 585))]
RISK_REGISTER = [
    (15, (515, 579, 722), (28, 56, 220, 328, 585)),
    (16, (37, 131, 196, 275, 370, 434, 499, 563, 628, 707), (28, 56, 220, 328, 585)),
    (17, (37, 87, 136, 185, 236, 286, 380, 445, 524, 574, 625), (28, 56, 220, 328, 585)),
]
CONTROLS = [
    (18, (151, 245, 310, 374, 439, 503, 568, 632, 718), (28, 56, 286, 370, 475, 585)),
    (19, (37, 101, 181, 275, 385, 449, 499, 564, 628, 678), (28, 56, 286, 370, 475, 585)),
    (20, (37, 102, 181, 226), (28, 56, 286, 370, 475, 585)),
]
SEVERITY = (15, (153, 204, 262, 320, 379), (28, 93, 585))

HEADERS = [
    (9, (119, 164), (56, 165, 327, 475, 585)),
    (15, (477, 515), (56, 220, 328, 585)),
    (18, (113, 151), (56, 286, 370, 475, 585)),
]


def normalized(text):
    return " ".join(text.split())


def read_cell(page, left, top, right, bottom):
    text = page.get_text("text", clip=pymupdf.Rect(left, top, right, bottom), sort=True)
    # The two line-end hyphens wrap existing compound words.
    text = re.sub(r"(third-|internet-)[ \t]*\n(?=party|facing)", r"\1", text)
    return normalized(text)


def read_rows(document, regions):
    return [
        (page_number, [
            read_cell(document[page_number - 1], left, top, right, bottom)
            for left, right in zip(columns, columns[1:])
        ])
        for page_number, rows, columns in regions
        for top, bottom in zip(rows, rows[1:])
    ]


def verify_tables(document, soup):
    tables = soup.select("table")
    assert len(tables) == 3, "Expected the three ARTEX source tables"
    for table, (_, headers), regions in zip(
        tables, read_rows(document, HEADERS), (TOP_RISKS, RISK_REGISTER, CONTROLS), strict=True
    ):
        first_page = regions[0][0]
        figure = table.find_parent("figure", class_="table-figure")
        scroller = table.parent
        assert figure and figure.get("data-source-page") == str(first_page)
        assert "table-scroll" in scroller.get("class", [])
        assert scroller.get("tabindex") == "0" and scroller.get("role") == "region"
        caption = table.find("caption", recursive=False)
        caption_box = {15: (446, 464), 18: (37, 57)}.get(first_page)
        if caption_box:
            assert caption
            label = caption
            if first_page == 18:
                label, note = caption.find_all(recursive=False)
                assert label.name == "span" and note.name == "p"
                assert note.get("data-source-page") == "18"
                assert normalized(note.get_text()) == read_cell(document[17], 30, 64, 590, 102)
                assert caption.find_next_sibling().name == "thead"
            assert label.get("id")
            assert normalized(label.get_text()) == read_cell(
                document[first_page - 1], 30, caption_box[0], 590, caption_box[1]
            )
            assert scroller.get("aria-labelledby") == table.get("aria-labelledby") == label["id"]
        else:
            assert caption is None and scroller.get("aria-label") == read_cell(
                document[first_page - 1], 30, 37, 590, 60
            )
        column_headers = table.select("thead > tr > th")
        assert [normalized(cell.get_text()) for cell in column_headers] == headers, first_page
        assert all(cell.get("scope") == "col" and cell.get("id") for cell in column_headers)
        previous_page = first_page
        for (page, expected), row in zip(read_rows(document, regions), table.select("tbody > tr"), strict=True):
            number, title, *values = expected
            cells = row.find_all(["th", "td"], recursive=False)
            actual = [normalized(cell.get_text(" ")) for cell in cells]
            assert actual == [f"{number} {title}", *values], (
                f"Table on p{first_page}, row {number} (source p{page}): "
                f"expected {[f'{number} {title}', *values]!r}, found {actual!r}"
            )
            assert row.get("data-source-page") == str(page)
            if page != previous_page:
                assert row.get("id") == f"pdf-page-{page}"
                assert len(soup.find_all(id=f"pdf-page-{page}")) == 1
            previous_page = page
            row_header, *data_cells = cells
            assert row_header.name == "th" and row_header.get("scope") == "row" and row_header.get("id")
            for cell, heading in zip(data_cells, column_headers[1:], strict=True):
                assert cell.name == "td" and set(cell.get("headers", [])) == {row_header["id"], heading["id"]}


def verify_severity(document, soup):
    heading = read_cell(document[14], 30, 132, 590, 153)
    expected = [cell for _, row in read_rows(document, [SEVERITY]) for cell in row]
    legends = [
        node for node in soup.find_all("dl")
        if node.find("dt") and normalized(node.find("dt").get_text()) == expected[0]
    ]
    assert len(legends) == 1, "Expected one severity legend"
    legend = legends[0]
    assert [cell.name for cell in legend.find_all(["dt", "dd"])] == ["dt", "dd"] * 4
    assert [normalized(cell.get_text(" ")) for cell in legend.find_all(["dt", "dd"])] == expected
    assert legend.find_previous(string=lambda value: normalized(value) == heading), heading


def main():
    report = json.loads((ROOT / "src" / "content" / "reports" / f"{SLUG}.json").read_text())
    source = ROOT / "public" / report["pdfPath"].lstrip("/")
    soup = BeautifulSoup(report["html"], "html.parser")
    with pymupdf.open(source) as document:
        verify_tables(document, soup)
        verify_severity(document, soup)
    print("PASS: ARTEX three tables, 44 rows, severity legend, source-page mappings, and header associations.")


if __name__ == "__main__":
    main()
