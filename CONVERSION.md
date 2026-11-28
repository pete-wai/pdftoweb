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

# Hegseth articles of impeachment conversion record

Source: user-supplied `hegseth_articles_of_impeachment.pdf`, received November 9, 2026. The unchanged 34-page original is retained at `public/sources/hegseth-articles-of-impeachment.pdf`. The publication itself is undated and leaves its resolution number blank (`H. RES. __`); neither is inferred from the PDF metadata. “Mr. MASSIE” is the introducer named in the source. This reading edition makes no claim that the supplied resolution was officially introduced, adopted, or authenticated. No explicit reuse license appears in the supplied document; no new rights over its text are asserted.

## Layout transformations

- Reproduce using `uv run --locked python scripts/convert-hegseth.py`; the NIST and GovRAMP importers remain separate.
- All substantive text remains in source order, including repeated title text, the signature placeholder label, every allegation, and all dates, punctuation, and citations. Only whitespace and printed line wraps normalize. No claims are verified or editorially corrected.
- The dotted signature rule and running footer page numerals are omitted. The original PDF preserves those layout elements.
- Adjacent title lines and continued paragraphs are joined. Source hyphens remain, including hyphens at line endings. Source bold and italic spans are retained semantically.
- Eight article headings become linked semantic headings. Numbered clauses become nested ordered lists with literal source labels retained and browser markers suppressed. Source-page mappings include every page contributing to a continued block.
- The PDF contains no tables, footnotes, or explanatory figures; review findings are retained under `evidence/hegseth-articles-of-impeachment/`.

## Verification

The independent checker compares all 56,861 non-whitespace source characters and all 10,170 whitespace-separated tokens in order, verifies all eight article headings and all 34 source-page mappings, and checks the original PDF checksum. Shared checks cover built-text equality and every local link/anchor. Independent Luna prose and tables/layout reviews are retained beside the page extraction and block mappings. Approved hashes are added only after findings are resolved.

Browser access was unavailable in this session (no enabled browser; Chrome reported unavailable). Interactive phone portrait, 200% text, theme switching, keyboard navigation, and search behavior could not be exercised. The existing shared reader styles and interactions are unchanged; static structure, anchors, no-JavaScript prose, build output, and search index generation are checked. See the UI review record for details.

# ARTEX expedited strategy briefing

The supplied draft of *The Third Wave: ARTEX and Agentic Offensive Frameworks (AOFs)* prints version 0.8 and an original release date of 24 November, 2026. The attachment filename ends in 0.81. The reading edition uses the printed version. The original PDF is retained at `public/sources/cisos-artex.pdf`. The cover links to the publisher, and the page 4 notice identifies the CC BY-NC 4.0 license.

Reproduce with `uv run --locked python scripts/convert-artex.py`. Physical page numbers appear in the HTML as `data-source-page` on prose blocks and table rows. The two-column pages read down the left column first. Three paragraphs continue across a gutter. The edition rejoins line wraps, consolidates hyperlink rectangles and omits running footers, decorative icons, and background artwork. On page 7 the visible numeral in “1. Hardened Defenses” is restored from the rendered page. Section and table headings use the text layer’s casing.

At the requester’s direction, the reading edition omits the lead authors, authors and contributors on pages 2–4. The collective cover byline is available under Attribution. The publication notices from page 4 and the credits in the bibliography are retained.

The side-by-side table on page 9 has three rows. The risk register spans pages 15–17 and the controls list spans pages 18–20. Numbered row headers, explicit header associations, and keyboard-scrollable wrappers preserve relationships within the three tables. Page 15's severity legend uses a definition list. Table 2's caption includes the introductory note in printed order.

Independent GPT-6.2 Sol prose and table review records and Chromium browser checks are under `evidence/cisos-artex/`. The requester approved this reviewer substitution.

# NIST SP 800-144

Wayne Jansen and Timothy Grance’s *Guidelines on Security and Privacy in Public Cloud Computing* is dated December 2011. The edition retains both covers, the front matter, seven numbered sections, and both appendices from the [80-page NIST PDF](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-144.pdf). Attribution and commercial-product notices remain in the text.

Reproduce with `uv run --locked python scripts/convert-sp800144.py`. The importer uses the PDF’s ordered structure tree, normalizes line wrapping, omits page numbers and dot leaders, and joins continued paragraphs and list items. Webdings and Wingdings list markers become native bullets. The unnumbered publication and resources tables have editorial accessibility captions. Table 1 spans physical pages 45–46 and retains one copy of the column headings. The diagram and the cover branding come from the embedded PDF images. The 27 page-bottom notes become linked endnotes. Reference labels retain their original spelling. Two source-page attributes can occur in one paragraph when it crosses a physical page boundary.

The original source hash is in the report metadata. The page extraction, independent Terra prose and table reviews, and Chromium phone-portrait checks are in `evidence/nist-sp-800-144/`. The source checker compares character inventories by physical page and checks table count, acronym pairs, and both directions of the note links.

# NIST SP 800-53A Revision 5

The edition follows the [733-page January 2022 NIST PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53Ar5.pdf) supplied by the requester. Joint Task Force is the printed author. The original publication, including its attribution, patent, copyright, and commercial-product notices, is retained. The web edition uses the content of this PDF, including its printed examples and control identifiers.

Reproduce with `uv run --locked python scripts/convert-sp80053a.py`. The importer uses the tagged structure of the front matter, chapters and appendices. In the catalog on physical pages 51–694 the horizontal rules define the rows. Each identifier is associated with its printed value, and control titles repeated at a page break remain in the edition. Private-use glyphs and ligatures are decoded by embedded font face. Running headers, rotated margin notices, repeated catalog footers, page numbers and dotted contents leaders are omitted. The source PDF retains these elements. The contents, chapters and all 20 control families have anchors, and the catalog remains on the same page as the introductory chapters, references and six appendices.

The HTML carries physical page mappings, including continuations. The figures retain their original artwork and have native text disclosures. Figure 8’s disclosure describes the arrows and groups the text by phase. Figure 9 associates each finding and assessor comment with its objective. The visible source spelling “foreach” remains in Figure 1. Editorial captions label otherwise untitled tables. Footnotes 1–65 have linked return paths. Several Word structure tags placed text following a footnote call in the wrong position. Those paragraphs were reconstructed from the printed lines, including the bullet that continues the list on page 14.

The complete page extraction and separate `gpt-6.1-terra` review records are in `evidence/nist-sp-800-53a-r5/`. The report JSON records the SHA-256 of the unmodified source. Browser checks use a 390-pixel Chromium phone viewport, both themes, 200% text, and JavaScript-disabled reading.

For SP 800-53A, the verifier also compares the character inventory of each of the 89 physical pages outside the catalog and the printed text immediately surrounding each footnote call. All 65 calls match their source context. The catalog review compares all 7,104 keyed rows and the ordered text on each of the 644 catalog pages.
