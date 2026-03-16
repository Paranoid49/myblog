# 历史规划文档归档摘要

> ⚠️ 以下原始文件已归档，新人请直接阅读本摘要即可。原始文件仅供考古参考，不影响当前实现。
> 当前实现的权威依据请参见 `docs/product/`、`docs/architecture/`、`docs/api/`、`docs/engineering/`。

## 合并的原始文件
- implementation-alignment-remediation-checklist.md
- next-phase-optimization-todos.md
- philosophy-score-optimization-checklist.md
- project-philosophy-9plus-optimization-todos.md
- roadmap-and-remediation.md
- rule-authority-index.md

---

## 各文件核心要点摘要

### 1. implementation-alignment-remediation-checklist.md

文档与实现边界统一整改清单（方案 B），日期 2026-03-11。所有任务已完成。

- **P1 任务**：将默认数据库切回 SQLite 基线、补齐 GIF 图片上传支持、补齐作者资料字段（头像/昵称/简介/链接）、补齐前台分类/标签检索链路
- **P2 任务**：统一后台鉴权到 `get_current_admin`、为 taxonomy 公开能力建立更清晰边界、补充 API 契约文档
- **P3 任务**：控制 `api_v1_posts.py` 与 `AdminPostsPage.jsx` 的复杂度
- **核心原则**：以项目哲学（轻量/克制/可扩展）为约束，依据真实需求决定是补实现还是收文档

### 2. next-phase-optimization-todos.md

后续优化 TODO 清单，日期 2026-03-12。所有 9 项 TODO 已完成。

- **P1**：收口开发态前后端联调约定、补关键浏览器冒烟测试、统一后台入口行为
- **P2**：继续控制后台内容管理复杂度、统一前端认证体验细节、整理调试/临时脚本管理方式
- **P3**：持续观察路由边界、主题与扩展机制保持轻量、文档只做收口不做膨胀
- **明确禁止**：不引入 JWT、不拆成大量细碎模块、不做审美重构、不升级为重型插件系统

### 3. philosophy-score-optimization-checklist.md

哲学提分优化执行清单，日期 2026-03-13。所有 8 项任务已完成。

- **P0**：统一后台未授权收敛逻辑、将守则接入开发文档入口、清理调试残留、文档降承诺检查
- **P1**：对 `api_v1_posts.py` 做薄收口、对 `AdminPostsPage.jsx` 做薄收口、将文章模块边界写入文档
- **P2**：对扩展点做"稳定化"而非"增强化"
- **核心方法**：通过收口热点、统一失配、冻结边界来提分，而不是增加新系统

### 4. project-philosophy-9plus-optimization-todos.md

项目哲学 9.0+ 优化执行清单，日期 2026-03-14。P0 至 P5 所有任务已完成。

- **P0**：清理历史文档噪音、补 docs 总入口、清理调试残留
- **P1**：建立变更边界检查清单、补强扩展点契约说明、为扩展边界补测试、给热点模块设职责红线
- **P2**：热点文件小幅收口拆分、减少同一规则多处定义、统一开发入口
- **P3-P5**：错误码单点定义、媒体规则收口、哲学冻结规则测试、核心回归测试包、文档维护规则、关键规则权威来源索引
- **目标**：从 8.2 提升到 9.0+ 再冲 9.5+，路径是减噪收口 → 边界固化 → 优雅收束

### 5. roadmap-and-remediation.md

计划与整改总览，汇总了已完成整改工作与下一阶段优化方向。

- 文档与实现边界统一（方案 B）的 P1/P2/P3 已全部完成
- 下一阶段 9 项 TODO 已全部完成
- 后续执行原则：不扩张功能边界、先稳现有能力、不做审美式重构
- 建议持续关注：开发联调稳定性、浏览器路径回归、热点文件膨胀、临时文件清理

### 6. rule-authority-index.md

关键规则权威来源索引，日期 2026-03-14。

- 定义了 9 类关键规则的权威来源位置：错误码、初始化状态判定、API 响应结构、图片上传限制、扩展边界、开发入口、SiteSettings 与作者资料、taxonomy 规则、文档入口
- 核心目标：快速回答"某类规则该去哪看、去哪改"，减少同一事实多处定义
- 与 `development-guide.md`、`change-review-checklist.md`、`long-term-guardrails.md` 配合使用
