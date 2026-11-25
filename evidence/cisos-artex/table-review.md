# Independent table fidelity review

I rendered physical pages 9 and 15–20 of the supplied PDF and inspected the column boundaries, row placement, captions, severity legend, and page transitions. I independently extracted each cell from rectangles measured against those renders, then compared the cells with the generated report HTML using `scripts/check-artex-tables.py`. The checker does not import the conversion code or use its extraction settings.

| Source material | Physical pages | Result |
| --- | --- | --- |
| Section III side-by-side table | 9 | All three row numbers and four content columns match. The section heading labels the table because the PDF has no separate caption. |
| Table 1, risk register | 15–17 | All 21 risk numbers, titles, severity labels, and observations match. Continuations begin at risks 3 and 12. |
| Table 2, controls list | 18–20 | All 20 control numbers, descriptions, start times, types, and Frontier Ready codes match. The note follows the title and precedes the column headings as in the PDF. Continuations begin at controls 9 and 18. |
| Severity legend | 15 | All four severity terms and their definitions match, including the complete explanation of “Validated” under LOW. |

The tables preserve all 199 independently extracted body entries, 11 column headings, and both numbered captions. The HTML places each circled numeral and its title together in the row header. The checker verifies the resulting row and column header associations, scroll-region labeling, source page on each row, and the anchor at the first row of each continuation page. The PDF’s severity triangles are visual cues for the severity words.

The comparison normalizes whitespace and joins two existing compounds wrapped by the PDF, `third-party` and `internet-facing`. It preserves underlying PDF text casing, including lowercase `control` in the page 9 header. The rendered PDF draws these headers and captions in uppercase.

The generated report passed the complete comparison. No table fidelity findings remain.
