# Primary-literature reading and citation notes

Date: 2026-10-02. Reading for this writing round is separated from the preceding reference-metadata audit. Downloading a PDF or scanning its title is not recorded as reading its full text.

## Full-text reading completed this round

The following five original papers were downloaded from the ACL Anthology and read through their extracted full text, including the main text, references, and appendices where present. Local PDFs/text are in the ignored temp/dual_manuscript_readings/ directory. This is full-text reading, not replication of their experiments or page-by-page visual proofreading of those external PDFs.

| Paper and primary source | Scope read | Used in our writing | Does not establish |
|---|---|---|---|
| Yang et al. (2018), [HotpotQA](https://aclanthology.org/D18-1259.pdf) | Full 12-page text, including collection, distractor/full-wiki settings, metrics, analysis, appendices | Define multihop evidence and sentence-level support; distinguish supplied candidates from corpus retrieval | Our closed-candidate results are full-wiki results, or our evaluator is automatically official |
| Trivedi et al. (2022), [MuSiQue](https://aclanthology.org/2022.tacl-1.31.pdf) | Full 16-page text, including composition, shortcut control, split construction, models, metrics and analysis | Explain connected reasoning, answerable versus unanswerable settings, and paragraph support | Our subsets eliminate all shortcuts or measure sentence-chain recall |
| Lin and Bilmes (2011), [A Class of Submodular Functions for Document Summarization](https://aclanthology.org/P11-1052.pdf) | Full 11-page text, including objectives, optimization assumptions, experiments and references | Organize explicit objective → property → algorithm → empirical test; delimit fixed-prefix coverage bound | The historical HGRAG score is a true marginal, or a coverage bound guarantees answer F1 |
| Liu et al. (2024), [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9.pdf) | Full 17-page text, including all appendices on ambiguity, distractors, GPT-4 and Llama-2 | Motivate distinguishing evidence content from placement; report context sensitivity precisely | Protecting exactly ten units is optimal, or our insertion-set comparison isolates pure order |
| Dror et al. (2018), [The Hitchhiker's Guide to Testing Statistical Significance in NLP](https://aclanthology.org/P18-1128.pdf) | Full 10-page text, including test discussion, empirical examples and references | Separate effect estimate, uncertainty, null hypothesis, paired design and dependence assumptions | Any bootstrap tail proportion is a generally calibrated p-value |

No paragraphs are copied from these papers. The manuscripts use original prose around this project's actual evidence. Borrowed methodological ideas are cited; the fixed-prefix coverage discussion is identified as a specialization of a standard greedy bound, not a new theorem guaranteeing HGRAG performance.

## Additional cited papers: narrower reading/verification

These are not described as fully read this round. The earlier audit's official metadata checks are retained, and the current writing claims are confined to the definitions below. No external method's published number is copied into an experimental comparison table.

| Citation | Current source/scope | Claim supported |
|---|---|---|
| Karpukhin et al. (2020), DPR | [ACL official page](https://aclanthology.org/2020.emnlp-main.550/), abstract and metadata; full reading not claimed | Dense dual-encoder retrieval background |
| Xiong et al. (2021), MDR | [Author arXiv record](https://arxiv.org/abs/2009.12756); prior audit also checked conference PDF identity | Iterative multihop dense retrieval; not a matched baseline run here |
| Trivedi et al. (2023), IRCoT | [ACL official page](https://aclanthology.org/2023.acl-long.557/), abstract and metadata | Interleaving retrieval and generated reasoning |
| Sarthi et al. (2024), RAPTOR | [Author arXiv record](https://arxiv.org/abs/2401.18059), abstract and metadata; ICLR identity carried from prior official-source audit | Recursive embedding/clustering/summarization tree |
| Gutiérrez et al. (2024), HippoRAG | [Official NeurIPS page](https://proceedings.neurips.cc/paper_files/paper/2024/hash/6ddc001d07ca4f319af96a3024f6dbd1-Abstract-Conference.html), abstract and metadata | Knowledge-graph and Personalized PageRank retrieval background |
| Luo et al. (2025), HyperGraphRAG | [Official NeurIPS page](https://proceedings.neurips.cc/paper_files/paper/2025/hash/df55ee6e59f8ac4a625219e11fe9ddba-Abstract-Conference.html), abstract and metadata | n-ary relational facts represented by hyperedges; different from query-local facet relations |
| Carbonell and Goldstein (1998), MMR | Prior official DOI-registration audit and [author publication page](https://www.cs.cmu.edu/~jade/); publisher page inaccessible this round | Classical relevance–redundancy alternative; no claim that we ran or beat it |
| Xia et al. (2019), granular-ball computing | Prior official DOI-registration audit; [publisher abstract record](https://www.sciencedirect.com/science/article/abs/pii/S0020025519300106); full text unavailable this round | Granular representation background only; not proof that our radius gate or grouping is effective |

OpenReview forum pages returned a browser-verification screen this round; author arXiv records and the preceding official conference metadata audit were used instead. ACM and ScienceDirect full-text access was not obtained. This is disclosed rather than relabeled as full-paper reading.

## Reference identity and attribution

The shared bibliography is a byte-for-byte copy of the preceding corrected 27-entry repository bibliography. Both manuscripts cite the same 13 entries, with no missing BibTeX keys and no undefined citations in their final build logs. Remaining unused entries are not rendered as references.

MuSiQue's authors are Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, and Ashish Sabharwal, confirmed from the paper front page. HyperGraphRAG uses the published 2025 NeurIPS entry, not mixed metadata from an earlier preprint. Iyer's expanded conference-PDF name versus abbreviated arXiv name is not treated as a different author. Xia et al.'s registered Yuoguo Luo spelling is retained rather than guessed.

The earlier full metadata record is audit/2026-10-02_reproducibility/REFERENCE_AUDIT.md. This writing pass does not claim a second independent bibliography audit, a complete retraction search, or full-text reading of all 27 stored entries.
