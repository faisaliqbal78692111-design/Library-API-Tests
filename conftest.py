import uuid

import pytest

from framework import config
from framework.clients import PlaywrightClient, RequestsClient


def pytest_addoption(parser):
    parser.addoption(
        "--client",
        choices=["playwright", "requests", "both"],
        help="HTTP backend to run tests with (overrides API_CLIENT env var)",
    )


def pytest_generate_tests(metafunc):
    # Every test using the `api` fixture runs once per selected backend.
    if "api" in metafunc.fixturenames:
        opt = metafunc.config.getoption("--client")
        clients = config.CLIENTS if not opt else (["playwright", "requests"] if opt == "both" else [opt])
        metafunc.parametrize("api", clients, indirect=True, scope="session")


@pytest.fixture(scope="session")
def playwright_client(playwright):
    ctx = playwright.request.new_context(
        extra_http_headers=config.default_headers(),
        timeout=config.TIMEOUT_MS,
    )
    yield PlaywrightClient(ctx, config.BASE_URL)
    ctx.dispose()


@pytest.fixture(scope="session")
def requests_client():
    client = RequestsClient(config.BASE_URL, config.default_headers(), config.TIMEOUT_MS)
    yield client
    client.close()


@pytest.fixture(scope="session")
def api(request):
    # Resolve lazily so a requests-only run never starts Playwright.
    return request.getfixturevalue(f"{request.param}_client")


@pytest.fixture
def new_book(api):
    """Builds a book payload with a unique ISBN and deletes every book it made after the test.

    Unique ISBNs keep tests independent: the API rejects duplicates, and both backends
    (and parallel CI jobs) hit the same shared server.
    """
    created = []

    def make(name="Learn Appium Automation with Java", aisle="227", author="John foe"):
        book = {"name": name, "isbn": f"qa{uuid.uuid4().hex[:8]}", "aisle": str(aisle), "author": author}
        created.append(book["isbn"] + book["aisle"])
        return book

    yield make
    for book_id in created:
        api.post("/DeleteBook.php", json={"ID": book_id})
