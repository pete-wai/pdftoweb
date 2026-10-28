# PDFtoWeb

A mobile-first library of full-length reports, converted to continuous, semantic HTML.

**[Read the library](https://pete-wai.github.io/pdftoweb/)** · **[NIST IR 8547](https://pete-wai.github.io/pdftoweb/reports/nist-ir-8547/)**

The first reading edition is *Transition to Post-Quantum Cryptography Standards* (October 2026). This is an independent reading edition, not an official NIST website. The original PDF remains authoritative.

## Develop

Install [mise](https://mise.jdx.dev/) and [uv](https://docs.astral.sh/uv/), then:

```sh
mise install
uv sync --locked
mise exec -- pnpm install --frozen-lockfile
mise exec -- pnpm dev
```

Development binds to localhost. The site uses `/pdftoweb/` as its base path. Full-text search is generated at build time; test it against the production preview:

```sh
mise exec -- pnpm build
uv run --locked python scripts/verify.py
mise exec -- pnpm preview
```

Node and pnpm are pinned in `.mise.toml`; Python is pinned in `.python-version`. Dependencies and lockfiles are committed. Astro emits static pages; Pagefind adds a static search index. No API keys, analytics, remote fonts, paid services, or application backend are required.

## Add another report

1. Save the original, unmodified PDF in `public/sources/`. Record its URL, publication date, authors, and SHA-256 checksum. Review its reuse conditions.
2. Extract page-mapped text and inspect rendered PDF pages. `scripts/convert.py` is deliberately specific to NIST IR 8547; do not run it on unrelated layouts. Write a report-specific importer or carefully prepared content.
3. Add `src/content/reports/<slug>.json` with these fields:

```json
{
  "slug": "stable-report-slug",
  "title": "Exact report title",
  "identifier": "Publisher identifier",
  "authors": ["Author name"],
  "date": "Month YYYY",
  "sourceUrl": "https://publisher.example/report.pdf",
  "sourceSha256": "sha256-of-original-pdf",
  "pdfPath": "/sources/report.pdf",
  "description": "Short library description, separate from the report text.",
  "headings": [{"id": "introduction", "text": "Introduction", "level": 2}],
  "html": "<h2 id=\"introduction\">Introduction</h2><p>Faithful source text.</p>"
}
```

4. Use semantic headings with stable IDs, real lists, `<dl>` glossary entries, linked references and return links for notes. Place tables in `.table-figure > .table-scroll > table`; provide captions, column headers, and explicit header associations for merged cells. Use `tabindex="0"`, `role="region"`, and a caption-based label on scroll wrappers. Images need meaningful alternative text and responsive sizing; the shared reader adds expansion controls automatically. Only trusted, reviewed HTML belongs in report JSON.
5. Preserve substantive source content verbatim. Record layout-only transformations. Independently review prose and every table against the PDF using Luna subagents, resolve findings, and retain reports under `evidence/`. Character inventories help detect loss but do not prove correct order or meaning; visual and independent reviews are required.
6. Add source and content files to `evidence/approved-content.json` using SHA-256 hashes **after** review. Add report-specific source comparisons and structural checks to the validation scripts; do not merely update a baseline to silence a failing check.
7. Build and verify. Test phone portrait widths, enlarged text, themes, keyboard interaction, figure expansion, search filters, and every internal link. The library and search discover new report JSON automatically.
8. Commit and push to `main`. GitHub Actions validates and deploys to Pages. Exceptionally long reports should only be split after an explicit editorial decision; continuous reading is the default.

## Fidelity and evidence

- Original source: `public/sources/nist-ir-8547.pdf`.
- Original text by physical PDF page: `evidence/source-pages.json`.
- Curated, visually checked table cells: `evidence/tables.json`; generator: `scripts/tables.py`.
- Block mapping, independent Luna review findings, and browser QA: `evidence/`.
- Layout transformations and known source quirks: [CONVERSION.md](CONVERSION.md).

To reproduce this conversion, run `uv run --locked python scripts/tables.py` and `uv run --locked python scripts/convert.py`. Inspect diffs and run the checks before accepting any changes.

## Deployment

The public repository uses GitHub Pages with GitHub Actions as the publishing source. The workflow builds on pushes to `main`; pull requests run checks without deploying. It checks approved checksums, independently accounts for source prose, and checks the built text and local links before publishing.

To change hosting later, update Astro's `site`/`base` settings and source-PDF links emitted by the converter together. To roll back, revert the offending commit and push; the same validated deployment workflow runs again.

## Source rights

The report is attributed to NIST and retains its publication notices. Site code does not assert new rights over the source publication. See the source PDF's Copyright, Use, and Licensing Statements for the original terms.
