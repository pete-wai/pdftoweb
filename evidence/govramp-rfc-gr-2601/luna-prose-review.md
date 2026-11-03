# GovRAMP RFC GR – 2601 prose fidelity review

Reviewer: independent prose review (`gpt-6-luna`)

Source: `public/sources/govramp-rfc-gr-2601.pdf` (17 physical pages)
Converted content: `src/content/reports/govramp-rfc-gr-2601.json`
Importer: `scripts/convert-govramp.py`

## Follow-up review (regenerated conversion)

Re-reviewed the regenerated JSON against the PDF page text and the supplied rendered page montages. The initial-character losses recorded in the first review are fixed. In particular, the words “ongoing,” “operational,” “Outstanding,” “objectives,” “organizations,” “objective,” “on,” and “obligations” now appear intact. I also revisited the suspected duplicate content using direct text nodes and list nesting rather than recursive BeautifulSoup `get_text()`: nested list text is not duplicated in the HTML; recursive extraction had made parent `<li>` items appear to contain their child-list wording.

The source-to-reading order is sound across the front matter, main report, response instructions, and appendix. The important nested structures now match the source layout, including the Tab 2 component list; the Core/Ready/Authorized crosswalk details; submission questions; response questions and subquestions; and the benefit explanation bullets. The source montage shows these nested/numbered groups in the expected order. I found no remaining substantive prose omission, addition, or repeated prose in those structures.

## Remaining notes

1. **Inline link boundaries contain whitespace-only anchors and punctuation is split into separate anchors.** For example, the paragraph on physical p. 2 has `References:` followed by an empty-space FedRAMP link, the title link, another space-only link, “and,” the GovRAMP link, and a separate link for `)`. Physical p. 4 similarly separates `Appendix` and `)`; physical p. 15 separates `FIPS 200` and its comma. These render as contiguous text in the supplied visual output and do not change wording, but the HTML has noisy, fragmented link boundaries. It would be cleaner and more faithful for accessible reading to link the reference words alone and leave adjacent punctuation as ordinary text.

2. **Ordinal suffix formatting is flattened for a linked reference.** Physical p. 16 prints “October 9th” with the `th` raised; the converted link text contains “View October 9th” without superscript markup. The wording remains intact; this is a minor formatting discrepancy.

3. **No remaining list/paragraph hierarchy discrepancy found.** Specifically, earlier concerns about repeated descriptions in nested lists were false positives from recursive text extraction. Parent list items have direct lead-in text, with detail items nested once beneath them; visually this follows the source on the supplied page renders. Prose paragraphs separated at section/subsection boundaries also match the document structure.

## Scope notes

- This review covers prose, headings, navigation text, links, paragraphs, and lists. Tables and their cell fidelity are excluded for the separate table reviewer.
- Source wording, including its editorial oddities, must remain verbatim. No source typos, dates, numbers, punctuation, or standards references should be silently corrected.
- The metadata description is library summary text and is not treated as report prose.

## Disposition

The regenerated conversion passes the prose/order/list-hierarchy review, with the two minor inline-link/formatting notes above. Those notes do not alter substantive prose. Retain this review alongside the conversion evidence; the earlier truncation and duplication concerns are superseded by this follow-up.

## Final formatting follow-up

The final regenerated HTML now wraps the linked `th` in `<sup>` for “October 9th” on physical p. 16. It also unwraps whitespace-only anchors. The remaining anchors around some punctuation/annotation fragments are retained intentionally to preserve the source PDF's original link annotations; they do not introduce or alter visible prose, so I accept those boundaries as source-faithful. `uv run --locked python scripts/check-govramp-source.py` passes, confirming the ordered normalized source text, tables, links, list numbering, and all 17 page images. No actionable prose, formatting, or hierarchy findings remain.

Final disposition: prose review approved for this regenerated conversion.
