# 有限检索记录（2026-10-02）

这是定向最近邻审核，不是系统综述。附件作为检索种子，判断回到出版商、正式论文和 arXiv。附件提到的另两份 registry/bib 未在给定附件中提供；本目录重新建立登记，不假定已读它们。

## 一轮定向检索

实际使用六篇题名、SAGHL/MGHRL 缩写和八个 DOI；查询组合包括：

- `SAGHL granular pdf`；`granular-ball 3716345 pdf`；两个长题名加作者和 `manuscript/pdf`。
- `(granular-ball OR granularball OR granular ball) (hypergraph OR hyperedge OR hypernetwork) retrieval question answering`。
- `粒球 超图 超边 检索 增强 生成 粒计算`。
- `granular computing hypergraph dynamic coverage`。
- `HyperGraphRAG Cross-Granularity Hyper-RAG 2026`。

来源：ScienceDirect、IEEE Xplore、AAAI OJS、NeurIPS proceedings、Nature、arXiv、Crossref。DBLP/搜索摘要只发现线索；不以抓取日期、DOI 年份或会议模板推断接收。

## 一轮邻接追踪与版本查找

- 从 Wang 等 AAAI 正文参考文献追到 HyperGraphRAG、Hyper-RAG 的 arXiv 版本，再核对正式版。AAAI 的实体—段落扩散是直接任务近邻。
- MGHRL 参考文献指向 Xia 2019、粒球谱聚类、HGNN/UniGNN；这些是粒球/超图谱系，不是已经完成的 QA baseline。
- ESWA 预览引文出现 `A hypergraph model of granular computing` (2008)，以及普通 granular computing 的后续模糊超图工作。仅作谱系线索；未读其全文，不作为粒球构造首创判断的充分证据，也不新增到论文正式引用。
- 定向前向查询 `SAGHL MGHRL hypergraph`、三个 RAG 方法共同出现的检索，没有得到需要本轮另行部署的已核实直接控制。搜索无结果不证明不存在先行工作。
- arXiv histories 核对 AAAI v1、MGHRL v1、HyperGraphRAG v1/v2/v3、Hyper-RAG v1。出版商核对 journal/proceedings 状态；未做跨版本全文 diff。

## 纳入、排除和停止

六个种子全部纳入；另两篇 2027 卷期论文保留为相关先行线索，不因 DOI 含 2026 就改成 2026 卷期。其精确 online 日期仍未知。
超像素、优化算法、普通粒球分类、医学 RAG 非近邻等结果不扩大阅读，原因是不能改变本轮核心构造/QA 比较。没有统计或声称 PRISMA 数量。

SAGHL、TKDE 已尝试出版商和合法作者稿检索；本轮未取得完整论文。SAGHL 仅 publisher introduction/section previews，TKDE 仅 abstract。未购买、绕过权限或联系作者。Hyper-RAG 普通 PDF 链接返回一页访问占位内容；使用可读 HTML，并把阅读范围记为部分全文，不能写成 PDF 全文通读。合法公开 PDF 只留 ignored `temp/bounded_literature/`，不提交第三方全文。

没有继续无限扩展。缺口转入 REVIEW：更强算法新颖性为 C，已评估论文可以收窄完成；另有确认集独立性未核实的 D 执行停止，回到已授权写作流程。
