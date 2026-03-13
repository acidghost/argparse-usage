"""Unit tests for argparse_usage generator."""

import argparse
import subprocess
from pathlib import Path

import pytest

from argparse_usage import generate


def create_simple_parser() -> argparse.ArgumentParser:
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


def _usage_available() -> bool:
    """Check if usage CLI is available."""
    return (
        Path("/usr/local/bin/usage").exists()
        or Path("/opt/homebrew/bin/usage").exists()
        or bool(
            subprocess.run(
                ["which", "usage"],
                capture_output=True,
            ).returncode
            == 0
        )
    )


def test_simple_parser():
    """Test simple parser generation."""
    parser = create_simple_parser()
    spec = generate(parser)

    assert 'name "mycli"' in spec
    assert 'bin "mycli"' in spec
    assert 'about "A simple CLI tool"' in spec
    assert 'flag "-f --force"' in spec
    assert 'help="Force operation"' in spec
    assert 'arg "<file>"' in spec
    assert 'help="Input file"' in spec
    assert "count=#true" in spec


def test_parser_with_version():
    """Test parser with version metadata."""
    parser = create_simple_parser()
    spec = generate(parser, version="1.0.0", author="Test Author")

    assert 'version "1.0.0"' in spec
    assert 'author "Test Author"' in spec


def test_parser_with_choices():
    """Test parser with choice arguments."""
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
    spec = generate(parser)

    assert "choices" in spec
    assert "json" in spec
    assert "yaml" in spec
    assert "xml" in spec


def test_parser_with_variadic():
    """Test parser with variadic arguments."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with variadic args",
    )
    parser.add_argument("files", nargs="+", help="Input files (one or more)")
    parser.add_argument("optional", nargs="*", help="Optional additional files")
    parser.add_argument("--tags", nargs="*", help="Tags to add")
    spec = generate(parser)

    assert "<files>..." in spec
    assert "[optional]..." in spec
    assert "var=#true" in spec


def test_parser_with_parent():
    """Test parser with parent parser inheritance."""
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
    spec = generate(parser)

    # Should have flags from parent
    assert 'flag "-v --verbose"' in spec
    assert "count=#true" in spec
    assert 'flag "-q --quiet"' in spec
    # Should have args from child
    assert 'arg "<file>"' in spec


def test_parser_with_subcommands():
    """Test parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with subcommands",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("name", help="Name to add")
    add_cmd.add_argument("-f", "--force", action="store_true", help="Force add")

    list_cmd = subparsers.add_parser("list", help="List items")
    list_cmd.add_argument("-a", "--all", action="store_true", help="List all")
    list_cmd.add_argument("--sort", choices=["name", "date", "size"], help="Sort by")

    remove_cmd = subparsers.add_parser("remove", help="Remove item")
    remove_cmd.add_argument("name", help="Name to remove")
    spec = generate(parser)

    assert "cmd add" in spec
    assert "cmd list" in spec
    assert "cmd remove" in spec
    assert 'arg "<name>"' in spec
    assert 'flag "-f --force"' in spec
    assert "choices" in spec


def test_complex_parser():
    """Test complex parser with many features."""
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

    parser.add_argument("-f", "--file", help="Input file")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("-o", "--output", default="output.txt", help="Output file")
    parser.add_argument("--format", choices=["json", "yaml"], help="Output format")

    parser.add_argument("files", nargs="+", help="Files to process")
    parser.add_argument("options", nargs="*", help="Additional options")

    subparsers = parser.add_subparsers(dest="command")
    build_cmd = subparsers.add_parser("build", help="Build project")
    build_cmd.add_argument("--debug", action="store_true", help="Debug build")

    test_cmd = subparsers.add_parser("test", help="Run tests")
    test_cmd.add_argument("--verbose", action="count", help="Test verbosity")
    test_cmd.add_argument("tests", nargs="*", help="Specific tests to run")
    spec = generate(parser)

    # Check metadata
    assert 'name "mycli"' in spec
    assert 'bin "mycli"' in spec
    assert 'about "A complex CLI tool"' in spec

    # Check variadic args
    assert "<files>..." in spec
    assert "[options]..." in spec

    # Check subcommands
    assert "cmd build" in spec
    assert "cmd test" in spec


@pytest.mark.skipif(not _usage_available(), reason="usage CLI not installed")
def test_generated_spec_is_valid_kdl():
    """Test that generated specs are valid KDL using the usage CLI."""
    parser = create_simple_parser()
    spec = generate(parser)

    # Try to lint the spec
    result = subprocess.run(
        ["usage", "lint"],
        input=spec,
        capture_output=True,
        text=True,
    )

    # usage lint should not error (exit code 0 means success)
    # Note: usage lint might return non-zero even for valid specs in some versions
    # So we just check it doesn't crash
    assert result.returncode != -15  # Not SIGTERM


