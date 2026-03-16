"""轻量级内存速率限制器。

适合单进程部署场景，不引入 Redis 等外部依赖。
"""

import time
from collections import defaultdict


class InMemoryRateLimiter:
    """基于内存的滑动窗口速率限制器"""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300, cleanup_interval: int = 100) -> None:
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._cleanup_interval = cleanup_interval
        self._call_count = 0
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def is_blocked(self, key: str) -> bool:
        """检查指定 key 是否已超过限制"""
        # 定期清理所有 key 的过期记录，防止内存泄漏
        self._call_count += 1
        if self._call_count % self._cleanup_interval == 0:
            self._cleanup_expired()

        now = time.monotonic()
        # 清理当前 key 的过期记录
        self._attempts[key] = [t for t in self._attempts[key] if now - t < self.window]
        return len(self._attempts[key]) >= self.max_attempts

    def _cleanup_expired(self) -> None:
        """清理所有 key 中的过期记录，防止内存泄漏"""
        now = time.monotonic()
        expired_keys = [k for k, v in self._attempts.items() if all(now - t >= self.window for t in v)]
        for k in expired_keys:
            del self._attempts[k]

    def record(self, key: str) -> None:
        """记录一次尝试"""
        self._attempts[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        """重置指定 key 的记录（登录成功时调用）"""
        self._attempts.pop(key, None)


# 登录速率限制器：5 分钟内最多 5 次失败尝试
login_limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=300)
