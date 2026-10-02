# 本轮文件变更说明

同步时新增本目录 `.gitattributes`，将 PDF/PNG 明确标记为二进制，避免 Git 将期刊 PDF 误识别为文本。未修改 PDF 内容。

写作轮仅新增 paper/versions/2026-10-02_dual_manuscripts/ 下的论文交付内容。没有删除文件，没有修改正式实验源码、配置或 results/ 工件。初次交付保持本地；用户随后授权持续 GitHub 同步，本论文包据此提交与推送。

同步轮另在根 AGENTS.md 增加持续同步规则、在根 README.md 增加两版论文入口。仅提交这两处新增内容，不夹带其余上轮审计修改。新增本目录 .gitignore 排除重复 PDF 和 LaTeX 临时辅助文件，保留真实构建日志和页面检查图；没有删除本地文件。

| 新增内容 | 用途 |
|---|---|
| conference/main.tex、journal/main.tex | 两份完整英文正文 |
| conference/HyperGranular-RAG_Conference.pdf、journal/HyperGranular-RAG_Journal.pdf | 实际编译的阅读版 PDF |
| shared/numbers.tex、effects.json | 从旧聚合结果派生的统一效应/区间 |
| shared/workflow.pdf、effects.pdf、components.pdf、mechanisms.pdf | 新稿图示及真实结果的矢量可视化 |
| shared/ 下复制的 CSV | 已有表格、置换、插入分布和案例来源，保留原值 |
| shared/references.bib、acl.sty、acl_natbib.bst | 复制既有已勘误参考文献和论文样式，旧文件不被覆盖 |
| build_assets.py | 仅从已有聚合结果/CSV生成文稿资产 |
| check_manuscript_evidence.py | 核对表格转录、引用 key 与旧论文保留身份 |
| build_manuscripts.py | 本地编译、真实日志捕获和逐页渲染 |
| fetch_readings.py | 下载公开一手论文供阅读，不读取科研数据 |
| 两版 build/、page_review/、BUILD_STATUS.json | 实际构建日志、辅助输出、逐页图像和状态 |
| 本目录说明、台账和交接文档 | 故事链、证据/版本、阅读范围、构建与剩余事项 |

本轮写作中修改过新稿公式换行、native 几何措辞、长提交号分页及期刊稿中的版本关系说明，以纠正排版和表述。新稿重编译覆盖的是本轮派生输出，不是旧论文或冻结科学工件。

另新增的 temp/dual_manuscripts_env/ 和 temp/dual_manuscript_readings/ 均在原有忽略目录中，分别用于文档专用依赖和公开论文阅读缓存。没有删除这些缓存，也没有将它们作为科研结果。

进入本轮前工作区已有上轮审计修改及 Stage6 开发未跟踪工件；原样保留，不计作本轮完成的新实验。旧 paper/latex/main.tex、main.pdf 和原参考文献文件与写作开始时的身份一致，详见 shared/manuscript_consistency.json。
