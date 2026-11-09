# Independent table and layout fidelity review

Source: `public/sources/hegseth-articles-of-impeachment.pdf` (34 physical pages)
Converted content: `src/content/reports/hegseth-articles-of-impeachment.json`

## Findings

- No tables, figures, or footnotes/endnotes appear in the source PDF. The conversion contains no table, figure, image, superscript, or endnote markup. There are no corresponding visual or textual objects to preserve.
- The source has eight bold, uppercase article headings, beginning on physical pages 1, 5, 7, 11, 17, 24, 28, and 31. All eight appear as level-two headings, in source order, with the matching page mapping and article wording. The cover's `H. RES. __` and `RESOLUTION` bold text and the italicized “Resolved,” are represented with emphasis markup.
- Numbered and lettered clauses are represented as nested ordered lists. The observed hierarchy includes parenthetical Arabic numerals, uppercase letters, and lowercase Roman numerals. Labels remain explicit in the list-item text (for example `(1)`, `(A)`, `(i)`), and the source nesting is reflected by nested `<ol>` elements. Long items crossing page breaks remain one item with their page mapping spanning both pages.
- Prose is reflowed from the PDF's justified, indented print layout into continuous paragraphs. The source's paragraph boundaries and visible list hierarchy are retained. No diagrams, charts, callouts, tables, or other non-text layout elements were found.
- Page footer numerals and the signature dotted rule on page 1 are omitted as authorized layout-only omissions.

## Discrepancies

The initial review found two fidelity issues. On physical page 22, `(I) pursuant to Little v. Barreme` had been flattened to an alphabetic sibling at the `(A)` level. The importer was corrected; the final HTML places it at depth four as upper-Roman item 1 beneath `(i)`. The cover text had also acquired false spaces (`119 TH CONGRESS 2D S ESSION`). The importer was corrected to join spans by visual line; the final JSON now reads `119TH CONGRESS / 2D SESSION` as shown in the PDF. Re-review of the final JSON found both issues resolved.

Final JSON SHA-256: `172500fb1d2bbfe78b2a6c135f358beafd3355dc5d4dc8213aa36046198ba09c`.

## Review method

Inspected rendered PDF pages, including the cover and pages containing nested enumerations; inspected PDF text and font styling; compared the converted HTML structure, heading order, page mappings, list nesting, and emphasis markup. This review covers tables and layout; it is not a full word-for-word prose audit.
