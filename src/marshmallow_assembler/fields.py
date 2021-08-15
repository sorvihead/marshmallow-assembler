import typing
from marshmallow.base import SchemaABC
from marshmallow.fields import Nested
from marshmallow import ValidationError
from src.marshmallow_assembler.types import IterableOrMapping
from src.marshmallow_assembler.base import BaseAssemblerSchema


class Relationship(Nested):
    def __init__(
        self,
        nested: typing.Union[SchemaABC, type, str, typing.Callable[[], SchemaABC]],
        *,
        on: typing.Callable[
            [typing.Mapping[str, typing.Any], typing.Mapping[str, typing.Any]], bool
        ],
        **kwargs
    ):
        super().__init__(nested, **kwargs)
        self._condition = on

    @property
    def schema(self) -> BaseAssemblerSchema:
        res = super().schema
        if not isinstance(res, BaseAssemblerSchema):
            raise TypeError(
                "All schemas in hierarchy must be a subclasses from AssemblerSchema"
            )
        return res

    def join(
        self,
        data: typing.Mapping[str, typing.Any],
        direct_relation: typing.Iterable[typing.Mapping[str, typing.Any]],
        inner_relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
    ) -> typing.Optional[IterableOrMapping]:
        if self.many:
            return self._one_to_many(data, direct_relation, inner_relations)
        else:
            return self._one_to_one(data, direct_relation, inner_relations)

    def _one_to_many(
        self,
        data: typing.Mapping[str, typing.Any],
        direct_relation: typing.Iterable[typing.Mapping[str, typing.Any]],
        inner_relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
    ) -> typing.List[typing.Mapping[str, typing.Any]]:
        return [
            self.schema.prepare_relationship_data(item, inner_relations, many=False)
            for item in direct_relation
            if self._condition(data, item)
        ]

    def _one_to_one(
        self,
        data: typing.Mapping[str, typing.Any],
        direct_relation: typing.Iterable[typing.Mapping[str, typing.Any]],
        inner_relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
    ) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        result = self._one_to_many(data, direct_relation, inner_relations)
        if not result:
            return None
        if len(result) == 1:
            return result[0]
        else:
            raise ValidationError(
                "One to one relationship must have one linked entity."
            )
