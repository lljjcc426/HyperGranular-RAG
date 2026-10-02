# 回退定位与投稿目标（2026-10-02 核验）

本轮没有新增算法实测，不能据文献刷新提高投稿目标。保留两种呈现形式，但它们是同一组研究结果的替代稿，不是可同时投稿的两项独立工作。

## 现实选择

**期刊优先候选：Journal of Intelligent Information Systems（JIIS），research paper。** 其范围包含智能检索、知识表示、系统分析及实现经验，与当前“受限证据选择与放置的条件性研究”相符。匹配范围不是录用保证；其仍要求实质改进，缺少简单匹配控制和外部系统实测仍是风险。本轮不以顶刊/强方法创新定位。

- [官方范围](https://link.springer.com/journal/10844/aims-and-scope)：作为系统与证据分析稿定位，不声称强检索 SOTA。
- [作者指南](https://link.springer.com/journal/10844/submission-guidelines)：25页上限包含参考文献、图表；要求 LaTeX。页面同时给出 Springer Nature 模板及较早 smallcondensed 指引，最终模板需人工核定。当前23页为通用 article 排版，**不能据此宣称正式模板页数已合规**。需扁平化提交包、作者页及 Statements and Declarations，未经确认不填。
- [费用](https://link.springer.com/journal/10844/how-to-publish-with-us)：subscription 路线不收 APC；可选 OA 当前列 £2590 / $3590 / €2890，可能变动且税另计。不授权付费，本轮支出0。具体单/双匿名要求未从已读指南明确核实，保留匿名工作稿，不自作决定。

**会议候选：ARR long paper → NAACL 2027，经验分析/可复现性方向。** 不再把“新的强检索 SOTA”作为投递卖点。保留 Findings 风格的稳健有限结论，但当前 NAACL CFP 未明确写 Findings 路径，故不宣称已核实可直接投稿 Findings。

- [NAACL 2027 CFP](https://2027.naacl.org/calls/main_conference_papers/) 覆盖 RAG、分析与可复现性；ARR 截止2026-10-12，官方会议页 commitment 为2026-12-23（AoE）。[ARR dates](https://aclrollingreview.org/dates) 的聚合记录有12-20差异，实际提交前应再核对，不能静默选一个保证准确。
- [ARR CFP](https://aclrollingreview.org/cfp)：long 主文8页，结论之后 Limitations/ethics、参考文献与附录另计。新会议稿主文至结论在第7页结束，含限制/伦理至第7页，参考文献第8页，附录第8–10页；总10页不等于10页计数主文。当前使用现有 ACL review style，未声明最终模板已认证。
- 作者 reviewer registration、ORCID/profile、匿名补充材料、注册/展示费用等由人确认；本轮不对外提交或注册，不承诺费用为0。

没有理由为凑 short paper 删掉必要算法与反证。优先保留完整长稿。若选 JIIS，不同时送 ARR；若会议先发表，期刊版不能仅扩写同样结果冒充新的原创投稿，必须另行满足该刊扩展与重叠政策。

## 中文故事链

多跳问答需要同时解决“选什么”和“放哪里”。HyperGranular-RAG 在已提供的句子候选中，以几何分组和 query facets 做有限补全，保护原排名前缀。已有数据支持对 MiniLM 的重复改善和指定 facet 对照；固定可见证据的排序对照支持 protected 相对 front insertion。原 Full 明确低于 BGE，BGE 扩展与生成器迁移未决。

近邻说明粒球超图和超图 RAG 本身并非本项目独占。论文的可保留价值是可精确定义的局部补全实现，以及选择、覆盖、置换与答案之间的经验边界。无事实抽取是实现差异，尚不是已验证的总成本优势；高阶结构不可替代、普通分组不如粒球、强检索增益均未建立。

会议稿用核心结果与归因边界表表达这一问题；期刊稿增加近邻结构对象表和“已有证据/缺失控制”表，保留直接相关数学解释、成本口径和完整限制。没有新增实验表格分数，没有改图。
