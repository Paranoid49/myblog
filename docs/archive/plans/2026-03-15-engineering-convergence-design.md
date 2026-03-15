# 工程收敛整改设计文档

日期：2026-03-15

## 1. 背景

以项目自身哲学（轻量、克制、可扩展）为评分标尺，由全新外部审计员对原始代码做了逐行审计。

**基线评分：7.58 / 10**

审计员一句话总结：
> 代码层面真正做到了"轻量克制"，但文档治理失控（文档比代码多一倍）、代码重复散落各处、扩展机制缺乏健壮性，暴露出项目在"治理自身复杂度"上的克制力不如其在"控制代码复杂度"上的克制力。

### 核心发现

| # | 问题 | 扣分维度 | 证据 |
|---|------|----------|------|
| 1 | 文档 10,000 行 vs 代码 4,295 行（2.33:1）；plans/ 19 文件 5,796 行在活跃目录；engineering/ 9 文件 2,091 行多份重叠 | 轻量 | docs/ |
| 2 | `_serialize_post` 后端重复 2 处、`formatDate` 前端重复 4 处、`renderAvatar` 重复 2 处、Create/Update Request 完全重复 | 克制 | posts.py:32 taxonomy.py:37 4 个 Public 页面 schemas/post.py:12-39 |
| 3 | Schema 定义位置不一致：3 个在 schemas/，2 个内联在路由 | 工程质量 | api_v1_author.py:16 api_v1_taxonomy.py:18 |
| 4 | post_service ↔ admin_post_service 隐式循环依赖 | 工程质量 | post_service.py:101 admin_post_service.py:5 |
| 5 | HookBus 吞异常无日志、ExtensionLoader 无容错、DatabaseProvider 无差异化 | 可扩展 | hook_bus.py:27 extension_loader.py:13 database_provider.py |
| 6 | CSS 单文件 1,091 行 | 前端 | theme.css |
| 7 | 前台页面高度同质（Category/Tag 几乎相同）、行内 style 散落 8 个文件 | 前端 | PublicCategoryPage.jsx PublicTagPage.jsx |
| 8 | 无 404 页面，path="*" 静默跳首页 | 前端 | App.jsx:58 |

### 整改原则

1. **改完后"轻量、克制、可扩展"更强，而非更弱**
2. **不引入新的抽象层、新的依赖、新的概念**
3. **消除复杂度，而非搬迁复杂度**
4. **有真实收益才改，不为规范而规范**

---

## 2. 整改清单

### P0：消除代码重复与职责越界（克制 + 工程质量）

这些是审计报告 Top 5 中的前 4 项，直接影响克制和工程质量两个维度。

---

#### P0-1 提取统一序列化模块

**问题**：`_serialize_post` 在 `api_v1_posts.py:32-45` 和 `api_v1_taxonomy.py:37-50` 逐行重复 14 行。`_serialize_category`、`_serialize_tag`、`_serialize_author` 散落在各路由文件中。

**方案**：新建 `app/schemas/serializers.py`，集中 `serialize_post`、`serialize_category`、`serialize_tag`、`serialize_author` 四个函数。三个 route 文件改为 import。

**改动**：新建 1 文件，修改 3 文件。

---

#### P0-2 db 写操作下沉到 service 层

**问题**：`db.add/commit/refresh` 和 `hook_bus.emit` 散落在 route 层（`api_v1_posts.py:48-60`、`api_v1_taxonomy.py:92-113`、`api_v1_author.py:65-71`）。Service 层只做纯构造/查询，不管持久化。

**方案**：
- `post_service.py` 增加 `save_new_post`、`save_post_update`、`save_publish`、`save_unpublish`（含 commit + hook）
- `taxonomy_service.py` 增加 `create_category`、`create_tag`
- 新建 `app/services/author_service.py` 增加 `update_author`
- Route 层删除所有 `db.add/commit/refresh` 和 `hook_bus.emit`
- `api_v1_media.py` 的 hook 就地保留并加注释（单一接口不值得建 service）

