"""In-memory login attempt limiter. Suitable for a small 10–15 user deployment."""

from __future__ import annotations

import time
from collections import defaultdict

from app.core.config import get_settings
from app.core.exceptions import AppError


class LoginAttemptTracker:
    def __init__(self) -> None:
        self._failures: dict[str, list[float]] = defaultdict(list)

    def _prune(self, key: str, now: float, window: int) -> None:
        self._failures[key] = [stamp for stamp in self._failures[key] if now - stamp < window]

    def check(self, key: str) -> None:
        settings = get_settings()
        now = time.time()
        self._prune(key, now, settings.login_lockout_seconds)
        if len(self._failures[key]) >= settings.login_max_attempts:
            raise AppError(
                "Too many sign-in attempts. Please wait a few minutes and try again.",
                status_code=429,
                code="RATE_LIMITED",
            )

    def record_failure(self, key: str) -> None:
        self._failures[key].append(time.time())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


login_attempts = LoginAttemptTracker()
