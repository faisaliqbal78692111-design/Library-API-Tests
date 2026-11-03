import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://216.10.245.166/Library")
TIMEOUT_MS = float(os.getenv("API_TIMEOUT_MS", "15000"))
API_TOKEN = os.getenv("API_TOKEN", "")
# Optional API key header, sent only when API_KEY is set
API_KEY = os.getenv("API_KEY", "")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "x-api-key")
# On HTTP 429, wait for the server's reset time and retry (ReqRes free tier: 20 requests/minute)
RATE_LIMIT_RETRIES = int(os.getenv("RATE_LIMIT_RETRIES", "5"))
RATE_LIMIT_MAX_WAIT_S = float(os.getenv("RATE_LIMIT_MAX_WAIT_S", "65"))
# Which HTTP backend(s) to run tests with: playwright, requests, or both
API_CLIENT = os.getenv("API_CLIENT", "both").lower()
CLIENTS = ["playwright", "requests"] if API_CLIENT == "both" else [API_CLIENT]


def default_headers() -> dict:
    headers = {"Accept": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    if API_KEY:
        headers[API_KEY_HEADER] = API_KEY
    return headers