**改动**：修改 3 service + 3 route，新建 1 service。

---

#### P0-3 合并重复 Schema + 删除死代码 + 统一位置

**问题**：
- `AdminPostCreateRequest` 和 `AdminPostUpdateRequest`（`schemas/post.py:12-39`）字段与 validator 完全重复
- `schemas/auth.py` 的 `LoginForm` 全项目零引用
- `NameCreateRequest`（`api_v1_taxonomy.py:18`）、`AuthorProfileUpdateRequest`（`api_v1_author.py:16`）、`SetupRequest/SetupStatusResponse`（`api_v1_setup.py:29-45`）内联在路由文件中

**方案**：
- 合并为 `AdminPostWriteRequest`
- 删除 `schemas/auth.py`
- 新建 `schemas/taxonomy.py`、`schemas/author.py`、`schemas/setup.py`，将内联 Schema 移入

**改动**：删 1 文件，新建 3 文件，修改 4 文件。

---

#### P0-4 消除循环依赖 — 提取 slugify 为独立工具

**问题**：`post_service.py:101` 函数内延迟 import `admin_post_service`，而 `admin_post_service.py:5` import `post_service.slugify`。同时 `api_v1_media.py:13` 也跨层引用 `post_service.slugify`。

**方案**：新建 `app/utils/text.py`，将 `_normalize_chunks` 和 `slugify` 移入。所有引用方改为 `from app.utils.text import slugify`。函数内 import 提升到文件顶部。

**效果**：循环依赖消除，跨层工具引用消除，post_service 减少约 30 行。

**改动**：新建 1 文件，修改 4 文件 import。

---

#### P0-5 修复 `_get_post_or_404` 联合返回类型

**问题**：`api_v1_posts.py:63` 返回 `Post | JSONResponse`，导致 4 处 `isinstance` 检查重复。

**方案**：`post_service.py` 新增 `PostNotFoundError` 异常类 + `get_post_or_raise` 函数。Route 层改为 `try/except`。

**改动**：post_service.py 增加 ~10 行，api_v1_posts.py 修改 4 处。

---

#### P0-6 统一错误响应机制

**问题**：route 层用 `error_response()` 返回 JSONResponse，`deps.py:9` 手动构造 dict 作为 HTTPException.detail。两条并行路径。

**方案**：`api_response.py` 增加 `build_error_detail` 函数。`deps.py` 改用 `build_error_detail` 构造 UNAUTHORIZED_DETAIL。

**改动**：2 文件各改几行。

---

### P1：安全与正确性

---

#### P1-1 中间件硬编码错误码

**问题**：`main.py:71` 硬编码 `1001`，而 `error_codes.py` 已定义 `SITE_NOT_INITIALIZED = 1001`。

**方案**：import `SITE_NOT_INITIALIZED` + `build_error_detail`，替换硬编码 dict。

**改动**：`main.py` 增加 2 import，修改 1 行。

---

#### P1-2 setup route 不泄露内部异常

**问题**：`api_v1_setup.py:70,75` 将内部异常 `e` 拼入响应 message 返回前端。

**方案**：error_response 中不再拼接 `{e}`，改用 `logger.exception` 记录详情。

**改动**：增加 logging，修改 2 行 error_response。

---

#### P1-3 secret_key 默认值警告

**问题**：`config.py:14` 默认 `secret_key = "change-me"`，忘改则 session 可伪造。

**方案**：`main.py` 启动时检测默认值并 `logger.warning`。

**改动**：增加 3 行。

---

#### P1-4 HTTPException handler 扩大范围

**问题**：`main.py:38` 只拦截 `status_code == 401`，其他状态码带 dict detail 会格式不一致。

**方案**：去掉 401 限制，只要 `isinstance(exc.detail, dict)` 就统一返回。

**改动**：修改 2 行。

---

#### P1-5 Setup route 状态码常量化 + 加注释

**问题**：`api_v1_setup.py` 4 处裸数字状态码（400/500/409），`_create_session` 绕开 get_db 无注释说明。

