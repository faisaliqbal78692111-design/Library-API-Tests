# Library API Tests (Playwright + Requests + pytest)

Automated tests for the Library API at `http://216.10.245.166/Library`, built on the shared
API automation framework (`framework/`). Every test runs on both Playwright and Python Requests.

## Endpoints covered
| Endpoint | Method | Tests |
|---|---|---|
| `/Addbook.php` | POST | add (3 books from CSV), duplicate add, schema |
| `/GetBook.php?ID=` | GET | book details, schema, 404 for unknown ID |
| `/GetBook.php?AuthorName=` | GET | returns all of an author's books, schema, 404 for unknown author |
| `/DeleteBook.php` | POST | delete, confirm gone, 404 for unknown ID |

`test_book_lifecycle` (smoke) runs the full flow: add, get by ID, get by author, delete, confirm deleted.
Each test creates books with a unique ISBN and deletes them afterwards, so runs never collide.

## Differences between the API spec and real behaviour
The tests follow what the API actually returns:
- `GET ?ID=` returns a **list** with one book (including `author`), not a single object.
- `aisle` is returned as a **string** (`"227"`); the spec says integer.
- Adding an existing book returns **200** with `"Msg": "Book Already Exists"`.
- Unknown ID or author returns **404** with a `msg` explaining the book does not exist.

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

pytest -n auto              # all tests, both backends, in parallel
pytest -m smoke             # lifecycle test only
pytest --client requests    # one backend only
start reports\report.html
```

## Add test cases
- New books to add: add a row to `test-data/books.csv`.
- New error cases: add an entry to `test-data/negative_cases.json`.

## CI
`.github/workflows/api-tests.yml` runs on push, pull request, nightly and on demand, with a job per backend,
HTML report artifacts and an Allure report on GitHub Pages (`gh-pages` branch).
Override the target with the repo variable `BASE_URL`.
