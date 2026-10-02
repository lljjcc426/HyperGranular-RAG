"""Narrow document invariants and an original-source diff, not experiment tests."""
from collections import Counter
import difflib
import json
from pathlib import Path
import re
import pymupdf

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASE = REPO / "paper/versions/2026-10-02_editorial_final"

def environments(text, names):
    return [item for name in names for item in re.findall(
        r"\\begin\{" + re.escape(name) + r"\}.*?\\end\{" + re.escape(name) + r"\}",
        text, flags=re.S)]

def cited(text):
    return {k.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", text)
            for k in group.split(",")}

def main():
    shared = {p.name: p.read_bytes() == (BASE / "shared" / p.name).read_bytes()
              for p in (ROOT / "shared").iterdir() if p.name != "references.bib"}
    bib = (ROOT / "shared/references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\{([^,]+),", bib)
    dois = re.findall(r"doi\s*=\s*\{([^}]+)\}", bib, flags=re.I)
    report = {"baseline": "7a91fa1a4029d5fde85a4277bca1856fc45b306e",
              "scope": "Document-only checks; no predictions, Gold or algorithm execution",
              "unchanged_shared_assets": shared,
              "unique_bib_keys": len(keys) == len(set(keys)),
              "unique_dois": len(dois) == len(set(x.lower() for x in dois)),
              "versions": {}}
    diffs = []
    for version in ("conference", "journal"):
        old = (BASE / version / "main.tex").read_text(encoding="utf-8")
        new = (ROOT / version / "main.tex").read_text(encoding="utf-8")
        tables_old = Counter(environments(old, ["tabular", "longtable"]))
        tables_new = Counter(environments(new, ["tabular", "longtable"]))
        log = (ROOT / version / "build/main.log").read_text(errors="replace")
        pdf = pymupdf.open(ROOT / version / f"HyperGranular-RAG_{version.capitalize()}.pdf")
        report["versions"][version] = {
            "equations_unchanged": environments(old, ["equation", "align*"]) == environments(new, ["equation", "align*"]),
            "inline_math_multiset_unchanged": Counter(re.findall(r"(?<!\\)\$[^$]*\$", old)) == Counter(re.findall(r"(?<!\\)\$[^$]*\$", new)),
            "all_old_table_bodies_retained": not (tables_old - tables_new),
            "old_citations_retained": cited(old) <= cited(new),
            "all_citations_resolve": cited(new) <= set(keys),
            "anonymous_author": r"\author{Anonymous authors}" in new,
            "figures_tables_referenced": all("ref{"+label+"}" in new for label in re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", new)),
            "no_overfull_or_undefined_or_rerun_warning": not re.search(r"Overfull|undefined|Rerun to get", log),
            "pages": len(pdf),
            "visual_review": "Recorded separately in FINAL_EDITORIAL_CHECK.md; not inferred from successful compilation"
        }
        diffs.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                     fromfile=f"editorial_final/{version}/main.tex", tofile=f"bounded_refresh/{version}/main.tex"))
    oldbib = (BASE / "shared/references.bib").read_text(encoding="utf-8")
    diffs.extend(difflib.unified_diff(oldbib.splitlines(True), bib.splitlines(True),
                 fromfile="editorial_final/shared/references.bib", tofile="bounded_refresh/shared/references.bib"))
    report["passed"] = all(shared.values()) and report["unique_bib_keys"] and report["unique_dois"] and all(
        all(v for v in checks.values() if isinstance(v, bool)) for checks in report["versions"].values())
    (ROOT / "DOCUMENT_CHECK.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    (REPO / "literature_refresh/2026-10-02_bounded/MANUSCRIPT_DIFF.patch").write_text("".join(diffs), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
