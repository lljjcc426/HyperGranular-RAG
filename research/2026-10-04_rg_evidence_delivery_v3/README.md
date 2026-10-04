# RG-evidence-delivery-v3.0

本轮规格：用户附件 `CODEX_RG_EVIDENCE_DELIVERY_V3_ZH.md`（2026-10-04，12节），基准 `0aa197852d985965db549a97142d19746f8720e0`。仅已暴露 Stage4E/F、D0/D1 开发材料；没有独立确认。旧 v2 成绩保持不变。

A 在全部64题、Flat/GB-feedback/KM-feedback 的旧16-probe已保存状态上比较完整束、局部原文交付与数量条件化Dense。先构造全部输入，再仅为新提示调用原FP16 reader。A不采用B的核验或状态修复。

B实现多值关系三态核验、条件作用域、语义假设/见证分离、单关系—绑定—窗口任务。C按指定SHA规则选Hotpot bridge8 + MuSiQue2hop8，五臂共享修复，优先全体8任务点，再全体16点；不得依据成绩决定继续哪些方法。两类首题GB/KM反馈8点绕缓存复跑。所有失败保留分母。

GPU进程墙钟10800秒、CPU进程10800秒、新增磁盘1GB、付费0；reader最多768调用、前端2500调用。累计此前GPU16497.4784秒、CPU至少15355.4061秒；历史未计时CPU仍未知。尽量保留至少一半GPU给C。无训练、模型下载、论文修改或受限数据访问。

复用本地 Qwen2.5-3B `aa8e72537993ba99e69dfaafa59ed015b17504d1`、v2 LoRA、BGE `d4aa6901d3a41ba39fb536a557fa166f842b0e09`；前端NF4，核验base-only，reader原FP16，greedy32输出tokens、单线程。原文/预测/缓存仅在忽略的local目录，代码和公开汇总才同步。新增文件用途和实际完成状态在DEV_LOG与最终报告中记录。

运行环境：仓库根 `temp/stage4e_env/Scripts/python.exe`。代码入口随后随实现补齐；本记录是运行前范围与资源优先级，不是完成声明。
