"""JSON schemas for Library API responses, used with jsonschema.validate()."""

ADD_BOOK = {
    "type": "object",
    "required": ["Msg", "ID"],
    "properties": {"Msg": {"type": "string"}, "ID": {"type": "string"}},
}

# GET ?ID= returns a one-item list of these (the spec shows a single object)
BOOK_BY_ID = {
    "type": "object",
    "required": ["book_name", "isbn", "aisle", "author"],
    "properties": {
        "book_name": {"type": "string"},
        "isbn": {"type": "string"},
        "aisle": {"type": "string"},
        "author": {"type": "string"},
    },
}

# GET ?AuthorName= returns a list of these; aisle is a string although the spec says integer
BOOK_BY_AUTHOR = {
    "type": "object",
    "required": ["book_name", "isbn", "aisle"],
    "properties": {
        "book_name": {"type": "string"},
        "isbn": {"type": "string"},
        "aisle": {"type": "string"},
    },
}

MESSAGE = {
    "type": "object",
    "required": ["msg"],
    "properties": {"msg": {"type": "string"}},
}


def list_of(item_schema: dict) -> dict:
    return {"type": "array", "items": item_schema}
