"""Unit tests for argparse to spec conversion."""

import argparse

from argparse_usage._argparse import _generate_spec
from argparse_usage._usage import Arg, Cmd, Flag


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


def test_simple_parser():
    """Test simple parser generation."""
    parser = create_simple_parser()
    spec = _generate_spec(parser)

    assert spec.name == "mycli"
    assert spec.bin == "mycli"
    assert spec.about == "A simple CLI tool"

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 3

    force = next((f for f in flags if f.long == "--force"), None)
    assert force is not None
    assert force.short == "-f"
    assert force.help == "Force operation"

    verbose = next((f for f in flags if f.long == "--verbose"), None)
    assert verbose is not None
    assert verbose.short == "-v"
    assert verbose.count is True

    output = next((f for f in flags if f.long == "--output"), None)
    assert output is not None
    assert output.default == "output.txt"

    args = [c for c in spec.children if isinstance(c, Arg)]
    assert len(args) == 1
    assert args[0].name == "file"
    assert args[0].help == "Input file"


def test_parser_with_version():
    """Test parser with version metadata."""
    parser = create_simple_parser()
    spec = _generate_spec(parser, version="1.0.0", author="Test Author")

    assert spec.version == "1.0.0"
    assert spec.author == "Test Author"


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
    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    format_flag = flags[0]
    assert format_flag.choices == ["json", "yaml", "xml"]

    args = [c for c in spec.children if isinstance(c, Arg)]
    action_arg = args[0]
    assert action_arg.choices == ["create", "update", "delete"]


def test_parser_with_variadic():
    """Test parser with variadic arguments."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI with variadic args",
    )
    parser.add_argument("files", nargs="+", help="Input files (one or more)")
    parser.add_argument("optional", nargs="*", help="Optional additional files")
    parser.add_argument("--tags", nargs="*", help="Tags to add")
    spec = _generate_spec(parser)

    args = [c for c in spec.children if isinstance(c, Arg)]
    files_arg = next((a for a in args if a.name == "files"), None)
    assert files_arg is not None
    assert files_arg.var is True
    assert files_arg.var_min == 1
    assert files_arg.var_max is None

    optional_arg = next((a for a in args if a.name == "optional"), None)
    assert optional_arg is not None
    assert optional_arg.var is True
    assert optional_arg.var_min == 0
    assert optional_arg.var_max is None

    tags_flag = [c for c in spec.children if isinstance(c, Flag)][0]
    assert tags_flag.long == "--tags"
    assert tags_flag.var is True
    assert tags_flag.var_min == 0


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
    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 2

    verbose = next((f for f in flags if f.long == "--verbose"), None)
    assert verbose is not None
    assert verbose.count is True

    quiet = next((f for f in flags if f.long == "--quiet"), None)
    assert quiet is not None

    args = [c for c in spec.children if isinstance(c, Arg)]
    assert len(args) == 1
    assert args[0].name == "file"


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
    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 3

    add = next((c for c in cmds if c.name == "add"), None)
    assert add is not None
    assert add.help == "Add something"

    add_args = [c for c in add.children if isinstance(c, Arg)]
    assert len(add_args) == 1
    assert add_args[0].name == "name"

    list_cmd_obj = next((c for c in cmds if c.name == "list"), None)
    assert list_cmd_obj is not None
    sort_flag = next(
        (
            f
            for f in list_cmd_obj.children
            if isinstance(f, Flag) and f.long == "--sort"
        ),
        None,
    )
    assert sort_flag is not None
    assert sort_flag.choices == ["name", "date", "size"]


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
    spec = _generate_spec(parser)

    assert spec.name == "mycli"
    assert spec.bin == "mycli"
    assert spec.about == "A complex CLI tool"

    args = [c for c in spec.children if isinstance(c, Arg)]
    files_arg = next((a for a in args if a.name == "files"), None)
    assert files_arg is not None
    assert files_arg.var is True

    options_arg = next((a for a in args if a.name == "options"), None)
    assert options_arg is not None
    assert options_arg.var is True

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 2

    build = next((c for c in cmds if c.name == "build"), None)
    assert build is not None
    assert build.help == "Build project"

    test_cmd_obj = next((c for c in cmds if c.name == "test"), None)
    assert test_cmd_obj is not None
    assert test_cmd_obj.help == "Run tests"


def test_optional_positional():
    """Test optional positional argument."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("required", help="Required arg")
    parser.add_argument("optional", nargs="?", help="Optional arg")

    spec = _generate_spec(parser)

    args = [c for c in spec.children if isinstance(c, Arg)]
    assert len(args) == 2

    required_arg = next((a for a in args if a.name == "required"), None)
    assert required_arg is not None
    assert required_arg.required is True

    optional_arg = next((a for a in args if a.name == "optional"), None)
    assert optional_arg is not None
    assert optional_arg.required is False


