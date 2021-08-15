from marshmallow import types

import typing

from src.marshmallow_assembler.base import BaseAssemblerSchema
from src.marshmallow_assembler.types import IterableOrMapping

from src.marshmallow_assembler.fields import Relationship


class AssemblerSchema(BaseAssemblerSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._relationships: typing.Dict[str, Relationship] = {}
        self._move_relationships_from_fields()

    def _move_relationships_from_fields(self):
        attrs = list(self.fields.keys())
        for attr_name in attrs:
            if isinstance(self.fields[attr_name], Relationship):
                self._relationships[attr_name] = typing.cast(
                    Relationship, self.fields.pop(attr_name)
                )

    def load(
        self,
        data: typing.Union[
            typing.Mapping[str, typing.Any],
            typing.Iterable[typing.Mapping[str, typing.Any]],
        ],
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None,
        unknown: typing.Optional[str] = None,
        **relation_data
    ):
        if relation_data:
            processed_data = self.prepare_relationship_data(
                data, relation_data, many=many
            )
        else:
            processed_data = data
        return super().load(processed_data, many=many, partial=partial, unknown=unknown)

    def prepare_relationship_data(
        self,
        original: IterableOrMapping,
        relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
        many: typing.Optional[bool],
    ):
        many = self.many if many is None else many

        inner_relationship_keys = set(relations.keys()) - self._relationships.keys()
        inner_relations = {key: relations[key] for key in inner_relationship_keys}

        if many:
            return self._join_iterable_sequence(
                typing.cast(typing.Iterable[typing.Mapping[str, typing.Any]], original),
                relations,
                inner_relations,
            )
        else:
            return self._join_scalar_data(
                typing.cast(typing.Mapping[str, typing.Any], original),
                relations,
                inner_relations,
            )

    def _join_iterable_sequence(
        self,
        original: typing.Iterable[typing.Mapping[str, typing.Any]],
        relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
        inner_relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
    ):
        joined_collection = []
        for item in original:
            joined_collection.append(
                self._join_scalar_data(item, relations, inner_relations)
            )
        return joined_collection

    def _join_scalar_data(
        self,
        original: typing.Mapping[str, typing.Any],
        relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
        inner_relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
    ):
        extra_data = {}
        for attr_name, joiner in self._relationships.items():
            relation = relations[attr_name]
            extra_data[attr_name] = joiner.join(original, relation, inner_relations)
        return {**original, **extra_data}


if __name__ == "__main__":
    from marshmallow import fields
    from dataclasses import dataclass
    from typing import List

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

    class BookSchema(AssemblerSchema):
        __model__ = Book
        id = fields.Integer()
        name = fields.String()

    class AuthorSchema(AssemblerSchema):
        __model__ = Author
        id = fields.Integer()
        name = fields.String()
        rank = fields.Float()
        books = Relationship(
            BookSchema, on=lambda self, inner: inner["id"] in self["books"], many=True
        )

    books = [
        {"id": 1, "name": "The last wish"},
        {"id": 2, "name": "Sword of Destiny"},
        {"id": 3, "name": "Blood of Elves"},
    ]
    author = {"id": 1, "name": "Andzhey Sapkovsky", "rank": 10.0, "books": [1, 2, 3]}
    schema = AuthorSchema()
    print(schema.load(author, books=books))
