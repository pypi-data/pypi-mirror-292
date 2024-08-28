from abc import ABC, abstractmethod
from collections import UserDict
from types import MappingProxyType
from typing import Any, Callable, Hashable, Iterable, Mapping, Protocol, overload

from rewire.dep import UNSET


class ImmutableDict[K, V](Mapping[K, V]):
    """Dict with locked keys and values, values still can be mutated"""

    __slots__ = ("container",)

    def __init__(self, container: Mapping[K, V]) -> None:
        self.container = MappingProxyType(dict(container))

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "container" and name not in dir(self):
            super().__setattr__(name, value)
            return
        raise NotImplementedError("FrozenDict is immutable")

    def __getattribute__(self, name: str) -> Any:
        if name in (
            "__hash__",
            "container",
            "__init__",
            "__str__",
            "__repr__",
            "__getitem__",
        ):
            return super().__getattribute__(name)
        return getattr(self.container, name)

    def __getitem__(self, key: K):
        return self.container[key]

    def __str__(self) -> Any:
        return f"FrozenDict({self.container!s})"

    def __repr__(self) -> Any:
        return f"FrozenDict({self.container!r})"

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        return iter(self.container)

    def updated(self, data: Mapping[K, V]):
        return type(self)({**self, **data})


class FrozenDict[K: Hashable, V: Hashable](ImmutableDict[K, V]):
    """Dict that cannot be changed in any way"""

    __slots__ = ("container",)

    def __init__(self, container: Mapping[K, V]) -> None:
        super().__init__(container)
        hash(self)  # ensure that this dict is hashable

    def __hash__(self) -> int:
        return hash(tuple((k, v) for k, v in self.container.items()))


class ContainerKey[K: Hashable, I]:
    """Key for Container that returns I upon getting"""

    key: K
    item: I

    @overload
    def __init__(self, key: K) -> None: ...
    @overload
    def __init__(self, key: K, value: I) -> None: ...
    def __init__(self, key, value=UNSET) -> None:
        self.key = key
        if value is not UNSET:
            self.item = value  # type: ignore

    def __container_key__(self):
        return self


class HasContainerKey[I](Protocol):
    __container_key__: Callable[[], ContainerKey[Any, I]]


class _ContainerBase[T: HasContainerKey](ABC):
    def get[I, F](self, item: HasContainerKey[I], default: F = None) -> I | F:
        key = item.__container_key__()
        if self.contains(key):
            return self.find(key)  # type: ignore
        return default

    def find[I](self, item: HasContainerKey[I]) -> I:
        return self[item.__container_key__().key]  # type: ignore

    def contains[I](self, item: HasContainerKey[I]) -> bool:
        return item.__container_key__().key in self  # type: ignore

    def with_set(self, item: HasContainerKey[T]):
        value = item.__container_key__()
        return type(self)({**self} | {value.key: value.item})  # type: ignore

    def with_updated(self, items: Iterable[HasContainerKey[T]]):
        return type(self)(
            {**self}  # type: ignore
            | {
                value.key: value.item
                for value in map(lambda x: x.__container_key__(), items)
            }
        )


class Container[T: HasContainerKey](UserDict, _ContainerBase[T]):
    """Type safe mapping that returns type based on key provided"""

    def set(self, item: HasContainerKey[T]):
        value = item.__container_key__()
        self[value.key] = value.item

    def update(self, items: Iterable[HasContainerKey[T]]):
        for item in items:
            self.set(item)


class ImmutableContainer[T: HasContainerKey](FrozenDict, _ContainerBase[T]):
    """Type safe mapping that returns type based on key provided, cannot be mutated"""


class FrozenContainer[T: HasContainerKey](FrozenDict, _ContainerBase[T]):
    """Type safe mapping that returns type based on key provided, cannot be changed in any way"""
