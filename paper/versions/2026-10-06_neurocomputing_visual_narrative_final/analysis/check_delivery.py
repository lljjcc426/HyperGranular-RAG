"""Bounded editorial checks and physical-width figure previews, not evaluation."""
import json
import re
import shutil
import zipfile
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw, ImageOps

H = Path(__file__).resolve().parents[1]
OLD = H.parent/'2026-10-06_neurocomputing_visual_closeout'
POLISH = H.parent/'2026-10-06_neurocomputing_final_polish'
FIGURES = ['motivating_examples', 'study_design', 'selected_scores',
           'joint_transitions', 'index_cost']
TABLES = ['data_roles_table.tex', 'qa_table.tex', 'paired_table.tex',
          'decomposition.tex', 'reference_table.tex', 'cost_table.tex']


def same(a, b):
    return a.read_bytes() == b.read_bytes()


def labels(path, kind):
    return [{'label': x[0], 'number': int(x[1]), 'page': int(x[2])}
            for x in re.findall(r'\\newlabel\{(' + kind +
                                r':[^}]+)\}\{\{(\d+)\}\{(\d+)\}',
                                path.read_text(encoding='utf-8'))]


def main():
    neutral = fitz.open(H/'manuscript/main.pdf')
    clean = fitz.open(H/'build/clean_source/main.pdf')
    authored = fitz.open(H/'submission_local/authored/main.pdf')
    shutil.copyfile(H/'submission_local/authored/main.pdf',
                   H/'submission_local/Manuscript_Neurocomputing_WithAuthors_VisualNarrativeFinal.pdf')
    report = {
        'neutral_pages': len(neutral), 'authored_pages': len(authored),
        'independent_source_build_text_equal':
            [p.get_text() for p in neutral] == [p.get_text() for p in clean],
        'unchanged_tables': {n: same(H/'manuscript'/n, OLD/'manuscript'/n) for n in TABLES},
        'unchanged_references': {n: same(H/'manuscript'/n, OLD/'manuscript'/n)
                                 for n in ['references.bib', 'additions.bib', 'nc_references.bib']},
        'unchanged_highlights': {n: same(H/n, OLD/n) for n in ['Highlights.txt', 'Highlights.docx']},
        'unchanged_numerical_supplement': same(H/'Reproducibility_Supplement.zip', OLD/'Reproducibility_Supplement.zip'),
        'unchanged_private_materials': {p.name: same(p, OLD/'submission_local'/p.name)
                                        for p in (H/'submission_local').iterdir()
                                        if p.suffix in ('.docx', '.tex')},
        'saved_plot_values_unchanged': json.loads((H/'analysis/PLOT_DATA.json').read_text()) ==
                                       json.loads((POLISH/'analysis/PLOT_DATA.json').read_text()),
        'figures': labels(H/'manuscript/main.aux', 'fig'),
        'tables': labels(H/'manuscript/main.aux', 'tab'),
        'authored_figures': labels(H/'submission_local/authored/main.aux', 'fig'),
        'authored_tables': labels(H/'submission_local/authored/main.aux', 'tab'),
        'new_training_inference_rescoring_tests_paid_calls': 0,
    }
    # Infer inclusion scale from Arial spans in the final page. Form BBox is
    # intrinsic and would omit the page's placement transform.
    out = H/'build/figure_previews'
    out.mkdir(exist_ok=True)
    previews = []
    for name, entry in zip(FIGURES, report['figures']):
        page = neutral[entry['page']-1]
        doc = fitz.open(H/'figures'/f'{name}.pdf')
        fonts = doc[0].get_fonts(full=True)
        embedded = all(len(doc.extract_font(x[0])[3]) > 0 for x in fonts)
        spans = [s for b in doc[0].get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        page_sizes = [s['size'] for b in page.get_text('dict')['blocks'] if 'lines' in b
                      for line in b['lines'] for s in line['spans']
                      if s['text'].strip() and 'Arial' in s['font']]
        scale = min(page_sizes)/min(s['size'] for s in spans)
        width = doc[0].rect.width*scale
        previews.append(dict(name=name, width_pdf_points=width,
                             width_mm=width/72*25.4,
                             minimum_inserted_font_points=min(s['size'] for s in spans)*scale,
                             font_names=sorted(set(x[3] for x in fonts)), embedded=embedded))
        images = []
        for factor, label in [(1, 'actual_144dpi'), (.75, 'scale75_108dpi')]:
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(scale*2*factor, scale*2*factor))
            im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            im.save(out/f'{name}_{label}.png')
            gray = ImageOps.grayscale(im).convert('RGB')
            gray.save(out/f'{name}_{label}_gray.png')
            images.extend([(label, im), (label+' gray', gray)])
        cell_width = max(im.width for _, im in images)+20
        canvas = Image.new('RGB', (cell_width*2, max(im.height for _, im in images)*2+100), 'white')
        for i, (label, im) in enumerate(images):
            x=(i%2)*cell_width+10; y=(i//2)*(images[0][1].height+50)+30
            canvas.paste(im, (x, y)); ImageDraw.Draw(canvas).text((x,y-20), name+' '+label, fill='black')
        canvas.save(out/f'{name}_QC.png')
    report['figure_previews'] = previews
    report['builds'] = {name: json.loads((H/'build'/f'{name}_build.json').read_text())
                        for name in ['main', 'authored', 'clean_source']}
    report['latex_issues'] = {}
    for name, path in [('neutral', H/'manuscript/main.log'),
                       ('authored', H/'submission_local/authored/main.log'),
                       ('clean', H/'build/clean_source/main.log')]:
        text = path.read_text(encoding='utf-8', errors='replace')
        report['latex_issues'][name] = [l for l in text.splitlines()
                                       if re.search('Overfull|Underfull|Warning|undefined', l)]
    report['docx_figure_number_mentions'] = {}
    for p in [H/'Highlights.docx', H/'submission_local/Cover_Letter_DRAFT.docx']:
        with zipfile.ZipFile(p) as z:
            xml = z.read('word/document.xml').decode('utf-8')
        text = re.sub('<[^>]+>', '', xml)
        report['docx_figure_number_mentions'][p.name] = re.findall(r'(?i)(?:figure|fig\.)\s*\d+', text)
    with zipfile.ZipFile(H/'Neurocomputing_VisualNarrativeFinal_Source.zip') as z:
        report['public_source_members'] = z.namelist()
    (H/'analysis/DELIVERY_CHECK.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
