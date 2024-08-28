from abc import ABC
from dataclasses import dataclass, field
from io import BytesIO
from itertools import count
from types import EllipsisType
from typing import Hashable, Iterable
from urllib.parse import quote
import webbrowser
from xml.etree.ElementTree import ElementTree

from rewire.container import FrozenDict, ImmutableDict

id_gen = count()


class Match:
    pass


@dataclass()
class MatchedDependency:
    dependency: int
    inherited: tuple["DependencySelector", ...]


class DependencySelector(ABC):
    def initial_candidates(self, graph: "DependencyGraph"):
        return [MatchedDependency(id(x), tuple()) for x in graph.dependencies]

    def candidates(
        self, previous: Iterable[MatchedDependency], graph: "DependencyGraph"
    ):
        pass

    def match(self, other: "DependencySelector") -> Match | None | EllipsisType:
        if not isinstance(other, type(self)):
            return ...
        return self == other


@dataclass(frozen=True)
class Typed[T](DependencySelector):
    type: type[T]

    def match(self, spec: "SearchSpec") -> tuple[DependencySelector, ...] | None:
        return None

    def __str__(self):
        return f"Typed({getattr(self.type, "__name__", self.type)})"


class SearchSpec:
    selectors: tuple[DependencySelector, ...]

    def __init__(self, *dependencies: DependencySelector):
        self.selectors = dependencies

    def add(self, *selector: DependencySelector):
        return SearchSpec(*self.selectors, *selector)

    def matching(self, other: "SearchSpec"):
        matched = []
        for selector in self.selectors:
            for i in other.selectors:
                if selector.matched(i):
                    matched.append(i)
                    break
            else:
                return None
        return matched

    def __hash__(self):
        return hash(self.selectors)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({", ".join(repr(x) for x in self.selectors)})"

    def __str__(self) -> str:
        return f"{type(self).__name__}({", ".join(str(x) for x in self.selectors)})"

    def _graphviz(self):
        return "\n".join(f"@{x}" for x in self.selectors)


@dataclass()
class Dependency:
    # TODO: remove?
    # id: int = field(default_factory=lambda: next(id_gen), kw_only=True)
    inputs: dict[str, SearchSpec]
    output: SearchSpec
    label: str
    indirect: list[SearchSpec] = field(default_factory=list)

    def _graphviz(self):
        import xml.etree.ElementTree as ET
        from graphviz.quoting import quote

        def add_br(root: ET.Element, text: str):
            current = root
            lines = text.splitlines()
            current.text = lines[0]
            for line in lines[1:]:
                current = ET.SubElement(root, "br", align="left")
                current.tail = line
            ET.SubElement(root, "br", align="left")

        a = ET.Element(
            "table", border="0", cellborder="1", cellspacing="0", cellpadding="4"
        )
        row = first_row = ET.SubElement(a, "tr")
        if self.inputs:
            for i, (input, input_spec) in enumerate(self.inputs.items()):
                add_br(
                    ET.SubElement(
                        row,
                        "td",
                        port=input,
                        align="left",
                    ),
                    f"{input}\n{input_spec._graphviz()}",
                )
                if i + 1 != len(self.inputs):
                    row = ET.SubElement(a, "tr")

        add_br(
            ET.SubElement(
                first_row,
                "td",
                port="return",
                rowspan=str(max(1, len(self.inputs))),
                align="left",
            ),
            f"{self.label}\n{self.output._graphviz()}",
        )

        out = BytesIO()
        ElementTree(a).write(out)
        out.seek(0)

        return f"{id(self)}", quote(f"<{out.read().decode()}>"), {"shape": "plain"}


@dataclass(frozen=True)
class GraphLink:
    source: int
    into: str | None = None
    direct: bool = False


@dataclass
class CompiledGraph:
    dependencies: ImmutableDict[int, Dependency]
    links: FrozenDict[int, tuple[GraphLink, ...]]

    def graphviz(self):
        from graphviz import Digraph

        graph = Digraph()
        graph.node
        for node in self.dependencies.values():
            graph.node(*node._graphviz())
        for node, links in self.links.items():
            for link in links:
                if link.into is None:
                    graph.edge(
                        f"{link.source}:return:e", f"{node}:return:n", style="dashed"
                    )
                else:
                    graph.edge(f"{link.source}:return:e", f"{node}:{link.into}:w")
        return graph


