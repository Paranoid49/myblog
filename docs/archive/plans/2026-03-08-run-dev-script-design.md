# 本地调试启动脚本设计

**日期：** 2026-03-08
**主题：** 为本地开发提供一键启动 FastAPI 调试脚本

## 目标

提供一个简单稳定的本地调试启动入口，替代每次手动输入完整的 uvicorn 命令。用户应能通过单条命令快速启动当前博客项目的开发服务器，并保留最小必要的端口覆盖能力，方便调试时切换端口。

## 范围

本设计仅覆盖本地开发调试的启动便利性：

- 新增 `scripts/run_dev.py`
- 默认启动 `app.main:app`
- 默认监听 `127.0.0.1:8000`
- 默认开启 `reload`
- 默认使用 `debug` 日志级别
- 支持可选参数 `--port`

明确不做：

- 生产环境启动脚本
- 自动修复数据库问题
- 自动初始化 `.env`
- 自动打开浏览器
- 自动执行 `/setup`
- 自动打印复杂诊断信息
- 多套 host/reload/log-level 组合开关

## 方案选择

### 选定方案
采用**一键启动脚本 + 最小参数覆盖**方案：

- 默认命令：`python scripts/run_dev.py`
- 可选覆盖端口：`python scripts/run_dev.py --port 8001`
- 脚本内部直接调用 `uvicorn.run(...)`

### 选择原因

该方案兼顾了：

- 一键启动的简洁性
- 本地调试中最常见的端口冲突场景
- 最低维护成本
- 不引入第二套复杂启动体系

### 未选方案

- **纯固定脚本**：最简单，但端口被占用时不够方便
- **带大量预检查和环境诊断的脚本**：功能更强，但超出当前需求，容易变成第二套运维入口

## 架构设计

### 文件位置
新增文件：

- `scripts/run_dev.py`

放在现有 `scripts/` 目录下，与 `scripts/create_admin.py` 保持一致的项目结构。

### 脚本职责
该脚本仅负责：

1. 解析可选 `--port`
2. 调用 `uvicorn.run(...)`
3. 固定当前项目本地调试默认值：
   - `app="app.main:app"`
   - `host="127.0.0.1"`
   - `port=8000`
   - `reload=True`
   - `log_level="debug"`

该脚本不负责任何数据库 bootstrap、setup 提交、浏览器自动化或环境修复逻辑。

## 调用方式

### 默认启动
```bash
python scripts/run_dev.py
```

等价于：

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

### 覆盖端口
```bash
python scripts/run_dev.py --port 8001
```

此能力仅用于本地开发时解决端口占用问题，不引入更多可选参数。

## 错误处理

本期保持最小实现：

- 参数解析交给标准库 `argparse`
- 非法端口值由 argparse 负责报错
- uvicorn 启动失败时直接显示原始启动错误

不额外包装异常，也不新增调试输出层。

## 测试策略

建议新增轻量脚本测试，覆盖：

1. 默认调用 `uvicorn.run` 时参数正确
2. `--port 8001` 能覆盖默认端口

测试方式：

- patch `uvicorn.run`
- 调用脚本入口函数
- 断言传入参数

不需要：

- 真正启动 HTTP 服务
- 执行端到端网络测试
- 绑定 PostgreSQL 做集成测试

## 预期收益

完成后，本地调试启动将从：

```bash
python -m uvicorn app.main:app --reload
```

收敛为：

```bash
python scripts/run_dev.py
```

同时保留必要的端口切换能力，减少手输错误，提高日常调试效率。
