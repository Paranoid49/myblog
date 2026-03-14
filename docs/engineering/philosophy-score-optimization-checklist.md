# 哲学提分优化执行清单

日期：2026-03-13

## 目标

本清单用于将项目当前的哲学优化方向落到可执行层面，围绕以下三个目标持续提分：

- 轻量
- 克制
- 可扩展

本清单是对以下文档的执行化补充：

- `docs/engineering/evolution-guardrails.md`
- `docs/architecture/architecture-and-boundaries.md`
- `docs/engineering/development-guide.md`
- `docs/engineering/manual-checks-governance.md`

排序原则：

1. 优先做投入小、收益高的收口项
2. 优先做能减少系统失配和热点复杂度的项
3. 优先做不会引入新平台层或新抽象层的项

---

## 一、P0：优先立即执行

这些项具备“低成本、高收益、符合当前守则”的特点，建议优先处理。

### 1. 统一后台未授权收敛逻辑
**状态：已完成**

#### 实施优先级
P0

#### 目标
当前前端本地登录态与后端 session 可能出现失配。该优化用于让错误状态快速回到一致状态。

#### 涉及文件

- `frontend/src/shared/api/client.js`
- `frontend/src/shared/auth/session.js`
- `frontend/src/shared/auth/AuthGuard.jsx`
- `frontend/src/admin/pages/LoginPage.jsx`
- 如有必要，可补充相关测试文件

#### 建议动作

- 在统一 API 请求层识别后端未授权错误
- 发生未授权时统一：
  1. 清理本地登录缓存
  2. 跳转 `/admin/login`
- 避免在多个页面各自实现一套未授权处理逻辑
- 不新增 session restore、AuthContext 或更复杂认证状态机

#### 预期收益

- **轻量**：避免为了修补状态失配引入更复杂认证层
- **克制**：把问题收口在统一入口，而不是到处打补丁
- **可扩展**：明确“后端 session 才是真认证”的稳定边界

#### 完成判断

- 后台 API 失效时，前端会统一回登录页
- 本地缓存与后端状态失配不会长期停留
- 没有在页面层新增重复未授权处理代码

---

### 2. 将守则接入开发文档入口
**状态：已完成**

#### 实施优先级
P0

#### 目标
让守则从“存在的文档”变成“开发默认会看到的文档”。

#### 涉及文件

- `docs/engineering/development-guide.md`
- `docs/engineering/evolution-guardrails.md`

#### 建议动作

- 在 `development-guide.md` 中增加一段简短说明
- 明确以下改动应先参考守则：
  - 架构边界调整
  - 认证相关改动
  - 文章模块能力扩展
  - 扩展机制增强
  - 手工检查与调试产物处理
- 不增加过长说明，保持指南简洁

#### 预期收益

- **轻量**：不新增流程系统，仅通过文档入口收口
- **克制**：让边界约束进入日常开发路径
- **可扩展**：让扩展边界说明更容易被遵守

#### 完成判断

- 开发指南中存在对守则文档的明确引用
- 新人按开发指南阅读时可以自然触达到守则

---

### 3. 清理一次无长期价值的调试与手工检查残留
**状态：已完成**

#### 实施优先级
P0

#### 目标
降低仓库噪音，提升轻量感和工程卫生一致性。

#### 涉及文件

重点关注：

- `project_logs/manual_checks/` 下的 `debug_*`
- `project_logs/manual_checks/` 下的 `todo*`
- `project_logs/manual_checks/` 下的 `*_result.txt`
- 一次性 HTML 调试页、截图、日志文件

可参考规范：

- `docs/engineering/manual-checks-governance.md`

#### 建议动作

- 盘点现有临时材料
- 删除无长期价值的临时文件
- 保留确有复盘价值的阶段材料
- 后续继续统一使用临时前缀：
  - `debug_`
  - `todo_`
  - `tmp_`

#### 预期收益

- **轻量**：减少仓库中一次性噪音文件
- **克制**：避免调试痕迹长期侵蚀主仓库
- **可扩展**：无直接提升，但能稳定工程边界

#### 完成判断

