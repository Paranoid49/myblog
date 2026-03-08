# Setup 自动创建 PostgreSQL 数据库设计

**日期：** 2026-03-08
**主题：** 首次初始化向导支持自动创建 PostgreSQL 目标数据库

## 目标

让博客在 `DATABASE_URL` 指向的 PostgreSQL 目标数据库尚不存在时，仍然能够通过 `/setup` 完成初始化。用户提交安装表单后，系统应先自动创建目标数据库，再执行 Alembic migration、初始化站点数据，并自动登录后台。

## 范围

本设计仅覆盖 setup 场景下的数据库自动创建：

- 仅支持 PostgreSQL
- 仅在 `/setup` 初始化流程中触发自动建库
- 使用现有 `DATABASE_URL` 中的用户名、密码、主机和端口
- 目标数据库不存在时，临时连接维护库 `postgres` 执行存在性检查和 `CREATE DATABASE`
- 建库成功后继续执行现有 migration 与初始化数据写入流程

明确不做：

- MySQL / SQLite / 其他数据库的自动建库
- 应用启动时的全局自动建库
- 通用数据库管理框架
- 第二套数据库管理员配置
- 对其他业务路由做“无数据库也能运行”的泛化改造

## 方案选择

### 选定方案
采用**轻量 database bootstrap service + setup 路由编排**的折中方案：

- 新增 `app/services/database_bootstrap_service.py`
- service 只负责 PostgreSQL 目标数据库存在性保障
- setup 路由先执行 bootstrap，再执行 migration 和初始化数据写入
- 保持 `migration_service` 与 `setup_service` 职责单一

### 选择原因

相比把建库逻辑塞进应用启动流程或 Alembic 封装里，这个方案的收益是：

- 只影响 setup 初始化链路，blast radius 最小
- 不给普通请求增加隐式副作用
- 避免把连接细节耦合进业务初始化逻辑
- 后续测试边界更清楚

### 未选方案

- **应用启动阶段自动建库**：副作用过大，普通启动也会尝试建库，不适合当前个人博客需求
- **把建库逻辑塞进 `migration_service`**：会混淆“建数据库”和“升级表结构”两层职责
- **做通用 database manager 框架**：当前需求很明确，过度设计

## 架构设计

### 现状问题
当前 `app/routes/setup.py` 在 `GET /setup` 和 `POST /setup` 都通过 `Depends(get_db)` 获取目标库 session。`app/core/db.py` 的 `SessionLocal` 绑定到 `settings.database_url` 指向的目标数据库。

这意味着：

- 目标数据库不存在时，setup 路由本身就无法正常进入初始化逻辑
- 现有 `upgrade_database()` 也只能对已存在的数据库执行 migration

### 新模块边界

#### `app/services/database_bootstrap_service.py`
职责限定为：

1. 解析 `settings.database_url`
2. 验证当前数据库方言是否为 PostgreSQL
3. 构造维护库连接 URL（数据库名改为 `postgres`）
4. 检查目标数据库是否已存在
5. 若不存在则执行 `CREATE DATABASE`

不负责：

- Alembic migration
- ORM session 生命周期管理
- `SiteSettings` / `User` 业务数据初始化

#### `app/services/migration_service.py`
保持当前职责：

- 仅负责对**已经存在的目标数据库**执行 `alembic upgrade head`

#### `app/services/setup_service.py`
保持当前职责：

- 判断系统是否已初始化
- 创建 `SiteSettings`
- 创建管理员用户
- 拒绝重复初始化

#### `app/routes/setup.py`
调整为 setup 的总编排器：

- 先处理“数据库可能还不存在”的 bootstrap 阶段
- 再处理 migration 和站点初始化阶段
- 在需要目标库 session 时手动创建并释放 session

## 连接设计

### 为什么要连接维护库 `postgres`
PostgreSQL 连接必须落到一个**已经存在的数据库**上。当前 `DATABASE_URL` 里的目标库例如 `myblog` 若尚不存在，就不能直接连接它并执行 `CREATE DATABASE myblog`。

因此必须先临时连接一个已存在的数据库，通常是 `postgres`：

- 原始 URL：`postgresql+psycopg://postgres:123456@localhost:5432/myblog`
- 维护库 URL：`postgresql+psycopg://postgres:123456@localhost:5432/postgres`

在维护库连接上完成：

- 检查 `myblog` 是否存在
- 若不存在，执行 `CREATE DATABASE myblog`

### 与现有 `app/core/db.py` 的关系
不推翻现有 `engine` / `SessionLocal` 设计。

策略是：

