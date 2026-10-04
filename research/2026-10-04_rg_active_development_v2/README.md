# RG-active-development-v2.0

基准 `1449ae36e72e36add4aec3f5bebdfb9f827c5808`；用户 2026-10-04 的 v2.0 规格覆盖 v1 单次提示修订和 D0 停止限制。旧结果保持原身份。本目录进行共享前端开发和固定 D1 比较，不修改论文。

当前实现目标：LM Format Enforcer 约束单一对象；程序生成关系编号；原句 ID/短片段定位；保存提及、身份与依据；开发/运行使用同一核验序列化。复用 v1 搜索引擎的 GB/KM/Flat 调度和有限细化，公共前端不作为粒球创新。

D0 全 32 题是已暴露开发材料；A 只看问题，B 使用问题审阅参考关系与最多两个窗口，C 使用预测关系。D1 固定原 64 题及分层，不用其答案选择提示/adapter。自然比较八臂，16/32 probes，1024 序列化输入 tokens；全部题保留，失败统一 Dense 回退。主要输出 canonical EM/F1，主机制 Hotpot bridge / MuSiQue 2hop 各自报告并等权，边界单列；配对 GB-feedback 对 uniform/fixed/KM-feedback/Flat/Dense。无确认性 PASS。

复用 Qwen2.5-3B-Instruct `aa8e72537993ba99e69dfaafa59ed015b17504d1` FP16 greedy batch1，BGE `d4aa6901d3a41ba39fb536a557fa166f842b0e09` CLS/L2。不下载新基座。优先接口研发；仅在格式修复后仍有稳定语义缺陷时考虑规定的小型 LoRA，reader 保持原始 3B。

本轮上限 GPU 21600s、CPU 14400s、新增 2GB、付费0。此前已记录累计 GPU 1343.813s、CPU 至少1395.453s（另有25.078s下载观测，历史未计时CPU仍 unknown）、磁盘约6.649GB。开发与比较共用本轮预算，优先为自然比较保留一半 GPU。进程在请求边界检查已记录预算，不因普通长计算任意终止。

仅开放的 Stage4E/F 材料；不读 Stage6 confirmation、reservation、Stage3B，不训练/选择于 D1，不对外投稿。原文/预测/缓存留 `local/`，只同步代码及允许公开的派生汇总。运行入口与实际完成范围随开发结果更新。
