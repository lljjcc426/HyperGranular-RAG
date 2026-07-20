# Stage4E-E2E Level B 集中审核请求

请对 Stage4E-E2E 当前 package 做一次集中 Level B 审核，不建立逐文件、逐提交或逐命令审批链。

## 审核对象

- Level A protocol：`docs/STAGE4E_STATIC_HGRAG_E2E_ANSWER_QUALITY_LEVEL_A_PROTOCOL.md`；
- implementation commit：`712077edbe3f85d15da7d4290d294ab05bbdc9fc`；
- official config：`configs/stage4e_e2e_official_train1000_v1.json`；
- input/model/environment manifests；
- `results/stage4e_e2e_official_train1000_v1_verified_input.json`；
- targeted suite：19/19 PASS；
- implementation report：`docs/STAGE4E_E2E_LEVEL_B_IMPLEMENTATION_REPORT.md`。

## 请重点核对

1. 1,000-query selection、历史零重叠、blind/Gold/metadata 隔离与 supporting-fact unit mapping；
2. encoder/generator snapshot 全文件身份、精确 CUDA 环境与 synthetic byte/token determinism；
3. runner 是否只读 blind channel，且只调用 Dense 与静态 all-query q25，不调用 U1/Stage4D model；
4. prompt token cap、method-order、decode、main/rerun 和 no-overwrite transaction；
5. evaluator 是否在 `STAGE4E_PRE_GOLD_ARTIFACTS_VERIFIED` 前不能读 Gold，metadata 是否延迟到 aggregate decision 后；
6. verifier 是否独立实现 answer metric、bootstrap 和 decision，而不导入 evaluator；
7. config 中 official retrieval/generation 与 Gold evaluation 是否仍为双重 `authorized=false`；
8. reservation、Stage3B 和 U2 是否继续锁定。

## 建议 verdict

若无实质缺陷：

```text
ACCEPT_STAGE4E_LEVEL_B_IMPLEMENTATION
STAGE4E_GOLDFREE_OFFICIAL_COMMAND_CONFIRMATION_ALLOWED
STAGE4E_GOLD_EVALUATION_REMAINS_NOT_AUTHORIZED
```

若有缺陷，请只返回精确、可复现的最小完整性问题及限定修正范围。普通路径、控制台、日志或非科学表现问题不应恢复 Amendment 链。

本审核请求本身不授权 official retrieval、generation、Gold evaluation、reservation、Stage3B 或 U2。
