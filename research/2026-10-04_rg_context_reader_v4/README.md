# RG-context-reader-v4.0

SPEC_ID=HGRAG-CONTEXT-READER-V4-20261004

采用 `C:\Users\cc\Downloads\CODEX_RG_CONTEXT_READER_V4_ZH.md` 完整12节规格；参考提交 `93e27c82333d83ee276113ad586cfe26d50ad062`。本目录保存新实现及派生结果，不修改旧轨迹、论文或无关工程文件。

研究问题：已有原文的选取/删减能否改变reader表现，效应能否由长度和公共输出协议解释；GB与Flat/KM的旧搜索产物是否不同。仅EXPOSED_DEVELOPMENT；沿用v3全部16题（两数据集各8），无新确认、搜索、抽取、核验、embedding、训练或下载。

固定8上下文 D/A_G/L_G/R/A_F/L_F/A_K/L_K × P0/P1/P2，共384逻辑结果。自动包复用各自16任务状态，允许来源全在Dense，只交付一个完整出处包、不fill；优先级按附件。L为A正文token上限条件化的BGE完整窗口选择。R独立读取已开放支持标注，不向自动构造器传递；MuSiQue用支持段落全部原句。三协议共同正文、原FP16 3B且无adapter、1024实际输入token上限。D从末尾删完整单元以同时适配三协议；A不可截断核验出处；R按固定来源/句序逐块纳入，超限标不完整。

P0原提示32输出tokens，P1同提示128，P2仅answer字符串对象且禁止额外字段、128tokens。P0/P1原文本完整canonical评分，P2合法字段完整评分；非法结构统一空预测。没有新p值或等效声明。所有16题保留；R和有包子集仅诊断。

D0按已有sampling_hash两类各取4题，不按表现选；先开发输出接口再跑主比较。先完成全部核心192行，再归因192行。复跑固定每类v3选样hash前2题的D/A_G P2，共8真实调用，绕缓存。身份包括权重、FP16、adapter关闭、tokenizer/template、完整输入tokens、生成配置及schema/约束实现；不同生成上限不互用缓存。

限额：GPU进程墙钟7200s、CPU进程7200s、新增512MB、付费0；比较384逻辑行、D0最多64真实调用、复跑最多8，总新reader不超456。在安全请求边界保存；资源不足标NOT_RUN，不按胜负选择去留。此前累计GPU19515.444s，CPU至少18269.750s，未知CPU不补零；同时受累计12h/24h约束。

使用 academic-research-suite / experiment-agent 的执行与可复现性角色；用户本轮授权覆盖实现、运行、修复及同步，不套用逐命令确认或默认硬超时。新增成本与历史搜索成本分开；公开代码和派生表，原文/回答/标注留忽略的local目录。

当前：范围已登记，实施中。完成后以 RESULTS_AND_NEXT_DECISION.md 为实际结果入口。
