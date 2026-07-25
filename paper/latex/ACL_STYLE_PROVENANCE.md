# ACL Style Provenance

The manuscript uses unmodified files from the official
[`acl-org/acl-style-files`](https://github.com/acl-org/acl-style-files)
repository.

- Upstream branch: `master`
- Upstream commit: `d5adc823ff0f80f98c80405ca0ab66c68e684409`
- Retrieved: 2026-07-25
- Copied files:
  - `vendor/acl.sty`
  - `acl_natbib.bst` (kept beside `main.tex`, as required by the official
    style's `\bibstyle{acl_natbib}` directive)
- Local modifications to either vendor file: none

SHA-256:

- `vendor/acl.sty`:
  `7DEF961AC900A2BBCC091DA0EE71796B277E6D14A707C9EED52B76EF5D25AE2A`
- `acl_natbib.bst`:
  `99DBB3C8E53F0DF971AE882F02C35D37AC2BF387558518B822DB16109A799F44`

The tracked review source loads `vendor/acl.sty` with the `review` option.
Defining `\HGRUseCameraReady` before the style is loaded selects `final`, but
the separate fail-closed identity switch still requires fully human-confirmed
camera-ready metadata.

The upstream files must not be edited locally. Update them only by recording a
new upstream commit, replacing the files byte-for-byte, and revising this
provenance record.
