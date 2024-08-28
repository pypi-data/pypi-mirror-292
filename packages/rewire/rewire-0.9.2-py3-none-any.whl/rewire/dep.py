from abc import ABC
from dataclasses import dataclass
from typing import LiteralString

from rewire.container import ContainerKey, ImmutableContainer

UNSET = object()


class DependencySelector(ABC):
    def __container_key__(self):
        return ContainerKey(type(self), self)


class OutputDependencySelector(DependencySelector):
    """Dependency selector that can be easily matched by complex search spec"""


@dataclass(frozen=True)
class Marked[T](OutputDependencySelector):
    mark: T


@dataclass(frozen=True)
class Typed[T: type](OutputDependencySelector):
    type: T


@dataclass(frozen=True)
class Tagged[T: LiteralString](OutputDependencySelector):
    tag: T


class OutputSpec:
    dependencies: ImmutableContainer[OutputDependencySelector]


class SearchSpec:
    dependencies: list[DependencySelector]


d = OutputSpec().dependencies.find(Typed(int))
