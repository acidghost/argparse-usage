"""Internal AST representation for usage spec."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Spec:
    """Root usage spec node."""

    name: str | None = None
    bin: str | None = None
    version: str | None = None
    author: str | None = None
    about: str | None = None
    children: list = field(default_factory=list)


@dataclass
class Flag:
    """Flag/option node."""

    short: str | None = None
    long: str | None = None
    help: str | None = None
    required: bool = False
    default: Any = None
    count: bool = False
    var: bool = False
    var_min: int | None = None
    var_max: int | None = None
    choices: list[str] | None = None
    long_help: str | None = None
    takes_arg: bool = False


@dataclass
class Arg:
    """Positional argument node."""

    name: str
    help: str | None = None
    required: bool = True
    default: Any = None
    var: bool = False
    var_min: int | None = None
    var_max: int | None = None
    choices: list[str] | None = None
    long_help: str | None = None


@dataclass
class Cmd:
    """Command/subcommand node."""

    name: str
    help: str | None = None
    children: list = field(default_factory=list)
