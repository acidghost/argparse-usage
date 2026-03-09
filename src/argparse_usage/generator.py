"""Generate usage specs from argparse.ArgumentParser."""

import argparse

from argparse_usage.parser import _generate_ast
from argparse_usage.formatter import _KDLFormatter


def generate_usage_spec(
    parser: argparse.ArgumentParser,
    name: str | None = None,
    version: str | None = None,
    author: str | None = None,
    bin_name: str | None = None,
) -> str:
    """Generate a usage spec KDL string from an ArgumentParser.

    Args:
        parser: The ArgumentParser instance to convert.
        name: The friendly name for the CLI (defaults to parser.prog or description).
        version: The version of the CLI.
        author: The author of the CLI.
        bin_name: The binary name (defaults to parser.prog).

    Returns:
        A KDL-formatted usage spec string.
    """
    ast = _generate_ast(
        parser=parser, name=name, version=version, author=author, bin_name=bin_name
    )
    formatter = _KDLFormatter()
    return formatter.format(ast)
