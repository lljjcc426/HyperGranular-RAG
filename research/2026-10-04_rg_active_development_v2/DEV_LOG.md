# v2 开发记录

- 基准已提交，无需复制/冻结旧失败设计。保留全部无关 dirty 文件。
- 首轮改动针对已定位问题：object/list 冲突改为约束对象；模型不生成 id/answer_var；长引文改为句 ID 和实体片段定位；标题/别名依据进入统一核验与 renderer。D0 全部是 exposed development，参考计划只在 B 使用。
- 环境没有 XGrammar/LM Format Enforcer。选择轻量 LM Format Enforcer 的 HF 接口；只安装新增小依赖，不升级 torch/transformers，不下载模型。官方接口依据：https://github.com/noamgat/lm-format-enforcer 。版本与真实运行记录随后追加。
