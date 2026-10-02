# Actual build and page review

Both complete English manuscripts were compiled locally on 2026-10-02 with MiKTeX pdfTeX and BibTeX. Final PDFs: conference 9 pages; journal 21 pages. These totals include references and appendices. They are internal revision manuscripts, not a claim of venue-specific submission clearance.

The conference initially required another LaTeX pass to resolve ACL line-number placement around floats. The build driver now includes that pass. Final conference commands 1–5 all exit 0; journal commands 1–4 all exit 0. Final logs have no undefined references/citations, overfull boxes, or warning messages. One shell inspection returned code 1 because `rg` found no warnings, not because compilation failed.

Every journal page 1–21 was individually rendered and viewed. Every conference page 1–9 was individually viewed, then all nine final pages were viewed again after the line-number fix. Equations, symbols, table values and captions, forest plot labels, references, headers, page numbers, and page transitions were checked. The review used full page PNGs, not only text extraction or contact sheets. No clipping or text/line-number overlap remains in the final renderings.

The final reproduction-detail addition records the actual Qwen seed/thread settings and renderer truncation rule. After rebuilding, the two affected last pages (conference 9 and journal 21) were rendered and inspected again; page counts and preceding content are unchanged.

`conference/BUILD_STATUS.json` and `journal/BUILD_STATUS.json` contain one explicit inspection note per page. `page_review/page_*.png` preserves the reviewed final renderings; contact sheets aid navigation. The actual compiler stdout/stderr logs, final main.log/BibTeX log, and extracted text are preserved under each `build/` directory. Regenerable LaTeX auxiliaries are ignored.

Rebuild from repository root:

```powershell
temp/dual_manuscripts_env/Scripts/python.exe paper/versions/2026-10-02_revision2/derive_assets.py
temp/dual_manuscripts_env/Scripts/python.exe paper/versions/2026-10-02_revision2/build_manuscripts.py conference journal
```

The second command resets page-review flags to PENDING: a future rebuild must be visually reviewed again before recording completion. `finalize_review.py` records completed manual agent inspection and derives count-based rates; it is not an automated visual verifier. No official scientific runner is involved in document building.
