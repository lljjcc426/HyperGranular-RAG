# Anonymous numerical supplement (Online Resource 1)

This supplement accompanies the evidence-set selection study. It reconstructs the main QA summaries from existing numeric per-question records. It does not execute a model, rescore prediction text, or introduce a new experiment. All 128 questions (64 per dataset) remain in each method's denominator.

Run with Python 3.10 or newer, using only the standard library:

```text
python reconstruct.py --out reconstructed
```

The command produces:

- `same_panel_qa.csv`: annotated support completeness, counts, F1, EM, input length, and F1 difference from MMR.
- `dataset_qa.csv`: separate HotpotQA and MuSiQue means.
- `own_static.csv`: all four aligned architectures against their corresponding static checkpoint in both seeds.
- `paired_counts.csv`: the joint support-change/F1-change counts for static versus aligned H4, with no hypothesis test.

`qa_records.csv` contains 2,432 method-question records, not 2,432 independent samples. Sequential labels q001–q128 preserve pairing only; they are not benchmark IDs or hashes of question text. The public table retains numeric scores and lengths but no questions, answers, source IDs, selected text, prompts, credentials, or machine paths. The original canonical scoring results are inputs to this reconstruction, not independently revalidated by it.

The accompanying aggregate files retain the original static-selection, checkpoint-selection, and timing boundaries. They are supplied for inspection; they cannot be regenerated from QA records alone. `DATA_AND_REPRODUCTION.md` describes assets and preparation rules needed beyond this package. The full training/retrieval/generation pipeline is not bundled, and a one-command model reproduction is not claimed.

This anonymous package contains no author or project-repository links. Source data and weights must be obtained from their respective providers under their terms; they are not redistributed here. No dataset or model license is inferred from their public availability.
