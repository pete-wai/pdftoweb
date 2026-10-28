# Independent table content audit: NIST IR 8547

## Coverage and method

- Compared all eight tables in `src/content/reports/nist-ir-8547.json` and the built report HTML at `dist/reports/nist-ir-8547/index.html` against the source PDF `public/sources/nist-ir-8547.pdf`.
- Rendered and visually inspected PDF physical pages 22–26 with PyMuPDF (`uv run --locked python -c 'import fitz'`), corresponding to the printed report pages 15–19. The render was at 2× scale.
- Checked table captions, headers, every visible body-cell value, family grouping/merged cells, superscripts, transition styling/text, and footnotes 2, 3, and 4. The rendered HTML contains tables 1–8 in the same sequence and their cell data and group spans agree with the source pages.

## Findings

- **No substantive table-content discrepancies found** across tables 1–8. Values, spelling, punctuation, and cell associations match the source PDF.
- Merged family cells are represented consistently with the source: ML-DSA, SLH-DSA, LMS/HSS, and XMSS/XMSSMT groups in table 3; ML-KEM in table 5; AES in table 6; and SHA-1, SHA-2, SHA-3, and Ascon groups in table 8. The split of table 4 across printed pages 16–17 retains its three schemes and their per-row parameters/transitions.
- Superscript references are preserved: table 3's note 2 reference on ML-DSA-44; table 8's note 3 reference in the preimage-strength header and note 4 reference on SHA-1. Footnotes 2–4 match the source text, including note 3's (2^N) expression and italic (N).
- Source spelling **`AES-AEAD128`** in table 7 is retained. No editorial correction was made.
- Captions and column headings match, including “Hash functions and XOFs,” “Collision Security Strength (classical),” and “Preimage Security Strength (classical).”

## Images and figures

The inspected report pages 15–19 are text and tables; they contain no separate meaningful illustrations or charts. A whole-document image-object scan found cover assets on PDF pages 1–2 (the NIST marks/seal and “Check for updates” mark) and small page-6 image objects associated with the contents page; these are publication furniture, not omitted explanatory figures. The rendered report represents the substantive material on the audited pages as accessible HTML tables.

## Limits

This was a manual visual comparison of source pages 22–26 and a content/structure inspection of the generated report HTML. It is not a character-by-character OCR comparison of the entire 34-page report. The images/figures assessment used visual inspection of the cover, contents page, and all image-bearing PDF pages reported by PyMuPDF.
