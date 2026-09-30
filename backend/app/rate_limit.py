from time import monotonic

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    """Simple per-process rate limiter for authentication endpoints."""

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = {}

    def reset(self) -> None:
        self._hits.clear()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = monotonic()
        recent = [
            timestamp
            for timestamp in self._hits.get(key, [])
            if now - timestamp < window_seconds
        ]
        if len(recent) >= limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
            )
        recent.append(now)
        self._hits[key] = recent


limiter = InMemoryRateLimiter()


def client_key(request: Request, scope: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{scope}:{client_host}"
