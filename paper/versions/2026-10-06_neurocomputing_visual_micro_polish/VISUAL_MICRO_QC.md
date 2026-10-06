# NC visual micro-polish — completed

Task: `NC-visual-micro-polish-v3.0`  
Specification: `HGRAG-NEUCOM-FIG12-MICRO-POLISH-20261006`  
Baseline: `b1886d239eb2c7a0c53923cc8034bd6b79f14796`  
Date: 2026-10-06

## Changes

- Figure 1: retained the inspected C12/C10 cases, answers, support states and saved F1. Replaced conversational labels with question targets; aligned retained-source cards, Static/Aligned badges, answer rows and support/F1 rows. Used a light divider and a normal-weight endpoint statement. The arrows describe observed transitions, not causes.
- Figure 2: added recognizable query, document-stack and selected-evidence-set shapes; nested Flat/GB/KM inside the H4 search backend and attached RQ3 directly below it. Selected support and answers have separate dashed evaluation paths into RQ2. Support/answer labels have no return path into deployed inputs. Training detail moved to the caption.
- `manuscript/main.tex`: only the Figure 2 caption differs from the baseline. Introduction, RQ definitions, equations, result descriptions, conclusions and other captions are unchanged. Figure numbering remains 1–5; table numbering remains 1–6.
- Build/package/check helpers were adapted for this new delivery directory. No historical file was deleted or overwritten. Private author inputs and unrelated workspace changes were preserved.

The Fig.2 PDF contains 70 whitespace-delimited text tokens versus 85 previously (about 18% fewer). This all-label count is below the attachment's approximate 25–35% prose-reduction target; it includes the newly required evidence-set/backend labels. Qualifiers were moved to the caption without reducing label font size.

## Frozen content check

Direct comparisons confirm identical Figures 3–5 PDF/PNG assets, their plotting script, all six table source files, three bibliography files, numerical supplement ZIP, Highlights, saved plot values, private author TEX and declaration/cover-letter DOCX files. The main TEX comparison removes only the Figure 2 caption and is otherwise identical. No scientific value, formula, data role, comparison boundary or conclusion changed. See `analysis/DELIVERY_CHECK.json`.

## Actual build and visual inspection

- Neutral manuscript: 26 pages, including declarations and references; all pages rendered and visually inspected. The final small Fig.1 line-wrap adjustment was rechecked on page 3.
- Private authored manuscript: 26 pages, including author front matter, declarations and references; all 26 final pages rendered and visually inspected.
- Both versions place Figures 1–5 on pages 3, 6, 14, 17 and 19; Tables 1–6 on pages 9, 13, 15, 16, 17 and 20. Captions and in-text numbering agree.
- Figures 1–2 inspected at the actual inserted width (137.08 mm), 75% scale, and in grayscale. Figure typography is embedded Arial; the smallest inserted text is approximately 9.26 pt. Solid/dashed connections and explicit labels remain distinguishable without color. No overlapping labels, clipped text, unreadable arrows or rasterized vector content observed.
- The paired cases and design overview remain compact contextual figures; Figure 4 retains its separate, larger empirical-result panel. No body font, margins or bibliography spacing was compressed.
- Neutral, authored and independently extracted source builds completed successfully. The public ZIP contains 20 self-contained manuscript/figure source assets; the independently rebuilt PDF has identical page text to the neutral build. It contains no private author files.
- No overfull boxes, undefined references or oversized floats reported. Two existing bibliography underfull-box notices remain. The authored build also retains four hyperref PDF-string notices from author macros; the visible author page was inspected. These are not reported as zero warnings.

Build commands and exit statuses are recorded in `analysis/DELIVERY_CHECK.json` and `analysis/DIAGRAM_BUILD.json`. Local logs and rendered page/scale/grayscale previews are retained under ignored `build/`. The public source ZIP builds with pdfLaTeX/BibTeX; editable figure TEX additionally requires XeLaTeX and Arial. Font files are not distributed.

## Boundary and handoff

New experiments, inference, training, retrieval, embeddings, rescoring, statistical tests and paid calls: **0**. No account login, email or submission occurred. The academic-research-suite and PDF workflows were used for visual hierarchy, source preservation and rendered-page inspection; no new scientific workflow was opened.

Only this version directory's public files are allowed for Git synchronization. `submission_local/` remains ignored. Author approval and live submission-field checks remain human tasks; this build is not a claim of final journal acceptance or verified live submission requirements. Work stops after this delivery.