def test_exactly_n_positional():
    """Test positional with exact count."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("coords", nargs=3, help="Three coordinates")

    spec = _generate_spec(parser)

    args = [c for c in spec.children if isinstance(c, Arg)]
    assert len(args) == 1
    assert args[0].name == "coords"
    assert args[0].var is True
    assert args[0].var_min == 3
    assert args[0].var_max == 3


def test_store_true_flag():
    """Test store_true action flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--force", action="store_true", help="Force operation")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--force"
    assert flags[0].default is False
    assert flags[0].takes_arg is False


def test_count_flag():
    """Test count action flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("-v", "--verbose", action="count", default=0)

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].short == "-v"
    assert flags[0].long == "--verbose"
    assert flags[0].count is True
    assert flags[0].default == 0
    assert flags[0].takes_arg is False


def test_flag_with_default():
    """Test flag with default value."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--output", default="output.txt", help="Output file")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--output"
    assert flags[0].default == "output.txt"
    assert flags[0].takes_arg is True


def test_custom_bin_name():
    """Test custom binary name."""
    parser = create_simple_parser()
    spec = _generate_spec(parser, bin_name="my-custom-cli")

    assert spec.bin == "my-custom-cli"


def test_epilog():
    """Test epilog (after_help) generation."""
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="A CLI",
        epilog="For more info, visit https://example.com",
    )
    parser.add_argument("file")

    spec = _generate_spec(parser)

    assert spec is not None
    assert spec.name == "mycli"


def test_string_flag_with_argument():
    """Test that string flags have takes_arg=True."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--output", help="Output file")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--output"
    assert flags[0].takes_arg is True


def test_int_flag_with_argument():
    """Test that integer flags have takes_arg=True."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--port", type=int, help="Port number")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--port"
    assert flags[0].takes_arg is True


def test_bool_flag_no_argument():
    """Test that bool flags do NOT take arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--force", action="store_true", help="Force operation")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--force"
    assert flags[0].takes_arg is False


def test_count_flag_no_argument():
    """Test that count flags do NOT take arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("-v", "--verbose", action="count", help="Increase verbosity")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--verbose"
    assert flags[0].count is True
    assert flags[0].takes_arg is False


def test_flag_with_choices_has_arg():
    """Test that flags with choices have takes_arg=True."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument(
        "--format", choices=["json", "yaml", "xml"], help="Output format"
    )

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--format"
    assert flags[0].choices == ["json", "yaml", "xml"]
    assert flags[0].takes_arg is True


def test_flag_with_variadic_args():
    """Test flags that accept multiple arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--tags", nargs="*", help="Tags")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--tags"
    assert flags[0].var is True
    assert flags[0].var_min == 0


def test_flag_with_exact_nargs():
    """Test flags that accept exact number of arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--coords", nargs=2, help="Two coordinates")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--coords"
    assert flags[0].var is True
    assert flags[0].var_min == 2
    assert flags[0].var_max == 2


def test_multiple_flags_mixed():
    """Test multiple flags with different types."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--config", help="Config file")
    parser.add_argument("--force", action="store_true", help="Force")
    parser.add_argument("-v", "--verbose", action="count", help="Verbose")
    parser.add_argument("--port", type=int, default=8080, help="Port")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 4

    config = next((f for f in flags if f.long == "--config"), None)
    assert config is not None
    assert config.takes_arg is True

    force = next((f for f in flags if f.long == "--force"), None)
    assert force is not None
    assert force.takes_arg is False

    verbose = next((f for f in flags if f.long == "--verbose"), None)
    assert verbose is not None
    assert verbose.count is True
    assert verbose.takes_arg is False

    port = next((f for f in flags if f.long == "--port"), None)
    assert port is not None
    assert port.takes_arg is True
    assert port.default == 8080


