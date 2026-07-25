# Author and Submission Metadata Checklist

Status: `PARTIALLY_CONFIRMED` / `SUBMISSION_METADATA_PENDING`

The canonical, human-maintained source is
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml).
Its confirmed values and field order must not be replaced from this checklist.
Every future human-confirmed change must also be appended to
[`../AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md`](../AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md).

No unconfirmed author, affiliation, funding, conflict, acknowledgement,
license, or venue fact may be inferred.

## Paper identity

- Final title: `[AUTHOR_CONFIRM_TITLE]`
- Short title: `[AUTHOR_SUPPLY_SHORT_TITLE]`
- Target venue: `TBD_AFTER_STAGE4I` (retained exactly from the human metadata
  record; still requires a new human selection)
- Submission type: ACL/ARR `long_paper`
- Keywords: retrieval-augmented generation; multi-hop question answering;
  structure-aware retrieval; evidence completion; reproducibility

## Author order

| Order | Confirmed Chinese name / role | Published English name | Affiliation ID | Email | ORCID | Corresponding author |
|---:|---|---|---|---|---|---|
| 1 | 李珈辰 / first author | `TBD_HUMAN_INPUT` | `affiliation_1` | `TBD_HUMAN_INPUT` | `TBD_HUMAN_INPUT` | No |
| 2 | 陈耀洋 / second author | `TBD_HUMAN_INPUT` | `affiliation_1` | `TBD_HUMAN_INPUT` | `TBD_HUMAN_INPUT` | No |
| `TBD_HUMAN_INPUT` | advisor | `TBD_HUMAN_INPUT` | `TBD_HUMAN_INPUT` | `TBD_HUMAN_INPUT` | `TBD_HUMAN_INPUT` | Yes |

The first and second positions above are human-confirmed. Overall author order
is not frozen because the advisor's position and any additional authors remain
undetermined. Do not add an author without a human-confirmed name, order,
affiliation, and contribution.

## Affiliations

| ID | Department / school | Institution | City | Country | Applies to |
|---|---|---|---|---|---|
| `affiliation_1` | `TBD_HUMAN_INPUT` | Chongqing University of Posts and Telecommunications | Chongqing | China | author_1; author_2 |

## Contributions

Use CRediT roles only after contributors confirm them.

- Conceptualization: `[REQUIRED]`
- Methodology: `[REQUIRED]`
- Software: `[REQUIRED]`
- Validation: `[REQUIRED]`
- Formal analysis: `[REQUIRED]`
- Investigation: `[REQUIRED]`
- Data curation: `[REQUIRED]`
- Visualization: `[REQUIRED]`
- Writing — original draft: `[REQUIRED]`
- Writing — review and editing: `[REQUIRED]`
- Supervision: `[IF_APPLICABLE]`
- Project administration: `[REQUIRED]`
- Funding acquisition: `[IF_APPLICABLE]`

## Funding

`[AUTHOR_SUPPLY_EXACT_FUNDER_NAMES_GRANT_NUMBERS_AND_RECIPIENTS_OR_STATE_NO_EXTERNAL_FUNDING]`

## Competing interests

`[EACH_AUTHOR_MUST_DECLARE_INTERESTS_OR_CONFIRM_NONE]`

## Acknowledgements

`[AUTHOR_SUPPLY_OR_EXPLICITLY_STATE_NONE]`

Do not place acknowledgements in an anonymized review manuscript.

## Data and code availability

Draft wording, subject to license selection:

> Code, configuration files, derived evaluation artifacts, figure source data,
> and verification manifests are maintained in the project repository. Original
> benchmark data and model weights are not redistributed; they must be obtained
> from their official sources under their respective terms. Large local caches
> are excluded from version control.

Repository URL: `https://github.com/lljjcc426/HyperGranular-RAG`

Public reuse wording cannot be finalized until the repository code license is
chosen.

## Ethics statement

Draft factual scope:

> The study uses existing benchmark datasets and publicly documented model
> artifacts. It does not recruit human participants or collect new personal
> data. `[AUTHOR_OR_INSTITUTION_MUST_CONFIRM_WHETHER_FORMAL_ETHICS_APPROVAL_WAS_NOT_REQUIRED]`.

## AI-assistance disclosure

The authors must confirm the final wording and ensure venue compliance. Draft:

> OpenAI Codex was used as an author-controlled tool for repository inspection,
> code/document editing, literature metadata organization, figure generation,
> and language revision. Scientific decisions and all submitted claims remain
> the responsibility of the human authors. Citations and numerical claims were
> independently checked against primary sources and frozen project artifacts.

Add tool version, access URL, and use dates if required by the selected venue.

## License statement

- Manuscript license: `[VENUE_DEPENDENT]`
- Repository code license: `[AUTHOR_CHOICE_REQUIRED_NO_LICENSE_CURRENTLY_DECLARED]`
- Derived artifact license: `[AUTHOR_CHOICE_REQUIRED]`
- Third-party dataset/model terms: retain original licenses; no redistribution.

## Final author approvals

- [ ] Every author approves authorship and order.
- [ ] Every affiliation and ORCID is correct.
- [ ] Funding and conflicts are complete.
- [ ] Contributions are approved.
- [ ] AI-assistance disclosure is approved.
- [ ] Data/code/license wording is approved.
- [ ] Corresponding author accepts responsibility.
- [ ] Target venue and submission type are selected.
