# 技术总监评审 10 分整改计划

> **基准评分**：8.06 / 10（B+）
> **目标评分**：10.0 / 10（S）
> **约束前提**：所有整改必须遵守项目哲学——**轻量、克制、可扩展**，拒绝引入不必要的复杂度
> **制定日期**：2026-03-17
> **完成日期**：2026-03-17
> **评审方法**：3 路并行代码审查 + 逐项代码验证 + 哲学合规自检
> **首轮整改结果**：✅ 17/17 项全部完成（183 passed, 0 failed, 覆盖率 94.58%）
> **二轮独立评审**：8.78 / 10（A-），较首轮基准 +0.72

---

## 评分修正说明

初始审查后经逐行代码验证，发现以下问题**已解决**，需从扣分项中移除：

| 原扣分项 | 实际状态 | 验证依据 |
|----------|----------|----------|
| N+1 查询隐患 | ✅ 已修复 | `post_service.py` 已全面使用 `selectinload(Post.category, Post.tags)` |
| 前端测试完全缺失 | ✅ 已有 15 个测试文件 | 覆盖 LoginPage、SetupPage、MarkdownRenderer、API Client 等核心组件 |
| CI/CD pipeline 缺失 | ✅ 已完整 | `.github/workflows/ci.yml` 含后端测试、前端 lint+测试、后端 lint、安全审计 4 个 job |
| 无 ESLint/Prettier | ✅ 已配置 | `package.json` 含 eslint v9.0、prettier v3.4 |

**修正后基准评分**：8.65 / 10

---

## 整改清单（按优先级排序）

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### P0 — 必须修复（安全 / 数据完整性）
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#### 1. ✅ 分类删除批量更新替代内存遍历

- **当前问题**：`taxonomy_service.py:107-108` 使用 `for post in category.posts` 逐条修改 `category_id`，大数据量下导致 N 条 UPDATE 语句、长事务、潜在 OOM
- **影响维度**：性能 +0.3 / 代码质量 +0.1
- **整改方案**：改用 `sa_update(Post).where(Post.category_id == category.id).values(category_id=default_id)` 批量更新
- **完成状态**：✅ 已完成 — `taxonomy_service.py` 已修改

---

#### 2. ✅ SiteSettings 单行约束

- **当前问题**：`site_settings.py` 模型无数据库层面的单行约束，若代码 bug 导致插入多行，`scalar_one_or_none()` 会抛异常
- **影响维度**：架构 +0.1
- **整改方案**：在 `initialize_site` 中增加防御性检查（不改模型层，保持迁移兼容）
- **完成状态**：✅ 已完成 — `setup_service.py` 已修改

---

#### 3. ✅ 密码确认校验

- **当前问题**：`SetupRequest` 定义了 `confirm_password` 字段
- **影响维度**：安全性 +0.2
- **整改方案**：经验证，路由层 `api_v1_setup.py:63-64` **已有** `AppError("password_mismatch", ...)` 业务层校验（返回 400 + 错误码 2001）。最终方案：**保留路由层业务校验**，不在 Schema 层重复校验（避免 Pydantic 的 422 破坏统一错误码约定）
- **完成状态**：✅ 已完成 — 确认路由层校验完备，Schema 层保持简洁

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### P1 — 应该修复（工程健壮性）
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#### 4. ✅ 依赖版本精确锁定

- **当前问题**：`requirements.txt` 使用 `>=` 范围约束（如 `fastapi>=0.115`），生产环境部署时可能安装到不兼容的新版本
- **影响维度**：工程基建 +0.3
- **整改方案**：使用 `pip-compile` 生成 `requirements.lock` + `requirements-dev.lock`
- **完成状态**：✅ 已完成 — 两个 lock 文件已生成，pip-tools 已卸载

---

#### 5. ✅ Alembic 连接串硬编码清理

- **当前问题**：`alembic.ini` 中硬编码了 PostgreSQL 默认凭据
- **影响维度**：工程基建 +0.1 / 安全性 +0.1
- **整改方案**：替换为安全占位符 `sqlite:///./blog.db`
- **完成状态**：✅ 已完成 — `alembic.ini` 已修改

---

#### 6. ✅ Email 校验增强

