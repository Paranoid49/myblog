# 文档与实现边界统一整改清单（方案 B）

日期：2026-03-11

## 1. 目标

本清单用于推进“文档与实现边界统一”的**方案 B**：

> 以当前项目哲学 **轻量、克制、可扩展** 为约束，优先补齐实现，使核心能力与已冻结文档保持一致，而不是简单下调文档承诺。

适用范围：

- `docs/v1-scope.md`
- `docs/api-v1-contract.md`
- 当前后端与前端实现
- 相关测试与验收链路

---

## 2. 执行原则

### 2.1 轻量
- 只补齐文档已明确承诺、且对博客主闭环有价值的能力。
- 不借机引入新的复杂抽象、基础设施或大规模重构。

### 2.2 克制
- 优先复用现有结构与能力。
- 不因为边界统一任务，顺手做无关“优化”。
- 不扩大 V1 范围，不新增文档未承诺的能力。

### 2.3 可扩展
- 补齐实现时，尽量沿用已有扩展点：数据库 provider、主题注册、事件总线（发布订阅）。
- 新增能力不能破坏现有 API 契约稳定性。

---

## 3. 当前差距总览

当前已识别的文档 / 实现差距如下：

### D1. 默认数据库不一致
- 文档：默认 SQLite（`docs/v1-scope.md`）
- 代码：默认 `database_url` 为 PostgreSQL（`app/core/config.py`）

### D2. 图片格式支持不一致
- 文档：支持 `jpg/png/webp/gif`
- 代码：当前只允许 `jpeg/png/webp`

### D3. 作者资料字段不一致
- 文档：头像 / 昵称 / 简介 / 链接
- 代码：当前仅有 `name/bio/email`

### D4. 前台分类 / 标签检索未完整落地
- 文档：前台支持按分类 / 标签检索
- 代码：当前前台无对应公开页面与链路

---

## 4. 任务优先级清单

---

# P1：必须优先完成

这些任务直接影响项目边界认知与 V1 验收口径，必须优先完成。

## Task P1-1：将默认数据库切回 SQLite 基线
**状态：已完成**

### 目标
让默认运行路径与项目哲学、V1 文档保持一致：

- 默认单体部署
- 默认 SQLite
- PostgreSQL 作为官方支持选项，而非默认基线

### 预期收益
- 统一“轻量优先”的默认开发体验
- 降低新环境启动门槛
- 文档与配置一致，减少理解偏差

### 风险评估
- 可能影响依赖默认配置的脚本、测试或本地已有环境
- 需要确认 PostgreSQL 自动建库流程仍作为可选能力保留

### 实施建议
1. 修改 `app/core/config.py`
   - 将默认 `database_url` 改为 SQLite 路径
2. 检查以下脚本在默认 SQLite 下仍可正常工作
   - `scripts/start_blog.py`
   - `scripts/start_fullstack.py`
   - `scripts/run_dev.py`
3. 确保 PostgreSQL 路径仍可通过环境变量显式启用
4. 补充 / 修正测试
   - 配置测试
   - 启动脚本测试

### 涉及文件
- `app/core/config.py`
- `scripts/start_blog.py`
- `scripts/start_fullstack.py`
- `scripts/run_dev.py`
- `tests/test_config.py`
- `tests/test_start_blog_script.py`
- `tests/test_start_fullstack_script.py`

### 验收标准
- 不提供 `.env` 时，项目默认使用 SQLite 启动
- 显式提供 PostgreSQL `DATABASE_URL` 时，自动建库 / 迁移流程仍可用
- 文档中的“默认 SQLite”与实际行为一致

---

## Task P1-2：补齐 GIF 图片上传支持
**状态：已完成**

### 目标
使图片上传能力与 V1 文档一致：支持 `jpg/png/webp/gif`。

### 预期收益
- 文档与实现一致
- Markdown 写作体验更完整
- 不改变现有上传接口结构，改动范围可控

### 风险评估
- GIF 文件体积通常更大，需要确认大小限制策略是否仍合理
- 若仅按 MIME 放开，不应额外引入图像处理复杂度