**方案**：改为 `status.HTTP_xxx` 常量；`_create_session` 上方加注释。

**改动**：修改 4 处 + 增加 2 行注释。

---

### P2：扩展点修复（可扩展）

---

#### P2-1 HookBus 异常日志

**问题**：`hook_bus.py:27-28` 静默吞掉异常无日志。

**方案**：增加 `logger.exception`。

**改动**：3 行。

---

#### P2-2 ExtensionLoader 异常保护

**问题**：`extension_loader.py:13` 无 try/except，加载失败直接崩溃。

**方案**：包裹 try/except + `logger.exception`。

**改动**：4 行。

---

#### P2-3 简化 DatabaseProvider

**问题**：两个 provider 子类 `create_engine` 实现完全相同，继承体系无实际收益。`conftest.py:20` 自己加 `check_same_thread=False`。

**方案**：砍掉类继承，用 `create_app_engine` 函数替代。SQLite 加 `check_same_thread=False`，PostgreSQL 加 `pool_pre_ping=True`。

**改动**：重写 1 文件（41→15 行），修改 db.py + conftest.py + test_database_provider.py。

---

### P3：文档精简（轻量）

---

#### P3-1 精简 engineering/ 治理文档

**问题**：engineering/ 9 文件 2,091 行，管 1,422 行后端代码。多份文档内容重叠。

**方案**：合并为 3 份：
- `development-guide.md`：保留，合并 dev-fullstack-contract + manual-checks-governance 核心内容
- `engineering-guardrails.md`：新建，合并 evolution-guardrails + long-term-guardrails + change-review-checklist
- `core-regression-suite.md`：保留

归档到 `docs/archive/planning/`：philosophy-score-optimization-checklist、rule-authority-index、project-philosophy-9plus-optimization-todos。

**改动**：合并/删除 6 文件，归档 3 文件，新建 1 文件。

---

#### P3-2 归档 plans/ 历史文档

**问题**：plans/ 19 文件 5,796 行仍在活跃目录，项目自己的规则说应归档。

**方案**：整个 `docs/plans/` 移入 `docs/archive/plans/`。

**改动**：移动 1 目录。

---

#### P3-3 合并 product-overview 和 v1-scope

**问题**：V1 范围在 product-overview.md 和 v1-scope.md 被定义两次。

**方案**：删除 v1-scope.md（product-overview 已完整包含其内容）。

**改动**：删 1 文件，修改引用。

---

#### P3-4 API 文档补齐 + CLAUDE.md 修正

**问题**：api-v1-contract.md 缺 3 个已实现端点（编辑/导入/导出）。CLAUDE.md 说"内存数据库"实际是文件数据库。

**方案**：补齐端点定义；修正表述。

**改动**：2 文件小改。

---

### P4：前端改善

---

#### P4-1 提取 formatDate 公共工具

**问题**：`formatDate` 在 4 个 Public 页面完全重复。

**方案**：新建 `frontend/src/shared/utils/format.js`，提取 `formatDate`。4 个页面改为 import。

**改动**：新建 1 文件，修改 4 文件。

---

#### P4-2 拆分 theme.css

**问题**：1,091 行单文件，既是变量又是组件又是页面又是响应式。

**方案**：拆为 `variables.css`、`base.css`、`components.css`、`admin.css`、`markdown.css`。`theme.css` 变为纯 import 入口。

**改动**：拆 1 文件为 5+1 文件。

---

#### P4-3 增加 404 页面

**问题**：`App.jsx:58` path="*" 静默跳首页。

**方案**：新建 `NotFoundPage.jsx`，App.jsx 改为渲染 404 页面。

**改动**：新建 1 文件，修改 1 文件。

---

#### P4-4 合并 Category/Tag 页面为共享组件

**问题**：`PublicCategoryPage.jsx` 和 `PublicTagPage.jsx` 52 行中有 45+ 行结构一致。

**方案**：新建 `PublicTaxonomyPage.jsx` 共享组件，接收 `type`（category/tag）参数。两个页面变为薄包装。

