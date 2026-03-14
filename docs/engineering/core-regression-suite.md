# 核心回归测试包

日期：2026-03-14

## 目标

本清单用于明确项目当前最值得长期保留的高价值回归测试集合。

这些测试的目标不是追求数量，而是覆盖：

- 核心用户路径
- 关键工程入口
- 已冻结的项目哲学基线
- 最小扩展边界

当后续发生中型及以上改动时，优先保证这组测试可运行、可通过。

---

## 一、建议纳入核心回归范围的测试

### 1. 初始化链路
- `tests/test_setup_service.py`
- `tests/test_database_bootstrap_service.py`
- `tests/test_database_state_service.py`

关注点：
- 初始化状态判定
- 首次安装闭环
- PostgreSQL 显式配置场景下的建库与迁移

### 2. 认证链路
- `tests/test_api_v1_auth.py`
- `tests/test_admin_auth.py`
- `tests/test_philosophy_guardrails.py`

关注点：
- 登录 / 登出
- session 认证基线
- 登录接口仍使用 form 提交契约
- API 统一响应结构不漂移

### 3. 文章主链路
- `tests/test_api_v1_posts.py`
- `tests/test_admin_posts.py`
- `tests/test_post_service.py`

关注点：
- 文章创建 / 更新 / 发布 / 取消发布
- Markdown 导入 / 导出
- 公开文章读取
- 默认分类行为

### 4. taxonomy 链路
- `tests/test_taxonomy_service.py`
- `tests/test_admin_taxonomy.py`
- `tests/test_api_v1_posts.py`（分类 / 标签公开查询覆盖）

关注点：
- 分类 / 标签创建
- 重名冲突处理
- 前台分类 / 标签检索

### 5. 图片上传链路
- `tests/test_api_v1_posts.py`（媒体上传相关用例）

关注点：
- 支持格式
- 大小限制
- URL 返回格式

### 6. 扩展边界
- `tests/test_hook_bus.py`
- `tests/test_extension_loader.py`
- `tests/test_database_provider.py`
- `tests/test_philosophy_guardrails.py`

关注点：
- hook bus 最小行为
- extension loader 成功 / 失败路径
- database provider 最小行为
- 媒体规则与默认基线保持不漂移

### 7. 启动脚本与开发入口
- `tests/test_start_blog_script.py`
- `tests/test_start_fullstack_script.py`
- `tests/test_run_dev_script.py`

关注点：
- 后端开发入口
- 全栈开发入口
- 历史兼容脚本仍可运行

---

## 二、建议执行方式

### 日常中型改动后
优先运行：

```bash
pytest tests/test_philosophy_guardrails.py tests/test_api_v1_auth.py tests/test_api_v1_posts.py tests/test_admin_posts.py
```

### 涉及扩展边界时
优先追加：

```bash
pytest tests/test_hook_bus.py tests/test_extension_loader.py tests/test_database_provider.py
```

### 涉及启动与联调路径时
优先追加：

```bash
pytest tests/test_start_blog_script.py tests/test_start_fullstack_script.py tests/test_run_dev_script.py
```

### 完整回归时
直接运行：

```bash
pytest
```

---

### 最小高价值回归命令

当后续发生中型改动，需要快速判断是否仍守住主链路和边界时，优先运行：

```bash
pytest tests/test_philosophy_guardrails.py tests/test_api_v1_auth.py tests/test_api_v1_posts.py tests/test_admin_posts.py tests/test_hook_bus.py tests/test_extension_loader.py tests/test_database_provider.py tests/test_start_blog_script.py tests/test_start_fullstack_script.py
```

这套命令覆盖：
- 哲学冻结规则
- 认证主链路
- 文章主链路
- 扩展边界
- 启动脚本与开发入口

---

## 三、维护原则

- 不追求把所有测试都塞进“核心回归包”
- 只保留对边界稳定性和主链路可靠性最关键的集合
- 当新能力成为稳定承诺后，再决定是否纳入本清单
- 若某项测试失去长期价值，应及时移出核心回归包，避免噪音增长
