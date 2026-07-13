# Stage4B-U1-D Pre-Gold Amendment 4 批准决定

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Decision date: 2026-07-13
- Amendment ID: `STAGE4B_U1_D_PREGOLD_AMENDMENT_4`
- Decision: `APPROVE_CACHE_FAIL_CLOSED_IMPLEMENTATION_SYNTHETIC_ONLY`
- Bound Amendment 4 package commit: `e5a0e2187e770c9d7b9e9a85a6b8e91067ed2af1`
- Returned v2.3 resumption package: `dbb4e057405069aceda5a7c5d88d9d39a4d14775`
- Baseline implementation commit: `a1d9ea0c517fcbad1ef27e78e760738d5c04d8b3`
- Official execution: `NOT_AUTHORIZED`
- Official data/source audit/ranking/cache access: `NOT_AUTHORIZED`
- Gold evaluation or U1-D metrics: `NOT_AUTHORIZED`
- Reservation: `KEEP_LOCKED`
- Stage3B: `KEEP_LOCKED`
- Other project conversations, thread tools, and global memory used: No

## 批准范围

1. checkpoint 更新为 `stage4b_u1_v2_3_1`；
2. controller 增加 `--embedding-cache-mode require-existing` 与 `--expected-embedding-cache-sha256`；
3. require-existing 模式在任何编码或正式输出前核验 cache path、SHA、bytes、exact six members、ID 顺序、模型元数据、dtype、shape、finite 和 normalization；
4. require-existing 模式禁止调用 `embed_texts`、`mkdir` 或 `np.savez_compressed`；
5. controller 计算后、正式输出提升前再次核验 cache 指纹；
6. decisions、rankings、policy 先写入 OS 临时目录，所有 cache 与等价门通过后才提升；
7. synthetic runner 增加 repo-relative 附加治理文件 hash binding，拒绝缺失、repo 外、重复和未登记路径；
8. manifest 中十个 `v2_3_1` 正式工件路径保持原样冻结；
9. 保留 33 项测试并新增 cache fail-closed 与 governance-binding hardening；
10. 完整 suite 连续运行两次，全部通过、零 failure/error/skip 且 evidence 字节一致；
11. 形成 implementation audit、完整 SHA、synthetic evidence 和新的 implementation-bound official-resumption 包后停止。

## 冻结 Cache

```text
SHA-256 = 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D
bytes = 210714667
unit shape = (143820, 384)
query shape = (4500, 384)
dtype = float32
```

完整 members、ID 和元数据规则以 `docs/STAGE4B_U1_PREGOLD_AMENDMENT_4_MANIFEST.json` 为准。所有测试必须使用 synthetic cache，不得读取真实 official cache。

## 继续禁止

- 不读取 official development、source audit、official ranking 或 official cache 内容；
- 不运行 official preflight、channel preparer、controller、cache audit、verifier 或 evaluator；
- 不创建、重建、覆盖、删除或迁移 fresh/legacy cache；
- 不修改 retrieval、effective-K、q25、score、ECDF、预算、trigger、ranking 或 endpoint；
- 不运行 Gold evaluation，不读取或解释 U1-D 指标；
- 不访问 reservation 或 Stage3B；
- 不修改、覆盖或删除 v2.2 失败工件；
- 不在 synthetic hardening 后自动恢复 official execution。

Amendment 4 实现/evidence 推送后，official execution 仍保持锁定，必须重新提交并获得 implementation-bound 恢复批准。
