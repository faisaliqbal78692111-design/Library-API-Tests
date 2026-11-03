import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from framework.clients.base import ApiClient, Result


class RequestsClient(ApiClient):
    """Backend using python-requests with a pooled Session and retries on transient errors."""

    name = "requests"

    def __init__(self, base_url: str, headers: dict, timeout_ms: float, retries: int = 2):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_ms / 1000
        self.session = requests.Session()
        self.session.headers.update(headers)
        retry = Retry(total=retries, backoff_factor=0.5, status_forcelist=[502, 503, 504], allowed_methods=None)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))

    def _request(self, method, path, *, params=None, json=None, headers=None) -> Result:
        resp = self.session.request(
            method, f"{self.base_url}{path}", params=params, json=json, headers=headers, timeout=self.timeout
        )
        return Result(status=resp.status_code, url=resp.url, text=resp.text, headers=dict(resp.headers))

    def close(self):
        self.session.close()
