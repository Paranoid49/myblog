# docs 文档导航

## 1. 先看什么

如果你是第一次接手这个项目，按下面顺序看，基本就能无障碍上手：

### 必读 4 篇
1. `../CLAUDE.md`
2. `product/product-overview.md`
3. `architecture/architecture-and-boundaries.md`
4. `engineering/development-guide.md`

这 4 篇解决 90% 的上手问题：
- 项目是什么
- 边界在哪
- 结构怎么组织
- 平时怎么启动和开发

---

## 2. 按目的阅读

### 我想快速上手项目
读：
- `../CLAUDE.md`
- `product/product-overview.md`
- `architecture/architecture-and-boundaries.md`
- `engineering/development-guide.md`

### 我想看接口契约
读：
- `api/api-v1-contract.md`
- `api/api-and-extension-overview.md`

### 我想理解扩展机制
读：
- `architecture/lightweight-extension-boundaries.md`
- `api/extension-api-v1.md`

### 我想改代码但不想越界
先读：
- `engineering/development-guide.md`

再按目的进入：
- 改动前边界判断与风险检查：`engineering/engineering-guardrails.md`

### 我想跑关键回归
读：
- `engineering/core-regression-suite.md`

---

## 3. 文档分层

### 当前真相文档
这些文档直接描述当前项目，应优先作为实现依据：

- `product/`
- `architecture/`
- `api/`
- `engineering/`

### 历史设计档案
这些文档只用于理解项目为什么演进成现在这样，不直接指导当前实现：

- `archive/plans/`
- `archive/planning/`

如果历史文档与当前代码或当前真相文档冲突，以当前真相文档为准。

---

## 4. 文档维护规则

为了保持文档新人友好、最小化、低噪音，统一遵守：

- 当改动影响产品范围、架构边界、API 契约、开发入口、扩展边界时，必须同步更新对应真相文档
- 新增文档前，先判断现有文档是否可以补充
- 若一份文档只剩历史参考价值，应归档，不继续放在当前活跃目录制造噪音
- `archive/planning/` 与 `archive/plans/` 只保存历史材料

### 执行要求
- 默认先补旧文档，再考虑新建文档
- 若新文档会与现有真相文档形成同主题并行维护，默认不新增
- 若只是补充现有规则、边界、执行清单，应优先回到原文档追加，而不是新开一份同类文档
- 若确需新增文档，必须能明确回答：为什么现有文档无法承载、谁来长期维护、它不会制造哪一种平行真相

---

## 5. 当前最小阅读集

如果你只愿意读最少内容，请至少读这 5 篇：

1. `../CLAUDE.md`
2. `product/product-overview.md`
3. `architecture/architecture-and-boundaries.md`
4. `api/api-v1-contract.md`
5. `engineering/development-guide.md`

读完这 5 篇，基本就能：
- 理解项目定位与范围边界
- 理解 API 契约
- 理解日常开发路径

---

## 6. 还需要看历史时

只有在你想回答"为什么以前这样设计"时，再去读：

- `archive/plans/*.md`
- `archive/planning/*.md`

这些文档不是上手必读。
