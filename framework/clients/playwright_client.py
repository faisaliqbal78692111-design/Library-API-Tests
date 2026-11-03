from playwright.sync_api import APIRequestContext

from framework.clients.base import ApiClient, Result


class PlaywrightClient(ApiClient):
    """Backend using Playwright's APIRequestContext."""

    name = "playwright"

    def __init__(self, context: APIRequestContext, base_url: str):
        self.context = context
        # Joined manually: Playwright's base_url drops a path prefix (e.g. /api) for paths starting with "/"
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, *, params=None, json=None, headers=None) -> Result:
        resp = self.context.fetch(f"{self.base_url}{path}", method=method, params=params, data=json, headers=headers)
        return Result(status=resp.status, url=resp.url, text=resp.text(), headers=resp.headers)
