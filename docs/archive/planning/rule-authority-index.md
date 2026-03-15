# 关键规则权威来源索引

日期：2026-03-14

## 目标

本索引是“某类规则该去哪看、去哪改”的收口入口，不替代日常开发入口与改动前检查：

- 日常开发先看 `docs/engineering/development-guide.md`
- 改动前边界判断先看 `docs/engineering/change-review-checklist.md`
- 长期治理约束再看 `docs/engineering/long-term-guardrails.md`

本索引用于快速回答：

> 某类规则当前应该去哪里看、去哪里改？

优先减少“同一事实多处定义”与“靠记忆找权威文件”的情况。

---

## 1. 错误码

### 权威来源
- 代码：`app/core/error_codes.py`
- 文档：`docs/api/api-v1-contract.md`

### 说明
- 业务错误码常量以 `app/core/error_codes.py` 为准
- API 文档负责说明语义，不再充当数字定义的唯一来源

---

## 2. 初始化状态判定与 setup 错误码

### 权威来源
- 初始化判定代码：`app/services/setup_service.py`
- setup 路由入口：`app/routes/api_v1_setup.py`
- setup 错误码：`app/core/error_codes.py`
- 文档：`docs/architecture/architecture-and-boundaries.md`、`docs/api/api-v1-contract.md`

### 说明
- 是否已初始化，以 `setup_service.py` 中的真实判定逻辑为准
- setup 接口的响应结构应复用 `app/schemas/api_response.py`
- setup 相关错误码常量以 `app/core/error_codes.py` 为准
- 文档只解释规则，不重复定义实现细节

---

## 3. API 响应结构

### 权威来源
- 代码：`app/schemas/api_response.py`
- 文档：`docs/api/api-v1-contract.md`

### 说明
- 通用 `code / message / data` 响应结构以 `app/schemas/api_response.py` 为准
- 其他 route 不应长期维护各自平行实现

---

## 4. 图片上传限制

### 权威来源
- 代码：`app/routes/api_v1_media.py`
  - `IMAGE_MAX_BYTES`
  - `IMAGE_EXTENSION_BY_TYPE`
  - `IMAGE_RULES`
- 文档：`docs/api/api-and-extension-overview.md`

### 说明
- 支持 MIME 类型、扩展名映射、大小限制以 `api_v1_media.py` 为准
- 文档只做说明与索引

---

## 5. 扩展边界

### 权威来源
- 文档：
  - `docs/api/extension-api-v1.md`
  - `docs/architecture/lightweight-extension-boundaries.md`
- 代码：
  - `app/core/database_provider.py`
  - `app/core/extension_loader.py`
  - `app/core/hook_bus.py`
  - `frontend/src/shared/theme/ThemeProvider.jsx`

### 说明
- 边界先看文档，落地细节再看代码
- 若文档与实现冲突，以当前真相文档 + 当前代码联合核对

---

## 6. 开发入口

### 权威来源
- 代码：
  - `scripts/start_blog.py`
  - `scripts/start_fullstack.py`
  - `scripts/run_dev.py`（历史兼容）
- 文档：
  - `docs/engineering/development-guide.md`
  - `docs/engineering/dev-fullstack-contract.md`

### 说明
- 全栈联调默认入口：`start_fullstack.py`
- 仅后端开发默认入口：`start_blog.py`
- `run_dev.py` 不再作为主文档入口推荐

---

## 7. SiteSettings 与作者资料边界

### 权威来源
- 代码：
  - `app/models/site_settings.py`
  - `app/routes/api_v1_author.py`
  - `app/routes/api_v1_setup.py`
- 文档：
  - `docs/architecture/architecture-and-boundaries.md`
  - `docs/engineering/long-term-guardrails.md`

### 说明
- `SiteSettings` 只承载站点级基础设置与作者基础资料最小集合
- setup 与 author 修改同一份站点设置时，以 `site_settings.py` 的字段边界为准
- 若新增字段不属于站点基础设置，默认不应先塞进 `SiteSettings`

---

## 8. taxonomy 公开查询与创建规则

### 权威来源
- 代码：
  - `app/routes/api_v1_taxonomy.py`
  - `app/services/taxonomy_service.py`
  - `app/services/admin_post_service.py`
  - `app/services/post_service.py`（slug 规则）
- 文档：
  - `docs/api/api-v1-contract.md`
  - `docs/engineering/long-term-guardrails.md`

### 说明
- taxonomy 公开查询、后台创建与 slug 命名规则应优先回到上述位置核对
- 分类/标签创建冲突、公开查询返回结构、slug 生成不要在多处各自解释一套
- 若规则发生变化，优先更新权威来源，而不是补第二份平行说明

---

## 9. 当前真相文档入口

### 权威来源
- `docs/README.md`

### 说明
- 当不确定应该先读哪份文档时，先看 `docs/README.md`
- 真相文档、规划记录、历史档案的分层也以这里为总入口
