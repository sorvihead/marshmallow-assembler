# marshmallow-assembler
Plugin for converting one-to-many relationships to Python objects

## Declare your Domain Models
```python3
@dataclass
class Book:
  id: int
  name: str


@dataclass
class Author:
  id: int
  name: str
  rank: float
  books: List[Book]
```

## Generate Marshmallow schemas
```python3
class BookSchema(AssemblerSchema):
  __model__ = Book
  id = fields.Integer()
  name = fields.String()


class AuthorSchema(AssemblerSchema):
  __model__ = Author
  id = fields.Integer()
  name = fields.String()
  rank = fields.Float()
  books = fields.Relationship(BookSchema, on=lambda self, inner: inner["id"] in self["books"], many=True)
```

## Load data by AssemblerSchema
```python3
books = [{"id": 1, "name": "The last wish"}, {"id": 2, "name": "Sword of Destiny"}, {"id": 3, "name": "Blood of Elves"}]
author = {"id": 1, "name": "Andzhey Sapkovsky", "rank": 10.0, "books": [1, 2, 3]}
schema = AuthorSchema()
print(schema.load(author, books=books))
>>> Author(id=1, name="Andzhey Sapkovsky", rank=10.0, books=[Book(id=1, name="The last wish"), Book(id=2, name="Sword of Destiny"), Book(id=3, name="Blood of Elves")])
```
