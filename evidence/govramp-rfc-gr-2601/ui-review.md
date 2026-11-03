# GovRAMP reader QA

## Completed

- Production Astro build includes the new report in the library and report-filtered Pagefind index.
- Independent PDF-to-HTML ordered prose and cell comparisons pass.
- Source visuals inspected on all 17 pages; independent review confirms delivered page images are pixel-identical to PDF renders.
- Static reader keeps all prose visible without JavaScript. Native disclosures are limited to navigation and supplementary page images.
- Both tables have keyboard-focusable overflow wrappers, caption labels, column headers and row-header associations; the existing shared reader supplies expansion controls.
- All original source URI destinations are represented. All internal IDs and local links are checked by the shared verifier.
- Logo retains a white background for legibility in either theme; page images use responsive sizing, intrinsic dimensions and lazy loading.
- No footnotes are present in this source.

## Unavailable interactive checks

The browser tool returned `Local browser use is disabled in Work settings` when opening the localhost production preview. No interactive browser checks were performed. Phone portrait widths, 200% text, theme switching, keyboard/dialog focus, page-image expansion, and live search results still need browser QA. Static structure and build checks are not a substitute for those checks.
