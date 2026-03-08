# 首页在目标数据库不存在时跳转 Setup 设计

**日期：** 2026-03-08
**主题：** 修复首页在 PostgreSQL 目标数据库不存在时先连库导致的启动访问失败

## 目标

让用户在目标数据库尚未创建时访问首页 `/`，不再触发 `sqlalchemy.exc.OperationalError`，而是直接跳转到 `/setup`，从而进入已有的初始化流程。

## 问题根因

当前首页路由 `app/routes/public.py` 在函数签名中直接声明 `db: Session = Depends(get_db)`。这会导致请求 `/` 时，框架先通过 `get_db()` 创建数据库 session，并尝试连接 `settings.database_url` 指向的目标数据库。

当目标数据库 `myblog` 还不存在时，请求甚至还没进入“未初始化跳转 `/setup`”的业务判断，就已经在数据库连接层失败，因此用户看到的是 PostgreSQL 的 `database does not exist` 错误，而不是安装引导页面。

## 方案选择

### 选定方案
采用**抽取轻量数据库存在性判断函数，并在首页路由前置判断**的方案：

- 将“目标数据库是否存在”的判断逻辑抽到轻量 service 中
- `app/routes/setup.py` 继续复用它
- `app/routes/public.py` 在创建数据库 session 前先判断
- 若数据库不存在，直接 `302` 跳转 `/setup`

### 选择原因

该方案：

- 直接修复当前根因：避免首页先连接不存在的数据库
- 保持 `get_db()` 语义简单，不把路由分支逻辑塞进底层数据库依赖
- 避免路由模块之间直接互相 import，降低耦合
- 改动面小，符合这次 bug 修复的最小原则

### 未选方案

- **直接在 `public.py` 里 import `setup.py` 的 `database_exists()`**：能用，但让路由模块互相依赖，不够干净
- **在 `get_db()` 中捕获并吞掉不存在数据库异常**：会让底层数据库依赖承担业务分流职责，异常语义变差，不适合作为这次的最小修复

## 具体设计

### 新增轻量 service

新增一个仅负责判断目标数据库是否存在的轻量 service，例如：

- `app/services/database_state_service.py`

职责：

1. 读取 `settings.database_url`
2. 对 PostgreSQL：连接维护库 `postgres`
3. 查询目标数据库是否存在
4. 非 PostgreSQL 时直接返回 `True`

行为保持与当前 `setup.py` 中已有判断一致，不扩展出更多状态枚举或复杂抽象。

### 首页路由改造

修改 `app/routes/public.py` 的首页逻辑：

1. 去掉首页函数签名中立即创建 DB session 的方式
2. 在路由开头先判断目标数据库是否存在
3. 若不存在，直接返回 `RedirectResponse("/setup")`
4. 若存在，再创建 session 并执行当前已有的初始化判断与首页渲染逻辑

这样可以确保“数据库不存在”和“数据库存在但尚未初始化”两种情况都统一流向 `/setup`。

### Setup 路由改造

`app/routes/setup.py` 不改变产品行为，只把当前内联的数据库存在性判断改为调用新的轻量 service，避免逻辑重复。

## 测试策略

本次测试只覆盖与该 bug 直接相关的最小行为：

1. 在 `tests/test_public_pages.py` 新增测试：
   - patch 数据库存在性判断为 `False`
   - 请求首页 `/`
   - 断言响应为 `302`
   - 断言 `location == "/setup"`

2. 运行该新测试，先确认失败

3. 实现最小修复

4. 回归以下测试：
   - `tests/test_public_pages.py`
   - `tests/test_admin_auth.py` 中与 setup 相关的测试
   - 必要时全量 `pytest`

## 预期结果

修复后：

- 当 `DATABASE_URL` 指向的 PostgreSQL 数据库不存在时，访问 `/` 会直接跳转 `/setup`
- 用户可以继续通过 setup 页面完成自动建库和初始化
- 不再在首页看到 `database "myblog" does not exist` 的底层连接错误
