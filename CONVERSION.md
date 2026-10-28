# NIST IR 8547 conversion record

Source: https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf

Edition: October 2026. Downloaded October 28, 2026. The original 34-page PDF is retained without modification; its SHA-256 is recorded with the report and in `evidence/approved-content.json`.

## Layout transformations

- Physical page 1 duplicates the publication identity and authors on page 2. The complete textual content of page 2 is preserved as publication details; the duplicate first cover is consolidated. Cover logos/seals are publication branding rather than explanatory figures and are not used as site branding. The PDF remains available in full.
- Running publication headers, footer page labels, blank lines, and dotted TOC leaders are removed. Source links use physical PDF page numbers. Each substantive block retains `data-source-page`; a paragraph continued across pages retains its starting page.
- Prose is reflowed. Original hyphens, punctuation, wording, and Unicode characters remain; line wrapping and whitespace are normalized. Italics, bold text, and superscripts are represented semantically where present.
- Body paragraphs split across physical pages are joined only at verified continuations. A source extraction fragment interrupting the SP80052 citation on physical page 26 is joined back into its paragraph.
- The printed contents and list of tables become linked disclosure lists. Their labels remain, including “4. Toward a PQC Standards Transition Timeline,” although the body heading is “4. PQC Standards Transition Timeline.” Rasterized TOC lines are represented as text links to the corresponding sections.
- Tables are semantic HTML. Tables 4 and 8 are joined across page breaks and their repeated column headings consolidated. Merged family cells retain their row relationships. The SHA-2 family continues across the original Table 8 page break.
- Four page-bottom footnotes move to a linked endnote section with return links. References retain their labels and ordering; the glossary uses 35 term/definition pairs.
- Publication details and footnotes are present in the continuous page. Collapsible content is limited to navigation lists, not report prose.

## Source quirks intentionally retained

No editorial corrections are applied. Examples include `AES-AEAD128` in Table 7, repeated `[SP800131A][SP800131A]`, “the at least the” in the paragraph following Table 3, and the different section 4 wording between contents and body.

## Verification

Two independent `gpt-6-luna` subagents reviewed prose/front matter/references/glossary and tables/superscripts/footnotes respectively. Their reports are retained in `evidence/luna-prose-review.md` and `evidence/luna-table-review.md`. The glossary segmentation finding was corrected and re-reviewed; no unresolved content discrepancy remains in those reviews.

An independent source-character inventory compares 58,232 non-whitespace prose characters, excluding explicitly documented layout regions and tables; it reports zero missing or additional characters. This is an accounting guard, not a substitute for checking order and meaning. Tables are separately curated and visually checked against physical pages 22–26, then protected by approved-content checksums. The built report's text must equal the approved report text, and structural counts and internal links are checked.

The verification baseline is a reviewed snapshot, not a claim that PDF extraction is universally reliable. Future reports need their own extraction and review. No legal, cryptographic, or policy conclusions have been added to the report.
