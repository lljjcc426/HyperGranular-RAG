// Editable submission materials; personal data is loaded only into ignored outputs.
const fs=require('fs'),path=require('path');
const {Document,Packer,Paragraph,TextRun,AlignmentType,LevelFormat}=require(path.resolve('temp/nc_conversion_runtime/node_modules/docx'));
const H=path.resolve('paper/versions/2026-10-06_neurocomputing_final_polish');
const meta=JSON.parse(fs.readFileSync(path.resolve('temp/nc_final_polish_v2_input/private/author_metadata.json'),'utf8'));
const authors=meta.authors.sort((a,b)=>a.order-b.order),corr=authors.find(a=>a.corresponding_author);
const full=a=>a.given_name+' '+a.family_name;
const title='From Set Prediction to Evidence Selection: An Empirical Study of Surrogate Objectives in Multi-hop RAG';
const funding='This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.';
const coi='The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.';
function para(text,opts={}){return new Paragraph({spacing:{after:135,line:255},...opts,children:[new TextRun({text,font:'Arial',size:22,...opts.run})]});}
function heading(t){return para(t,{run:{bold:true,size:27},spacing:{after:230}});}
async function write(n,children){const doc=new Document({creator:'',title:path.basename(n,'.docx'),numbering:{config:[{reference:'bullets',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:360,hanging:180}}}}]}]},sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1134,bottom:1134,left:1134,right:1134}}},children}]});fs.writeFileSync(path.join(H,n),await Packer.toBuffer(doc));}
async function main(){
const highlights=[
 'Strong set discrimination can coexist with losses of annotated support.',
 'Answer losses can occur even when complete annotated support is retained.',
 'Search-aligned training has model-dependent effects on answer quality.',
 'Exact ball indexes preserve choices but add cost at 128 candidates.'
];
if(highlights.some(t=>t.length>85))throw Error('Highlight exceeds 85 characters');
fs.writeFileSync(path.join(H,'Highlights.txt'),highlights.join('\n')+'\n');
await write('Highlights.docx',[heading('Highlights'),...highlights.map(t=>para(t,{numbering:{reference:'bullets',level:0}}))]);
await write('submission_local/Title_Page.docx',[heading(title),para(authors.map(a=>full(a)+(a.corresponding_author?'*':'')).join(', ')),para(corr.affiliation+', '+corr.country),para('* Sole corresponding author: '+full(corr)),...authors.flatMap(a=>[para(full(a),{run:{bold:true}}),para('Email: '+a.email+' | ORCID: '+a.orcid)])]);
await write('submission_local/Author_Declarations.docx',[
 heading('Author declarations'),para('CRediT authorship contribution statement',{run:{bold:true}}),
 ...authors.map(a=>para(full(a)+': '+a.credit.join(', ')+'.')),
 para('Funding',{run:{bold:true}}),para(funding),para('Declaration of competing interests',{run:{bold:true}}),para(coi)
]);
await write('submission_local/Funding.docx',[heading('Funding'),para(funding)]);
await write('submission_local/Competing_Interests.docx',[heading('Declaration of competing interests'),para(coi)]);
await write('submission_local/Cover_Letter_DRAFT.docx',[
 heading('Cover letter — author-review draft'),para('6 October 2026'),para('Dear Editors of Neurocomputing,'),
 para('We present “'+title+'” for consideration as a research article, subject to the authors’ final approval before submission.'),
 para('The manuscript examines whether neural scores that distinguish supplied evidence sets also select better contexts and improve answers. First-, second-, and fourth-order factorization models and a DeepSets control share candidates, annotation supervision, and a fixed reader. A common search-state training intervention is compared with static training and an optimizer-update-matched replay control.'),
 para('The central analysis joins support and answer changes on the same questions. For the fourth-order model, the largest negative F1 contribution occurs among questions retaining complete annotated support; newly complete-support groups contribute positively. Second-order continuation gives small gains under both seeds. Exact ball indexes preserve choices but do not reduce measured selection time at this scale. These findings connect a neural training objective to the decisions it induces, within explicitly described development dependencies.'),
 para('The paper provides reproducible numerical summaries, editable figures, and transparent research and writing AI disclosures. Its focus on neural objectives, evidence selection, and downstream behavior is relevant to Neurocomputing’s learning-systems scope. We do not claim independent confirmation or general superiority of a model family.'),
 para('The authors have confirmed withdrawal of the earlier conference submission, no specific grant funding, and no relevant competing interests. Subscription publication is preferred, subject to the journal’s actual options. This draft does not certify final approval of the new manuscript.'),
 para('Sincerely,'),para(full(corr)+', sole corresponding author'),para(corr.affiliation+', '+corr.country),para(corr.email)
]);
const texEscape=s=>s.replace(/&/g,'\\&');
const front=authors.map(a=>'\\author[aff]{'+full(a)+(a.corresponding_author?'\\corref{cor1}':'')+'}\n\\ead{'+a.email+'}').join('\n')+'\n\\cortext[cor1]{Corresponding author.}\n\\affiliation[aff]{organization={'+corr.affiliation+'},country={'+corr.country+'}}\n';
fs.writeFileSync(path.join(H,'submission_local/author_frontmatter.tex'),front+'\\global\\bibsep=6pt\\relax\n');
fs.writeFileSync(path.join(H,'submission_local/author_credit.tex'),'\\section*{CRediT authorship contribution statement}\n'+authors.map(a=>'\\noindent\\textbf{'+full(a)+':} '+texEscape(a.credit.join(', ').replace(/–/g,'--'))+'.\n').join('\n'));
fs.writeFileSync(path.join(H,'analysis/DOCUMENT_BUILD.json'),JSON.stringify({highlights:highlights.map(text=>({text,characters:text.length})),confirmed_funding:true,confirmed_competing_interests:true,credit_source:'Current user-supplied private metadata',withdrawal:'AUTHOR_CONFIRMED_WITHDRAWN_NOT_INDEPENDENTLY_ACCESSED',final_approval:'PENDING_NEW_MANUSCRIPT_AUTHOR_REVIEW'},null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});