def test_block_attribute_format():
    """Test that flags with choices get the correct attributes."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--format", choices=["json", "yaml"], help="Output format")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].long == "--format"
    assert flags[0].choices == ["json", "yaml"]
    assert flags[0].help == "Output format"


def test_subparser_with_bool_flag():
    """Test subparser with bool flag."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("--force", action="store_true", help="Force add")

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 1

    add = cmds[0]
    assert add.name == "add"

    add_flags = [c for c in add.children if isinstance(c, Flag)]
    assert len(add_flags) == 1
    assert add_flags[0].long == "--force"
    assert add_flags[0].takes_arg is False


def test_subparser_with_flag_arg():
    """Test subparser with flag that accepts an argument."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_cmd = subparsers.add_parser("build", help="Build project")
    build_cmd.add_argument("--output", help="Output directory")

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 1

    build = cmds[0]
    assert build.name == "build"

    build_flags = [c for c in build.children if isinstance(c, Flag)]
    assert len(build_flags) == 1
    assert build_flags[0].long == "--output"
    assert build_flags[0].takes_arg is True


def test_subparser_help_from_help_parameter():
    """Test that subparser help text is taken from help parameter, not description."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", help="Add something")
    add_cmd.add_argument("--name", help="Item name")

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 1
    assert cmds[0].help == "Add something"


def test_subparser_help_fallback_to_description():
    """Test that subparser help falls back to description if help is not provided."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_cmd = subparsers.add_parser("add", description="Add something else")
    add_cmd.add_argument("--name", help="Item name")

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    assert len(cmds) == 1
    assert cmds[0].help == "Add something else"


def test_nested_subparser_help():
    """Test that nested subparsers also get help text from help parameter."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_cmd = subparsers.add_parser("config", help="Manage config")
    config_subparsers = config_cmd.add_subparsers(dest="config_command", required=True)

    get_cmd = config_subparsers.add_parser("get", help="Get a config value")
    get_cmd.add_argument("key", help="Config key")

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    config = next((c for c in cmds if c.name == "config"), None)
    assert config is not None
    assert config.help == "Manage config"

    nested_cmds = [c for c in config.children if isinstance(c, Cmd)]
    get = next((c for c in nested_cmds if c.name == "get"), None)
    assert get is not None
    assert get.help == "Get a config value"


def test_help_text_with_default_placeholder():
    """Test that %(default)s placeholder is replaced with actual default value."""
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument(
        "--type", default="default", help="Item type (default: %(default)s)"
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Max results (default: %(default)s)"
    )

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]

    type_flag = next((f for f in flags if f.long == "--type"), None)
    assert type_flag is not None
    assert type_flag.help == "Item type (default: default)"

    limit_flag = next((f for f in flags if f.long == "--limit"), None)
    assert limit_flag is not None
    assert limit_flag.help == "Max results (default: 20)"


def test_help_text_with_prog_placeholder():
    """Test that %(prog)s placeholder is replaced with program name."""
    parser = argparse.ArgumentParser(prog="myprog")
    parser.add_argument("--config", help="Config file (prog: %(prog)s)")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]
    assert len(flags) == 1
    assert flags[0].help == "Config file (prog: myprog)"


def test_help_text_in_subcommand():
    """Test that placeholders are expanded in subcommand arguments."""
    parser = argparse.ArgumentParser(prog="mycli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_cmd = subparsers.add_parser("create", help="Create an item")
    create_cmd.add_argument(
        "--type", default="default", help="Item type (default: %(default)s)"
    )

    spec = _generate_spec(parser)

    cmds = [c for c in spec.children if isinstance(c, Cmd)]
    create = cmds[0]

    create_flags = [c for c in create.children if isinstance(c, Flag)]
    assert len(create_flags) == 1
    assert create_flags[0].help == "Item type (default: default)"


def test_argument_defaults_help_formatter():
    """Test argparse.ArgumentDefaultsHelpFormatter."""
    parser = argparse.ArgumentParser(
        prog="mycli", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--type", default="default", help="Item type")
    parser.add_argument("--limit", type=int, default=20, help="Max results")

    spec = _generate_spec(parser)

    flags = [c for c in spec.children if isinstance(c, Flag)]

    type_flag = next((f for f in flags if f.long == "--type"), None)
    assert type_flag is not None
    assert type_flag.help == "Item type (default: default)"

    limit_flag = next((f for f in flags if f.long == "--limit"), None)
    assert limit_flag is not None
    assert limit_flag.help == "Max results (default: 20)"
