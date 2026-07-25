# Verified Literature Corpus

Status: `VERIFIED_LITERATURE_CORPUS_COMPLETE`

Verification date: 2026-07-25. The corpus was checked against publisher,
conference, ACL Anthology, PMLR, OpenReview, Microsoft Research, ScienceDirect,
JMLR, Nature, or official arXiv records. A preprint and its published version are
not counted as separate works. “Use” describes the exact manuscript claim the
source is allowed to support; it does not transfer the source's empirical claims
to HyperGranular-RAG.

| Bib key | Title and authors | Year / venue | Persistent identity and official source | Peer reviewed | Permitted manuscript use |
|---|---|---|---|---|---|
| `karpukhin2020dpr` | *Dense Passage Retrieval for Open-Domain Question Answering* — Vladimir Karpukhin, Barlas Oğuz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, Wen-tau Yih | 2020, EMNLP | DOI `10.18653/v1/2020.emnlp-main.550`; [ACL Anthology](https://aclanthology.org/2020.emnlp-main.550/) | Yes | Dense passage retrieval as a standard learned retrieval baseline. |
| `lewis2020rag` | *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — Patrick Lewis et al. | 2020, NeurIPS | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) | Yes | Retrieval-conditioned generation and non-parametric evidence access. |
| `guu2020realm` | *REALM: Retrieval-Augmented Language Model Pre-Training* — Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, Ming-Wei Chang | 2020, ICML | [PMLR 119](https://proceedings.mlr.press/v119/guu20a.html) | Yes | Joint retrieval/language-model pretraining as related, not directly compared, work. |
| `yang2018hotpotqa` | *HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering* — Zhilin Yang et al. | 2018, EMNLP | DOI `10.18653/v1/D18-1259`; [ACL Anthology](https://aclanthology.org/D18-1259/) | Yes | HotpotQA task definition and supporting-fact supervision. |
| `trivedi2022musique` | *MuSiQue: Multihop Questions via Single-hop Question Composition* — Harsh Trivedi, Tushar Khot, Ashish Hartmann, Ruskin Manku, Ashish Sabharwal | 2022, TACL | DOI `10.1162/tacl_a_00475`; [ACL Anthology](https://aclanthology.org/2022.tacl-1.31/) | Yes | MuSiQue task construction and reduced reasoning-shortcut motivation. |
| `xiong2021mdr` | *Answering Complex Open-Domain Questions with Multi-Hop Dense Retrieval* — Wenhan Xiong et al. | 2021, ICLR | [OpenReview](https://openreview.net/forum?id=EMHoBG0avc1) | Yes | Iterative multi-hop dense retrieval and evidence-chain construction. |
| `zhao2021beamdr` | *Multi-Step Reasoning Over Unstructured Text with Beam Dense Retrieval* — Chen Zhao, Chenyan Xiong, Jordan Boyd-Graber, Hal Daumé III | 2021, NAACL | DOI `10.18653/v1/2021.naacl-main.368`; [ACL Anthology](https://aclanthology.org/2021.naacl-main.368/) | Yes | Beam-based iterative evidence-chain retrieval. |
| `trivedi2023ircot` | *Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions* — Harsh Trivedi, Niranjan Balasubramanian, Tushar Khot, Ashish Sabharwal | 2023, ACL | DOI `10.18653/v1/2023.acl-long.557`; [ACL Anthology](https://aclanthology.org/2023.acl-long.557/) | Yes | Interleaving retrieval and reasoning; distinct from one-shot bounded insertion. |
| `sun2019pullnet` | *PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text* — Haitian Sun, Tania Bedrax-Weiss, William W. Cohen | 2019, EMNLP-IJCNLP | DOI `10.18653/v1/D19-1242`; [ACL Anthology](https://aclanthology.org/D19-1242/) | Yes | Iterative retrieval over text and structured knowledge. |
| `sarthi2024raptor` | *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval* — Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh Khanna, Anna Goldie, Christopher D. Manning | 2024, ICLR | [OpenReview](https://openreview.net/forum?id=GN921JHCRw) | Yes | Hierarchical organization and retrieval over recursively summarized text. |
| `gutierrez2024hipporag` | *HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models* — Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su | 2024, NeurIPS | [OpenReview](https://openreview.net/forum?id=hkujvAPVsg) | Yes | Graph-based evidence integration and personalized propagation. |
| `mavromatis2025gnnrag` | *GNN-RAG: Graph Neural Retrieval for Efficient Large Language Model Reasoning on Knowledge Graphs* — Costas Mavromatis, George Karypis | 2025, Findings of ACL | DOI `10.18653/v1/2025.findings-acl.856`; [ACL Anthology](https://aclanthology.org/2025.findings-acl.856/) | Yes | Graph-neural retrieval as a structure-aware RAG family. |
| `edge2024graphrag` | *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* — Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Jonathan Larson | 2024, Microsoft Research preprint | arXiv `2404.16130`; [Microsoft Research](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/) | No; preprint | Graph-based community summarization; not a directly compared QA baseline. |
| `feng2019hgnn` | *Hypergraph Neural Networks* — Yifan Feng, Haoxuan You, Zizhao Zhang, Rongrong Ji, Yue Gao | 2019, AAAI | DOI `10.1609/aaai.v33i01.33013558`; [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/4235) | Yes | General motivation for representing high-order relations with hypergraphs. |
| `xia2019granularball` | *Granular Ball Computing Classifiers for Efficient, Scalable and Robust Learning* — Shuyin Xia, Yunsheng Liu, Xin Ding, Guoyin Wang, Hong Yu, Yuoguo Luo | 2019, Information Sciences | DOI `10.1016/j.ins.2019.01.010`; [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0020025519300106) | Yes | Origin and properties of granular-ball computing; the present use is retrieval-specific. |
| `liu2024lostmiddle` | *Lost in the Middle: How Language Models Use Long Contexts* — Nelson F. Liu et al. | 2024, TACL | DOI `10.1162/tacl_a_00638`; [ACL Anthology](https://aclanthology.org/2024.tacl-1.9/) | Yes | Context position can affect model use of evidence, motivating placement evaluation. |
| `xu2024recomp` | *RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation* — Fangyuan Xu, Weijia Shi, Eunsol Choi | 2024, ICLR | [OpenReview](https://openreview.net/forum?id=mlJLVigNHp) | Yes | Selective/compressed augmentation under limited context, not direct superiority. |
| `ram2023incontext` | *In-Context Retrieval-Augmented Language Models* — Ori Ram et al. | 2023, TACL | DOI `10.1162/tacl_a_00605`; [ACL Anthology](https://aclanthology.org/2023.tacl-1.75/) | Yes | Retrieval-to-generation interaction and in-context use of retrieved text. |
| `izacard2021fid` | *Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering* — Gautier Izacard, Edouard Grave | 2021, EACL | DOI `10.18653/v1/2021.eacl-main.74`; [ACL Anthology](https://aclanthology.org/2021.eacl-main.74/) | Yes | Multi-passage generation as evidence that retrieval and reading are coupled. |
| `petroni2021kilt` | *KILT: A Benchmark for Knowledge Intensive Language Tasks* — Fabio Petroni et al. | 2021, NAACL | DOI `10.18653/v1/2021.naacl-main.200`; [ACL Anthology](https://aclanthology.org/2021.naacl-main.200/) | Yes | Provenance-aware evaluation for knowledge-intensive tasks. |
| `pineau2021reproducibility` | *Improving Reproducibility in Machine Learning Research* — Joelle Pineau et al. | 2021, JMLR | [JMLR 22(164)](https://jmlr.org/papers/v22/20-303.html) | Yes | Reproducibility checklists, artifact transparency, and reporting discipline. |
| `amrhein2019retire` | *Scientists Rise Up against Statistical Significance* — Valentin Amrhein, Sander Greenland, Blake McShane | 2019, Nature comment | DOI `10.1038/d41586-019-00857-9`; [Nature](https://www.nature.com/articles/d41586-019-00857-9) | Editorial/comment | Caution against dichotomizing uncertainty; supports precise inconclusive wording. |
| `xiao2023bge` | *C-Pack: Packaged Resources To Advance General Chinese Embedding* — Shitao Xiao, Zheng Liu, Peitian Zhang, Niklas Muennighoff, Defu Lian, Jian-Yun Nie | 2023, arXiv technical report | arXiv `2309.07597`; [arXiv](https://arxiv.org/abs/2309.07597) | No; preprint | Identity and motivation of the pre-specified BGE embedding family; actual model identity is frozen separately. |

## Corpus-level decisions

- The manuscript cites peer-reviewed versions when available.
- `edge2024graphrag` and `xiao2023bge` are explicitly identified as
  preprints/technical reports.
- Model-card and license facts are kept in
  [`LICENSE_AND_AVAILABILITY.md`](../submission/LICENSE_AND_AVAILABILITY.md),
  not inferred from academic papers.
- No citation is used to claim direct superiority over GraphRAG, iterative
  retrieval, or strong dense retrievers because those head-to-head experiments
  were not conducted.
- The complete machine-readable citation records are in
  [`verified_references.bib`](verified_references.bib).
