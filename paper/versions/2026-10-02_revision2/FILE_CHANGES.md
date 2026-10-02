# File changes and preservation

No file was deleted. No frozen scientific artifact or old manuscript was overwritten. All new scientific-review and paper files are under `paper/versions/2026-10-02_revision2/`; the only existing-file edit for this round is the README's new revision-2 navigation block.

| Paths | Purpose |
|---|---|
| `REANALYSIS_PLAN.md` | Fixed scope and retrospective choices before score inspection; separately committed |
| `rescore.py`, `placement.py` | Independent historical metric reconstruction/canonical migration and prompt-visible-content review |
| `test_revision2.py`, `TEST_OUTPUT.txt` | Six focused differential/real-output checks and actual execution output |
| `scoring/*.csv`, `scoring/*.json`, `scoring/rescore_execution.txt` | Append-only derived scores, comparisons, affected prediction list, input identities, placement and token accounting |
| `conference/main.tex`, `journal/main.tex`, their PDFs | Complete second-revision English manuscripts, created from preserved first versions |
| `shared/` | Version-local styles/bibliography and historical non-score figure sources copied without changing originals; canonical effect numbers/forest plots and new reproduction/budget text |
| `derive_assets.py`, `build_manuscripts.py`, `finalize_review.py` | Document-only derivation, local builds and recording of completed page review |
| `*/build/`, `*/page_review/`, `*/BUILD_STATUS.json`, `MANUSCRIPT_CONSISTENCY.json` | Actual build evidence and per-page inspection records |
| `SCORER_LINEAGE_AND_MIGRATION.md`, `CLAIM_IMPACT.md`, `PLACEMENT_AND_VISIBLE_CONTEXT_AUDIT.md` | Scientific review and bounded interpretation |
| `README.md`, `REVISION_LOG.md`, `BUILD_AND_PAGE_REVIEW.md`, `FINAL_STATUS.md`, `.gitignore`, `.gitattributes` | Version entry, handoff, build status and local artifact rules |
| Repository `README.md` new top block only | Current revision links; earlier sections retained as history |

The existing dirty audit/config/Stage6 source changes, untracked audit materials and 12 untracked Stage6 development artifacts remain in the worktree and outside this round's index/commits. The prior `2026-10-02_dual_manuscripts` directory, `paper/latex/`, root bibliography, and all `results/` files are unchanged by this round.

Moving mathematical material means relocating paragraphs between body and appendix inside the new manuscripts; it does not delete historical evidence. The official metric sources are cached in ignored `temp/`, and no raw Gold, weights, or restricted dataset is staged.

The two existing public qualitative examples retain their previously published question/evidence/reference excerpts in the copied figure-source CSV. This is reuse of the old illustrative paper material, not publication of a raw Gold map. Compiler logs and the copied bibliography style retain their original whitespace; they are not reformatted to manufacture a clean whitespace check.
