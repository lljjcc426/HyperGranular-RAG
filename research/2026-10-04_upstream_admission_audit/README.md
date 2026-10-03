# 上游准入诊断（2026-10-04，已完成）

- [结果与决定](RESULTS_AND_DECISION.md) · [限定实施卡](RUN_CARD.md)
- [共同失败](GATE_JOINT_FAILURES.csv) · [六条件与数量匹配](MASK_AND_BREADTH_COMPARISON.csv)
- [分组与饱和](GROUPING_AND_SATURATION.csv) · [案例审阅](CASE_REVIEW.md)
- [饱和性质](SATURATION_PROOF.md) · [论文影响](MANUSCRIPT_IMPACT.md)
- [对账](RECONCILIATION.json) · [输出检查](SUPPLEMENTARY_CHECKS.json) · [清单与成本](manifest.json)

复现使用现有temp/stage4e_env/Scripts/python.exe，先tests.py，再audit.py，最后
verify_and_summarize.py；本次已经完成，不因阅读本文件而重复运行。
audit.py显式拒绝覆盖已有输出，输出仅在新目录；fresh reproduction需要明确的新目录。
inspect_results.py只读摘要/固定案例。未加载模型、调用GPU、生成答案、重评分或bootstrap。
输入角色为已暴露历史探索，不是独立确认。病例原文/逐组/逐题目标留在ignored local/。

表格口径：MASK表的queries为200，hits/targets及其他计数为总计；query_mean_er/cr为
query等权均值，target_micro_coverage为目标总命中率，两者不可替代。pre/two/proposal
是不含Dense fill的扩展支路，final是完整列表。COUNT_MATCHED_DENSE行的vs_g0参考
是同分组RULE G0，不是参照自己的G0。空池数量单列、平均标注比例只在非空池上计算；
NA不表示零。未标注支持的单位不是自动无关或噪声。
GROUPING表BASE的k、每题最大组大小、size-L1、seed差等为总和，除以queries得到均值；
不是全体最大值。GATE表的独立失败重叠，joint行才是互斥组合，分母分别列明。
Hotpot支持句与MuSiQue支持段落从不相加充当同一粒度样本量。
