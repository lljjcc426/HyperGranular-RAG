# Position, visible content, and budget review

This is an independent read-only reconstruction of the completed Stage4I sidecar's two placement arms. `placement.py` imports no production retrieval or prompt renderer. It loads only the existing local tokenizer, not model weights, and performs no generation. Bound blind units, rankings, and prompt audits match their frozen identities.

## Set identity and actual constraints

For K=20, prefix=10, and m<=4 distinct insertion IDs outside baseline Top-20, Protected is `(D[:10]+I+D[10:])[:20]` and Unprotected is `(I+D)[:20]`. Since 20−m>=10, both sets equal `I union D[:20-m]`. This is not a theorem for arbitrary K/prefix/budget. For the observed K<20 cases, the baseline covers the entire candidate universe and legal outside-set insertion is empty.

The independent procedure checked every actual query's effective K, distinctness, outside-Top20 constraint, insertion budget, and exact protected/unprotected ordered lists against the frozen rankings before comparing final membership.

| Dataset | Queries | Identical final sets | Identical visible ID/title/text multiset | Own serialized prompts verified | Order changes | K<20 |
|---|---:|---:|---:|---:|---:|---:|
| HotpotQA | 1,000 | 1,000 | 1,000 | 2,000 | 458 | 12 |
| MuSiQue | 1,500 | 1,500 | 1,500 | 3,000 | 1,070 | 0 |

Each arm's actual chat-template prompt was reconstructed from bound question, system message, ranking, titles and sentence texts. Its SHA and tokenizer count match its own stored audit. We did not require the two reordered complete prompts to have equal hashes. Their visible `(unit_id,title,text)` multisets were compared directly, with a derived digest recorded for review. Position numbering changes with order and is part of the placement policy. All 12 short HotpotQA lists have zero insertions.

No whole evidence unit is dropped and no rank-one partial truncation occurs in either arm. Thus all 2,500 pairs fix prompt-visible evidence content. Of these, 1,528 actually change order; the remaining 972 have identical prompts. The main outcome still averages the entire original query set, not a favorable post-hoc subset.

This supports **ordering/placement-policy comparison at fixed visible evidence** for this historical sidecar. It does not identify internal attention, establish Protected > BGE, or automatically validate another method's placement contrast.

## Entry budget is not token exhaustion

| Dataset, either sidecar arm | Min | Median | p95 | Max | Mean | Cap hits | Whole-unit drops | Partial truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HotpotQA | 184 | 923.5 | 1,156.0 | 1,907 | 929.945 | 0/1,000 | 0/1,000 | 0/1,000 |
| MuSiQue | 504 | 884.0 | 1,186.1 | 2,881 | 910.430 | 0/1,500 | 0/1,500 | 0/1,500 |

Counts are equal within each paired query, not only in mean. The 4,096 limit includes chat serialization and question; it is separate from the maximum twenty evidence entries. Supporting evidence displaced from Top-20 was displaced by list membership, not by observed exhaustion of context-token capacity.

`scoring/BUDGET_UTILIZATION_SUMMARY.csv` additionally covers all 74,750 historical main prediction/prompt records, including native development, by stage/dataset/method. It reports min/median/p95/max/mean and counts with denominators. All recorded cap-hit, dropped-unit, and partial-truncation counts are zero (rates 0%). Rankings were joined to each prompt's visible evidence IDs to establish whole-unit drops. This broader check reads historical audit fields; full text/chat-template reconstruction was performed for the 5,000 sidecar prompts, not all 74,750 prompts. No rerun or cache-hit count is added to the main denominator.

Machine-readable evidence: `scoring/PLACEMENT_QUERY_CHECKS.csv`, `PLACEMENT_SUMMARY.json`, `PLACEMENT_INPUT_IDENTITIES.json`, and the budget CSV. Raw Gold and the full blind candidate corpus are not added to this package.

Native timing records retain their actual scopes: cumulative checkpoint generation seconds, total transaction calls, and calls in the final resumed process differ. They are not automatically inconsistent, nor do they establish an uncached speed advantage.
