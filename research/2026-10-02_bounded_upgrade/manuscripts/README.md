# Bounded literature refresh: two revised manuscripts

- [Conference PDF — 10 total pages](conference/HyperGranular-RAG_Conference.pdf)
- [Journal PDF — 23 total pages](journal/HyperGranular-RAG_Journal.pdf)
- [Editorial and visual check](FINAL_EDITORIAL_CHECK.md)
- [Document invariants](DOCUMENT_CHECK.json)
- [Venue choice and Chinese story](../TARGETS_AND_STORY.md)
- [Literature review](../../../literature_refresh/2026-10-02_bounded/REVIEW.md)

Both are complete English manuscripts derived non-destructively from
`paper/versions/2026-10-02_editorial_final/`. All previous results, equations,
numeric tables and figure assets are retained. New tables are conceptual or
evidence-boundary comparisons; they contain no new experimental scores.

Local build (Python with PyMuPDF and Pillow; MiKTeX under the current user's
AppData as in the existing build):

```powershell
python build_manuscripts.py conference journal
python check_revision.py
```

Run from this directory or pass the script's full path. The invariant checker
also expects the preserved baseline inside this repository. No model, Gold or
experiment runtime is needed. Real build logs and contact sheets are retained;
full-resolution page renders are reproducible ignored local files.

These are alternative manuscripts on the same evidence, not authorization
for duplicate submission. Venue formatting, human authorship and disclosures
remain to be finalized before any external submission.
