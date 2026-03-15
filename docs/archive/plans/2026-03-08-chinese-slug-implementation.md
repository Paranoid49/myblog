# Chinese Slug Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将当前仅支持英文的 slug 生成逻辑升级为适合中文博客的混合智能 slug 方案，支持中文转拼音、英文保留、数字保留和稳定的唯一化策略。

**Architecture:** 继续沿用现有 `app/services/post_service.py` 作为 slug 规则中心，实现一个统一的字符串分词与归一化过程。通过新增轻量拼音依赖，把中文字符转换为无声调拼音，再统一清洗为 `-` 分隔格式；测试层在 `tests/test_post_service.py` 固化中文、混合标题、特殊符号、重复和兜底场景。

**Tech Stack:** Python, pypinyin, pytest

---

## 0. 实施前约束

- 遵循 DRY / YAGNI，只修改 slug 规则引擎与对应测试。
- 必须遵循 @superpowers:test-driven-development：先写失败测试，再实现，再验证通过。
- 当前用户全局偏好禁止非查询类 git 操作，因此本计划不执行任何 `git add`、`git commit`、`git push`。
- 当前已存在英文 slug 测试与实现，升级时要保留英文场景能力，不要只顾中文。

---

### Task 1: 引入中文 slug 依赖并补中文失败测试

**Files:**
- Modify: `requirements.txt`
- Modify: `tests/test_post_service.py`

**Step 1: Write the failing test**

在 `tests/test_post_service.py` 中追加最小中文失败测试：

```python
def test_slugify_converts_chinese_title_to_pinyin() -> None:
    assert slugify("我的第一篇博客") == "wo-de-di-yi-pian-bo-ke"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py::test_slugify_converts_chinese_title_to_pinyin" -v`
Expected: FAIL，因为当前 `slugify()` 会把中文清洗为空字符串。

**Step 3: Write minimal implementation**

先只修改 `requirements.txt`，加入：

```text
pypinyin
```

此步不修改生产逻辑，只先让依赖方向落位。

**Step 4: Run test to verify it still fails for the right reason**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py::test_slugify_converts_chinese_title_to_pinyin" -v`
Expected: 仍然 FAIL，但失败原因应是 slug 结果不正确，而不是导入错误。

**Step 5: Dependency install**

Run: `"D:/projects/python/myblog/.venv/Scripts/python.exe" -m pip install pypinyin`
Expected: 安装成功。

---

### Task 2: 实现中文转拼音 slug 核心规则

**Files:**
- Modify: `app/services/post_service.py`
- Test: `tests/test_post_service.py`

**Step 1: Write the failing test**

保持 Task 1 中的测试不变，并追加一个中英混合场景：

```python
def test_slugify_handles_mixed_chinese_english_and_numbers() -> None:
    assert slugify("FastAPI 入门教程 2026") == "fastapi-ru-men-jiao-cheng-2026"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py" -v`
Expected: 中文相关测试 FAIL，英文旧测试可能仍 PASS。

**Step 3: Write minimal implementation**

在 `app/services/post_service.py` 中实现最小中文友好版 `slugify()`。建议实现如下：

```python
import re
from pypinyin import Style, lazy_pinyin


def _normalize_chunks(value: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []

    for char in value.strip():
        if char.isascii() and char.isalnum():
            current.append(char.lower())
            continue

        if current:
            chunks.append("".join(current))
            current = []

        if "\u4e00" <= char <= "\u9fff":
            chunks.extend(lazy_pinyin(char, style=Style.NORMAL))

    if current:
        chunks.append("".join(current))

    return chunks


def slugify(value: str) -> str:
    chunks = _normalize_chunks(value)
    slug = "-".join(chunk for chunk in chunks if chunk)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug
```

注意：
- 标点、空格、特殊符号在这里天然充当分隔符
- 英文连续字符保留为一个词
- 中文逐字转拼音并以 `-` 分隔

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py" -v`
Expected: 英文和中文/混合标题测试全部 PASS。

**Step 5: Quick manual check**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -c "from app.services.post_service import slugify; print(slugify('FastAPI 入门教程 2026！'))"`
Expected: 输出 `fastapi-ru-men-jiao-cheng-2026`

---

### Task 3: 固化符号分隔规则与空结果兜底

**Files:**
- Modify: `tests/test_post_service.py`
- Modify: `app/services/post_service.py`

**Step 1: Write the failing test**

在 `tests/test_post_service.py` 中追加：

```python
def test_slugify_treats_symbols_as_separators() -> None:
    assert slugify("Python & PostgreSQL 实战！") == "python-postgresql-shi-zhan"


