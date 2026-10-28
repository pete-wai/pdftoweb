# PDFtoWeb maintenance

- Preserve source publication content verbatim. Only layout and formatting may change; never silently correct source typos, numbers, dates, punctuation, or standards references.
- Keep original PDFs and source checksums. Record permitted layout transformations and source-page mappings.
- Use independent `gpt-6-luna` subagents for prose and table fidelity review of each new conversion, and retain findings under `evidence/`. Resolve findings before updating approved-content hashes.
- Read README.md and CONVERSION.md before adding reports. New imports must not overwrite the NIST-specific converter.
- Use exact runtime pins: `mise exec -- ...`, `uv run --locked ...`, project-local `.venv`. Preserve lockfiles.
- Build with `mise exec -- pnpm build`, then validate with `uv run --locked python scripts/verify.py`. For content edits, independently compare with the source before updating verification baselines.
- Preserve `/pdftoweb/` base-path compatibility, continuous reading, no-JavaScript prose, relative font sizes, both color modes, and phone portrait usability.
- Test tables, footnotes, internal anchors, search, and 200% text on narrow screens. Never publish QA fixture reports.
