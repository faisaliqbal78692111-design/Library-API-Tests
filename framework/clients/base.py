import logging
import time
from dataclasses import dataclass, field
from typing import Any

import allure

from framework import config

log = logging.getLogger("api")


def _retry_after_seconds(headers: dict) -> float | None:
    """Seconds to wait after a 429, from Retry-After or RateLimit-Reset.

    None means the limit won't reset soon (e.g. a daily quota), so retrying is pointless.
    """
    lower = {k.lower(): v for k, v in headers.items()}
    for name in ("retry-after", "ratelimit-reset"):
        try:
            wait = float(lower[name])
        except (KeyError, ValueError):
            continue
        return wait + 1 if wait <= config.RATE_LIMIT_MAX_WAIT_S else None
    return None


@dataclass
class Result:
    """Backend-agnostic response, so tests read the same for Playwright and Requests."""

    status: int
    url: str
    text: str
    headers: dict = field(default_factory=dict)
    elapsed_ms: float = 0.0

    def json(self) -> Any:
        import json

        return json.loads(self.text)


class ApiClient:
    """Common interface. Subclasses implement `_request` for a specific HTTP library."""

    name = "base"

    def _request(self, method: str, path: str, *, params=None, json=None, headers=None) -> Result:
        raise NotImplementedError

    def _send(self, method: str, path: str, **kwargs) -> Result:
        with allure.step(f"[{self.name}] {method} {path}"):
            for attempt in range(config.RATE_LIMIT_RETRIES + 1):
                start = time.perf_counter()
                result = self._request(method, path, **kwargs)
                result.elapsed_ms = (time.perf_counter() - start) * 1000
                if result.status != 429 or attempt == config.RATE_LIMIT_RETRIES:
                    break
                wait = _retry_after_seconds(result.headers)
                if wait is None:
                    log.error("[%s] 429 rate limit with no short reset; not retrying: %s", self.name, result.text[:300])
                    break
                log.warning("[%s] 429 rate limited on %s %s, retrying in %.0f s", self.name, method, path, wait)
                time.sleep(wait)
            log.info("[%s] %s %s -> %s (%.0f ms)", self.name, method, result.url, result.status, result.elapsed_ms)
            allure.attach(
                f"{method} {result.url}\nStatus: {result.status}\nTime: {result.elapsed_ms:.0f} ms\n"
                f"Request body: {kwargs.get('json')}\n\n{result.text[:4000]}",
                name="exchange",
                attachment_type=allure.attachment_type.TEXT,
            )
        return result

    def get(self, path, **kw):
        return self._send("GET", path, **kw)

    def post(self, path, **kw):
        return self._send("POST", path, **kw)

    def put(self, path, **kw):
        return self._send("PUT", path, **kw)

    def patch(self, path, **kw):
        return self._send("PATCH", path, **kw)

    def delete(self, path, **kw):
        return self._send("DELETE", path, **kw)