### 实施建议
1. 扩展上传允许的 MIME 类型
   - 增加 `image/gif`
2. 增加扩展名映射
   - `.gif`
3. 保持现有大小限制与命名策略不变
4. 补充测试
   - GIF 上传成功
   - 现有非法类型校验仍成立

### 涉及文件
- `app/routes/api_v1_posts.py`
- `tests/test_api_v1_posts.py`

### 验收标准
- `image/gif` 上传返回 201
- 返回 URL 结构与现有图片格式一致
- 非法类型仍返回原有错误码

---

## Task P1-3：补齐作者资料字段到“头像 / 昵称 / 简介 / 链接”
**状态：已完成**

### 目标
使作者资料能力达到文档承诺的最小完整形态。

### 预期收益
- 公开作者页能力与文档一致
- 后台作者资料编辑功能更完整
- 更符合博客产品定位

### 风险评估
- 会涉及模型字段扩展与迁移
- 需谨慎处理 API 向后兼容
- 前端表单与展示需要同步调整

### 实施建议
1. 为 `SiteSettings` 扩展最小字段集
   - `author_avatar`
   - `author_link`
   - 保留现有 `author_name` / `author_bio`
2. 更新迁移
   - 新增字段 migration
3. 扩展作者 API
   - GET 返回新增字段
   - POST 支持更新新增字段
4. 扩展后台作者页表单与前台作者页展示
5. 补充测试
   - API 字段读写
   - 前端展示链路（如已有可测范围）

### 字段设计建议
- `author_avatar`：字符串 URL，允许为空
- `author_link`：字符串 URL，允许为空
- 若继续保留 `email`，需明确它是附加字段，不替代“链接”能力

### 涉及文件
- `app/models/site_settings.py`
- `app/routes/api_v1_author.py`
- 迁移文件（新增）
- `frontend/src/admin/pages/AdminAuthorPage.jsx`
- `frontend/src/public/pages/PublicAuthorPage.jsx`
- `tests/test_api_v1_author.py`
- 相关前端 / 集成测试

### 验收标准
- 作者资料至少支持：头像、昵称、简介、链接
- 前台作者页可展示新增字段
- 后台可编辑新增字段
- API 返回结构与文档承诺一致

---

## Task P1-4：补齐前台分类 / 标签检索链路
**状态：已完成**

### 目标
实现文档承诺的“前台按分类 / 标签检索”。

### 预期收益
- 前台阅读侧内容发现路径完整
- V1 内容组织能力闭环
- 分类 / 标签不再只是后台管理字段

### 风险评估
- 会同时涉及 API、前端路由、前端页面、可能的 service 收口
- 若实现过重，容易把 taxonomy 复杂度推高

### 实施建议
1. 后端补齐公开 taxonomy 查询接口
   - 方案 A：新增公开接口，如 `/api/v1/categories/{slug}`、`/api/v1/tags/{slug}`
   - 方案 B：在现有 posts API 基础上增加公开查询能力
2. 前端增加公开页面
   - `/categories/:slug`
   - `/tags/:slug`
3. 在首页 / 详情页中提供可点击入口
4. 尽量复用现有 `PublicLayout`
5. 如 taxonomy 逻辑增长明显，再考虑把 route / service 职责适度收口

### 涉及文件
- `app/routes/api_v1_posts.py` 或新增 taxonomy/public route
- `app/services/taxonomy_service.py`
- `frontend/src/App.jsx`
- `frontend/src/public/pages/*`（新增分类页、标签页）
- `frontend/src/public/pages/PublicHomePage.jsx`
- `frontend/src/public/pages/PublicPostDetailPage.jsx`
- `tests/test_api_v1_posts.py` 或新增 taxonomy API tests
- 前端 / e2e 测试

### 验收标准
- 访客可通过分类或标签查看相关文章列表
- 首页 / 详情页存在进入分类 / 标签页的可见入口
- 分类 / 标签页面在无内容时有合理空状态

---

# P2：应紧随其后完成