- `project_logs/manual_checks/` 中临时文件数量明显下降
- 剩余文件都能说明长期保留理由
- 任务完成时清理动作成为默认标准

---

### 4. 做一次文档降承诺检查
**状态：已完成**

#### 实施优先级
P0

#### 目标
防止“文档先写满、实现被动补齐”的膨胀路径继续发生。

#### 涉及文件

优先检查：

- `docs/product/product-overview.md`
- `docs/product/v1-scope.md`
- `docs/api/api-v1-contract.md`
- `docs/api/api-and-extension-overview.md`
- `docs/planning/*.md`

#### 建议动作

- 标记哪些内容属于“当前已确认能力”
- 标记哪些内容只是“未来可能方向”
- 对容易被误解为已承诺的表述做降承诺处理
- 能收文档就先收文档，不默认补实现

#### 预期收益

- **轻量**：减少由文档驱动带来的额外实现压力
- **克制**：强化“真实需求优先”
- **可扩展**：让扩展边界与承诺边界更加清晰

#### 完成判断

- 核心文档中“已确认”和“探索性”表达更清楚
- 没有明显超出当前产品体量的默认承诺

---

## 二、P1：建议尽快执行

这些项主要用于降低热点模块复杂度，提升系统的可读性和后续可维护性。

### 5. 对 `api_v1_posts.py` 做一次薄收口
**状态：已完成**

#### 实施优先级
P1

#### 目标
降低后端热点文件复杂度，避免文章模块持续中心化。

#### 涉及文件

- `app/routes/api_v1_posts.py`
- `app/services/post_service.py`
- `app/services/admin_post_service.py`
- 如拆分路由，可能新增：
  - `app/routes/api_v1_posts_public.py`
  - `app/routes/api_v1_posts_admin.py`
- `app/main.py`（如路由拆分需要重新注册）
- 相关测试文件：
  - `tests/test_api_v1_posts.py`

#### 建议动作

可按以下两种最小方式选其一：

##### 方案 A：单文件内部分区整理
- 明确 public read / admin write / import-export / publish workflow 分区
- 统一函数顺序与命名风格
- 补充最小边界说明

##### 方案 B：只拆成两个路由文件
- 公共读取接口一组
- 后台写接口一组
- 不继续细拆 controller/usecase/repository 层

#### 预期收益

- **轻量**：降低单热点文件认知复杂度
- **克制**：防止文章模块继续自然膨胀
- **可扩展**：让“公共读”和“后台写”的边界更稳定

#### 完成判断

- 文章路由职责分组更清晰
- 无新增重型分层
- 现有能力与测试仍保持完整可用

---

### 6. 对 `AdminPostsPage.jsx` 做一次薄收口
**状态：已完成**

#### 实施优先级
P1

#### 目标
降低后台文章页的容器复杂度，避免其继续演化成前端万能中心。

#### 涉及文件

- `frontend/src/admin/pages/AdminPostsPage.jsx`
- `frontend/src/admin/components/AdminPostEditor.jsx`
- `frontend/src/admin/components/AdminPostFilters.jsx`
- `frontend/src/admin/components/AdminPostList.jsx`
- 如有需要，可新增轻量模块：
  - `frontend/src/admin/hooks/useAdminPostsState.js`
  - 或 `frontend/src/admin/utils/*.js`

#### 建议动作

- 将表单初始化、重置、筛选映射、刷新逻辑等可抽离部分做轻量整理
- 保持 `AdminPostsPage.jsx` 作为页面容器，不引入全局状态管理
- 将局部交互继续下沉给现有子组件

#### 预期收益

- **轻量**：降低单页面状态编排复杂度
- **克制**：防止后台文章页继续承载非核心能力
- **可扩展**：未来局部增强更容易局部修改

#### 完成判断

- 页面主体更聚焦于数据编排
- 局部逻辑已下沉，但未引入新全局层
- 阅读页面时更容易区分状态、视图和动作边界

---

### 7. 将文章模块边界明确写入文档和实现附近说明
**状态：已完成**

#### 实施优先级
P1

#### 目标
让“文章模块不继续平台化”从口头共识变成稳定边界。

