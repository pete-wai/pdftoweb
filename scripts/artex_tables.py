"""Extract the three ARTEX tables using their source column and row alignment."""

from bisect import bisect_right
from collections import defaultdict
from html import escape

import pymupdf


def page_lines(page):
    lines = []
    for block in page.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)["blocks"]:
        for line in block["lines"]:
            x, y, _, _ = line["bbox"]
            value = "".join(span["text"] for span in line["spans"]).strip()
            if value:
                lines.append((x, y, value))
    return sorted(lines, key=lambda line: (line[1], line[0]))


def join_cell(lines):
    value = ""
    for line in lines:
        # These source line breaks occur inside hyphenated compounds.
        separator = "" if not value or value.endswith(("third-", "internet-")) else " "
        value += separator + line
    return value


def page_rows(lines, columns):
    # The number in the left margin sits slightly below the first text line.
    starts = [(y - 4, value) for x, y, value in lines
              if 40 <= x < 54 and y < 710 and value.isdecimal()]
    cuts = [y for y, _ in starts]
    cells = defaultdict(list)
    for x, y, value in lines:
        row_index = bisect_right(cuts, y) - 1
        if row_index >= 0 and x >= 60 and y < 710:
            cells[row_index, bisect_right(columns, x) - 1].append(value)
    return [
        [number, *(join_cell(cells[row_index, col]) for col in range(len(columns)))]
        for row_index, (_, number) in enumerate(starts)
    ]


def table_data(doc):
    """Return the source table captions, headers, and individually mapped rows."""
    specs = [
        ("top-three-risks-and-controls", (9,), (60, 165, 325, 475), (125, 155), None, 3),
        ("risk-register", (15, 16, 17), (60, 220, 325), (485, 500), 446, 21),
        ("controls-list", (18, 19, 20), (60, 285, 370, 475), (120, 140), 37, 20),
    ]
    data = {}
    for slug, pages, columns, head_range, caption_y, expected_rows in specs:
        first_lines = page_lines(doc[pages[0] - 1])
        headers = defaultdict(list)
        for x, y, value in first_lines:
            if head_range[0] <= y < head_range[1]:
                headers[bisect_right(columns, x) - 1].append(value)
        rows = []
        for page in pages:
            rows.extend(
                {"page": page, "cells": cells}
                for cells in page_rows(page_lines(doc[page - 1]), columns)
            )
        if [row["cells"][0] for row in rows] != [str(i) for i in range(1, expected_rows + 1)]:
            raise ValueError(f"Unexpected row numbers in {slug}")
        if any(not all(row["cells"]) for row in rows):
            raise ValueError(f"Empty cell in {slug}")
        caption = None
        if caption_y is not None:
            caption, = [value for _, y, value in first_lines if abs(y - caption_y) < 1]
        headings = [join_cell(headers[i]) for i in range(len(columns))]
        if not all(headings):
            raise ValueError(f"Missing column heading in {slug}")
        data[pages[0]] = {
            "id": slug,
            "pages": pages,
            "caption": caption,
            "headers": headings,
            "rows": rows,
        }
    return data


def render_table(data):
    slug = data["id"]
    first_page = data["pages"][0]
    caption = data["caption"]
    caption_id = f"{slug}-caption"
    label = (
        f'aria-labelledby="{caption_id}"' if caption
        else 'aria-label="III. Top Three Risks and Controls"'
    )
    html = [
        f'<figure class="table-figure" data-source-page="{first_page}">',
        f'<div class="table-scroll" tabindex="0" role="region" {label}>',
        f'<table {label}>',
    ]
    if caption:
        html.append(f'<caption id="{caption_id}">{escape(caption)}</caption>')
    html.append("<thead><tr>")
    for col, header in enumerate(data["headers"]):
        html.append(f'<th scope="col" id="{slug}-col-{col}">{escape(header)}</th>')
    html.append("</tr></thead><tbody>")
    previous_page = first_page
    for row in data["rows"]:
        page = row["page"]
        anchor = f' id="pdf-page-{page}"' if page != previous_page else ""
        previous_page = page
        number, title, *cells = row["cells"]
        row_id = f"{slug}-row-{number}"
        html.append(f'<tr data-source-page="{page}"{anchor}>')
        html.append(f'<th scope="row" id="{row_id}">{number} {escape(title)}</th>')
        for col, value in enumerate(cells, start=1):
            html.append(f'<td headers="{row_id} {slug}-col-{col}">{escape(value)}</td>')
        html.append("</tr>")
    html.append("</tbody></table></div></figure>")
    return "".join(html)


def tables(doc):
    return {page: render_table(data) for page, data in table_data(doc).items()}
