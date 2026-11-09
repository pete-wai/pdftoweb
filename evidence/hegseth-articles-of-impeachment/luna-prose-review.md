# Independent prose fidelity review

**Source:** `public/sources/hegseth-articles-of-impeachment.pdf` (34 pages)  
**Converted content:** `src/content/reports/hegseth-articles-of-impeachment.json`  
**Mapping checked:** `evidence/hegseth-articles-of-impeachment/block-map.json`

## Final findings

No unresolved prose fidelity discrepancies remain. The final converted content was checked after the importer fixes.

The initial cover conversion inserted spaces within the small-cap text, rendering the source wording `119TH CONGRESS` and `2D SESSION` as `119 TH CONGRESS` and `2D S ESSION`. The importer now concatenates spans within each source line before joining lines. The final report and block map preserve the source wording as `119TH CONGRESS` and `2D SESSION`. The separate page 22 list-nesting correction does not alter prose.

I rechecked the PDF's extracted text against the page-mapped blocks and followed the report from its cover through all eight articles. After removing only footer page numerals and the decorative signature dots, the PDF extraction and the 170 mapped blocks have identical 11,921-token streams; the final report and block map also have identical token streams. This includes capitalization, dates, numbers, citations, quotations, punctuation, and paragraph order. Paragraphs continued across page breaks read continuously, including the transitions on pages 2–3, 6–7, 17–18, 24–25, 27–28, 28–29, and 31–32. Article headings and enumerated clauses remain distinct and in source order.

Emphasis represented in the report is limited to formal labels and headings and the italicized case names and named vessels visible in the source. The page-one signature placeholder is retained. Footer page numerals and decorative signature dots are omitted as documented layout exclusions.

## Final content checksum

SHA-256 of `src/content/reports/hegseth-articles-of-impeachment.json`:

`172500fb1d2bbfe78b2a6c135f358beafd3355dc5d4dc8213aa36046198ba09c`

## Review scope

This was a prose, ordering, and paragraph-join review. No edits were made to the converter or report content. Table fidelity and browser behavior were outside this review.
