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

# GovRAMP RFC GR – 2601 conversion record

Source: user-supplied `GovRAMP - Request for Comments (RFC) GR - 2601.pdf`, November 2026. The unchanged 17-page original is retained at `public/sources/govramp-rfc-gr-2601.pdf`; its SHA-256 is recorded in the report and approved-content manifest. No publisher download URL was supplied, so the source link points to this retained PDF. GovRAMP is attributed as the issuing organization; document metadata's software author is not presented as a publication author. No explicit reuse license was found in the supplied publication; this edition does not assert new rights over its content. No external attachments have been imported or represented as part of the supplied PDF.

## Layout transformations

- `scripts/convert-govramp.py` is independent of the NIST importer. Reproduce with `uv run --locked python scripts/convert-govramp.py`.
- Prose reflows continuously. Printed line wraps and whitespace normalize; original punctuation, hyphens, numbers, dates, and wording remain. Paragraphs and list items spanning pages are joined. Bold, italics and superscript are retained.
- Bullets and numbering become real nested HTML lists. Source bullet glyph variations become browser list markers. Printed question numbers remain explicit list values.
- The cover's textual publication details remain in the reading text. The original logo is cropped from the cover. All graphics, watermarks, decorative rules, repeated footer logos, and exact original layouts remain in 17 full-page images under “Original page layouts,” with PDF page links. These supplementary images can be expanded without hiding prose and work as native disclosures without JavaScript.
- The cover contents become linked navigation. Dotted leaders are omitted; the original printed page numbers are retained even where they differ from physical PDF pages. Navigation links point to the actual headings.
- The Part A table is joined across physical pages 7–8 into one semantic table. The Part B table on physical page 9 is independently represented as a semantic table. Column and row headers have explicit associations; wrappers are keyboard-focusable scrolling regions. Editorial figure captions reuse source labels and are excluded from source accounting/search.
- Source URI annotations are retained. Whitespace-only link fragments are unwrapped. Internal PDF links become physical-page anchors. Physical page anchors, block/page mappings and original extraction are retained under `evidence/govramp-rfc-gr-2601/`; continued paragraphs carry their starting page. No footnotes were present.

## Source quirks intentionally retained

- The Ready row in the outstanding-controls table remains `17 / 4 / 3`.
- Source contents page numbers, `20 x`, `KSI’s`, `Indicate if.....`, `Determine if.....`, and references to future-dated documents remain unchanged.
- The title retains the source en dash and all prose retains its original Unicode punctuation.

## Verification

Independent `gpt-6-luna` prose and table/graphics reviews are retained under `evidence/govramp-rfc-gr-2601/`. The initial prose review caught an importer bullet-regex bug; this was corrected and reviewed again. The table reviewer independently confirmed every cell and pixel-compared all 17 delivered page images with source renders. `scripts/check-govramp-source.py` compares the full ordered body prose (24,203 non-whitespace characters), every table cell, list numbering, source URI coverage, and image structure against the PDF. This comparison runs from the shared verifier. The original NIST checks remain unchanged.

Browser interaction QA is unavailable in this session because local browser use is disabled in Work settings. Phone portrait, 200% text, both theme modes, keyboard expansion, and interactive search therefore remain unverified for this import; see `evidence/govramp-rfc-gr-2601/ui-review.md`. Static HTML, built-text equality, anchor/link integrity, accessible table structure, and search-index generation are verified. Publication was authorized by the user on November 3, 2026, with this browser-QA limitation disclosed.
