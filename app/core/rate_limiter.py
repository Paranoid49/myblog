"""轻量级内存速率限制器。

适合单进程部署场景，不引入 Redis 等外部依赖。
"""

import time
from collections import defaultdict


class InMemoryRateLimiter:
    """基于内存的滑动窗口速率限制器"""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300) -> None:
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)

    def is_blocked(self, key: str) -> bool:
        """检查指定 key 是否已超过限制"""
        now = time.monotonic()
        # 清理过期记录
        self._attempts[key] = [
            t for t in self._attempts[key] if now - t < self.window
        ]
        return len(self._attempts[key]) >= self.max_attempts

    def record(self, key: str) -> None:
        """记录一次尝试"""
        self._attempts[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        """重置指定 key 的记录（登录成功时调用）"""
        self._attempts.pop(key, None)


# 登录速率限制器：5 分钟内最多 5 次失败尝试
login_limiter = InMemoryRateLimiter(max_attempts=5, window_seconds=300)
