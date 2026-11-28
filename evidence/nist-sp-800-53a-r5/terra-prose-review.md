# Independent prose review

Reviewer: `gpt-6.1-terra`, as requested by the user. Source: retained `public/sources/nist-sp-800-53a-r5.pdf` (733 physical pages).

Review in progress. The assessment catalog runs from physical page 51 through page 694. The PDF text layer encodes several letter combinations using private-use glyphs, and the encoding of two glyphs differs between Calibri and Calibri-BoldItalic. `scripts/check-53a-prose.py` independently extracts the original text using font-sensitive mappings and audits line-fragment coverage and nearby source-page mappings. This audit is a guard rather than proof of reading order, completeness of short fragments, or table-cell relationships. The conversion JSON was not yet available when the audit was prepared; no passing comparison is claimed.

## Initial comparison

The first generated JSON was audited against 24,247 source line fragments (1,571 from the front matter and chapters 1–3, 21,386 from the catalog, and 1,290 from the appendices). All catalog fragments appeared in the output on the mapped or an adjacent page. The initial comparison reported 15 missing fragments: two lines of the first bullet on physical page 14 were absent; the other 13 belonged to text displaced around footnote calls on pages 10, 23, 37, 39, 48 and 732. For example, the first page 10 paragraph moves `1 SP 800-53 and [` to its end. Page 14 shows the second bullet but omits the first. Notes also appear out of reading order, including before the main prose on page 14, with no linked note calls. Findings were reported to the conversion author and remain open pending a regenerated output and recheck.

The nine delivered figure files on physical pages 24–30, 47, and 731 match source crop renders pixel-for-pixel. The audit excludes source text only when its complete line bounding box falls inside one of those verified crops; it does not exclude entire figure pages. This does not establish that the chosen crop boundaries contain every part of each original figure.

## Recheck

After regeneration, all 24,247 audited source line fragments were present and mapped to the same or an adjacent physical page, including all 21,386 catalog fragments. The omitted page 14 bullet and the six paragraphs displaced around note calls now follow the source in the checked locations. All nine figure files still matched their source crops. In the final snapshot, all 65 numbered notes and references occur exactly once, have reciprocal links, and are mapped to the same physical page; note 31 is now linked. Full reading order across all 733 pages and exact placement of every individual note call are not proven by the fragment audit.

The final audit checked 24,242 fragments with no missing or misplaced fragments. The count changed because the printed table of contents was rebuilt as links and its decorative dot leaders are excluded before applying the minimum fragment length. Figure text equivalents are excluded from the comparison, so they cannot mask missing prose. Verified figure crops are excluded only within their boundaries. No unresolved findings remain from the checks performed; these automated checks do not prove complete reading order or replace visual review.
