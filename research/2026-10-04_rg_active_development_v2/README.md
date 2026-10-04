# RG-active-development-v2.0

本轮已完成：D0 研发与有限 adapter、D1 64 题 × 8 管线 × 2 预算点、指定绕缓存复跑、canonical 评分与资源汇总。先读 [RESULTS_AND_NEXT_DECISION.md](RESULTS_AND_NEXT_DECISION.md)。各方法逐题交付的 reader 提示完全相同，未建立反馈或粒球的答案增量；这是本轮真实比较结果，不是 v1 结论复用。

基准 `1449ae36e72e36add4aec3f5bebdfb9f827c5808`；用户 2026-10-04 的 v2.0 规格覆盖 v1 单次提示修订和 D0 停止限制。旧结果保持原身份。本目录进行共享前端开发和固定 D1 比较，不修改论文。

当前实现：LM Format Enforcer 约束单一对象；程序生成关系编号；逐关系原句 ID/短片段定位；保存提及、身份与依据；开发/运行使用同一核验序列化。核验要求直接命题判断和不展示候选尾实体的对象定位一致，分数是离散接受标记，不是概率。复用 v1 搜索引擎的 GB/KM/Flat 调度和有限细化，公共前端不作为粒球创新。

D0 全 32 题是已暴露开发材料；A 只看问题，B 使用问题审阅参考关系与最多两个窗口，C 使用预测关系。D1 固定原 64 题及分层，不用其答案选择提示/adapter。自然比较八臂，16/32 probes，1024 序列化输入 tokens；全部题保留，失败统一 Dense 回退。主要输出 canonical EM/F1，主机制 Hotpot bridge / MuSiQue 2hop 各自报告并等权，边界单列；配对 GB-feedback 对 uniform/fixed/KM-feedback/Flat/Dense。无确认性 PASS。

复用 Qwen2.5-3B-Instruct `aa8e72537993ba99e69dfaafa59ed015b17504d1`，BGE `d4aa6901d3a41ba39fb536a557fa166f842b0e09` CLS/L2。不下载新基座。共享解析/抽取采用 NF4 + 固定 LoRA（本地 `adapters/v27`）；核验关闭 adapter；reader 在单独进程使用原始 FP16。均 greedy batch1、固定单线程。`v20` 等只是本目录的开发迭代标识，任务版本始终是 RG-active-development-v2.0。

本轮上限 GPU 21600s、CPU 14400s、新增 2GB、付费0。此前已记录累计 GPU 1343.813s、CPU 至少1395.453s（另有25.078s下载观测，历史未计时CPU仍 unknown）、磁盘约6.649GB。开发与比较共用本轮预算，优先为自然比较保留一半 GPU。进程在请求边界检查已记录预算，不因普通长计算任意终止。

仅开放的 Stage4E/F 材料；不读 Stage6 confirmation、reservation、Stage3B，不训练/选择于 D1，不对外投稿。原文/预测/缓存留 `local/`，只同步代码及允许公开的派生汇总。模型、adapter 和原文数据不上传。

已完成的 D0 开发：32/32 格式合规，10/32 全关系语义可用；参考关系 B 在 8/32 题产出原文见证，自解析 C 在 6/32 题产出见证。两诊断窗口下 B/C 均未形成完整束。**部分正确关系不等于正确完整链**，也不说明 GB 有优势。`PARSE_REVIEW.csv` 与 `VERIFIER_SOURCE_REVIEW.csv` 是助手基于问题/原文的开发审阅，不是独立专家金标准。

运行（仓库根目录，现有 `temp/stage4e_env/Scripts/python.exe`）：

```text
research/2026-10-04_rg_active_development_v2/tests.py
research/2026-10-04_rg_active_development_v2/develop.py A --round v27
research/2026-10-04_rg_active_development_v2/develop.py B --round v27
research/2026-10-04_rg_active_development_v2/develop.py C --round v27
research/2026-10-04_rg_active_development_v2/natural.py index
research/2026-10-04_rg_active_development_v2/natural.py run
research/2026-10-04_rg_active_development_v2/natural.py read
research/2026-10-04_rg_active_development_v2/natural.py rerun
research/2026-10-04_rg_active_development_v2/natural.py read-rerun
research/2026-10-04_rg_active_development_v2/evaluate.py
```

D0 每个迭代文件按已完成题恢复，不覆盖旧结果；不要用旧 round 名运行新提示。D1 同一选定版本按题保存，缓存只在方法请求对应窗口后返回，所有逻辑 probe 和模型调用成本仍计入各方法。重复 prompt 的 reader 结果仅减少实际调用数，不能冒称独立复跑。指定复跑绕过 probe/reader 缓存。实体仅在唯一页名或经核验的明确标题/原文身份依据下连接；未消解名称仍保持区别。

本地重建 adapter 的入口为 `adapt_data.py`、`adapt_train.py`、`adapt_evaluate.py`；需要已开放 D0 源材料，不需要 D1 标签。现有 adapter 已完成一次固定 3 epoch/30 step 训练，无需重复训练来查看本轮结果。运行依赖版本见最终资源记录，现有环境未整体升级。

自然结果的 `accepted_facts` 统计已请求窗口中的接受事件，重叠窗口可以重复见证同一事实，不代表独立事实数量；`complete_bundle` 是相对于预测计划的程序完整性，不等于原问题的语义正确链。`logical_model_and_encoding_seconds` 是按调用归账的模型与编码成本，另列分裂耗时；缓存条件下的 `recorded_search_transaction_seconds` 是实际整个搜索事务时间（最大32 probes），不能当作各预算点的独立部署时延，也不能与逻辑成本再次相加。
