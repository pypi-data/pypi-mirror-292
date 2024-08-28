from typing import Dict, Generic, Iterator, TypeVar


T = TypeVar("T")
K = TypeVar("K")


class Dictionary(Generic[T, K]):

    def __init__(self, data: Dict[T, K] | None = None):
        self._data = data or {}

    def to_dict(self) -> Dict[T, K]:
        return self._data

    def add(self, key: T, value: K) -> "Dictionary[T, K]":
        self._data[key] = value
        return self

    def remove(self, key: T) -> K:
        return self._data.pop(key)

    def at_key(self, key: T) -> K:
        return self._data[key]

    def keys(self) -> Iterator[T]:
        return iter(self._data.keys())

    def values(self) -> Iterator[K]:
        return iter(self._data.values())

    # Magic Methods

    def __getitem__(self, key: T) -> K:
        return self.at_key(key)

    def __setitem__(self, key: T, value: K) -> None:
        self.add(key, value)

    def __bool__(self) -> bool:
        return bool(self._data)
