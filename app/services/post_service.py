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
    return slug or "post"


def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing_slugs:
        index += 1
    return f"{base_slug}-{index}"
