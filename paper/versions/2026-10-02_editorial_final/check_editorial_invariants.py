"""Compare editorial sources with revision2; no data or experiment execution."""
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "2026-10-02_revision2"


def environments(text, names):
    result = []
    for name in names:
        result.extend(re.findall(
            r"\\begin\{" + re.escape(name) + r"\}.*?\\end\{"
            + re.escape(name) + r"\}", text, flags=re.S))
    return result


def check():
    shared = {
        p.name: p.read_bytes() == (BASE / "shared" / p.name).read_bytes()
        for p in sorted((ROOT / "shared").iterdir()) if p.is_file()
    }
    versions = {}
    for version in ("conference", "journal"):
        old = (BASE / version / "main.tex").read_text(encoding="utf-8")
        new = (ROOT / version / "main.tex").read_text(encoding="utf-8")
        def citations(text):
            return sorted(set(
                key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", text)
                for key in group.split(",")))
        versions[version] = {
            "displayed_equations_unchanged": environments(old, ["equation", "align*"])
                == environments(new, ["equation", "align*"]),
            "inline_math_multiset_unchanged": Counter(re.findall(r"(?<!\\)\$[^$]*\$", old))
                == Counter(re.findall(r"(?<!\\)\$[^$]*\$", new)),
            "table_bodies_unchanged": environments(old, ["tabular", "longtable"])
                == environments(new, ["tabular", "longtable"]),
            "citation_keys_unchanged": citations(old) == citations(new),
            "anonymous_author_unchanged": r"\author{Anonymous authors}" in new,
            "all_local_figures_and_tables_referenced": all(
                "ref{" + label + "}" in new for label in
                re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", new)),
        }
    report = {
        "baseline_commit": "790cbb38de60b98d71074756b3e72b8f1a0f4ce4",
        "comparison": "2026-10-02_revision2 to 2026-10-02_editorial_final",
        "scope": "Manuscript sources and shared presentation assets only; no rescoring.",
        "shared_files_identical": shared,
        "manuscripts": versions,
    }
    report["passed"] = all(shared.values()) and all(
        all(checks.values()) for checks in versions.values())
    (ROOT / "EDITORIAL_INVARIANTS.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    check()
