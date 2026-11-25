# Independent prose fidelity review

I compared the original 26-page attachment with the generated reading edition. I rendered all 20 pages with retained prose, inspected their reading order, and independently extracted glyph lines using page coordinates. I read down the left column and then down the right, grouped contents labels with page numerals, and grouped the severity legend by row. I compared ordered words and characters against the rendered HTML text in the report JSON. Tables were outside this review. I accounted separately for the printed table captions, native list numbering, and article title supplied by the reader header.

- The cover says “Version: 0.8” despite the attachment filename ending in 0.81. The date is printed “Original release date: 24 November, 2026.” Both appear in the reading text.
- The reading edition hides the collective cover byline in a closed attribution disclosure and omits the personal credits on physical pages 2–4. The notices on page 4 and bibliographic source credits on pages 25–26 remain.
- The 11 contents entries and their original printed page numbers match. The executive summary, faster patching example, and credential-theft item correctly continue across their source gutters on pages 6, 12, and 13.
- Page 7 prints “1. Hardened Defenses.” The first numeral is visible in the page render and absent from the source text extraction. The HTML restores it.
- Both columns of page 25 and the one column of page 26 yield 28 citations in order. Twenty-six have source hyperlinks. Retained prose contains all of the source's external link destinations for the reviewed pages.

## Initial findings

1. Two page 7 prose paragraphs were split mid-sentence at visually continuous line wraps.
2. The page 4 email anchor excluded its last two characters. Multiline source annotations yielded repeated identical anchors, and six citations on pages 25–26 left the first letter outside the anchor.
3. Two source titles on page 25 gained a space after their line-ending hyphens. Three source titles on page 25 and one on page 26 gained a space before source punctuation at the end of the linked title.
4. Page 12's three bulleted observations were represented as paragraphs. The caption above Table 2 on page 18 followed its explanatory paragraph in the reading edition.
5. Some source emphasis was absent, including the bold paragraph on page 7, bold leads on page 11, and italic board questions on page 21.

The first build preserved all ordered non-whitespace prose characters after accounting for native markers and the location of the Table 2 caption. The only ordered-word differences after normalizing spaces before punctuation were the two hyphenated citation titles.

## Re-review result

I verified the paragraph joins, complete email anchor, complete citation anchors, the three-item list on page 12, Table 2's caption and introduction order, and the restored emphasis on pages 6, 7, 11, 21, and 24. The final report matches 3,951 ordered prose tokens across 20 retained pages, including all 28 citations. Each of the 26 linked citations has a single anchor. The collective cover credit is complete in the closed attribution disclosure, and the report's authors field is empty. No prose fidelity findings remain open.

Run the independent comparison from the project root with `uv run --locked python evidence/cisos-artex/check-prose.py`.
