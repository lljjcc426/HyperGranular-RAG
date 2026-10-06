"""Package the public revision and stage the separately kept private build."""
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
    'study_design.pdf', 'study_design.tex',
    'motivating_examples.pdf', 'motivating_examples.tex',
]


def main():
    shutil.copyfile(H/'manuscript/main.pdf', H/'Manuscript_Neurocomputing_VisualMicroPolish.pdf')
    archive = H/'Neurocomputing_VisualMicroPolish_Source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in SOURCES:
            z.write(H/'manuscript'/name, name)
    clean = H/'build/clean_source'
    clean.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        z.extractall(clean)
    authored = H/'submission_local/authored'
    authored.mkdir(exist_ok=True)
    for name in SOURCES:
        shutil.copyfile(H/'manuscript'/name, authored/name)
    base = (H/'manuscript/main.tex').read_text(encoding='utf-8')
    (authored/'main.tex').write_text('\\def\\WithAuthors{1}\n'+base, encoding='utf-8')
    for name in ['author_frontmatter.tex', 'author_credit.tex']:
        shutil.copyfile(H/'submission_local'/name, authored/name)
    (H/'analysis/ARCHIVE_CONTENTS.json').write_text(
        json.dumps({'public_source': SOURCES, 'private_included': False}, indent=2), encoding='utf-8')
    print('Public source packaged and independently extracted; private build staged.')


if __name__ == '__main__':
    main()
