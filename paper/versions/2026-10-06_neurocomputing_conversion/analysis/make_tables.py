"""Editable article tables from the same saved observations as the supplement."""
import csv
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def read(name):
    with (H/'supplement'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(name,caption,label,cols,header,rows):
    text='\\begin{table}[t]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(r+' \\\\' for r in rows)+'\n\\bottomrule\\end{tabular}\n\\end{table}\n'
    (H/'manuscript'/name).write_text(text,encoding='utf-8')
qa=read('derived/QA_SUMMARY.csv');ix={(r['seed'],r['model'],r['phase']):r for r in qa}
rows=[]
for m,p in [('Dense','static'),('MMR','static'),('H4','static'),('H4-replay','aligned'),('H1','aligned'),('H2','aligned'),('DeepSets','aligned'),('H4','aligned')]:
    r=ix['1729',m,p];label=m+(' static' if m=='H4' and p=='static' else ' aligned' if p=='aligned' and m!='H4-replay' else '')
    rows.append(f"{label} & {r['full_count']}/128 & {float(r['f1']):.4f} & {float(r['em']):.4f} & {float(r['blocks']):.2f} & {float(r['input_tokens']):.1f}")
table('qa_table.tex','Answers and selected contexts on the same 128 development questions (64 per dataset), seed 1729. F1 and EM are proportions. Dense and MMR share the 1,024-token ceiling but may exceed six paragraphs; learned models cannot. Replay matches optimizer steps, not total computation.','tab:qa','lrrrrr','Selector & Full & F1 & EM & Blocks & Input tokens',rows)
rows=[]
for seed in ('1729','2026'):
    for m in ('H1','H2','H4','DeepSets'):
        a=ix[seed,m,'static'];b=ix[seed,m,'aligned']
        rows.append(f"{seed} & {m} & {a['full_count']} $\\to$ {b['full_count']} & {float(a['f1']):.4f} & {float(b['f1']):.4f} & {float(b['f1'])-float(a['f1']):+.4f}")
table('paired_table.tex','Each aligned model against its own static checkpoint on the same QA panel. The seeds reuse the same 128 questions; they do not create independent samples.','tab:paired','llrrrr','Seed & Model & Full count & Static F1 & Aligned F1 & $\\Delta$F1',rows)
rows=[]
for r in read('derived/ENDPOINT_DECOMPOSITION.csv'):
    if r['dataset']=='equal64+64' and r['model']=='H4':
        rows.append(f"{r['seed']} & {r['transition'][0]} $\\to$ {r['transition'][1]} & {r['n']} & {float(r['sum_delta_f1']):+.4f} & {float(r['mean_delta_f1']):+.4f} & {float(r['contribution_to_panel_mean']):+.4f}")
table('decomposition.tex','Descriptive decomposition of H4 answer change. The last column is the group sum divided by all 128 questions, so its four entries sum to the panel difference. It is not a causal attribution.','tab:decomp','lcrrrr','Seed & Full transition & $n$ & $\\sum\\Delta$F1 & Group mean & Panel contribution',rows)
rows=[]
for r in read('reference_gaps.csv'):
    rows.append(f"{r['tag'].replace('hotpot','HotpotQA').replace('musique','MuSiQue')} & {r['queries']} & {float(r['dense_k6_complete']):.4f} & {float(r['h4_complete']):.4f} & {r['lost_full_support']} & {r['gained_full_support']}")
table('reference_table.tex','Annotation gap to the feasible Dense-K6 reference on all TUNE questions, static H4, seed 1729. Loss/gain counts are relative to that reference. These are retained aggregate diagnostics; per-query reference logits were not saved.','tab:reference','lrrrrr','Dataset & $N$ & Dense-K6 full & H4 full & Lost & Gained',rows)
print('Four editable numeric tables generated.')
