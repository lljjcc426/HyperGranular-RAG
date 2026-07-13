# Stage4B-U1-D v2.2 Pre-Gold 硬失败审计 3

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Mode: run / hard-failure audit
- Audit date: 2026-07-13
- Verification Status: `STOPPED_HARD_FAILURE`
- Failure ID: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_3`
- Failure code: `HARD_FAILURE_VERIFIER_FIXED_TOP20_ASSUMPTION`
- Approval governance commit: `c13be1f`
- Synthetic rebinding evidence commit: `10ed570`
- Controller artifact commit: `9207bd78eea44d2ea3291fe9b6748526969a3224`
- Independent verifier execution count: `1`
- `VERIFIED_PRE_GOLD` generated: No
- Gold/evaluator arguments passed to verifier: No
- Gold evaluation or U1-D effect metrics read: No
- Reservation accessed: No
- Stage3B accessed: No

## 结论

independent verifier 在已提交工件 `9207bd78eea44d2ea3291fe9b6748526969a3224` 上单次运行，并在首个 ranking 结构检查处硬失败：

```text
ValueError: Top-20 length differs: 2wikimultihopqa::9219ff74093511ebbdaeac1f6bf848b6
```

失败位置为 `scripts/stage4b_u1_verify.py::derive_q25_inserted`。该函数无条件要求 dense 与 q25 列表长度都等于 20；失败查询的 Gold-free 候选池只有 17 个单元，因此 controller 生成的 dense/q25/final 列表长度均为 17。

verifier 在写出结果前失败，`results/stage4b_u1_d_official_dev4500_verified_pre_gold.json` 不存在。执行已立即停止，没有自动重跑。

## Gold-Free 结构诊断

停止后只对已提交 rankings 与本地 unlabeled query schema 做候选数/列表长度清点，不读取 score、Gold 或效果指标：

| 候选数与列表长度 | 查询数 |
|---|---:|
| 10 | 5 |
| 11 | 13 |
| 12 | 24 |
| 13 | 38 |
| 14 | 47 |
| 15 | 76 |
| 16 | 79 |
| 17 | 92 |
| 18 | 116 |
| 19 | 138 |
| 20 | 3,872 |

共 `628/4500` 个查询的候选池少于 20，最小候选数为 10。全部 4,500 条记录的 dense/q25/final 列表长度都精确等于：

```text
effective_k(query) = min(20, num_candidate_units(query))
```

结构清点中的 effective-K mismatch 为 `0`。这只说明 controller 输出与候选池大小一致，不替代独立 score、预算、ranking 复算，也不构成 U1-D 有效性证据。

## 证据边界

- dual-ID formal preflight 已通过；
- official channel preparation 已单次通过且没有计算 retrieval metrics；
- fresh cache 已单次创建并通过独立只读核查，SHA-256 为 `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D`；
- controller 已单次完成，现有 channel audit/decision/ranking/policy 已提交推送；
- 这些工件当前状态为 `UNVERIFIED_INVALID_FOR_GOLD`；
- Gold map 与 evaluator audit 没有传给 verifier，没有运行 evaluator；
- legacy cache 未修改、覆盖、迁移或删除；
- reservation 与 Stage3B 未访问。

## 停止与恢复条件

当前状态：

```text
PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_3
```

不得重跑 independent verifier，不得连接 Gold，不得修改现有工件。恢复前必须批准 Amendment 3，先完成 effective-K 协议/实现修正与 synthetic hardening，再对新的实现提交单独申请 official pre-Gold 恢复审批。
