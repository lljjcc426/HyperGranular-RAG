# Typesetting dependencies

Only these new manuscript directories use the locally supplied dependencies.
No historical class, paper, figure, or research environment was modified.

- `conference/llncs.cls` (v2.26, 2025-02-25) and `shared/splncs04.bst`: Springer LNCS distribution, obtained from the official CTAN `llncs` package. Original notices are retained.
- `journal/sn-jnl.cls` and `shared/sn-mathphys-num.bst`: Springer Nature author template, December 2024 distribution. Original notices are retained. The current JIIS guide links the Springer Nature template but also contains older formatting instructions; final venue-specific requirements remain a manual check.
- `journal/cuted.sty` (v2.10, 2025-12-15) was generated with docstrip from the official CTAN `sttools` package, https://mirrors.ctan.org/macros/latex/contrib/sttools.zip . The unmodified `cuted.dtx` source accompanies it, and its LPPL 1.3-or-later notice is preserved. The installed MiKTeX catalog did not provide this required class dependency; the local copy avoids upgrading the research environment or changing a frozen source.
- Conference font encoding uses the installed Latin Modern outline fonts to avoid the observed bitmap-font/microtype expansion error. Both new sources use `xurl`; the journal supplies a URL wrapper for bibliography URLs containing underscores. These are typesetting fixes, not changes to results.

The notices above describe third-party template dependencies. They do not choose an article, data, or project license, which remains for the human authors to confirm.