这些任务不是文档差距本身，但会显著降低补齐实现后的维护成本。

## Task P2-1：统一后台鉴权到 `get_current_admin`
**状态：已完成**

### 目标
统一后台鉴权行为，避免 route 内部保留较弱的 `_require_login()` 平行实现。

### 预期收益
- 鉴权逻辑一致
- 可校验用户存在与 active 状态
- 更符合“已有能力统一复用”的克制原则

### 风险评估
- 会影响多个后台接口的依赖签名
- 需确保现有测试按新行为调整

### 涉及文件
- `app/core/deps.py`
- `app/routes/api_v1_posts.py`
- `app/routes/api_v1_author.py`
- 相关测试

### 验收标准
- 后台路由统一基于 `get_current_admin`
- 禁用 / 删除重复 `_require_login()` 逻辑
- 相关测试保持通过

---

## Task P2-2：为 taxonomy 公开能力建立更清晰边界
**状态：已完成**

### 目标
在补齐前台分类 / 标签检索后，避免 taxonomy 逻辑继续挤压 `api_v1_posts.py`。

### 实施建议
- 若新增公开 taxonomy 能力后，`api_v1_posts.py` 明显继续变胖，则考虑：
  - 把 taxonomy 公开接口拆到独立 route
  - 把 taxonomy 查询逻辑进一步沉淀到 `taxonomy_service`

### 涉及文件
- `app/routes/api_v1_posts.py`
- `app/services/taxonomy_service.py`
- 可能新增 route 文件

### 验收标准
- taxonomy 相关代码边界更清晰
- 不引入过度抽象
- 文章 route 不继续无序增长

---

## Task P2-3：补充 API 契约文档到新增实现
**状态：已完成**

### 目标
在方案 B 下，文档不能只维持旧内容，必须同步新增已实现边界。

### 需同步内容
- GIF 上传支持
- 作者资料新增字段
- 分类 / 标签前台公开接口（若新增）
- 默认 SQLite 行为与 PostgreSQL 可选启用方式

### 涉及文件
- `docs/api-v1-contract.md`
- `docs/v1-scope.md`
- `docs/extension-api-v1.md`（如涉及扩展说明更新）

### 验收标准
- 文档与实现再次对齐
- 不出现“实现已补齐但文档未更新”的二次偏差

---

# P3：可在上述任务后酌情推进

## Task P3-1：控制 `api_v1_posts.py` 与 `AdminPostsPage.jsx` 的复杂度继续增长

### 目标
在补齐文档能力后，避免核心胖文件成为长期技术债热点。

### 实施建议
- 不做纯审美式重构
- 仅在新增功能已明显造成理解成本上升时，再做最小拆分

### 候选拆分方向
- 后端：media / taxonomy / public posts 分离
- 前端：编辑表单 / 列表区 / 工具栏区组件化

### 验收标准
- 拆分后职责更清晰
- 没有引入额外状态管理复杂度

---

## 5. 推荐执行顺序

建议顺序如下：

1. `Task P1-1` 默认数据库统一到 SQLite
2. `Task P1-2` GIF 上传支持
3. `Task P1-3` 作者资料字段补齐
4. `Task P1-4` 前台分类 / 标签检索补齐
5. `Task P2-1` 统一后台鉴权
6. `Task P2-2` taxonomy 边界收口
7. `Task P2-3` 文档同步更新
8. `Task P3-1` 控制胖文件复杂度

---

## 6. 任务完成判定

当以下条件同时满足时，可认为“文档与实现边界统一（方案 B）”完成：

- 默认运行路径与文档一致（默认 SQLite）
- 图片上传格式与文档一致（含 GIF）
- 作者资料字段达到文档承诺的最小集合
- 前台分类 / 标签检索链路完整可用
- API 契约文档同步更新
- 核心测试覆盖新增能力

---

## 7. 备注

本清单是**可执行整改清单**，不是重构宣言。

执行时应持续遵守：

- 不做无关功能扩展
- 不借机大规模重构
- 不引入超出项目哲学的新复杂度
- 优先完成闭环，再考虑局部收口
