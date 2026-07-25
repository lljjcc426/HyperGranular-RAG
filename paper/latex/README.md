# LaTeX submission identity switch

Current anonymous paper draft:

- [`main.tex`](main.tex)
- [`main.pdf`](main.pdf)
- [`DRAFT_BUILD_STATUS.md`](DRAFT_BUILD_STATUS.md)
- [`ACL_STYLE_PROVENANCE.md`](ACL_STYLE_PROVENANCE.md)

The tracked PDF is the visually inspected 12-page anonymous first draft built
from the tracked source. It contains eight pages of main text, two pages of
references, and two pages of appendix content. The build-status record binds
its exact bytes and SHA-256.

## Build

From `paper/latex/`, use Tectonic 0.16.9 or an equivalent compatible engine:

```powershell
$env:SOURCE_DATE_EPOCH = '1784950406'
tectonic -X compile --outdir ..\..\temp\stage5r_latex_build main.tex
```

The source uses the official ACL style snapshot recorded in
[`ACL_STYLE_PROVENANCE.md`](ACL_STYLE_PROVENANCE.md) and the verified
bibliography at `../references/verified_references.bib`.

The canonical human-maintained metadata record is
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml).
It must not be copied into the anonymous `main.tex`.

## Anonymous mode (default)

`main.tex` already loads the switch after the document class/style and before
`\begin{document}`:

```tex
\input{submission_mode.tex}
```

With no other definition, this produces:

```tex
\author{Anonymous Authors}
```

The tracked review source must keep this default. Missing human metadata does
not block writing or compiling the anonymous manuscript body.

The tracked draft also selects the official ACL style's `review` option in this
mode, so author identity is absent and review line/page numbers are enabled.

## Camera-ready mode

Camera-ready mode is an explicit human-controlled override:

```tex
\def\HGRUseCameraReady{1} % define before loading main.tex
```

Before enabling it:

1. every author, order, affiliation, corresponding-author field, email, ORCID,
   contribution, funding statement, conflict statement, and acknowledgement
   must be human-confirmed;
2. append the exact confirmed changes to
   [`../AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md`](../AUTHOR_AND_SUBMISSION_METADATA_HISTORY.md);
3. copy `camera_ready_author_block.tex.example` to
   `camera_ready_author_block.tex`;
4. replace all placeholders with the confirmed venue-specific `\author{...}`
   block and remove the deliberate `\PackageError`.

`camera_ready_author_block.tex` is ignored by Git while the repository is being
used for anonymous review preparation. The example contains no real author
identity.

The same explicit definition selects the official ACL style's `final` option.

## Fail-closed behavior

If camera-ready mode is enabled without a completed
`camera_ready_author_block.tex`, LaTeX raises an error. The switch never
converts `TBD_HUMAN_INPUT` or `TBD_HUMAN_CONFIRMATION` into inferred values.

The metadata YAML and its history are identity-exposing records and must be
excluded from any anonymous submission snapshot.
