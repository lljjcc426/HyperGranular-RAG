# Evidence delivery repair — completed exploratory study

- [Scientific results and decision](RESULTS_AND_DECISION.md)
- [Full historical loss-chain diagnosis](LOSS_CHAIN_REPORT.md)
- [All 13 arms, absolute scores and costs](PILOT_RESULTS.csv)
- [All paired contrasts and descriptive intervals](PAIRED_CONTRASTS.csv)
- [Aligned proxy/answer reference correction](PROXY_REFERENCE_CORRECTION.json)
- [Run card](RUN_CARD.md), [merged manifest](manifest.json), [final verification](FINAL_VERIFICATION.json)
- [Writing impact only](MANUSCRIPT_IMPACT.md), [engineering notes](ENGINEERING_NOTES.md), [actual execution record](EXECUTION_LOG.md)

Starting reference: ed7d96a0c1a1aa823c71662bf40260bfb3e5f682. All new code,
results and private local derivatives are isolated here; no old result was changed.
The public sampling IDs and rankings are derived artifacts. local/ contains full
prompts, predictions and annotation-derived diagnostic rows and is not committed.

CPU synthetic checks: `python tests.py`. Exact experiment runtime is the existing
`temp/stage4e_env/Scripts/python.exe`; PYTHONHASHSEED=0 and the bound numerical
thread settings apply. Existing files cause scientific runners to refuse overwrites.
Do not rerun completed generation as a routine verification step.

Recipe for an explicitly authorized fresh reproduction directory: prepare.py →
verify_rankings.py → generate.py → analyze.py → verify_results.py → delivery_details.py
→ proxy_review.py → finalize.py. The aligned proxy review is required because
analyze.py retains the original mixed-reference step table for transparent tracing.
The target namespace must be changed explicitly before a fresh reproduction;
this README does not grant new execution authority.

The study answered a development question, not independent-confirmation eligibility.
No manuscript, PDF, image, plotting script, locked data or external submission changed.
