# Reading-interface verification

Verified locally on 2026-10-28 against the production Astro build served at `http://127.0.0.1:4321/pdftoweb/`.

## Browser checks

- Inspected the desktop library and the portrait report visually in the in-app browser.
- Portrait viewport checks at 320, 390, and 430 CSS pixels found no page-level horizontal overflow: document scroll width equaled viewport width.
- Light and dark themes rendered correctly; the explicit Light choice persisted when navigating between report and search pages.
- Full-text search for `cryptography` returned the report with section links and excerpts. Current-report search for `ML-KEM` returned the report with the relevant section anchors.
- Expanded Table 8 successfully. At 125% zoom, its computed table text size was 20px; every cloned `headers` reference resolved within the expanded table (zero broken associations).
- Closing the table with its Close button restored the reading page. The parent agent also verified that Escape closes the dialog and restores focus to the originating Expand table button.
- No browser console errors or warnings were observed during these checks.

## Multiple-report integration

A temporary second report was added and indexed. The parent agent verified in the browser that `cryptography` returned two publications, and selecting the temporary report filter returned exactly one publication with its fixture section anchor. The fixture was then deleted and the production build recreated. Neither its source JSON nor its generated report route remains.

## Progressive enhancement and final build

Static inspection, rather than a JavaScript-disabled browser session, confirmed that the final HTML contains the full report: 8 tables, 8 horizontal-scroll wrappers, 43 section headings, 4 footnotes, and 72,090 prose text characters. Source and internal links are native anchors. Table/image expansion and full-text search require JavaScript; ordinary reading does not.

The final `mise exec -- pnpm build` succeeded, producing three static pages and a Pagefind index containing one publication. The local preview remains running for final review.

## Parent final checks

- Actual browser scripting-disabled reload at 390px: all 8 tables and 35 glossary terms present; no expand buttons (expected), no page overflow. Scripting restored afterward.
- Actual 200% root text at 390px exposed header overflow (418px). Header wrapping fixed and retested: 390px scroll width at 390px viewport, body text 34px. Test override removed.
- Escape from expanded Table 8 closes the dialog and returns focus to its Expand table button.
- Portrait abstract screenshot visually inspected after anchor scrolling settled; typography and margins read cleanly.
