# 双版本成稿范围

日期：2026-10-02。依据用户当前正文授权，连续完成写作、历史证据核对、派生图表和本地编译。
附件 `CODEX_NEXT_PHASE_DUAL_MANUSCRIPTS_ZH (1).md` 在指定路径未找到；已请求可访问路径，写作按消息正文继续。附件内容不作已读声明。

会议稿面向 ACL/EMNLP Findings 风格，期刊稿为未指定刊物的完整英文研究稿。两者是同一研究的备选呈现，不能当作两篇互不重叠的工作同时投稿。

## 写作前固定的主张

- 历史 compact/static-q25 在三个 Qwen closed-candidate 边界的配对 F1 点估计为正，记录的 95% percentile bootstrap 区间下界大于零。
- MiniLM Full 相对特定 centroid-only NoFacet 的增量成立于记录的比较；不证明粒球必要性或优于 MMR/coverage。
- 原 MiniLM Full 低于 BGE；cross-space sidecar 与 BGE-native 相对 BGE 的区间跨零，不能写成等效。
- sidecar protected/unprotected 固定的是候选插入集合，不是完整最终证据或截断后的 prompt；不能写成纯位置因果效应。
- 紧致度恒等式、划分性质与反例是分析，不是新正式实验；Stage6 v2 合成原型不解释历史成绩。
- 使用原历史评价器和统计量，不重新评分。HotpotQA 首次实验及 generator-transfer 保留 special-answer 规则；component/sidecar/native 的 legacy token-overlap 实现不含该规则。分别标明。

## 交付约定

写作轮只在本目录新增文稿、共享证据/图表、文献阅读记录、构建记录和中文交接。旧稿、冻结工件、人工作者与许可元数据保持原样，不运行正式实验。初次交付不提交或推送；用户随后明确要求持续同步 GitHub，已替代此项临时限制，但未扩大科学执行权限。
阅读全文的外部论文与仅核查元数据/部分正文的文献分开记录。PDF 以实际构建与逐页检查为准，不以源码完整代替构建成功。
