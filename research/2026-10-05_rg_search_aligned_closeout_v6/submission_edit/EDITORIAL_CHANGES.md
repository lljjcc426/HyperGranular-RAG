# v6 投稿前科学编辑：实际修改

状态：READY_FOR_AUTHOR_CHECK。任务：V6-SUBMISSION-EDITORIAL-ONLY-20261005。
来源提交：b7c91fde94d1de7213ab50382ba4f50f313187c3。没有新实验或新方法版本。

| 修改位置（相对本轮 v6 目录） | 实际修改及原因 |
|---|---|
| manuscripts/conference/main.tex，摘要、引言、方法、实验、结果、结论 | 主线收紧为集合评分→实际选择→回答；摘要改用同一 QA128 的 55/128→57/128 和 F1 0.4181→0.3766；说明 Dense-K6 已是可行终选候选，保留 MMR、回放与四类 aligned 控制；索引无加速压缩为系统观察。 |
| manuscripts/journal/main.tex，对应章节及历史结果讨论 | 展开同面板支持/答案变化、低阶与 seed 差异；保留旧句级结果但不作为新段落选择器消融；移除内部授权、预算预留、作者待办等管理叙述。 |
| manuscripts/shared/qa_table.tex、qa_interpretation.tex | 主表统一 Method / Full(count) / F1 / ΔF1(MMR)，全部以原 128 题为分母；加入从既有逐题结果得到的支持 gain/loss 和答案 gain/loss，不作因果推断。 |
| manuscripts/shared/data_roles.tex、aligned_results.tex | 新增 FIT/TUNE/DEV/MINE/DEV_SELECT/QA 角色表；明确 checkpoint 面板参与选择、与 QA 面板不相交但均为已暴露开发材料；DEV_SELECT 数字保留且不冒充外部确认。 |
| 两稿的方法和实验解释 | 明确干预同时改变样本、排序损失与 checkpoint 选择；equal-update replay 不匹配全部前向计算；共同 token 上限不等于等长输入；Dense/MMR 管线可能超过六块。 |
| 两稿的数据/代码与 AI 声明 | 对应实际匿名数值补充包，区分数值汇总重建与从预测重新评分/完整模型复现；如实披露 Codex 的实现、分析与写作参与。 |
| submission_edit/derive_editorial.py、verify_editorial.py、派生 CSV/JSON | 仅读已有逐题数值和数据角色，核实同面板计数；未调用模型、重评预测、重做 bootstrap 或改统计决策。 |
| submission_edit/anonymous_supplement/ | 便携 stdlib 重建脚本、匿名逐题数值、必要汇总和数据取得/方法说明；不含原文、答案、原始问题 ID、权重、凭证或个人路径。 |
| submission_edit/anonymous_conference/、submission_bundle/ | 实际编译的匿名会议包和无子目录期刊源码包；仅收录实际使用的文献条目、类/样式及输入文件。 |
| submission_edit/REFERENCE_CHECK.md | 按实际引用范围刷新一手元数据与相关方法段，逐项注明阅读深度；不声称所有全文本轮重读。 |
| SUBMISSION_WINDOW.md、ABSTRACT_READY.md、manuscripts/README.md | 更新实际交付入口和 ECIR→JIIS→IEEE Access 条件路线；摘要登记回执仍 UNKNOWN。旧摘要标为来源版本。 |
| submission_edit/private/HANDOFF.md | 本地忽略文件：作者、声明、许可、投稿登记及最终模板确认事项；不加入公开包。 |

H2 相对自身静态版本的两个 seed 小幅正变化、H1 的 seed 依赖、H4 的下降以及 MMR 优势点估计均保留。均值不同方向不被写成逐题负相关或“支持增加导致答案下降”。

使用 academic-research-suite 的来源核对与编辑/排版流程，以及 PDF 技能的实际渲染检查；未据技能恢复逐段审批，未冒称独立专家或人工作者已审阅。

没有删除文件。旧命名的两份 v6 PDF、历史实验工件和无关本地改动未修改；旧正文来源保存在上述 Git 提交。新增脚本只服务于本轮数值整理、构建和打包。
