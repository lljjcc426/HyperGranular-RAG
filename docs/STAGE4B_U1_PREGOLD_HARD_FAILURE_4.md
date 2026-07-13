# Stage4B-U1-D Pre-Gold Hard Failure 4

## Material Passport

- Origin Skill: `academic-research-suite / experiment-agent`
- Failure date: 2026-07-13
- Failure ID: `STAGE4B_U1_D_PREGOLD_HARD_FAILURE_4`
- Failure code: `HARD_FAILURE_V2_3_1_DECISIONS_EQUIVALENCE`
- Execution count: `1`
- Request-package commit: `e76c921454697d1784b0d76a9d9677113051f0f6`
- Implementation commit: `34349c70ee24b8240fd169393134d4280968b790`
- Approval-governance commit: `53850f58e57f51b3c6067ed3108edff6b99a2dfc`
- Rebinding-evidence commit: `a963befd812658972b156d2a7a26a488ac3c4482`
- Controller execution HEAD: `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`
- Status: `PREGOLD_EXECUTION_STOPPED_HARD_FAILURE_4`
- Gold metrics read or computed: No
- Reservation accessed: No
- Stage3B accessed: No

## 失败结论

唯一一次 v2.3.1 official Gold-free controller 使用 manifest 准确路径和以下冻结模式运行：

```text
--mode development
--model-name sentence-transformers/all-MiniLM-L6-v2
--batch-size 64
--max-length 192
--embedding-cache-mode require-existing
--expected-embedding-cache-sha256 69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D
--reference-policy E:\科研\HyperGranular-RAG\results\stage4b_u1_d_official_dev4500_policy.json
```

controller 在 OS temporary directory 写入 pending outputs 后，通过了 cache `after controller computation` 指纹门，随后在 `validate_formal_pending_equivalence` 的第一个 v2.2 等价门停止：

```text
ValueError: v2.3.1 decisions differ from the frozen v2.2 bytes
```

失败发生在 rankings/reference-policy 等价核验完成前、cache `after equivalence checks` 门前、formal output promotion 前。没有自动重跑。

## 失败后完整性核查

| 硬门 | 结果 |
|---|---|
| v2.3.1 decisions | 不存在 |
| v2.3.1 rankings | 不存在 |
| v2.3.1 policy | 不存在 |
| controller execution audit | 不存在 |
| `VERIFIED_PRE_GOLD` | 不存在 |
| pending temp outputs | `TemporaryDirectory` 退出后未保留 |
| fresh cache bytes | `210714667` |
| fresh cache SHA-256 | `69ED39ABC0636B7B63A41639B64CB037FAE556F10CB130FCD18AFB61CBE06F7D` |
| legacy cache SHA-256 | `746FC1130038C789190F2A37CB911BBFC46905CFCC138E361C1F6CF991A45F02` |
| v2.2 decisions SHA-256 | `6FB6EB6DBFE3C6B819E65ADD268D9F94CFEA24E5761C9E4CB53CD0965C3723C7` |
| v2.2 rankings SHA-256 | `ED289D234F6F4FEC58A48168CB6CA78950489CD5F5640E977068CA6A786E03CB` |
| v2.2 reference policy SHA-256 | `829E8A0DB7E4108C4D23F2D0CE3DD0C227F329E9EDF77BB4ED49C20544EC07DC` |
| v2.3.1 channel 五文件 | 保留且完整 |

## 证据边界

当前只证明 pending decisions 的**文件字节**未通过冻结 v2.2 等价门。未读取或解释 pending decisions 内容，未读取 U1-D retrieval/Gold 指标，因此不能在本审计中判断差异来源、大小、方向或科学影响。

不运行 independent verifier，不生成 `VERIFIED_PRE_GOLD`。若要诊断字节差异、修订等价定义或重跑 controller，必须先形成新的审查/Amendment、明确诊断数据边界并获得用户批准；在此之前 official execution 保持停止。

## 文件操作

本失败阶段保留一次成功 channel 的五个 versioned 文件，新增 channel audit 与本 hard-failure audit，并更新项目状态文档。没有删除、覆盖或改写 cache、v2.2 失败工件或旧审计。

审计草稿首次根据 Git 短 SHA 手工补写了错误的完整 `8e0bab18...`；提交前以 `git rev-parse HEAD` 发现并修正为实际 `8e0bab13ad20c06795dffd5ca71f167a814cdfb0`。该草稿错误没有影响执行命令、实验文件或 Git 历史。
