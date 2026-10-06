"""Create narrowly allowlisted public bundles and a same-source private article."""
import json
import shutil
import zipfile
from pathlib import Path

H = Path(__file__).resolve().parents[1]
SOURCES = [
    'main.tex', 'references.bib', 'additions.bib', 'nc_references.bib',
    'main.bbl', 'elsarticle.cls', 'elsarticle-num.bst',
    'data_roles_table.tex', 'qa_table.tex', 'paired_table.tex',
    'decomposition.tex', 'reference_table.tex', 'cost_table.tex',
    'joint_transitions.pdf', 'selected_scores.pdf', 'index_cost.pdf',
]


def main():
    shutil.copyfile(H/'manuscript/main.pdf', H/'Manuscript_Neurocomputing_FinalReview.pdf')
    archives = {}
    source_zip = 'Neurocomputing_Final_Source.zip'
    with zipfile.ZipFile(H/source_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in SOURCES:
            z.write(H/'manuscript'/name, name)
        archives[source_zip] = z.namelist()
    supplement_zip = 'Reproducibility_Supplement.zip'
    with zipfile.ZipFile(H/supplement_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((H/'supplement').rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p, p.relative_to(H/'supplement').as_posix())
        archives[supplement_zip] = z.namelist()
    # Fresh directories make these actual clean extraction checks, without deleting files.
    for archive, name in [(source_zip, 'clean_source_final'), (supplement_zip, 'clean_supplement_final')]:
        target = H/'build'/name
        target.mkdir(exist_ok=False)
        with zipfile.ZipFile(H/archive) as z:
            z.extractall(target)
    authored = H/'submission_local/authored_final'
    authored.mkdir(exist_ok=False)
    for name in SOURCES:
        shutil.copyfile(H/'manuscript'/name, authored/name)
    base = (H/'manuscript/main.tex').read_text(encoding='utf-8')
    (authored/'main.tex').write_text('\\def\\WithAuthors{1}\n'+base, encoding='utf-8')
    for name in ['author_frontmatter.tex', 'author_credit.tex']:
        shutil.copyfile(H/'submission_local'/name, authored/name)
    (H/'analysis/ARCHIVE_CONTENTS.json').write_text(json.dumps(archives, indent=2), encoding='utf-8')
    print(json.dumps({k: len(v) for k, v in archives.items()}))


if __name__ == '__main__':
    main()
