# v2 开发记录

- 基准已提交，无需复制/冻结旧失败设计。保留全部无关 dirty 文件。
- 首轮改动针对已定位问题：object/list 冲突改为约束对象；模型不生成 id/answer_var；长引文改为句 ID 和实体片段定位；标题/别名依据进入统一核验与 renderer。D0 全部是 exposed development，参考计划只在 B 使用。
- 环境没有 XGrammar/LM Format Enforcer。选择轻量 LM Format Enforcer 的 HF 接口；只安装新增小依赖，不升级 torch/transformers，不下载模型。官方接口依据：https://github.com/noamgat/lm-format-enforcer 。版本与真实运行记录随后追加。
- 安装 lm-format-enforcer 0.11.3 / pydantic 2.13.5 / interegular 0.3.3。HF 集成引用旧 `PreTrainedTokenizerBase` 位置，使用进程内类型别名兼容 Transformers 5.14.1，未改第三方源码。5项定向测试通过。首批6题均有实际 mask 调用、合法 JSON 和 EOS；不是补括号修复。
- v20 解析仍有描述短语充当常量、答案变量当中间实体、过度 ambiguous。v21 增加共享的二次角色/依赖修订（仍只输入问题与预测草稿），使用虚构同类例；保留 v20 全部输出。父亲方向已正确的 index26 用于退步检查。B/C 分开定位，不让参考计划进入 C。
