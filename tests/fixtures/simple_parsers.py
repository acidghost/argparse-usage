"""Simple test parser fixtures."""

import argparse


def create_simple_parser() -> argparse.ArgumentParser:
    """Create a simple ArgumentParser with basic flags and args."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A simple CLI tool",
    )
    parser.add_argument("-f", "--force", action="store_true", help="Force operation")
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )
    parser.add_argument("-o", "--output", default="output.txt", help="Output file")
    parser.add_argument("file", help="Input file")
    return parser


def create_parser_with_choices() -> argparse.ArgumentParser:
    """Create a parser with choice arguments."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with choices",
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "xml"],
        help="Output format",
    )
    parser.add_argument(
        "action", choices=["create", "update", "delete"], help="Action to perform"
    )
    return parser


def create_parser_with_variadic() -> argparse.ArgumentParser:
    """Create a parser with variadic arguments."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with variadic args",
    )
    parser.add_argument("files", nargs="+", help="Input files (one or more)")
    parser.add_argument("optional", nargs="*", help="Optional additional files")
    parser.add_argument("--tags", nargs="*", help="Tags to add")
    return parser


def create_parser_with_parent() -> argparse.ArgumentParser:
    """Create a parser with parent parser inheritance."""
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )
    parent_parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress output"
    )

    parser = argparse.ArgumentParser(
        prog="mycli",
        parents=[parent_parser],
        description="A CLI with parent parser",
    )
    parser.add_argument("file", help="Input file")
    return parser


def create_parser_with_subcommands() -> argparse.ArgumentParser:
    """Create a parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with subcommands",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add subcommand
    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("name", help="Name to add")
    add_cmd.add_argument("-f", "--force", action="store_true", help="Force add")

    # List subcommand
    list_cmd = subparsers.add_parser("list", help="List items")
    list_cmd.add_argument("-a", "--all", action="store_true", help="List all")
    list_cmd.add_argument("--sort", choices=["name", "date", "size"], help="Sort by")

    # Remove subcommand
    remove_cmd = subparsers.add_parser("remove", help="Remove item")
    remove_cmd.add_argument("name", help="Name to remove")

    return parser


def create_complex_parser() -> argparse.ArgumentParser:
    """Create a complex parser with many features."""
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )

    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A complex CLI tool",
        epilog="For more information, visit https://example.com",
        parents=[parent_parser],
    )

    # Add flags
    parser.add_argument("-f", "--file", help="Input file")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("-o", "--output", default="output.txt", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], help="Output format")

    # Positional arguments
    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("options", nargs="*", help="Additional options")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command")
    build_cmd = subparsers.add_parser("build", help="Build project")
    build_cmd.add_argument("--debug", action="store_true", help="Debug build")

    test_cmd = subparsers.add_parser("test", help="Run tests")
    test_cmd.add_argument("--verbose", action="count", help="Test verbosity")
    test_cmd.add_argument("tests", nargs="*", help="Specific tests to run")

    return parser