- **当前问题**：`author.py` 仅检查 `@` 符号
- **影响维度**：安全性 +0.1
- **整改方案**：使用标准库 `re` 正则校验
- **完成状态**：✅ 已完成 — `author.py` 已增加 `_EMAIL_RE` 正则

---

#### 7. ✅ Schema 验证器 DRY 重构

- **当前问题**：`_must_not_be_blank` 在 4 个 Schema 文件中重复定义
- **影响维度**：代码质量 +0.2
- **整改方案**：新建 `app/schemas/validators.py` 提供公共 `not_blank()` 函数
- **完成状态**：✅ 已完成 — 4 个 Schema 文件已统一调用 `not_blank()`

---

#### 8. ✅ 分类标签路由 get_or_404 模式统一

- **当前问题**：`api_v1_admin_taxonomy.py` 手动 `db.get() + if not` 检查
- **影响维度**：代码质量 +0.1
- **整改方案**：在 `deps.py` 增加 `get_category_or_404` / `get_tag_or_404` 依赖函数
- **完成状态**：✅ 已完成 — 4 个路由函数已改用 Depends 注入

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### P2 — 建议改进（锦上添花）
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#### 9. ✅ 中间件 DB Session 注释

- **当前问题**：`main.py` 中间件 Session 独立性缺少设计意图说明
- **影响维度**：架构 +0.1
- **完成状态**：✅ 已完成 — 增加了 3 行设计意图注释

---

#### 10. ✅ Feed 无锁缓存优化

- **当前问题**：`feed.py` 使用 `threading.Lock()` 全局锁
- **影响维度**：性能 +0.1
- **完成状态**：✅ 已完成 — 移除 `threading` 导入和锁，简化为无锁缓存

---

#### 11. ✅ Slug 竞态条件防御

- **当前问题**：`post_service.py` 的 `while _slug_exists` 是 Check-then-Act 竞态
- **影响维度**：架构 +0.1
- **完成状态**：✅ 已完成 — `save_new_post` 增加 `IntegrityError` 捕获和时间戳后缀重试

---

#### 12. ✅ Taxonomy 路由 HTTP 方法规范化

- **当前问题**：更新用 `POST /{id}`，删除用 `POST /{id}/delete`
- **影响维度**：代码质量 +0.1
- **完成状态**：✅ 已完成 — 后端 PUT/DELETE + 前端同步 + 测试同步

---

#### 13. ✅ 归档文档索引

- **当前问题**：`docs/archive/plans/` 下 20+ 个文件缺少索引
- **影响维度**：文档质量 +0.1
- **完成状态**：✅ 已完成 — 创建 `docs/archive/README.md` 含 29 个文件的索引表

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### 自检修复 — 哲学合规自检中发现的问题
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#### 14. ✅ deps.py 导入位置 E402 修复

- **发现阶段**：哲学合规自检
- **问题**：`deps.py` 第 31-33 行新增导入放在了函数定义之后，ruff 报告 E402（Module level import not at top of file）+ I001（Import block is un-sorted）
- **违反规则**：CI 管线 `ruff check app/` 会失败
- **修复方案**：将新增导入合并到文件顶部，与已有导入统一排序
- **完成状态**：✅ 已修复 — `deps.py` 导入块已整理到文件顶部

---

#### 15. ✅ API 契约文档同步更新

- **发现阶段**：哲学合规自检
- **问题**：`#12 路由 HTTP 方法规范化` 将 POST 改为 PUT/DELETE，但 `docs/api/api-v1-contract.md` 第 241-266 行未同步更新
- **违反规则**：工程守则 §5 — "改动是否同步更新了对应真相文档"
- **修复方案**：更新 api-v1-contract.md 中 4 个接口定义（7.3/7.4/7.6/7.7）
- **完成状态**：✅ 已修复 — 契约文档已与实现对齐

---

#### 16. ✅ taxonomy_service.py 导入排序 I001 修复

- **发现阶段**：哲学合规自检
- **问题**：新增 `update as sa_update` 导入后导入块未正确排序
- **修复方案**：`ruff check --fix` 自动修复
- **完成状态**：✅ 已修复

---

#### 17. ✅ post_service.py 行长度 E501 修复

- **发现阶段**：哲学合规自检
- **问题**：第 142 行 `base = select(Post).options(...)...` 超过 120 字符
- **修复方案**：拆分为多行括号表达式
- **完成状态**：✅ 已修复

