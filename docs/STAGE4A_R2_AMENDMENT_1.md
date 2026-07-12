# Stage4A-R2 Amendment 1: Deterministic Gold-Mapping QC Replacement

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Mode: source-integrity amendment
- Approval date: 2026-07-12
- Amendment Status: APPROVED_AND_FROZEN_BEFORE_EXTRACTION_RETRY
- Parent protocol: `docs/STAGE4A_R2_PROTOCOL.md`
- Parent protocol commit: `c65b18256359abb3ba74148037428068bbd5d24f`
- Retrieval metrics observed before amendment: No
- Embeddings generated before amendment: No
- Other conversations, thread tools, and memory files used: No

## Trigger

The first post-commit source extraction stopped at the protocol's 100% supporting-fact mapping gate. The extractor wrote no unified development data or source audit. The subsequent corpus command failed because the development file did not exist.

Read-only diagnosis of official rows `[800:5300)` found:

- Queries: 4,500
- Supporting facts: 11,003
- Mapped supporting facts: 10,984
- Out-of-range sentence indices: 19
- Missing supporting-fact titles: 0
- Affected queries: 19
- Queries with no mapped gold at all: 0

The official repository defines `sent_id` as a zero-based sentence index and describes the April 7 archive as a sentence-segmentation consistency fix. In these 19 records, `sent_id` is still at least the corrected context sentence count, so a sentence-level gold unit cannot be identified without inventing a repair or using a non-official source.

## Affected Base Rows

| Source row | Query ID | Type | Failure |
|---:|---|---|---|
| 1123 | `695689d20baf11ebab90acde48001122` | inference | supporting sentence index out of range |
| 1539 | `37a4158e0bb011ebab90acde48001122` | inference | supporting sentence index out of range |
| 2196 | `26af280a0bdc11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 2253 | `355ac9940bb011ebab90acde48001122` | inference | supporting sentence index out of range |
| 2388 | `dab62b000baf11ebab90acde48001122` | inference | supporting sentence index out of range |
| 2472 | `967024260bd911eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 2875 | `024076580bb011ebab90acde48001122` | inference | supporting sentence index out of range |
| 3163 | `dd2b76c60bda11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 3384 | `617f8d060bde11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 3883 | `f87c0e920bdd11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 4089 | `b7a7f4ba0bda11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 4328 | `618c39ce0bda11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 4514 | `3f210e940baf11ebab90acde48001122` | inference | supporting sentence index out of range |
| 4676 | `eb2a75220bdc11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 4935 | `ef8526a60bd911eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 4992 | `43bc7b940bde11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 5084 | `95bf64480bdd11eba7f7acde48001122` | compositional | supporting sentence index out of range |
| 5127 | `595209340bb011ebab90acde48001122` | inference | supporting sentence index out of range |
| 5182 | `593a648c0bb011ebab90acde48001122` | inference | supporting sentence index out of range |

## Approved Replacement Rule

1. Treat `[800:5300)` as the frozen base pool.
2. A record is eligible only when every official supporting-fact title exists and every official zero-based sentence index is within its official context sentence list.
3. Remove the 19 ineligible base records above. Eligibility uses source-label integrity only; no text similarity, embedding, retrieval score, strategy outcome, gain, or harm is computed.
4. Keep reservation rows `[5300:9800)` unchanged. Only their IDs and digest may be retained.
5. Scan the replacement pool `[9800:12576)` in ascending source-row order.
6. Append the earliest 19 fully mappable records. Skip any replacement-pool record that fails the same mapping rule and record the skipped row in the source audit.
7. Stop scanning immediately after 19 eligible replacements are found.
8. The final development set contains 4,500 unique records: 4,481 valid base records followed by 19 ascending-row replacements.
9. Write the base failures, replacement rows, replacement-pool failures, final development digest, reservation digest, and zero overlap to `docs/STAGE4A_R2_SOURCE_AUDIT.json`.

## Scientific Boundary

- The primary precision calculation remains valid at `n=4,500`.
- The estimand changes from the literal contiguous base range to the frozen policy's event rates among official records that have complete sentence-level supporting-fact labels under this deterministic QC rule.
- The 19/4,500 base exclusions (`0.4222%`) create a documented label-completeness selection boundary.
- No replacement is selected using method performance, so this amendment does not optimize q25 outcomes.
- No threshold, strategy, endpoint, alpha, bootstrap seed, or reservation rule changes.
- Controller fitting and Stage3B access remain prohibited.

## Retry Gate

The extractor may be retried only after this amendment, the amended protocol, the amended sample plan, and the amended extraction code are committed and pushed to GitHub. Any mismatch from 19 base failures, inability to find 19 fully mappable replacements, source hash drift, or reservation overlap is a new hard failure.
