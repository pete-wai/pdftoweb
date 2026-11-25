# ARTEX reader browser review

Reviewed the built report under the `/pdftoweb/` base path using Playwright and headless Chromium, served from a loopback-only static preview. The native Mac was locked. The headless run exercised the built site in a browser using iPhone 12 portrait emulation at 390 × 844 CSS pixels.

- Light and dark themes both rendered at 100% and 200% root text scale. Computed body prose grew from 17 px to 34 px. The document stayed 390 px wide at both scales. Tables that exceeded their 341 px containers remained horizontally scrollable through the last column. Screenshots at 200% confirmed the first table remained legible in both themes.
- The mobile Contents link opened the matching section and closed the disclosure. The `#pdf-page-16`, `#pdf-page-17`, `#pdf-page-19`, and `#pdf-page-20` links targeted the correct table continuation rows.
- Tab moved from the first table's scrolling region to its expansion button. Enter opened the dialog, the zoom control reached 200%, and Escape closed the dialog and returned focus.
- Report-filtered Pagefind returned the ARTEX report for the exact phrases “transitive trust” and “reconnaissance was easy to detect,” with matching table text in the excerpts.
- Loading the page with JavaScript disabled retained readable report text and all 44 table rows. The interactive run reported no page-level JavaScript errors.

The phone check used emulation. No physical device or Safari was used.
