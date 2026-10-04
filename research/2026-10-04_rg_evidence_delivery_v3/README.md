# RG-evidence-delivery-v3.0

本轮规格：用户附件 `CODEX_RG_EVIDENCE_DELIVERY_V3_ZH.md`（2026-10-04，12节），基准 `0aa197852d985965db549a97142d19746f8720e0`。仅已暴露 Stage4E/F、D0/D1 开发材料；没有独立确认。旧 v2 成绩保持不变。

A 在全部64题、Flat/GB-feedback/KM-feedback 的旧16-probe已保存状态上比较完整束、局部原文交付与数量条件化Dense。先构造全部输入，再仅为新提示调用原FP16 reader。A不采用B的核验或状态修复。

B实现多值关系三态核验、条件作用域、语义假设/见证分离、单关系—绑定—窗口任务。C按指定SHA规则选Hotpot bridge8 + MuSiQue2hop8，五臂共享修复，优先全体8任务点，再全体16点；不得依据成绩决定继续哪些方法。两类首题GB/KM反馈8点绕缓存复跑。所有失败保留分母。

GPU进程墙钟10800秒、CPU进程10800秒、新增磁盘1GB、付费0；reader最多768调用、前端2500调用。累计此前GPU16497.4784秒、CPU至少15355.4061秒；历史未计时CPU仍未知。尽量保留至少一半GPU给C。无训练、模型下载、论文修改或受限数据访问。

复用本地 Qwen2.5-3B `aa8e72537993ba99e69dfaafa59ed015b17504d1`、v2 LoRA、BGE `d4aa6901d3a41ba39fb536a557fa166f842b0e09`；前端NF4，核验base-only，reader原FP16，greedy32输出tokens、单线程。原文/预测/缓存仅在忽略的local目录，代码和公开汇总才同步。新增文件用途和实际完成状态在DEV_LOG与最终报告中记录。

## 实际完成状态

A/B/C及四次绕缓存复跑已完成。A的64题回放没有提示变化；C的16题、五方法、8/16任务点共160条输入也全部保持Dense。等权F1为0.12487007652911543、EM为0.0625，没有答案增益。反馈找到的一条正确完整链也被Flat和同反馈KMeans找到，其原文已在Dense。前端仍有自然角色/身份错误，不建议按当前配置扩大或启动确认。

先读 [RESULTS_AND_NEXT_DECISION.md](RESULTS_AND_NEXT_DECISION.md)。结果表为 `REPLAY_RESULTS.csv`、`FRONTEND_REGRESSION.csv`、`NATURAL_RESULTS.csv`、`NATURAL_PAIRED.csv`；逐题结果在 `NATURAL_QUERY_OUTCOMES.csv`。所有失败保留，未重新选择数据边界。

本轮实测GPU进程墙钟50.30分钟、CPU进程48.57分钟（不含未计时命令），目录约30.5MB，810次新前端调用及4次复跑reader调用；训练0、付费0。模型调用、逻辑缓存成本与独立复跑范围分别见 `ACTUAL_CALL_COSTS.csv`、`RESOURCE_SUMMARY.json`、`RERUN_CHECK.csv`。缓存命中不计为独立推理。

## 实现与复现入口

运行环境：仓库根 `temp/stage4e_env/Scripts/python.exe`，精确包版本见 `RESOURCE_SUMMARY.json`。依赖原v1/v2本地输入、模型、adapter、已开放数据及缓存；公开仓库不包含原文和模型，不能把仅有CSV称为可独立重建全部实验。

| 文件 | 用途 |
|---|---|
| `delivery.py`, `replay.py`, `check_replay.py` | 局部原文交付、A旧轨迹回放、提示与元数据核对 |
| `frontend.py`, `source_rules.py` | 目标化定位与多值关系核验、条件作用域、窄范围原文规则 |
| `state.py`, `search.py` | 语义状态/出处分离、共享接口上的五方法调度 |
| `common.py`, `runtime.py` | 既有输入/模型适配、预算与调用记录 |
| `regression.py`, `throughput.py`, `tests.py` | D0开发回归、真实接口贯通、定向测试 |
| `natural.py`, `evaluate.py`, `verify_outputs.py` | C自然比较、canonical评分、可见原文与复跑检查 |
| `resources.py` | 实际调用与资源汇总 |

实际执行顺序是 `replay.py construct` → `evaluate.py replay`；B开发及测试后，`natural.py run --budget 8` → `natural.py read --budget 8` → 对16点执行相同两命令 → `evaluate.py natural` → `natural.py rerun --budget 8` → `natural.py read-rerun --budget 8` → `evaluate.py rerun` → `verify_outputs.py` → `resources.py`。所有入口均位于本目录。不要为“复现状态”无条件重复已完成推理；输出按版本保留，已有文件受覆盖保护。

C使用v35共享接口，核验内核与v34相同。`FRONTEND_REGRESSION.csv`保留v30—v34的实际运行/规则重算；当前 `regression.py` 的新运行输出名为v35，该入口没有在本轮另作全套模型复跑，不把代码入口当运行证据。13个不同测试的实际日志见 `TEST_OUTPUT.txt`。

四次复跑绕过任务与条件编码缓存，并真实重跑reader；复用已固定的解析和scope计划，不声称全前端独立复跑。最终160条记录、3350个span的源坐标和token检查见 `FINAL_VERIFICATION.json`。语义人工审阅范围及反例见 `NATURAL_SOURCE_REVIEW.md`。

只新增或修改本目录文件，无文件删除。旧工件、论文及无关未提交工程工作保持原状。本任务完成后停止。
