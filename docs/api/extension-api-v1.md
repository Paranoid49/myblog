# 扩展开发文档（Extension API v1）

## 1. 数据库 Provider 扩展

### 1.1 内置 provider
- `sqlite`
- `postgresql`

### 1.2 注册表位置
- 文件：`app/core/database_provider.py`
- 工厂函数：`create_app_engine()`

### 1.3 当前职责边界
数据库 provider 当前只承担：

- 根据 `DATABASE_URL` 识别 driver
- 在 SQLite / PostgreSQL 之间选择 provider
- 封装 engine 创建时的最小差异

它不承担：

- ORM 抽象层
- 迁移框架替代
- 多租户数据库编排
- 为未来假设做通用数据库平台

### 1.4 扩展方式
在 `app/core/database_provider.py` 的 `create_app_engine()` 函数中添加新的 driver 分支：

```python
def create_app_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    driver = url.drivername

    if driver.startswith("sqlite"):
        return create_engine(...)
    elif driver.startswith("postgresql"):
        return create_engine(...)
    elif driver.startswith("mydb"):
        return create_engine(database_url, future=True, ...)
    else:
        raise ValueError(f"unsupported_database_driver:{driver}")
```

当 `DATABASE_URL` 不能匹配任何 provider 时，系统抛出：
- `ValueError("unsupported_database_driver:<driver>")`

---

## 2. 主题 Provider 扩展

### 2.1 注册表位置
- 文件：`frontend/src/shared/theme/ThemeProvider.jsx`
- 注册函数：`registerTheme(themeKey)`

### 2.2 当前职责边界
主题机制当前只承担：

- 注册主题 key
- 切换当前主题
- 把主题值写入 localStorage
- 通过 `data-theme` 暴露给样式层

它不承担：

- 主题包市场
- 动态主题资源下载
- 多层 provider 组合系统
- 脱离当前项目规模的复杂主题平台

### 2.3 扩展方式
在前端启动时注册主题：

```javascript
import { registerTheme } from './shared/theme/ThemeProvider';

registerTheme('ocean');
```

注册后可通过 `setTheme('ocean')` 切换。

---

## 3. Hook 事件总线

### 3.1 核心能力
- 位置：`app/core/hook_bus.py`
- API：
  - `subscribe(event_name, handler)` → 返回 `unsubscribe` 函数
  - `emit(event_name, payload)`
- 监听器异常隔离：单个 handler 抛错不会影响主流程。

### 3.2 当前职责边界
Hook 事件总线当前只承担：

- 单进程内轻量事件分发
- 已有业务事件通知
- 监听器异常隔离

它不承担：

- 跨进程消息传递
- 持久化
- 重试
- 顺序保证
- MQ 替代能力

### 3.3 事件命名与 payload 约定
- 事件命名建议使用 `domain.action`，例如 `post.published`
- payload 应保持最小化，只传递 handler 真正需要的字段
- 当前已落地事件 payload 以文章 id、slug、媒体 url 等轻量字段为主
- 扩展 handler 不应假设存在跨进程语义或持久化语义

### 3.4 内置事件
- `post.created`
- `post.updated`
- `post.published`
- `post.unpublished`
- `media.image_uploaded`

### 3.5 取消订阅

`subscribe()` 返回一个取消订阅函数，调用后即停止接收事件：

```python
from app.core.hook_bus import hook_bus

def my_handler(event):
    print(event.payload)

unsubscribe = hook_bus.subscribe("post.published", my_handler)

# 不再需要时取消订阅
unsubscribe()
```

---

## 4. 示例扩展

### 4.1 扩展加载机制边界
- 文件：`app/core/extension_loader.py`
- 启动入口：`app/main.py`
- 当前行为：按逗号分隔读取模块路径，逐个导入模块并返回成功导入列表

扩展加载机制当前只承担：

- 启动时导入扩展模块
- 借模块导入执行注册逻辑

它不承担：

- 插件安装 / 卸载系统
- 生命周期管理平台
- 依赖解析
- 隔离沙箱

扩展模块应尽量保持：

- 导入即注册
- 副作用最小
- 注册逻辑清晰可回退

### 4.2 示例扩展
- 文件：`app/extensions/sample_extension.py`
- 功能：订阅 `post.published` 事件。

启用方式（环境变量）：

```env
EXTENSION_MODULES=app.extensions.sample_extension
```

支持多个扩展（逗号分隔）：

```env
EXTENSION_MODULES=app.extensions.sample_extension,foo.bar_ext
```

系统在 `app/main.py` 启动时加载扩展模块。
