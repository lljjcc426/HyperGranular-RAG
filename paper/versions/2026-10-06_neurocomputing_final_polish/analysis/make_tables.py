"""Editable article tables from the same saved observations as the supplement."""
import csv, json, time
from pathlib import Path
H=Path(__file__).resolve().parents[1]
cpu=time.process_time()
def read(name):
    with (H/'supplement'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(name,caption,label,cols,header,rows):
    text='\\begin{table}[!htbp]\n\\centering\\small\n\\caption{'+caption+'}\\label{'+label+'}\n\\begin{tabular}{@{}'+cols+'@{}}\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(r+' \\\\' for r in rows)+'\n\\bottomrule\\end{tabular}\n\\end{table}\n'
    (H/'manuscript'/name).write_text(text,encoding='utf-8')
qa=read('derived/QA_SUMMARY.csv');ix={(r['seed'],r['model'],r['phase']):r for r in qa}
rows=[]
for m,p in [('Dense','static'),('MMR','static'),('H4','static'),('H4-replay','aligned'),('H1','aligned'),('H2','aligned'),('DeepSets','aligned'),('H4','aligned')]:
    r=ix['1729',m,p];label=m+(' static' if m=='H4' and p=='static' else ' aligned' if p=='aligned' and m!='H4-replay' else '')
    rows.append(f"{label} & {r['full_count']}/128 & {float(r['f1']):.4f} & {float(r['em']):.4f} & {float(r['blocks']):.2f} & {float(r['input_tokens']):.1f}")
table('qa_table.tex','Answers and contexts on 128 development questions (64 per dataset), seed 1729. Complete support is a question count; F1 and EM are proportions; paragraph and input-token counts are means. Dense/MMR share the 1,024-token ceiling but may exceed six paragraphs. Replay matches optimizer updates.','tab:qa','lrrrrr','Selector & \\shortstack{Complete\\\\support} & F1 & EM & \\shortstack{Mean\\\\paragraphs} & \\shortstack{Mean input\\\\tokens}',rows)
rows=[]
for seed in ('1729','2026'):
    for m in ('H1','H2','H4','DeepSets'):
        a=ix[seed,m,'static'];b=ix[seed,m,'aligned']
        rows.append(f"{seed} & {m} & {a['full_count']} $\\to$ {b['full_count']} & {float(a['f1']):.4f} & {float(b['f1']):.4f} & {float(b['f1'])-float(a['f1']):+.4f}")
rows[4]='\\addlinespace '+rows[4]
table('paired_table.tex','Continuation relative to each model\'s own static checkpoint. Complete-support counts are out of 128; F1 differences use the same full panel. Both seeds reuse the same questions.','tab:paired','llrrrr','Seed & Model & \\shortstack{Complete support\\\\static $\\to$ aligned} & \\shortstack{Static\\\\F1} & \\shortstack{Aligned\\\\F1} & $\\Delta$F1',rows)
rows=[]
for r in read('derived/ENDPOINT_DECOMPOSITION.csv'):
    if r['dataset']=='equal64+64' and r['model']=='H4':
        rows.append(f"{r['seed']} & {r['transition'][0]} $\\to$ {r['transition'][1]} & {r['n']} & {float(r['sum_delta_f1']):+.4f} & {float(r['mean_delta_f1']):+.4f} & {float(r['contribution_to_panel_mean']):+.4f}")
rows[4]='\\addlinespace '+rows[4]
table('decomposition.tex','H4 answer-change decomposition by annotated-support transition. Group mean divides the signed sum by group size $n$; panel contribution divides it by all 128 questions. The four contributions sum to the panel difference. Here 0 and 1 mean incomplete and complete annotated support.','tab:decomp','lcrrrr','Seed & \\shortstack{Support\\\\transition} & $n$ & $\\sum\\Delta$F1 & \\shortstack{Group mean\\\\$\\Delta$F1} & \\shortstack{Panel\\\\contribution}',rows)
rows=[]
for r in read('reference_gaps.csv'):
    rows.append(f"{r['tag'].replace('hotpot','HotpotQA').replace('musique','MuSiQue')} & {r['queries']} & {float(r['dense_k6_complete']):.4f} & {float(r['h4_complete']):.4f} & {r['lost_full_support']} & {r['gained_full_support']}")
table('reference_table.tex','Complete annotated support on all TUNE questions, static H4 versus its feasible Dense-K6 reference, seed 1729. Rates are proportions; lost/gained are question counts relative to Dense-K6. Per-question reference logits were not retained.','tab:reference','lrrrrr','Dataset & $N$ & \\shortstack{Dense-K6\\\\complete rate} & \\shortstack{H4\\\\complete rate} & Lost & Gained',rows)
table('data_roles_table.tex','Development roles and their nesting. MINE is inside FIT; DEV-SELECT and QA are disjoint subsets of TUNE. Initial static checkpoint selection used all TUNE, including QA.','tab:roles','p{2.5cm}rrp{5.2cm}','Role & HotpotQA & MuSiQue & Use',[
    'FIT & 748 & 2,418 & Supervised training',
    'TUNE & 196 & 542 & Initial checkpoint loss; selection analysis',
    'Historical DEV & 56 & 40 & Earlier exposed development',
    '\\addlinespace MINE (FIT) & 256 & 256 & Shared search-state pool',
    'DEV-SELECT (TUNE) & 64 & 64 & Continuation checkpoint selection',
    'QA (TUNE) & 64 & 64 & Saved answer comparison'])
cost=read('index_cost_refined64.csv');ci={(r['tag'],r['method']):r for r in cost}
rows=[]
for m,label in [('Flat','Flat'),('GB','Granular-ball'),('KM','K-means')]:
    a=ci['hotpot',m];b=ci['musique',m]
    rows.append(label+' & '+' & '.join(f'{float(x):.4f}' for x in [a['total_seconds'],a['median_seconds'],b['total_seconds'],b['median_seconds']]))
table('cost_table.tex','Measured selection time in seconds per question, 32 questions per dataset. Means and medians are retained aggregates of the refined-leaf diagnostic; per-question timing distributions are unavailable.','tab:cost','lrrrr','& \\multicolumn{2}{c}{HotpotQA} & \\multicolumn{2}{c}{MuSiQue} \\\\ \\cmidrule(lr){2-3}\\cmidrule(l){4-5}\nSelector & Mean & Median & Mean & Median',rows)
(H/'analysis/TABLE_BUILD.json').write_text(json.dumps({'tables':6,'cpu_seconds':time.process_time()-cpu,'source':'Unchanged v1 numerical supplement; table display only'},indent=2),encoding='utf-8')
print('Six editable tables generated from existing data.')
