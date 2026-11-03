# GovRAMP RFC GR-2601: independent table and graphics review

Reviewer: gpt-6 Luna (independent fidelity review)  
Scope: all tables and graphic/layout fidelity, with table source pages 7–9  
Source: `public/sources/govramp-rfc-gr-2601.pdf`  
Conversion: `src/content/reports/govramp-rfc-gr-2601.json` and `evidence/govramp-rfc-gr-2601/tables.json`

## Method

Rendered source physical pages 7–9 with the project-locked PyMuPDF and inspected each full page at original layout scale. Parsed the converted JSON HTML with BeautifulSoup, checking table order, text, cell grouping, row and column headers, explicit `headers` associations, source-page attributes, image inventory, and captions. Compared all 17 supplied page facsimiles to fresh PyMuPDF renders of the source at 2× (the delivered 1224×1584 dimensions); pixel samples match on every page. Visually inspected the extracted GovRAMP logo crop.

## Findings

- **Part A KSI mapping table, physical pages 7–8:** The conversion has the same three columns and two records, in source order: `KSI-CNA-EIS` (page 7), then `KSI-CNA-IBP` (page 8). All source guidance and assessment objectives are present, with their paired “Indicate if.....” / “Determine if.....” labels and each NIST control statement kept in its proper guidance/objective column. The page break is represented by one continuous table, with the original first record and second record mapped to their respective source pages. No repeated header is invented for the continuation page.
- **Part B outstanding controls table, physical page 9:** All four columns and three rows are present and correctly associated. Values match the source exactly: Core `7 / 4 / 3`; Ready `17 / 4 / 3`; Authorized `120 / 24 / 96`. The apparent Ready arithmetic inconsistency is preserved verbatim, as required.
- Both tables use column headers and row headers with `scope`, stable IDs, and explicit cell `headers` associations. Their scroll regions have keyboard focus and are labelled by the matching captions. Captions and source page mappings are present.
- **Footnotes:** No footnotes occur with these tables on source pages 7–9; none are added to the table content.
- **Graphics and layout:** The conversion includes page facsimiles for all 17 source pages. Each rendered image is pixel-identical to a fresh source-PDF render at the same scale, so all page graphics, logos, rules, colors, tables, and printed layout are retained in the expandable facsimiles. The standalone GovRAMP logo crop visibly contains the complete source mark and wordmark without clipping. The first-page logo has descriptive alternative text.

## Discrepancies

None found in the reviewed tables, source-page mappings, facsimiles, or logo crop. No conversion changes are requested.