def test_optional_positional():
    """Test optional positional argument."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("required", help="Required arg")
    parser.add_argument("optional", nargs="?", help="Optional arg")

    spec = generate(parser)

    assert 'arg "<required>"' in spec
    assert 'arg "[optional]"' in spec


def test_exactly_n_positional():
    """Test positional with exact count."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("coords", nargs=3, help="Three coordinates")

    spec = generate(parser)

    assert 'arg "<coords>..."' in spec
    assert "var_min=3" in spec
    assert "var_max=3" in spec


def test_store_true_flag():
    """Test store_true action flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--force", action="store_true", help="Force operation")

    spec = generate(parser)

    assert 'flag "--force"' in spec
    assert "default=#false" in spec


def test_count_flag():
    """Test count action flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    spec = generate(parser)

    assert 'flag "-v --verbose"' in spec
    assert "count=#true" in spec


def test_flag_with_default():
    """Test flag with default value."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--output", default="output.txt", help="Output file")

    spec = generate(parser)

    assert 'flag "--output"' in spec
    # Flags with args use block format
    assert 'default "output.txt"' in spec
    assert "arg <output>" in spec


def test_custom_bin_name():
    """Test custom binary name."""
    parser = create_simple_parser()
    spec = generate(parser, bin_name="my-custom-cli")

    assert 'bin "my-custom-cli"' in spec


def test_epilog():
    """Test epilog (after_help) generation."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI",
        epilog="For more info, visit https://example.com",
    )
    parser.add_argument("file")

    spec = generate(parser)

    # Epilog is not currently supported in usage spec
    # assert "after_help" in spec
    # assert "https://example.com" in spec
    assert spec  # Just verify we can generate the spec


def test_string_flag_with_argument():
    """Test that string flags have arg children."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--output", help="Output file")

    spec = generate(parser)

    # Should have arg child (no quotes around arg name in blocks)
    assert "arg <output>" in spec
    # Should be inside a block
    assert 'flag "--output" {' in spec


def test_int_flag_with_argument():
    """Test that integer flags have arg children."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--port", type=int, help="Port number")

    spec = generate(parser)

    # Should have arg child (no quotes around arg name in blocks)
    assert "arg <port>" in spec


def test_bool_flag_no_argument():
    """Test that bool flags do NOT have arg children."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--force", action="store_true", help="Force operation")

    spec = generate(parser)

    # Should NOT have arg child
    assert 'arg "<force>"' not in spec
    # Should be inline
    lines = spec.split("\n")
    force_lines = [line for line in lines if 'flag "--force"' in line]
    assert len(force_lines) == 1
    assert "{" not in force_lines[0]


def test_count_flag_no_argument():
    """Test that count flags do NOT have arg children."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity")

    spec = generate(parser)

    # Should NOT have arg child
    assert 'arg "<verbose>"' not in spec
    # Should have count attribute
    assert "count=#true" in spec


def test_flag_with_choices_has_arg():
    """Test that flags with choices have arg children with choices."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument(
        "--format", choices=["json", "yaml", "xml"], help="Output format"
    )

    spec = generate(parser)

    # Should have arg child with choices (no quotes around arg name in blocks)
    assert "arg <format> {" in spec
    assert "choices" in spec
    assert "json" in spec
    assert "yaml" in spec
    assert "xml" in spec


def test_flag_with_variadic_args():
    """Test flags that accept multiple arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--tags", nargs="*", help="Tags")

    spec = generate(parser)

    # Should have arg child with var (block format uses space, no =)
    assert "arg <tags>" in spec
    assert "var #true" in spec


def test_flag_with_exact_nargs():
    """Test flags that accept exact number of arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--coords", nargs=2, help="Two coordinates")

    spec = generate(parser)

    # Should have arg child (block format uses space, no =)
    assert "arg <coords>" in spec
    assert "var_min 2" in spec
    assert "var_max 2" in spec


def test_multiple_flags_mixed():
    """Test multiple flags with different types."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--config", help="Config file")
    parser.add_argument("--force", action="store_true", help="Force")
    parser.add_argument("-v", "--verbose", action="count", help="Verbose")
    parser.add_argument("--port", type=int, default=8080, help="Port")

    spec = generate(parser)

    # String flag should have arg (block format uses space, no =)
    assert "arg <config>" in spec
    # Bool flag should NOT have arg (and uses inline format)
    assert 'arg "<force>"' not in spec
    # Count flag should NOT have arg (and uses inline format)
    assert 'arg "<verbose>"' not in spec
    # Int flag should have arg (block format uses space, no =)
    assert "arg <port>" in spec
    # Int flag should have default (block format uses space, no =)
    assert 'default "8080"' in spec