---

## 整改收益汇总

| 序号 | 整改项 | 优先级 | 涉及维度 | 预期增分 | 状态 |
|------|--------|--------|----------|----------|------|
| 1 | 分类删除批量更新 | P0 | 性能 + 质量 | +0.4 | ✅ |
| 2 | SiteSettings 单行防御 | P0 | 架构 | +0.1 | ✅ |
| 3 | 密码确认校验 | P0 | 安全 | +0.2 | ✅ |
| 4 | 依赖版本锁定 | P1 | 工程基建 | +0.3 | ✅ |
| 5 | Alembic 连接串清理 | P1 | 基建 + 安全 | +0.2 | ✅ |
| 6 | Email 校验增强 | P1 | 安全 | +0.1 | ✅ |
| 7 | Schema 验证器 DRY | P1 | 代码质量 | +0.2 | ✅ |
| 8 | get_or_404 统一 | P1 | 代码质量 | +0.1 | ✅ |
| 9 | 中间件 Session 注释 | P2 | 架构 | +0.1 | ✅ |
| 10 | Feed 无锁缓存 | P2 | 性能 | +0.1 | ✅ |
| 11 | Slug 竞态防御 | P2 | 架构 | +0.1 | ✅ |
| 12 | 路由 HTTP 方法规范 | P2 | 代码质量 | +0.1 | ✅ |
| 13 | 归档文档索引 | P2 | 文档 | +0.1 | ✅ |
| 14 | deps.py 导入排序 | 自检 | 工程规范 | — | ✅ |
| 15 | API 契约文档同步 | 自检 | 文档一致性 | — | ✅ |
| 16 | taxonomy_service 导入排序 | 自检 | 工程规范 | — | ✅ |
| 17 | post_service 行长度 | 自检 | 工程规范 | — | ✅ |
| | | | **合计** | **+2.1** | **17/17** |

---

## 验证结果

```
183 passed, 2 skipped in 27.44s
覆盖率：94.58%（要求 ≥ 80%）
ruff check app/：0 errors（排除 1 个历史遗留 E501）
```

---

## 哲学合规自检结论

| 哲学原则 | 判定 |
|----------|------|
| 能不引入复杂度就不引入 | ✅ 零新运行时依赖 |
| 满足生产要求的最小集合 | ✅ 所有修改修复已有问题，未新增功能 |
| 核心极简，扩展开放 | ✅ 未改动扩展点 |
| 默认单体/SQLite/Session/无缓存 | ✅ 默认基线未破坏 |
| 统一响应结构 {code,message,data} | ✅ 密码校验保留路由层 400+错误码 |
| 代码注释和文档使用中文 | ✅ 所有新增注释为中文 |
| 禁止非查询 git 操作 | ✅ 全程未执行 git 写操作 |
| 改动同步更新真相文档 | ✅ api-v1-contract.md 已同步 |
| 任务完成后释放资源 | ✅ pip-tools 已卸载，团队已清理 |

---

## 不整改项（哲学审慎排除）

| 项目 | 排除原因 |
|------|----------|
| 引入 TypeScript | 个人博客前端复杂度有限，TS 的收益不足以覆盖引入成本，违反"克制"原则 |
| 服务端 Session 存储 | 当前 Cookie-based Session 完全满足个人博客需求，引入 Redis 违反"轻量"原则 |
| 密码要求特殊字符 | 8 位字母+数字已满足个人博客安全需求，过严策略降低用户体验 |
| 分布式锁解决 Slug 竞态 | 个人博客场景并发极低，数据库唯一约束已是足够的兜底方案 |
| 多作者权限体系 | 当前为单管理员设计，引入 RBAC 违反"功能恰好够用"原则 |
| 文件缓存/Redis 缓存 Feed | 内存缓存 + 5 分钟过期完全满足需求，引入外部缓存违反"轻量"原则 |

---

## 二轮独立评审发现的改进空间（8.78 → 9.5+）

> 以下 4 项由第二轮全新外部视角独立评审发现，均为"锦上添花"级改进。
> 已于 2026-03-17 当日全部实施完成。183 passed, 0 failed, 覆盖率 94.71%。

### P1 — 应该修复（一致性 / 可维护性）

