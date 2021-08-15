import typing


IterableOrMapping = typing.Union[
    typing.Mapping[str, typing.Any], typing.Iterable[typing.Mapping[str, typing.Any]]
]
