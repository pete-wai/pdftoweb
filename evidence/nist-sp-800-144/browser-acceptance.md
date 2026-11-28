# Browser acceptance: NIST SP 800-144

Reviewer: gpt-6.1-terra. Tested an isolated static build with Playwright Chromium at 390 × 844, using the `/pdftoweb/` base path.

Both light and dark modes passed at 100% and 200% root text size (prose 17px and 34px). Document width remained 390px; each table scroller reached its right edge. Mobile contents navigation, footnote 2 and its return link, report-filtered search, and reading text and tables with JavaScript disabled passed. No JavaScript page errors were observed.
