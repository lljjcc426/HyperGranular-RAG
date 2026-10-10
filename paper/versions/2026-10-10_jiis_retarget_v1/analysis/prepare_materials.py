"""Prepare supplementary methods and author-review documents from existing records."""
from pathlib import Path
import json,re,subprocess,shutil
H=Path(__file__).resolve().parents[1]
P=H/'submission_local'; S=H/'build/supplement'
m=json.loads((P/'confirmed_metadata.json').read_text())
title='From Set Prediction to Evidence Selection: An Empirical Study of Surrogate Objectives in Multi-hop RAG'
author_line=', '.join(m['authors'])
contact=m['authors'][0]+' (sole corresponding author), '+m['emails'][0]
header=f'# Online Resource 1: Methods and numerical reproduction\n\n**Article:** {title}\n\n**Journal:** Journal of Intelligent Information Systems\n\n**Authors:** {author_line}\n\n**Affiliation:** {m["affiliation"]}, China\n\n**Correspondence:** {contact}\n\n'
preface='''## Purpose and reading map

This resource documents the existing empirical study; it contains no additional model run, answer scoring or inferential test. It accompanies the complete main article, not an appendix excluded from the article page count. The five main figures and six main tables remain in the main article.

Online Resource 2 contains the saved numerical records and a Python standard-library reconstruction script. Its README maps files to endpoints. Table 1 uses data roles; Table 2 uses retained aggregate reference gaps; Tables 3–5 use saved outcomes and paired transitions; Table 6 uses the refined timing aggregate. Figures 3–5 use the corresponding score bins, transitions and measured times. Case notes support the source-text examples in Figure 1; Figure 2 is a study overview, not an additional result.

The initial static selection used TUNE including QA. Later DEV-SELECT excludes QA, but does not make the 128-question panel an independent test. Both seeds use the same questions. This resource cannot establish independent generalization or repair missing historical records.

## Reproduction command and limits

Extract Online Resource 2 and run `python reconstruct.py` in its root. No model package, raw answer file or network connection is required. The derived tables reconstruct existing saved scores; the script does not calculate a new answer score or regenerate a prediction. The reference-gap and refined-cost tables remain retained aggregates, not recovered per-question measurements. The archive includes the full existing de-identified 16-case notes, with their outcome-stratified and assistant-assisted interpretation limits.

'''
data=(S/'DATA_AND_REPRODUCTION.md').read_text(encoding='utf-8')
data=data.replace('FIT/TUNE/MINE/DEV_SELECT/QA roles','Development data roles')
notes=(S/'SUPPLEMENTARY_METHOD_NOTES.md').read_text(encoding='utf-8')
notes=notes.split('## Editorial and data role')[0]
notes=notes.replace('These notes relocate existing details from the first Neurocomputing draft. They introduce no new observations, inference, scores, or tests. All numeric files retain their prior contents.','These retained method and measured-cost details introduce no new observations, scores, or tests. All numerical inputs retain their prior contents.')
body=preface+data+'\n\n'+notes+'\n## Statements\n\nNo specific grant funding or relevant competing interests were declared by the authors. This computational study uses existing benchmarks and recruits no participants. The main article discloses ChatGPT/Codex assistance in research planning, implementation, analysis and manuscript preparation. Original source licenses and final author approval govern redistribution.\n'
(P/'Online_Resource_1.md').write_text(header+body,encoding='utf-8')
(H/'build/Online_Resource_1_Neutral.md').write_text('# Online Resource 1: Methods and numerical reproduction\n\n**Article:** '+title+'\n\n**Journal:** Journal of Intelligent Information Systems\n\nPublic neutral reading copy; submission metadata is supplied separately.\n\n'+body,encoding='utf-8')
# Public input-derived artifacts stay de-identified; only submission metadata differs.
si2head=header.replace('Online Resource 1: Methods and numerical reproduction','Online Resource 2: Numerical data and reconstruction')
(P/'Online_Resource_2_Metadata.md').write_text(si2head+'\nThis ZIP accompanies Online Resource 1. The numerical inputs and script derive existing scores only. It may be published as supplied: authors must approve this metadata and the release before submission.\n',encoding='utf-8')
letter=f'''# Cover letter — DRAFT FOR AUTHOR APPROVAL

10 October 2026

Dear Editors of the Journal of Intelligent Information Systems,

We propose the enclosed manuscript, “{title}”, for consideration as an original empirical research article.

The study concerns an interface in intelligent information access: a neural objective learned from support annotations selects a context, but the system's downstream endpoint is a reader's answer. We compare first-, second-, and fourth-order scorers and a DeepSets control under shared candidates and a common reader. An explicitly eligible dense reference exposes selection errors despite high constructed-set discrimination. Same-question records show why an aggregate support increase is insufficient to characterize the answer change: the largest negative fourth-order F1 contribution occurs in the group that retains complete annotated support. MMR and lower-order controls remain visible, and exact indexes preserve choices without reducing measured selector time at the studied scale.

The contribution is a bounded empirical account of surrogate objectives and induced decisions, not a state-of-the-art retrieval framework or a new mathematical guarantee. The development status is explicit: initial checkpoint selection included the answer panel, source documents overlap roles, both seeds reuse the same questions, and only one reader is studied. The findings are descriptive, not independent confirmation or causal evidence. We believe that the feasible-reference comparison, paired endpoint analysis and separate fidelity/cost accounting address the journal's interest in intelligent information retrieval and empirical system evaluation.

The submission materials include the complete Springer-format manuscript, editable flat source package, methods supplement and a numerical reconstruction archive. The archive rebuilds summaries from saved scores; it does not claim to regenerate all model outputs. ChatGPT/Codex research and writing assistance is disclosed. No specific grant funding or relevant competing interests have been declared.

This letter remains a draft until all four authors approve the final files and the corresponding author confirms that the manuscript is not under consideration elsewhere. No statement of completed submission or final author approval is made here.

Sincerely,\n\n{contact}\n\n{m['affiliation']}, China
'''
(P/'Cover_Letter_JIIS_DRAFT.md').write_text(letter,encoding='utf-8')
credit=(P/'source/main.tex').read_text(encoding='utf-8').split(r'\subsection*{Author contributions}',1)[1].split(r'\section*{Supplementary information}',1)[0]
credit=re.sub(r'\\textbf\{([^}]+)\}',r'**\1**',credit).replace(r'\noindent','').replace(r'\&','&')
decl=f'''# JIIS author information and declarations

**Article:** {title}\n\n**Authors:** {author_line}\n\n**Affiliation:** {m['affiliation']}, China\n\n**Sole corresponding author:** {contact}

## Identifiers

'''+ '\n'.join(f'- {n}: {e}; ORCID https://orcid.org/{o}' for n,e,o in zip(m['authors'],m['emails'],m['orcids']))+'''

## Author contributions (confirmed roles)

'''+credit+'''
## Funding

No specific grant from public, commercial or not-for-profit funding agencies.

## Competing interests

The authors declare no relevant competing financial interests or personal relationships.

## Data and code availability

Online Resource 2 contains de-identified saved scores and the reconstruction script. It does not include raw benchmark texts/answers, identifiable cohort manifests, source mappings or trained weights. Full experimental regeneration requires those additional authorized inputs and is not claimed. The main article and Online Resource 1 describe these limits and the original sources.

## AI assistance

ChatGPT and Codex assisted research planning, implementation/debugging, analysis scripts, case interpretation, literature organization, writing and editorial checks. Historical backend versions were not retained. The human authors retain responsibility for the scientific content. This declaration is not a claim that the tools were used only for language polishing.

## Ethics and consent

No newly recruited participants or new personal-data collection; existing benchmark materials only. Ethics approval and participant consent are not applicable to this computational study design.

## Final author approval and system checks — pending human action

- All four authors must approve this JIIS manuscript and supplementary release.
- Confirm the Elsevier “Do not transfer submission” state and absence of concurrent review. The prior Neurocomputing outcome was editorial desk screening, not external peer review.
- Check the live JIIS upload categories, sole correspondence, ORCIDs, contributions and interests fields. Submission-system declarations must match these files.
- Subscription is the intended route; do not select paid open access without new authorization.
- Supplementary files may be published as supplied. Approve their contents and source-license boundaries.
- No account access, transfer, submission, email or payment has been performed by this task.
'''
(P/'Author_Declarations_JIIS.md').write_text(decl,encoding='utf-8')
for name in ['Cover_Letter_JIIS_DRAFT','Author_Declarations_JIIS']:
    subprocess.run(['pandoc',str(P/(name+'.md')),'-o',str(P/(name+'.docx'))],check=True)
for src,dst in [(P/'Online_Resource_1.md',P/'Online_Resource_1.pdf'),(H/'build/Online_Resource_1_Neutral.md',H/'Online_Resource_1_Neutral.pdf')]:
    subprocess.run(['pandoc',str(src),'-o',str(dst),'--pdf-engine=xelatex','-V','geometry:margin=25mm','-V','fontsize=11pt','-V','mainfont=Latin Modern Roman'],check=True)
print('Private supplement, cover letter and declarations prepared; neutral supplement built.')
