# Independent table and figure review — in progress

Reviewer: independent GPT-6.1 Terra agent, explicitly selected by the parent agent at the user’s direction.

The source has four named summary tables, on physical PDF pages 30, 34, 41 and 44. Each has four rows (Purpose, Primary Roles, Supporting Roles, Outcomes) and two columns. Source-cell regions have been independently defined from the PDF geometry in `scripts/check-53a-tables.py`; the check compares every cell when the reading edition is available. The PDF table finder incorrectly subdivides these tables at line boundaries and duplicates some overlapping cells, so its inferred grid is not used as the reference.

The PDF has nine numbered figures: 1–6 on pages 24–29, 7 on page 30, 8 on page 47, and 9 on page 731. Figures 1–5 have callouts; figure 7 is a four-step process diagram, figure 8 a process diagram with flows and responsibilities, and figure 9 a findings matrix with per-row S/O values and comments. These relations need verification against the original renders. The text layer of figures 1–6, 8, and 9 contains misencoded glyphs; figure 7’s diagram text is not extracted. Text extraction alone is insufficient for a figure fidelity review.

The assessment catalog contains many visually keyed procedure rows; page-spanning procedures repeat control headings. Extraction of catalog text has font-specific private-use glyphs (for example, two different glyphs encode `tt` in “attempts” on page 93), so a single global character map is insufficient evidence of fidelity. Catalog row structure and figure crops await the generated edition and have not been reviewed yet.

## Results for the first generated edition

The four summary tables’ 32 cells match their independently clipped source regions after whitespace, bullet, and Unicode compatibility normalization. The first row’s value cell is marked as a header without a scope; it should be a data cell associated with the Purpose row header. Outcome bullets are included in the cells; the check does not separately validate individual list boundaries.

All nine original figure crops were visually inspected for complete boundaries and callouts, and each image pixel-matches its corresponding independently specified PDF region rendered at 2×. The crops preserve the source's visual row and diagram relationships. However, their brief alternate descriptions omit the detailed figure text and relationships, so the text and data within those images remain unavailable as selectable text or a full accessible equivalent. Figure 9’s row-by-row findings and figure 8’s responsibilities and outputs are especially material examples. This finding remains open pending an equivalent.

An independent source-coordinate scan checked 7,104 keyed catalog lines against the corresponding HTML row on the same physical page and matched stable fragments of the first source line. It does not check complete cell text or every unkeyed row, and cannot by itself establish exhaustive catalog fidelity. The four-table, figure-pixel, and keyed-line checks are reproducible with `uv run --locked python scripts/check-53a-tables.py`. This is not a substitute for the separately required Luna review or a complete independent cell-by-cell visual audit.


## Follow-up on figure equivalents and table semantics

The four Purpose value cells are now data cells and all four tables have row headers with scope. Figure 7 now transcribes all four full printed labels. Figure 8 is organized by its printed stages and organization/assessor swimlanes; a bracketed note describes the diagram arrows. Figure 9 is presented as a four-column matrix with all nine S/O results in their source rows. These were checked against the original crops.

The earlier extraction flag replaced ligatures in figures 1–6 with replacement characters. Using the PDF's default extraction flags and resolving the two observed glyphs fixes those characters. Automated checks now reject the observed broken glyphs and verify figure 7 labels, figure 9 findings sequence, all 32 summary cells and row semantics, and figure image pixels. The catalog check remains limited to stable portions of the first line of each keyed row, not full-cell fidelity; no complete independent catalog cell comparison has been performed.

## Full catalog-cell follow-up

The earlier first-line-only limitation is superseded. The independent checker now groups source lines using the PDF's drawn horizontal rules and compares each complete keyed value cell with the corresponding identifier and value in the HTML. All 7,104 keyed cells match. It also compares the text of every source row, caption, family heading, continuation and withdrawn notice with the corresponding HTML row or heading, in order, on all 644 catalog pages. A separate ordered page-text comparison accounts for every extracted character. Whitespace and Unicode compatibility ligatures normalize; font-specific private-use ligatures are decoded from the source font. All checks pass. The PDF table detector merged adjacent rows on some pages, so it was not used as the row-boundary authority.

These checks test extracted text and row association; they are not a visual inspection of every one of the 644 pages. Figure transcripts and original crops are reviewed separately above.

The parent agent reported that `uv run --locked python scripts/verify.py` passed with the upgraded full catalog checks included. The independent `scripts/check-53a-tables.py` run also passed after the final checker changes.