#### 18. ✅ 文章管理路由 HTTP 方法规范化

- **事实依据**：`api_v1_admin_taxonomy.py` 已使用 PUT/DELETE，但 `api_v1_admin_posts.py` 的更新（`POST /{post_id}`）和删除（`POST /{post_id}/delete`）仍为 POST，两个管理端路由风格不统一
- **影响维度**：架构一致性 +0.3
- **整改方案**：
  - `POST /admin/posts/{post_id}` → `PUT /admin/posts/{post_id}`
  - `POST /admin/posts/{post_id}/delete` → `DELETE /admin/posts/{post_id}`
  - 同步修改前端 API 调用、后端测试、`api-v1-contract.md` 第 6 节
- **复杂度**：中（前后端联动 + 文档同步）
- **哲学合规**：遵循 HTTP 标准语义，与 taxonomy 路由对齐
- **状态**：✅ 已完成 — 后端 PUT/DELETE + 前端同步 + 测试同步 + api-v1-contract.md 第 6 节已更新

---

#### 19. ✅ 序列化层重构：手动映射 → Pydantic from_attributes

- **事实依据**：`app/schemas/serializers.py` 通过手动字典映射将 ORM 对象转为 JSON，当模型字段增减时需手动同步，存在遗漏风险
- **影响维度**：代码质量 +0.2
- **整改方案**：
  - 为每个模型定义 Pydantic 响应 Schema（如 `PostResponse`），设置 `model_config = ConfigDict(from_attributes=True)`
  - 在路由层用 `PostResponse.model_validate(post)` 替代 `serialize_post(post)`
  - 删除 `serializers.py` 中的手动映射函数
- **复杂度**：中（涉及多个 Schema 和路由文件）
- **哲学合规**：利用 FastAPI/Pydantic 原生能力，减少自维护代码量，符合"克制"原则
- **注意**：需确保嵌套关系（如 Post 含 category、tags）的序列化行为一致
- **状态**：✅ 已完成 — 新增 TagResponse/CategoryResponse/PostResponse/AuthorResponse 四个 Pydantic 模型，serialize_* 函数签名不变，内部改用 model_validate + model_dump

---

### P2 — 建议改进（锦上添花）

#### 20. ✅ 标签删除批量解除关联

- **事实依据**：`taxonomy_service.py:127` 使用 `tag.posts = []` ORM 级联清空关联，对于大量关联文章会生成逐条 DELETE 语句
- **影响维度**：性能 +0.1
- **整改方案**：
```python
# 修改前
def delete_tag(db: Session, tag: Tag) -> None:
    tag.posts = []  # 逐条 DELETE
    db.delete(tag)
    db.commit()

# 修改后
from app.models.post import post_tags

def delete_tag(db: Session, tag: Tag) -> None:
    db.execute(delete(post_tags).where(post_tags.c.tag_id == tag.id))
    db.delete(tag)
    db.commit()
```
- **复杂度**：低（3 行改动）
- **哲学合规**：与 `delete_category` 的批量更新模式保持一致
- **状态**：✅ 已完成 — 改用 `sa_delete(post_tags).where(...)` 批量删除关联

---

#### 21. ✅ 文章路由 get_or_404 Depends 模式统一

- **事实依据**：`api_v1_admin_posts.py:33-38` 已定义本地 `get_post_or_404` 依赖函数并在所有写接口中使用 `Depends(get_post_or_404)`，与 taxonomy 的模式一致
- **影响维度**：代码质量 +0.1
- **状态**：✅ 已确认存在 — 无需修改，admin_posts.py 已独立实现该模式

---

### 三轮评审修复 — 新发现的实质性问题

#### 22. ✅ get_post_or_raise 缺少 selectinload（N+1 问题）

- **发现阶段**：第三轮独立评审
- **事实依据**：`post_service.py:168-173` 的 `get_post_or_raise` 使用 `db.get(Post, post_id)` 无预加载，后续 `serialize_post` 访问 `post.category` 和 `post.tags` 时触发懒加载（2 次额外 SQL），影响 PUT/DELETE/publish/unpublish 4 个管理端点
- **影响维度**：性能 +0.5
- **修复方案**：改用 `select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.id == post_id)`
- **状态**：✅ 已修复 — 183 passed, 覆盖率 94.71%