@dataclass()
class DependencyGraph:
    dependencies: list[Dependency]
    compiled: CompiledGraph | None = None

    def compile(self) -> CompiledGraph:
        if self.compiled is not None:
            return self.compiled
        dependencies = ImmutableDict({id(x): x for x in self.dependencies})

        def solve_one(dependency: Dependency):
            for spec in dependency.indirect:
                for dependency in self.dependencies:
                    pass
            return (GraphLink(id(pre_migrate_database)),)

        self.compiled = CompiledGraph(
            dependencies, FrozenDict({id(x): solve_one(x) for x in self.dependencies})
        )

        return self.compiled


@dataclass(frozen=True)
class Marked[T: Hashable](DependencySelector):
    mark: T

    # def __spec_key__(self) -> ContainerKey[Self, Self]:
    #     return ContainerKey(self, self)

    def match(self, spec: "SearchSpec") -> bool:
        return True


@dataclass(frozen=True)
class Tagged(Marked[str]):
    # def __spec_key__(self) -> ContainerKey[Self, Self]:
    #     return ContainerKey(self, self)

    def match(self, spec: "SearchSpec") -> bool:
        return True


@dataclass(frozen=True)
class Labeled(DependencySelector):
    label: str
    value: str

    # def __spec_key__(self) -> ContainerKey[Self, Self]:
    #     return ContainerKey(self, self)

    def match(self, spec: "SearchSpec") -> bool:
        return True

    @classmethod
    def template(cls, label: str):
        def result(value: str):
            return cls(label, value)

        return result


class DatabaseConfig: ...


class Database: ...


a = SearchSpec(Tagged("1"))
b = SearchSpec(Tagged("1"))
b.matching(a)

create_database_config = Dependency(
    {},
    SearchSpec(Typed(DatabaseConfig)),
    "create_database_config",
)
connect_database = Dependency(
    {
        "config": SearchSpec(Typed(DatabaseConfig)),
    },
    SearchSpec(Typed(Database)),
    "create_database",
)
check_db_connection = Dependency(
    {
        "db": SearchSpec(Typed(Database)),
    },
    SearchSpec(),
    "check_db_connection",
)
pre_migrate_database = Dependency(
    {
        "db": SearchSpec(Typed(Database)),
    },
    SearchSpec(Marked("pre-migrate")),
    "pre_migrate_database",
    [check_db_connection.output],
)
generate_migrations = Dependency(
    {
        "config": SearchSpec(Typed(DatabaseConfig)),
        "db": SearchSpec(Typed(Database)),
    },
    SearchSpec(Marked("generate-migrations")),
    "generate_migrations",
    [pre_migrate_database.output],
)
post_migrate_database = Dependency(
    {
        "db": SearchSpec(Typed(Database)),
    },
    SearchSpec(Marked("post-migrate")),
    "post_migrate_database",
    [generate_migrations.output],
)

graph = DependencyGraph(
    [
        create_database_config,
        connect_database,
        check_db_connection,
        pre_migrate_database,
        generate_migrations,
        post_migrate_database,
    ]
)
compiled = graph.compile()
source = (
    CompiledGraph(
        ImmutableDict({id(x): x for x in graph.dependencies}),
        FrozenDict(
            {
                id(connect_database): (
                    GraphLink(id(create_database_config), "config"),
                ),
                id(check_db_connection): (GraphLink(id(connect_database), "db"),),
                id(pre_migrate_database): (
                    GraphLink(id(connect_database), "db"),
                    GraphLink(id(check_db_connection)),
                ),
                id(generate_migrations): (
                    GraphLink(id(connect_database), "db"),
                    GraphLink(id(create_database_config), "config"),
                    GraphLink(id(pre_migrate_database)),
                ),
                id(post_migrate_database): (
                    GraphLink(id(connect_database), "db"),
                    GraphLink(id(generate_migrations)),
                ),
            }
        ),
    )
    .graphviz()
    .source
)
webbrowser.open(f"https://dreampuf.github.io/GraphvizOnline/#{quote(source)}")
