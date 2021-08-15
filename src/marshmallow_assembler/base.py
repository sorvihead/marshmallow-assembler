from abc import abstractmethod
import typing
from marshmallow import Schema
from marshmallow.decorators import post_load

from src.marshmallow_assembler.types import IterableOrMapping


class BaseAssemblerSchema(Schema):
    __model__: typing.Optional[type] = None

    @post_load
    def make_object(self, data, **kwargs):
        if not self.__model__:
            return data
        return self.__model__(**data)

    @abstractmethod
    def prepare_relationship_data(
        self,
        original: IterableOrMapping,
        relations: typing.Mapping[
            str, typing.Iterable[typing.Mapping[str, typing.Any]]
        ],
        many: bool,
    ):
        raise NotImplementedError("Subclasses must implement all methods of base class")