- `app/core/db.py` 继续服务正常业务请求
- bootstrap service 内部临时创建维护库 engine，仅用于 setup 自动建库
- setup route 在建库和 migration 完成后，再创建目标库 session 执行业务初始化

这样可以把新需求隔离在 setup 专用路径内。

## 请求流设计

### `GET /setup`
目标：即使目标数据库不存在，也能正常打开初始化页面。

建议流程：

1. 先判断目标数据库是否存在
2. 若不存在：直接返回 setup 页面
3. 若存在：再创建目标库 session
4. 用 `is_initialized(db)` 判断是否已初始化
5. 已初始化则重定向 `/`
6. 未初始化则返回 setup 页面

### `POST /setup`
目标：一键完成建库、建表、初始化和自动登录。

建议流程：

1. 校验表单
   - `blog_title` 非空
   - `username` 非空
   - `password` 非空
   - `confirm_password == password`
2. 调用 `ensure_database_exists()`
3. 调用 `upgrade_database()`
4. 手动创建目标库 session
5. 调用 `initialize_site(...)`
6. 写入 `request.session["user_id"]`
7. 重定向到 `/admin/posts`

### 关键实现约束
`POST /setup` 不能继续使用 `db: Session = Depends(get_db)`，因为 FastAPI 会在路由函数执行前就尝试连接目标数据库；如果数据库还不存在，请求会在进入函数前失败。

因此 setup POST 必须改为：

- 不通过依赖注入拿目标库 session
- 先 bootstrap + migration
- 再手动创建 session
- 用完后关闭

## 错误处理

### service 层异常
建议新增轻量异常类型：

- `DatabaseBootstrapError`
- `UnsupportedDatabaseBootstrapError`

用于表达：

- 当前并非 PostgreSQL URL
- 无法连接维护库
- 无权限创建数据库
- 建库失败

### route 层错误呈现
根据已确认的产品边界，前台只展示通用错误，不暴露数据库内部细节。

`POST /setup` 捕获 bootstrap 异常后：

- 返回 setup 页面
- 显示统一文案：`初始化失败，请检查数据库配置后重试`

不直接向用户展示：

- `permission denied to create database`
- 原始 psycopg 错误消息
- SQL 语句
- stack trace

### 半初始化语义
若发生以下情况：

- 数据库创建成功
- Alembic migration 成功
- 但 `initialize_site()` 失败

则系统仍视为未初始化，因为初始化判定仍然基于：

- 存在 `site_settings`
- 存在管理员用户

只要两者不同时存在，`/` 和后台入口仍会回到 `/setup`，允许重新初始化。

## 对现有模块的影响

### 保持不变的行为

- `/` 未初始化时仍跳转 `/setup`
- `/admin/login` 未初始化时仍跳转 `/setup`
- `/admin/posts*` 未初始化时仍跳转 `/setup`
- 已初始化后 `/setup` 仍禁用

### 需要改动的文件

#### 新增
- `app/services/database_bootstrap_service.py`
- `tests/test_database_bootstrap_service.py`

#### 修改
- `app/routes/setup.py`
- `tests/test_admin_auth.py`

#### 可能小改
- `app/core/db.py`
- `tests/conftest.py`

只有在需要抽出很小的 session/engine 工具时才修改这些文件，避免扩大影响面。

## 测试策略

### `tests/test_database_bootstrap_service.py`
覆盖：

1. PostgreSQL 维护库 URL 构造正确
2. 目标数据库已存在时不执行 `CREATE DATABASE`
3. 目标数据库不存在时执行 `CREATE DATABASE`
4. 非 PostgreSQL URL 抛不支持异常
5. 建库失败时抛统一 bootstrap 异常

### `tests/test_admin_auth.py`
新增或调整：

1. 目标数据库不存在时，`GET /setup` 仍返回安装页
2. `POST /setup` 会先调用 bootstrap，再调用 migration 和初始化逻辑
3. 密码不一致时不触发 bootstrap
4. bootstrap 失败时页面显示通用初始化失败文案
5. 已初始化后 `GET /setup` 仍重定向 `/`

### 回归验证
继续保留并运行：

- `tests/test_public_pages.py`
- `tests/test_admin_posts.py`
- `tests/test_setup_service.py`

确保自动建库改造不破坏既有首次安装语义。

## 实施边界

本次实现只解决一个明确问题：

> 当 `DATABASE_URL` 指向的 PostgreSQL 目标数据库不存在时，用户仍能通过 `/setup` 自动完成建库和初始化。

不延伸实现其他数据库方言支持，也不顺带重构整个数据库访问层。