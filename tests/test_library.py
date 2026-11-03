import uuid

import allure
import pytest
from jsonschema import validate

from framework import schemas
from framework.data_loader import load_csv, load_json


@allure.feature("Library")
class TestLibrary:
    @pytest.mark.smoke
    def test_book_lifecycle(self, api, new_book):
        """Add -> get by ID -> get by author -> delete -> confirm gone."""
        book = new_book(author="Lifecycle QA")
        book_id = book["isbn"] + book["aisle"]

        with allure.step("Add book"):
            r = api.post("/Addbook.php", json=book)
            assert r.status == 200
            assert r.json() == {"Msg": "successfully added", "ID": book_id}

        with allure.step("Get by ID"):
            r = api.get("/GetBook.php", params={"ID": book_id})
            assert r.status == 200
            assert r.json() == [
                {"book_name": book["name"], "isbn": book["isbn"], "aisle": book["aisle"], "author": book["author"]}
            ]

        with allure.step("Get by author"):
            r = api.get("/GetBook.php", params={"AuthorName": book["author"]})
            assert r.status == 200
            assert {"book_name": book["name"], "isbn": book["isbn"], "aisle": book["aisle"]} in r.json()

        with allure.step("Delete"):
            r = api.post("/DeleteBook.php", json={"ID": book_id})
            assert r.status == 200
            assert r.json()["msg"] == "book is successfully deleted"

        with allure.step("Confirm deleted"):
            assert api.get("/GetBook.php", params={"ID": book_id}).status == 404

    @pytest.mark.regression
    @pytest.mark.parametrize("row", load_csv("books.csv"), ids=lambda r: r["name"])
    def test_add_book_data_driven(self, api, new_book, row):
        book = new_book(name=row["name"], aisle=row["aisle"], author=row["author"])
        r = api.post("/Addbook.php", json=book)
        assert r.status == 200
        body = r.json()
        validate(body, schemas.ADD_BOOK)
        assert body["Msg"] == "successfully added"
        assert body["ID"] == book["isbn"] + book["aisle"]

    @pytest.mark.regression
    def test_add_duplicate_book(self, api, new_book):
        book = new_book()
        assert api.post("/Addbook.php", json=book).status == 200
        r = api.post("/Addbook.php", json=book)
        assert r.status == 200
        assert r.json()["Msg"] == "Book Already Exists"

    @pytest.mark.regression
    def test_get_book_by_id_schema(self, api, new_book):
        book = new_book()
        api.post("/Addbook.php", json=book)
        r = api.get("/GetBook.php", params={"ID": book["isbn"] + book["aisle"]})
        assert r.status == 200
        validate(r.json(), schemas.list_of(schemas.BOOK_BY_ID))
        assert len(r.json()) == 1

    @pytest.mark.regression
    def test_get_books_by_author_returns_all(self, api, new_book):
        author = f"qa-author-{uuid.uuid4().hex[:8]}"  # unique so only this test's books match
        books = [new_book(name=f"Book {i}", aisle=str(100 + i), author=author) for i in range(3)]
        for book in books:
            assert api.post("/Addbook.php", json=book).status == 200

        r = api.get("/GetBook.php", params={"AuthorName": author})
        assert r.status == 200
        validate(r.json(), schemas.list_of(schemas.BOOK_BY_AUTHOR))
        assert sorted(b["isbn"] for b in r.json()) == sorted(b["isbn"] for b in books)

    @pytest.mark.regression
    @pytest.mark.parametrize("case", load_json("negative_cases.json"), ids=lambda c: c["name"])
    def test_negative_data_driven(self, api, case):
        if case["method"] == "GET":
            r = api.get(case["path"], params=case["params"])
        else:
            r = api.post(case["path"], json=case["body"])
        assert r.status == case["expectedStatus"]
        validate(r.json(), schemas.MESSAGE)
        assert r.json()["msg"] == case["expectedMsg"]
