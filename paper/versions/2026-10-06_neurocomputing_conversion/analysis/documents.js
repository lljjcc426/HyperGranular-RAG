// Build editable submission documents. Private metadata stays outside public outputs.
const fs = require('fs');
const path = require('path');
const {Document,Packer,Paragraph,TextRun,AlignmentType,LevelFormat} = require(path.resolve('temp/nc_conversion_runtime/node_modules/docx'));
const H=path.resolve('paper/versions/2026-10-06_neurocomputing_conversion');
const meta=JSON.parse(fs.readFileSync(path.resolve('temp/nc_conversion_20261006_input/private/AUTHOR_METADATA_PRIVATE.json'),'utf8'));
const title='From Set Prediction to Evidence Selection: An Empirical Study of Surrogate Objectives in Multi-hop RAG';
function para(text,opts={}){return new Paragraph({spacing:{after:150,line:260},...opts,children:[new TextRun({text,size:22,font:'Arial',...opts.run})]});}
function heading(t){return para(t,{run:{bold:true,size:28},spacing:{after:240}});}
async function write(file,children){const doc=new Document({creator:'',title:path.basename(file,'.docx'),styles:{default:{document:{run:{font:'Arial',size:22}}}},numbering:{config:[{reference:'bullets',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:360,hanging:180}}}}]}]},sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1134,bottom:1134,left:1134,right:1134}}},children}]});fs.writeFileSync(path.join(H,file),await Packer.toBuffer(doc));}
async function main(){
const highlights=[
'Accurate set prediction can coexist with poor evidence selection.',
'Search-aligned training affects support and answer quality differently.',
'Simple relevance-diversity selection remains competitive in this study.',
'Exact ball indexes preserve choices but add cost at 128 candidates.'
];
if(highlights.some(x=>x.length>85))throw Error('Highlight exceeds 85 characters');
fs.writeFileSync(path.join(H,'Highlights.txt'),highlights.join('\n')+'\n');
await write('Highlights.docx',[heading('Highlights'),...highlights.map(x=>para(x,{numbering:{reference:'bullets',level:0}}))]);
const authors=meta.authors.sort((a,b)=>a.order-b.order);
const corresponding=authors.find(a=>a.corresponding_author);
const correspondingName=corresponding.given_name+' '+corresponding.family_name;
await write('submission_local/Title_Page.docx',[
heading(title),para(authors.map(a=>a.given_name+' '+a.family_name+(a.corresponding_author?'*':'')).join(', ')),
para(corresponding.institution+', '+corresponding.country_region),
para('* Sole corresponding author: '+correspondingName),
...authors.flatMap(a=>[para(a.given_name+' '+a.family_name,{run:{bold:true}}),para('Email: '+a.email+' | ORCID: '+a.orcid)]),
para('Author-review version. No department, postal address, degree, or author contribution has been inferred.',{run:{italics:true,size:20}})
]);
await write('submission_local/Cover_Letter_DRAFT.docx',[
heading('Cover letter — draft for author review'),para('6 October 2026'),para('Dear Editors of Neurocomputing,'),
para('Please consider the manuscript “'+title+'” as a research article after the outstanding submission checks below are completed.'),
para('The study examines how compact neural set scorers trained on support annotations translate supplied-set discrimination into actual evidence selection and reader answers. It compares first-, second-, and fourth-order factorized models with a DeepSets control under shared candidates, a fixed reader, and explicit input constraints. A search-aligned continuation and an equal-update replay control connect learned objectives to the decisions they induce.'),
para('The empirical contribution is a linked analysis of prediction, selection, answer quality, and measured cost. Same-question transitions show that the fourth-order model’s net answer decline is concentrated among questions retaining complete annotated support; second-order continuation instead gives small gains under both studied seeds. Exact indexes preserve decisions but add measured cost at this scale. The paper reports development dependencies and missing records explicitly, and claims neither architectural superiority nor independent confirmation.'),
para('This focus on neural learning objectives and their operational consequences fits the journal’s learning-systems scope. The submission package includes editable source, reproducible numerical summaries, and transparent disclosure of AI assistance. The authors have confirmed no relevant competing interests.'),
para('Before sending: ECIR submission #'+meta.ecir_submission_id+' has a withdrawal request but no verified success receipt. Final author approval, funding, CRediT, journal-specific requirements, and the Subscription route must be confirmed. This draft does not assert exclusivity or completed approval.'),
para('Sincerely,'),para(correspondingName+', sole corresponding author'),para(corresponding.institution+', '+corresponding.country_region),para(corresponding.email)
]);
await write('Declaration_of_Competing_Interests.docx',[heading('Declaration of competing interests'),para('The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.')]);
fs.writeFileSync(path.join(H,'analysis/DOCUMENT_BUILD.json'),JSON.stringify({highlights:highlights.map(text=>({text,characters:text.length})),private_documents:['Title_Page.docx','Cover_Letter_DRAFT.docx'],author_order_source:'Private metadata; no inferred roles',generated:true},null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});