def test_slugify_falls_back_to_post_when_slug_is_empty() -> None:
    assert slugify("！！！@@@") == "post"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py::test_slugify_falls_back_to_post_when_slug_is_empty" -v`
Expected: FAIL，因为当前空结果会返回空字符串。

**Step 3: Write minimal implementation**

更新 `slugify()` 的返回逻辑：

```python
def slugify(value: str) -> str:
    chunks = _normalize_chunks(value)
    slug = "-".join(chunk for chunk in chunks if chunk)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "post"
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py" -v`
Expected: 新增符号和兜底测试 PASS。

**Step 5: Manual verification**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -c "from app.services.post_service import slugify; print(slugify('！！！@@@'))"`
Expected: 输出 `post`

---

### Task 4: 验证唯一化策略兼容中文 slug

**Files:**
- Modify: `tests/test_post_service.py`
- Modify: `app/services/post_service.py`（仅当需要）

**Step 1: Write the failing test**

追加中文 slug 唯一化测试：

```python
def test_ensure_unique_slug_handles_chinese_generated_slug() -> None:
    base_slug = slugify("我的博客")
    assert ensure_unique_slug(base_slug, {"wo-de-bo-ke", "wo-de-bo-ke-2"}) == "wo-de-bo-ke-3"
```

**Step 2: Run test to verify it fails or proves current behavior**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py::test_ensure_unique_slug_handles_chinese_generated_slug" -v`
Expected: 如果现有逻辑已兼容，则 PASS；如果失败，再进入实现步骤。

**Step 3: Write minimal implementation**

只有在失败时才修改 `ensure_unique_slug()`。目标保持：

```python
def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing_slugs:
        index += 1
    return f"{base_slug}-{index}"
```

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py" -v`
Expected: 唯一化相关测试全部 PASS。

**Step 5: Keep implementation minimal**

如果 `ensure_unique_slug()` 无需修改，则不要为了“整洁”而重构别的逻辑。

---

### Task 5: 回归验证并更新设计一致性

**Files:**
- Modify: `docs/plans/2026-03-08-blog-design.md`
- Test: `tests/test_post_service.py`

**Step 1: Write the verification checklist in tests first (existing tests are the checklist)**

无需新增生产功能测试，确认以下用例已经存在：
- 英文标题
- 中文标题
- 中英混合标题
- 符号分隔
- 空结果兜底
- 唯一化后缀

**Step 2: Run test suite to verify coverage and behavior**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_post_service.py" -v`
Expected: 全部 PASS。

**Step 3: Write minimal design doc update**

将 `docs/plans/2026-03-08-blog-design.md` 中 slug 规则更新为：

- 英文保留并转小写
- 中文转拼音
- 数字保留
- 标点和空白作为分隔符
- 空结果回退为 `post`
- 重复追加 `-2`、`-3`
- 编辑文章默认不改 slug

**Step 4: Run broader regression**

Run: `PYTHONPATH="D:/projects/python/myblog" "D:/projects/python/myblog/.venv/Scripts/python.exe" -m pytest "D:/projects/python/myblog/tests/test_health.py" "D:/projects/python/myblog/tests/test_models.py" "D:/projects/python/myblog/tests/test_post_service.py" "D:/projects/python/myblog/tests/test_fixtures.py" "D:/projects/python/myblog/tests/test_admin_auth.py" -v`
Expected: 全部 PASS，无回归。

**Step 5: Record optimization log**

Run: `python scripts/log_change.py --type "中文 slug 升级" --purpose "让中文标题生成稳定可读 URL" --modules "slug 生成,测试用例,设计文档" --verification "中文/混合/符号/兜底/唯一化测试通过"`
Expected: 若日志脚本存在，则日志成功写入；若不存在，先记录为后续待补，不要为此扩展范围。

---

## 实施顺序建议

1. Task 1：先锁定依赖与第一个中文失败测试
2. Task 2：实现中文转拼音核心逻辑
3. Task 3：补全符号分隔与空结果兜底
4. Task 4：确认唯一化逻辑兼容中文场景
5. Task 5：回归验证并更新主设计文档

## 明确暂不实现

本轮不实现以下内容：

- 文章创建表单联动 slug 预览
- 手工自定义 slug 编辑功能
- 历史 slug 重定向
- 分类/标签实际 CRUD 页面
- 多语言 slug 策略切换
- SEO 扩展字段

