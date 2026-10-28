# Independent prose fidelity review: NIST IR 8547

Reviewed `public/sources/nist-ir-8547.pdf` against `src/content/reports/nist-ir-8547.json` on 2026-10-28. The PDF has 34 pages. I inspected the report HTML and its source-page mappings, checked `evidence/source-pages.json` and `evidence/block-audit.json`, and independently extracted the PDF with PyMuPDF. I rendered PDF page 34 to verify the glossary structure visually. Tables were excluded from the prose assessment because they have a separate reviewer.

## Findings from initial review

### [P1] Glossary entry was merged into the preceding definition — resolved

On PDF page 34 (printed page 27), `quantum-vulnerable algorithm` is a separate bold glossary term followed by its own definition. In the initial HTML, that term and definition were appended inside the `<dd>` for `public-key cryptography`. The updated HTML now has a separate `<dt>` and `<dd>` for `quantum-vulnerable algorithm`; its definition matches the source. The source page was visually checked at `/tmp/nist-ir8547-page34.png`.

### [P2] Front-matter contents pages were absent — resolved

PDF page 6 (printed page iii) contains the Table of Contents and page 7 (printed page iv) the List of Tables. The updated HTML includes both in `details.source-contents`. I verified 31 ToC links and 8 table links, all resolving to existing section/table IDs. The original ToC label “4. Toward a PQC Standards Transition Timeline” is retained while the body heading remains “4. PQC Standards Transition Timeline.” The 8 table labels match the source list.

## Checks that passed

- The report body prose and paragraph order match the source across the inspected source-page mappings; the block audit’s only normalized text differences are bullet glyphs on list items, which are represented as HTML list items. I found no missing or altered body prose in this pass.
- Front matter from the title page onward is present. The duplicate cover on PDF page 1 is consolidated into page 2, consistent with the permitted change. Running headers, footers, and page labels are omitted.
- All 31 reference labels are present in the same order, and extracted reference text matches after ignoring running headers and printed page numbers.
- The four prose footnotes are present, and their in-text markers are superscript links to the corresponding footnotes. Footnote 1 is correctly represented.
- Glossary definitions otherwise match the source text; the merged entry above is the structural exception.

## Targeted re-review

Re-reviewed after the fixes on 2026-10-28. The glossary now contains 35 separate `<dt>` terms with corresponding definitions, including `quantum-vulnerable algorithm`; its definition is correctly separate from `public-key cryptography`. The front-matter contents are present and linked as described above. All 43 heading metadata entries resolve to matching HTML headings. Both initial findings are resolved.

## Coverage and limits

This review covers the report’s prose, references, glossary, front matter, footnotes, and paragraph order. It does not assess table contents or visual layout beyond the rendered glossary page. No editorial corrections or summaries were introduced.
