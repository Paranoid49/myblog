# 扩展开发文档（Extension API v1）

## 1. 数据库 Provider 扩展

### 1.1 内置 provider
- `sqlite`
- `postgresql`

### 1.2 注册表位置
- 文件：`app/core/database_provider.py`
- 注册表变量：`DATABASE_PROVIDERS`

### 1.3 扩展方式
实现 `BaseDatabaseProvider` 并加入 `DATABASE_PROVIDERS`：

```python
class MyProvider(BaseDatabaseProvider):
    name = "mydb"

    def supports(self, url: URL) -> bool:
        return url.drivername.startswith("mydb")

DATABASE_PROVIDERS["mydb"] = MyProvider()
```

当 `DATABASE_URL` 不能匹配任何 provider 时，系统抛出：
- `ValueError("unsupported_database_driver:<driver>")`

---

## 2. 主题 Provider 扩展

### 2.1 注册表位置
- 文件：`frontend/src/shared/theme/ThemeProvider.jsx`
- 注册函数：`registerTheme(themeKey)`

### 2.2 扩展方式
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
  - `subscribe(event_name, handler)`
  - `emit(event_name, payload)`
- 监听器异常隔离：单个 handler 抛错不会影响主流程。

### 3.2 内置事件
- `post.created`
- `post.updated`
- `post.published`
- `post.unpublished`
- `media.image_uploaded`

---

## 4. 示例扩展

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
