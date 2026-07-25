# Submission Blockers

Status: `SUBMISSION_METADATA_PENDING`

The scientific manuscript and current-evidence audit can be completed without
inventing author facts. An actual submission cannot.

Canonical partial metadata:
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml).
The first author is 李珈辰, the second author is 陈耀洋, both share the
confirmed university affiliation, and the advisor role is corresponding
author. All fields still marked `TBD_HUMAN_INPUT` or
`TBD_HUMAN_CONFIRMATION` remain blocking facts and must not be inferred.

## Blocking author decisions

- [ ] Confirm final title.
- [ ] Select one target venue and article type.
- [ ] Supply both confirmed authors' English publication names.
- [ ] Confirm the advisor's identity, order, English publication name, and
      affiliation; confirm whether any additional authors exist.
- [ ] Supply the exact school/department names, all emails, and all ORCIDs (or
      explicitly record `NONE`).
- [ ] Supply the corresponding advisor's name, order, and email.
- [ ] Approve CRediT contributions.
- [ ] Supply funding/grant facts or confirm no external funding.
- [ ] Supply competing-interest declarations.
- [ ] Supply acknowledgements or confirm none.
- [ ] Approve the AI-assistance disclosure.

## Blocking rights and release decisions

- [ ] Select a repository code license; none is currently declared.
- [ ] Select a license for project-authored figures and derived artifacts.
- [ ] Confirm dataset attribution/share-alike handling for intended public
      artifacts.
- [ ] Decide whether to publish an anonymized repository snapshot.
- [ ] Confirm whether a Cambridge APC is covered or a waiver would be sought if
      that venue is selected.

## Venue-format work after selection

- [ ] Apply the venue's current LaTeX template.
- [ ] Fit essential claims and five figures within the current page limit.
- [ ] Create a fully anonymized manuscript and supplement where required.
- [ ] Complete venue-specific ethics/responsible-NLP/broader-impact forms.
- [ ] Add figure alt text and accessibility material if required.
- [ ] Recheck current deadlines, dual-submission rules, and artifact policy.
- [ ] Verify that all authors satisfy reviewer-registration obligations where
      applicable.

## Non-blockers for scientific completeness

- No new algorithm experiment is required by the current evidence audit.
- Full-wiki remains unevaluated and is not required to finish the current
  bounded manuscript.
- Inconclusive strong-retriever extensions are complete results, not missing
  values.
- The undefined flat granular-ball contrast is disclosed as a design boundary,
  not silently imputed.

## Explicit status

```text
STAGE5R_SCIENTIFIC_MANUSCRIPT_COMPLETE
SUBMISSION_METADATA_PENDING
SUBMISSION_READY = FALSE
```
