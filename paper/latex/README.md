# LaTeX submission identity switch

The canonical human-maintained metadata record is
[`../AUTHOR_AND_SUBMISSION_METADATA.yaml`](../AUTHOR_AND_SUBMISSION_METADATA.yaml).
It must not be copied into the anonymous `main.tex`.

## Anonymous mode (default)

Load the switch after the document class/style and before
`\begin{document}`:

```tex
\input{paper/latex/submission_mode.tex}
```

With no other definition, this produces:

```tex
\author{Anonymous Authors}
```

The tracked review source must keep this default. Missing human metadata does
not block writing or compiling the anonymous manuscript body.

## Camera-ready mode

Camera-ready mode is an explicit human-controlled override:

```tex
\def\HGRUseCameraReady{1}
\input{paper/latex/submission_mode.tex}
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

## Fail-closed behavior

If camera-ready mode is enabled without a completed
`camera_ready_author_block.tex`, LaTeX raises an error. The switch never
converts `TBD_HUMAN_INPUT` or `TBD_HUMAN_CONFIRMATION` into inferred values.

The metadata YAML and its history are identity-exposing records and must be
excluded from any anonymous submission snapshot.
