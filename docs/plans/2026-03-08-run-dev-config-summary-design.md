# 调试启动脚本打印配置摘要设计

**日期：** 2026-03-08
**主题：** 在本地 debug 启动脚本中打印脱敏数据库配置与启动参数摘要

## 目标

让 `scripts/run_dev.py` 在启动 uvicorn 之前，打印当前实际读取到的关键启动参数和脱敏后的数据库配置，帮助快速判断 `.env` 是否生效、端口是否正确以及当前连接目标是否符合预期。

## 范围

本设计仅覆盖 debug 启动前的摘要输出：

- 打印应用启动参数摘要
- 打印脱敏后的 `DATABASE_URL`
- 打印拆解后的数据库关键信息
- 保持密码始终脱敏

明确不做：

- 明文打印密码
- 自动检查数据库连通性
- 自动修复配置错误
- 打印所有环境变量
- 额外增加复杂日志等级开关

## 方案选择

### 选定方案
采用**完整脱敏 URL + 拆解字段摘要同时输出**的方案：

- 输出脱敏后的完整 `DATABASE_URL`
- 输出 `DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`
- 同时输出 `APP`、`HOST`、`PORT`、`RELOAD`、`LOG_LEVEL`

### 选择原因

该方案在不暴露密码的前提下，兼顾：

- 完整配置可见性
- 快速定位关键字段
- 本地排查的直观性

### 未选方案

- **只打印完整 URL**：可读性不足，排查仍要手动拆字段
- **只打印拆解字段**：看不到完整连接串形态，不利于发现 driver 或 URL 结构问题

## 架构设计

### 改动位置
仅修改：

- `scripts/run_dev.py`
- 对应测试 `tests/test_run_dev_script.py`

### 新增职责
`run_dev.py` 在调用 `uvicorn.run(...)` 前增加一段摘要打印逻辑：

1. 读取 `settings.database_url`
2. 解析 URL
3. 生成脱敏后的完整 `DATABASE_URL`
4. 生成拆解后的数据库字段摘要
5. 打印当前启动参数
6. 再启动 uvicorn

## 输出内容

### 启动参数摘要
例如：

```text
APP=app.main:app
HOST=127.0.0.1
PORT=8000
RELOAD=True
LOG_LEVEL=debug
```

### 数据库配置摘要
例如：

```text
DATABASE_URL=postgresql+psycopg://postgres:***@localhost:5432/myblog
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myblog
DB_USER=postgres
```

## 脱敏规则

### 完整 URL
- 保留 driver、用户名、主机、端口、数据库名
- 将密码替换为 `***`

### 拆解字段
- 仅打印：`DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`
- 不打印密码

## 异常处理

保持轻量实现：

- 如果 `DATABASE_URL` 可正常解析，则打印正常摘要
- 如果解析失败，则打印一个最小提示，例如：
  ```text
  DATABASE_URL=<invalid>
  ```
- 不在脚本中重写数据库校验逻辑，仍让后续真实启动过程负责抛出底层错误

## 测试策略

建议在 `tests/test_run_dev_script.py` 中补充：

1. 默认启动时打印脱敏后的配置摘要
2. 输出中不包含真实密码
3. 输出中包含启动参数摘要
4. `--port` 覆盖后，打印的 `PORT` 与 `uvicorn.run(...)` 参数保持一致

测试方式继续保持轻量：

- patch `uvicorn.run`
- 捕获标准输出
- 断言打印内容

不需要：

- 启动真实 HTTP 服务
- 连接真实数据库
- 增加额外集成测试

## 预期收益

以后运行：

```bash
python scripts/run_dev.py
```

即可在启动前直接看到：

- 当前程序实际读取到的数据库配置
- 当前监听端口
- 当前应用入口与日志模式

从而快速判断 `.env` 是否生效，减少本地 debug 时的盲查成本。