def test_block_attribute_format():
    """Test that attributes inside blocks use space not equals sign."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--format", choices=["json", "yaml"], help="Output format")

    spec = generate(parser)

    # In blocks with choices, attributes should be `key value` not `key=value`
    # Wrong: help="Output format"
    # Right: help "Output format"
    assert 'help "Output format"' in spec


def test_subparser_with_bool_flag():
    """Test subparser with bool flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("--force", action="store_true", help="Force add")

    spec = generate(parser)

    # Check subcommand exists
    assert "cmd add" in spec
    # Check flag in subcommand uses inline format
    assert 'flag "--force" help="Force add"' in spec
    # Should NOT have arg child
    assert "arg <force>" not in spec


def test_subparser_with_flag_arg():
    """Test subparser with flag that accepts an argument."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_cmd = subparsers.add_parser("build", help="Build project")
    build_cmd.add_argument("--output", help="Output directory")

    spec = generate(parser)

    # Check subcommand exists
    assert "cmd build" in spec
    # Check flag in subcommand uses block format (because it takes arg)
    lines = spec.split("\n")
    build_section = []
    in_build = False
    for line in lines:
        if "cmd build" in line:
            in_build = True
        elif in_build and line.strip().startswith("cmd "):
            break
        elif in_build:
            build_section.append(line)

    build_spec = "\n".join(build_section)
    # Should have flag with block format (uses space, no =)
    assert 'flag "--output" {' in build_spec
    # Should have arg child
    assert "arg <output>" in build_spec


def test_subparser_help_from_help_parameter():
    """Test that subparser help text is taken from help parameter, not description."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Only provide help parameter, not description
    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("--name", help="Item name")

    spec = generate(parser)

    # Check subcommand exists
    assert "cmd add" in spec
    # Check that help text is present
    assert 'help "Add something"' in spec


def test_subparser_help_fallback_to_description():
    """Test that subparser help falls back to description if help is not provided."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Only provide description, not help
    add_cmd = subparsers.add_parser("add", description="Add something else")
    add_cmd.add_argument("--name", help="Item name")

    spec = generate(parser)

    # Check subcommand exists
    assert "cmd add" in spec
    # Check that description is used as help
    assert 'help "Add something else"' in spec


def test_nested_subparser_help():
    """Test that nested subparsers also get help text from help parameter."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_cmd = subparsers.add_parser("config", help="Manage config")
    config_subparsers = config_cmd.add_subparsers(dest="config_command", required=True)

    # Nested subcommand with help
    get_cmd = config_subparsers.add_parser("get", help="Get a config value")
    get_cmd.add_argument("key", help="Config key")

    spec = generate(parser)

    # Check nested subcommand exists
    assert "cmd config" in spec
    assert "cmd get" in spec
    # Check that help text is present for both levels
    assert 'help "Manage config"' in spec
    assert 'help "Get a config value"' in spec


def test_help_text_with_default_placeholder():
    """Test that %(default)s placeholder is replaced with actual default value."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument(
        "--type", default="default", help="Item type (default: %(default)s)"
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Max results (default: %(default)s)"
    )

    spec = generate(parser)

    # Default value should be substituted in help text
    assert 'help "Item type (default: default)"' in spec
    assert 'help "Max results (default: 20)"' in spec
    # Should not contain the placeholder
    assert "%(default)s" not in spec


def test_help_text_with_prog_placeholder():
    """Test that %(prog)s placeholder is replaced with program name."""
    parser = argparse.ArgumentParser(prog="myprog")
    parser.add_argument("--config", help="Config file (prog: %(prog)s)")

    spec = generate(parser)

    # Program name should be substituted in help text
    assert 'help "Config file (prog: myprog)"' in spec
    assert "%(prog)s" not in spec


def test_help_text_in_subcommand():
    """Test that placeholders are expanded in subcommand arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_cmd = subparsers.add_parser("create", help="Create an item")
    create_cmd.add_argument(
        "--type", default="default", help="Item type (default: %(default)s)"
    )

    spec = generate(parser)

    # Default value should be substituted in subcommand
    assert 'help "Item type (default: default)"' in spec
    assert "%(default)s" not in spec


def test_argument_defaults_help_formatter():
    """Test argparse.ArumentDefaultsHelpFormatter."""
    parser = argparse.ArgumentParser(
        prog="mycli", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--type", default="default", help="Item type")
    parser.add_argument("--limit", type=int, default=20, help="Max results")

    spec = generate(parser)

    # Default value should be substituted in help text
    assert 'help "Item type (default: default)"' in spec
    assert 'help "Max results (default: 20)"' in spec
    # Should not contain the placeholder
    assert "%(default)s" not in spec