#### 涉及文件

- `docs/engineering/evolution-guardrails.md`
- 如有必要，可补充到：
  - `docs/architecture/architecture-and-boundaries.md`
  - `app/routes/api_v1_posts.py`
  - `frontend/src/admin/pages/AdminPostsPage.jsx`

#### 建议动作

- 在守则中突出文章模块边界
- 如确有必要，在热点文件附近补极少量边界说明
- 不写大段注释，只写有约束力的简短说明

#### 预期收益

- **轻量**：减少后续无意识扩张
- **克制**：形成可执行的功能红线
- **可扩展**：让扩展优先走现有边界，而不是继续堆进文章模块

#### 完成判断

- 文档中对文章模块的允许范围和禁入范围更明确
- 热点实现文件附近可见边界提示（如确有必要）

---

## 三、P2：按需执行但建议纳入近期计划

这些项不是立刻必须，但对把“可扩展”与“稳定边界”提升到更高分有帮助。

### 8. 对扩展点做“稳定化”而不是“增强化”
**状态：已完成**

#### 实施优先级
P2

#### 目标
让现有扩展点从“有入口”提升为“边界清晰、行为稳定、可验证”，而不是继续做强。

#### 涉及文件

后端：

- `app/core/database_provider.py`
- `app/core/hook_bus.py`
- `app/core/extension_loader.py`
- `app/extensions/sample_extension.py`

前端：

- `frontend/src/shared/theme/ThemeProvider.jsx`

测试：

- `tests/test_database_provider.py`
- `tests/test_hook_bus.py`
- `tests/test_extension_loader.py`
- 如需新增前端覆盖，可按现有测试策略最小补充

文档：

- `docs/architecture/architecture-and-boundaries.md`
- `docs/engineering/evolution-guardrails.md`

#### 建议动作

- 补最小测试覆盖，验证现有扩展点行为稳定
- 补最小文档说明，进一步明确“不做什么”
- 不新增插件元信息、优先级、重试、热加载等高级能力

#### 预期收益

- **轻量**：不通过增强抽象来追求“更强扩展”
- **克制**：守住“真实需求驱动”的底线
- **可扩展**：把现有扩展点变成稳定可靠的边界，而不是半平台化起点

#### 完成判断

- 关键扩展点具备最小可验证性
- 文档中对扩展边界与禁区说明更加明确
- 未引入新的平台层

---

## 四、建议执行顺序

如果只按最小投入追求哲学提分，建议按以下顺序实施：

1. 统一后台未授权收敛逻辑
2. 将守则接入开发文档入口
3. 清理一次无长期价值的调试与手工检查残留
4. 做一次文档降承诺检查
5. 对 `api_v1_posts.py` 做一次薄收口
6. 对 `AdminPostsPage.jsx` 做一次薄收口
7. 将文章模块边界明确写入文档和实现附近说明
8. 对扩展点做“稳定化”而不是“增强化”

---

## 五、预期整体收益

按本清单推进后，项目可预期获得以下改善：

### 对“轻量”的提升

- 热点文件和热点页面认知负担下降
- 临时产物不再持续侵蚀仓库整洁度
- 不会为局部问题引入新的全局层

### 对“克制”的提升

- 文章模块不再自然滑向平台化
- 文档不再持续对实现施加超前承诺压力
- 认证问题优先收口，而不是顺势扩成复杂体系

### 对“可扩展”的提升

- 扩展点边界更稳定、更明确
- 增强方式更偏向局部、可删、可回退
- 扩展能力不会反向污染核心模块

---

## 六、执行约束

在执行本清单时，统一遵守以下限制：

1. 不为“更优雅”引入与当前规模不匹配的新架构层
2. 不把局部优化扩展成平台化重构
3. 不把守则当作增加文档负担的理由
4. 优先修改边界、收口行为、减少复杂度，而不是新增能力

---

## 一句话结论

如果目标是把“轻量、克制、可扩展”三个维度尽量提高到 9 分左右，最有效的路径不是继续建设更多系统，而是：

> 收口热点、统一失配、冻结边界、降低承诺、清理噪音。
