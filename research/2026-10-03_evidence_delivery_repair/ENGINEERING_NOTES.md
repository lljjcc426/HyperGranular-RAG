# Implementation notes

- New code lives only in this round's namespace; legacy retrieval/renderer/scorer
  implementations are imported read-only. No previous uncommitted repairs are
  required by this experiment. No old algorithm or environment file was patched.
- Historical Stage4E blind format is context/sentences; Stage4F is candidate_units.
  Both are parsed by their actual historical blind loaders, with exact cache ID order.
- The Stage4F main telemetry is 6,000 calls/1,947.368 seconds, not the 12,000
  combined main/rerun count. The run card was corrected before generation.
- Initial inline Python inspection hit a PowerShell quote error before execution.
  Replaced it with the small UTF-8 inspect_inputs.py; no shell-boundary experiments.
  A filename search for a nonexistent Stage4H retrieve_generate was corrected to
  stage4h_cbe_retrieval/goldfree_runner; no scientific operation failed.
- The first Git push returned a TLS-connect error. An HTTP/1.1 transport retry
  succeeded before historical diagnostic execution. No local commit was rewritten.
- Synthetic checks passed before the pilot. An additional explicit title-only and
  duplicate-facet test was added during generation; the production selector and
  generation code did not change. Both actual test outputs are retained.
- Independent real-query checks use an ID-set reference for greedy final-list
  selection and exhaustive eviction; they do not call production r1/r2/phi/place.
- DATA_ROLES stores input identities once. No repeated repository-wide hashing.
- Original renderer audits lack full serialized text; the new pilot explicitly stores
  the actual input IDs and decoded visible prompt in ignored local/. Reconstructed
  Dense20/H0 prompts must match archived SHA/visible IDs/token count/truncation on
  the 400 pilot questions before generation.
- Full local diagnostics contain annotation-derived support IDs, and prompt audits
  contain corpus text. They remain ignored. Public files contain derived summaries,
  ranks, sampling IDs, recipe, provenance and resource counts, not raw Gold/weights.
- During interpretation, an explicit reporting error was found: summing R1 greedy
  step deltas measures Phi(R1)-Phi(Dense20), but the answer cross-tab used H0.
  No selector, predictions, EM/F1 or interval was wrong. proxy_review.py recomputes
  both references from fixed rankings; PROXY_REFERENCE_CORRECTION.json supersedes
  only that cross-tab. The original table is retained with a correction notice.
  The current, not-yet-published combined manifest is refreshed after this correction;
  no historical or generation result is overwritten or rerun.
