# Figure 1: inspected-case trace

No answer was generated or rescored for this figure. The source paragraphs, saved
outputs and prior case interpretation were read for the two specified cases.
The diagram uses short semantic paraphrases, not quotations or full prompts.

| Inspected case | Already saved facts used in the drawing | Saved endpoint change |
|---|---|---|
| C12, HotpotQA, seed 2026 | Jobs biography supplies the founder/chairman/CEO link to NeXT. The aligned context adds the NeXT paragraph locating the company in Redwood City. Static answer: Palo Alto; aligned answer: Redwood City. | Annotated support incomplete → complete; canonical F1 0 → 1 |
| C10, MuSiQue, seed 1729 | Inspector Willoughby's creator is Walter Lantz. Both contexts retain the production range 1929–1943 and the distinct 2006 rights-transfer event. Static answer: 1943; aligned answer: 2006. | Annotated support complete → complete; canonical F1 1 → 0 |

Local evidence anchors, relative to `paper/versions/`:

- `2026-10-06_neurocomputing_conversion/private/CASE_TEXT_FIRST.md`: C12 and C10 question/source sections, including retained/removed/added source paragraphs.
- `2026-10-06_neurocomputing_conversion/private/CASE_TEXT_NOTES.md`: existing source-text interpretation for those same cases.
- `2026-10-06_neurocomputing_conversion/private/CASE_OUTPUTS.json`: saved outputs and endpoint values for C12 and C10.
- `2026-10-06_neurocomputing_final_polish/supplement/CASE_ANALYSIS.md`: public prior case analysis.

The original question in C10 asks when the creator stopped producing Oswald
cartoons for Universal; the diagram abbreviates this need without changing its
date role. The 2006 date is **not newly introduced** by aligned selection. Other
paragraph membership and input lengths change in both pairs. Consequently the
figure does not isolate one paragraph's causal effect, imply identical contexts,
identify attention behavior, or estimate how frequently these patterns occur.
The two examples remain inspected development cases, not independent confirmation.

Only these short paraphrases and existing saved outcomes are published here;
private raw source records and author material remain outside the public package.