**改动**：新建 1 文件，修改 2 文件。

---

## 3. 不做清单

| 问题 | 不改原因 |
|---|---|
| 前台 style={{}} 行内样式 | 分散在 8 个文件中，改动量大但收益低。等有视觉重构需求时统一处理。 |
| renderAvatar 重复 | 前台和后台的 avatar 渲染逻辑虽然相似，但上下文不同（一个展示一个编辑预览），强行合并可能引入不必要耦合。 |
| response_model=ApiResponse 形同虚设 | 引入 Pydantic 响应模型做运行时校验会增加复杂度。当前"手动序列化 + 统一 serializer"已够用。 |
| HookBus 无 unsubscribe / 不支持异步 | 当前无真实消费者，加能力 = 加复杂度但无收益。 |
| 前端缺少组件测试 | 当前前端体量 2,873 行（含 CSS），引入 React Testing Library + jsdom 的工具链成本不匹配。 |
| POST 用于更新而非 PUT/PATCH | 功能正确，改动影响前后端多处调用。 |
| 缺少加载骨架 / Spinner | 属于 UX 打磨，不影响功能正确性。 |

---

## 4. 执行顺序

```
阶段一（P0）：消除代码重复与职责越界 ✅ 2026-03-15 完成，173 passed
  P0-1 提取统一序列化模块 ✅
  P0-2 db 写操作下沉到 service 层 ✅
  P0-3 合并重复 Schema + 删除死代码 + 统一位置 ✅
  P0-4 消除循环依赖 — 提取 slugify ✅
  P0-5 修复 _get_post_or_404 ✅
  P0-6 统一错误响应机制 ✅

阶段二（P1）：安全与正确性 ✅ 2026-03-15 完成
  P1-1 中间件硬编码错误码 ✅
  P1-2 setup route 不泄露内部异常 ✅
  P1-3 secret_key 默认值警告 ✅
  P1-4 HTTPException handler 扩大范围 ✅
  P1-5 Setup route 状态码常量化 + 加注释 ✅

阶段三（P2）：扩展点修复 ✅ 2026-03-15 完成
  P2-1 HookBus 异常日志 ✅
  P2-2 ExtensionLoader 异常保护 ✅
  P2-3 简化 DatabaseProvider ✅

阶段四（P3）：文档精简 ✅ 2026-03-15 完成
  P3-1 精简 engineering/ 治理文档 ✅
  P3-2 归档 plans/ 历史文档 ✅
  P3-3 合并 product-overview 和 v1-scope ✅
  P3-4 API 文档补齐 + CLAUDE.md 修正 ✅

阶段五（P4）：前端改善 ✅ 2026-03-15 完成
  P4-1 提取 formatDate 公共工具 ✅
  P4-2 拆分 theme.css ✅
  P4-3 增加 404 页面 ✅
  P4-4 合并 Category/Tag 页面 ✅

全部阶段测试：171 passed，0 failed
```

每阶段完成后跑 `pytest`，确认无回归。

---

## 5. 预期效果

| 维度 | 基线 | 目标 | 关键整改 |
|---|---|---|---|
| 轻量 | 7.5 | 9.5 | 文档从 10,000→~2,500 行，plans/ 归档，CSS 拆分 |
| 克制 | 8.0 | 9.5 | 消除全部代码重复，合并 Schema，Category/Tag 页面合并 |
| 可扩展 | 6.5 | 8.5 | 扩展点加日志/保护/差异化，DatabaseProvider 简化 |
| 工程质量 | 8.0 | 9.5 | 序列化统一、Schema 位置统一、循环依赖消除、错误处理统一 |
| 测试 | 8.5 | 8.5 | 不变（已足够好） |
| 前端 | 7.0 | 8.5 | formatDate 去重、CSS 拆分、404 页面、页面去重 |

**加权总分：7.58 → 9.1**

剩余差距来自：审计员可能发现的新问题、以及不做清单中有意保留的问题。
