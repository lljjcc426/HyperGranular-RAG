# RG-learned-set-v5.0

SPEC_ID=HGRAG-LEARNED-SET-V5-20261004. User-authorized exploratory development on already opened Stage4E/F only. This is a new learned selector, not a rerun or retrospective explanation of static q25.

Completed: four models × three training seeds; primary128 QA; fixed64 budget and closed-reference comparisons; exact index profiling and bounded leaf-pruning refinement. Read [results and decision](RESULTS_AND_NEXT_DECISION.md) first, then [run instructions](REPRODUCE.md). H4 has a small development signal but no stable advantage over all controls; exact GB/KM preserve selection and are slower than Flat at this scale. No next experiment is started.

## Design before results

Use the per-dataset union of blind-input paragraphs, frozen BGE CLS/L2 Top128, complete paragraphs, shared v4 P2 FP16 Qwen2.5-3B reader. No Gold injection at inference. Historical D0/D1 are DEV; other normalized-question/source-ID groups use SHA256 prefix `rg-learned-set-v5-split`, 80/20 FIT/TUNE. All derived subsets remain in their query group. Documents may overlap splits. This is not independent confirmation or full-wiki.

Train H1, H2, H4 and parameter-comparable DeepSets with the same annotation-conditioned supervision. K=6, rank32, hidden128, query batch8, eight subsets/query/step, AdamW 1e-3, decay1e-4, clip1, up to30 epochs. Select epoch using TUNE loss and same-cardinality ranking. Seed1729 precedes2026,426. Finite error-driven revisions are permitted and logged. Labels measure known support, not factual truth or answer utility.

Search uses beam4 to depth6, retains all depths and feasible Dense-K, never stops on a negative marginal. Flat is vectorized. GB/KM exact use identical conditional factors, maximum Euclidean radius, leaf8, conservative float64 bounds and identical ties/feasibility. Every member remains available. Exact outputs must agree; tree cost includes query-specific construction. One-representative approximation is a separate diagnostic.

All-TUNE selection supplies the 128-query QA panel (Hotpot64, MuSiQue64; specified hop strata selected by hash),1024 actual serialized input tokens. QA may consume completed rows while the remaining CPU selection continues; all primary rows finish before secondary-seed training. Eight primary logical arms: Dense-budget, MMR(.7)-budget, H1,H2,DeepSets,H4 Flat/GB/KM. Dense/MMR have no six-block cap. Subsequent priority: other seeds, fixed balanced64 at512/2048, same64 closed reference Dense/H1/H4. All queries including failures remain denominators. No significance PASS or model-selection on confirmation.

Limits: new GPU process wall5h, CPU process4h, disk2GB, paid0, reader calls3000; cumulative GPU12h/CPU24h/disk10GB. Starting recorded GPU19764.376329s; CPU lower bound18520.078s (older unknown CPU remains unknown). Reserve at least one third GPU allowance for natural QA. Stop complete lower-priority modules at resource boundary, irrespective of outcomes.

Raw text, labels, IDs, mappings, embeddings and weights stay ignored under `local/`. Public code and aggregate summaries only. No paper, PDF, figure or historical artifact edits. No restricted data, new base models, relation frontend or external submission.
