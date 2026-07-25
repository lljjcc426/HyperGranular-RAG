# License and Availability Record

Status: `LICENSE_SOURCES_VERIFIED_REPOSITORY_LICENSE_PENDING`
Verification date: 2026-07-25

This record distinguishes third-party licenses from the license of this
repository. A third-party dependency's license does not grant a license to the
project's own code.

## Benchmark data

| Resource | Official source | Officially stated terms | Repository handling |
|---|---|---|---|
| HotpotQA | [Official GitHub repository](https://github.com/hotpotqa/hotpot) and [dataset site](https://hotpotqa.github.io/) | Dataset: CC BY-SA 4.0; official repository code: Apache-2.0. | Original dataset is not redistributed in Git. Users obtain it from the official source. |
| MuSiQue | [Official StonyBrookNLP repository](https://github.com/StonyBrookNLP/musique) | Dataset: CC BY 4.0, as stated by the official repository. | Original dataset is not redistributed in Git. Users obtain it from the official source. |

The project commits derived query IDs, rankings, predictions, audits, aggregate
summaries, and verification records required for reproducibility. Before public
release, authors must confirm that any row-level derived artifact intended for
distribution complies with attribution and share-alike obligations.

## Models

| Exact family used | Official model source | License shown by official model card | Handling |
|---|---|---|---|
| `BAAI/bge-large-en-v1.5` | [Hugging Face model card](https://huggingface.co/BAAI/bge-large-en-v1.5) | MIT | Weights/cache are local and not committed. Exact revision and file hashes are recorded. |
| `Qwen/Qwen2.5-1.5B-Instruct` | [Hugging Face model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Apache-2.0 | Weights/cache are local and not committed. Exact revision is frozen. |
| `google/gemma-4-E2B-it-qat-mobile-transformers` | [Official Hugging Face model card](https://huggingface.co/google/gemma-4-E2B-it-qat-mobile-transformers) | The exact retrieved model card marks this snapshot Apache-2.0. | Official mobile-QAT weights/cache are local and not committed. Recheck the exact card before any redistribution because Gemma-family terms can differ by release. |

The Stage4G comparison is not a model-license or architecture benchmark. It
uses the exact deployable formats above and does not redistribute model files.

## Figure and analysis stack

| Package | Official license source | License |
|---|---|---|
| Python | [Python license](https://docs.python.org/3/license.html) | Python Software Foundation License |
| NumPy | [NumPy license](https://github.com/numpy/numpy/blob/main/LICENSE.txt) | BSD-3-Clause |
| SciPy | [SciPy license](https://github.com/scipy/scipy/blob/main/LICENSE.txt) | BSD-3-Clause |
| pandas | [pandas license](https://github.com/pandas-dev/pandas/blob/main/LICENSE) | BSD-3-Clause |
| Matplotlib | [Matplotlib license](https://matplotlib.org/stable/project/license.html) | PSF-based Matplotlib license |

Experimental runtime packages and revisions are separately frozen in
environment manifests. This table records the Stage5R figure/document stack,
not a license inventory of every transitive dependency.

## Project repository

Repository: `https://github.com/lljjcc426/HyperGranular-RAG`

As of this audit, the repository root has no `LICENSE`, `LICENSE.txt`, or
equivalent project license file. The accurate current statement is:

```text
NO_REPOSITORY_LICENSE_DECLARED
```

Therefore, public visibility of the repository must not be described as an
open-source license grant. A human author/rights holder must select and approve
the code and derived-artifact license before submission packaging or public
reuse language is finalized. Stage5R does not create a license automatically.

## Availability statement for the manuscript

Draft, valid before a project license is selected:

> The repository records code, configuration files, frozen derived evaluation
> artifacts, figure source data, and verification manifests. Original benchmark
> datasets, model weights, and large embedding/model caches are not
> redistributed and must be obtained from their official sources under their
> respective terms. The repository currently declares no license for reuse of
> project-authored code; availability and reuse rights will be finalized by the
> rights holders before submission.

## Large local artifacts

- benchmark source files remain in registered local data directories;
- model weights and embedding caches remain outside Git;
- no Stage5R task copies them into the paper package;
- exact identities needed for reproduction are recorded as model revisions,
  byte lengths, and SHA-256 values;
- a user must independently accept and comply with the upstream terms when
  downloading third-party resources.

## Remaining license blockers

1. Rights holders must choose a project code license.
2. Rights holders must choose a license for project-authored derived artifacts
   and figures.
3. The selected venue's manuscript publishing license must be accepted by all
   authors.
4. Dataset attribution text must be carried into the final venue-formatted
   manuscript.
5. The exact Gemma model card must be rechecked immediately before any public
   redistribution decision.