---

### 四轮评审修复 — 深度审查发现的问题（8.10 → 9.0+）

> 第四轮独立评审深入到 Schema 字段与数据库列长度对齐、X-Forwarded-For 信任链、
> CI 配置一致性等细节层面，共发现 15 项改进点，已全部实施。
> 最终结果：188 passed, 0 failed, 覆盖率 94.43%, ruff 0 errors。

#### P0 安全修复

- 23. ✅ 限流 key 增加 username 维度 — `api_v1_auth.py` 限流 key 从 `ip` 改为 `ip:username`，防止伪造 X-Forwarded-For 绕过
- 24. ✅ Schema max_length 与数据库对齐 — `setup.py` 增加 blog_title(200)/username(64)，`author.py` 增加 name(100)/email(200)/avatar(500)/link(500)

#### P1 工程健壮性

- 25. ✅ pyproject target-version 修正 — `py312` → `py311`，与 `requires-python>=3.11` 对齐
- 26. ✅ CI ruff 版本固定 — `pip install ruff` → `pip install -r requirements-dev.lock`
- 27. ✅ CI 增加前端构建验证 — frontend-lint job 增加 `npm run build` 步骤
- 28. ✅ E501 行长度修复 — `api_v1_taxonomy.py:38` 函数参数拆分为多行
- 29. ✅ 密码校验 strip 一致性 — `setup.py` 的 `_password_complexity` 返回 strip 后的值

#### P2 测试补全

- 30. ✅ 分类更新重名冲突测试 — `test_update_category_rejects_duplicate_name`
- 31. ✅ 标签更新重名冲突测试 — `test_update_tag_rejects_duplicate_name`
- 32. ✅ 标签删除后关联验证测试 — `test_delete_tag_removes_association_from_posts`
- 33. ✅ 超长标题边界测试 — `test_create_post_rejects_title_exceeding_max_length`
- 34. ✅ 超长分类名边界测试 — `test_create_category_rejects_name_exceeding_max_length`

#### P3 锦上添花

- 35. ✅ get_post_or_404 迁移到 deps.py — 与 get_category_or_404/get_tag_or_404 统一放置
- 36. ✅ feed 缓存大小限制 — 最多 10 个条目，超限清除最旧的
- 37. conftest 增加限流器重置 — 避免测试间累积触发 429

---

### 五轮评审修复 — 深度独立审查发现的问题（8.7 → 9.0+）

> 第五轮由全新外部视角独立审查（75 次文件读取，覆盖全部 47 个源文件），
> 深入到 inspect 调用开销、冗余异常类、slug 碰撞概率、部署配置提示、
> API 契约完整性、前端 CI 覆盖率等细节层面。共发现 6 项改进点，已全部实施。
> 最终结果：188 passed, 0 failed, 覆盖率 94.70%, ruff 0 errors。

#### 性能优化

- 38. ✅ `get_site_settings` 跳过冗余 inspect — 初始化完成后（`_initialized_cache is True`）直接查询 SiteSettings，不再每次调用 `_has_required_tables(db)` 执行 `inspect(db.bind)`

#### 代码清理

- 39. ✅ 删除冗余 `PostNotFoundError` + `get_post_or_raise` — 路由层已统一使用 `deps.py` 中的 `get_post_or_404`（基于 `NotFoundError`），`post_service.py` 中的 `PostNotFoundError` 异常类和 `get_post_or_raise` 函数已无调用方，属冗余代码
- 40. ✅ slug 冲突 fallback 改用 uuid — `save_new_post` 的 `IntegrityError` 回退从 `time()%10000`（可能碰撞）改为 `uuid4().hex[:8]`（碰撞概率 ~1/40亿）

#### 部署与文档

- 41. ✅ docker-compose 添加 SECRET_KEY 配置提示 — 在 environment 区域增加注释说明必须在 `.env` 中配置 SECRET_KEY
- 42. ✅ API 契约补充 Setup 接口 — `api-v1-contract.md` 新增 §9.5 初始化接口，包含 `GET /setup/status` 和 `POST /setup` 的完整字段说明、错误码

#### CI 强化

- 43. ✅ 前端 CI 启用覆盖率检查 — `ci.yml` 中 `npm test` 改为 `npm run test:coverage`
