"""Unit tests for spec to KDL conversion."""

from argparse_usage._usage import Arg, Cmd, Flag, Spec


def test_simple_parser():
    """Test simple parser generation."""
    spec = Spec(name="mycli", bin="mycli", about="A simple CLI tool")
    spec.children.append(Flag(short="-f", long="--force", help="Force operation"))
    spec.children.append(
        Flag(short="-v", long="--verbose", help="Increase verbosity", count=True)
    )
    spec.children.append(
        Flag(long="--output", default="output.txt", help="Output file", takes_arg=True)
    )
    spec.children.append(Arg(name="file", help="Input file"))

    kdl = spec.to_kdl()

    assert 'name "mycli"' in kdl
    assert 'bin "mycli"' in kdl
    assert 'about "A simple CLI tool"' in kdl
    assert 'flag "-f --force"' in kdl
    assert 'help="Force operation"' in kdl
    assert 'arg "<file>"' in kdl
    assert 'help="Input file"' in kdl
    assert "count=#true" in kdl


def test_parser_with_version():
    """Test parser with version metadata."""
    spec = Spec(
        name="mycli",
        bin="mycli",
        version="1.0.0",
        author="Test Author",
        about="A simple CLI tool",
    )

    kdl = spec.to_kdl()

    assert 'version "1.0.0"' in kdl
    assert 'author "Test Author"' in kdl


def test_parser_with_choices():
    """Test parser with choice arguments."""
    spec = Spec(name="mycli", bin="mycli", about="A CLI with choices")
    spec.children.append(
        Flag(
            long="--format",
            help="Output format",
            choices=["json", "yaml", "xml"],
            takes_arg=True,
        )
    )
    spec.children.append(
        Arg(
            name="action",
            help="Action to perform",
            choices=["create", "update", "delete"],
        )
    )

    kdl = spec.to_kdl()

    assert "choices" in kdl
    assert "json" in kdl
    assert "yaml" in kdl
    assert "xml" in kdl


def test_parser_with_variadic():
    """Test parser with variadic arguments."""
    spec = Spec(name="mycli", bin="mycli", about="A CLI with variadic args")
    spec.children.append(
        Arg(name="files", help="Input files (one or more)", var=True, var_min=1)
    )
    spec.children.append(
        Arg(name="optional", help="Optional additional files", var=True, var_min=0)
    )
    spec.children.append(
        Flag(long="--tags", help="Tags", var=True, var_min=0, takes_arg=True)
    )

    kdl = spec.to_kdl()

    assert "<files>..." in kdl
    assert "[optional]..." in kdl
    assert "var=#true" in kdl


def test_parser_with_parent():
    """Test parser with parent parser inheritance."""
    spec = Spec(name="mycli", bin="mycli", about="A CLI with parent parser")
    spec.children.append(
        Flag(short="-v", long="--verbose", help="Increase verbosity", count=True)
    )
    spec.children.append(Flag(short="-q", long="--quiet", help="Suppress output"))
    spec.children.append(Arg(name="file", help="Input file"))

    kdl = spec.to_kdl()

    assert 'flag "-v --verbose"' in kdl
    assert "count=#true" in kdl
    assert 'flag "-q --quiet"' in kdl
    assert 'arg "<file>"' in kdl


def test_parser_with_subcommands():
    """Test parser with subcommands."""
    spec = Spec(name="mycli", bin="mycli", about="A CLI with subcommands")

    add_cmd = Cmd(name="add", help="Add something")
    add_cmd.children.append(Arg(name="name", help="Name to add"))
    add_cmd.children.append(Flag(short="-f", long="--force", help="Force add"))
    spec.children.append(add_cmd)

    list_cmd = Cmd(name="list", help="List items")
    list_cmd.children.append(Flag(short="-a", long="--all", help="List all"))
    list_cmd.children.append(
        Flag(
            long="--sort",
            help="Sort by",
            choices=["name", "date", "size"],
            takes_arg=True,
        )
    )
    spec.children.append(list_cmd)

    remove_cmd = Cmd(name="remove", help="Remove item")
    remove_cmd.children.append(Arg(name="name", help="Name to remove"))
    spec.children.append(remove_cmd)

    kdl = spec.to_kdl()

    assert "cmd add" in kdl
    assert "cmd list" in kdl
    assert "cmd remove" in kdl
    assert 'arg "<name>"' in kdl
    assert 'flag "-f --force"' in kdl
    assert "choices" in kdl


def test_complex_parser():
    """Test complex parser with many features."""
    spec = Spec(name="mycli", bin="mycli", about="A complex CLI tool")
    spec.children.append(
        Flag(short="-v", long="--verbose", help="Increase verbosity", count=True)
    )
    spec.children.append(
        Flag(short="-f", long="--file", help="Input file", takes_arg=True)
    )
    spec.children.append(Flag(long="--stdin", help="Read from stdin"))
    spec.children.append(
        Flag(long="--output", default="output.txt", help="Output file", takes_arg=True)
    )
    spec.children.append(
        Flag(
            long="--format",
            help="Output format",
            choices=["json", "yaml"],
            takes_arg=True,
        )
    )
    spec.children.append(
        Arg(name="files", help="Files to process", var=True, var_min=1)
    )
    spec.children.append(
        Arg(name="options", help="Additional options", var=True, var_min=0)
    )

    build_cmd = Cmd(name="build", help="Build project")
    build_cmd.children.append(Flag(long="--debug", help="Debug build"))
    spec.children.append(build_cmd)

    test_cmd = Cmd(name="test", help="Run tests")
    test_cmd.children.append(Flag(long="--verbose", help="Test verbosity", count=True))
    test_cmd.children.append(
        Arg(name="tests", help="Specific tests to run", var=True, var_min=0)
    )
    spec.children.append(test_cmd)

    kdl = spec.to_kdl()

    assert 'name "mycli"' in kdl
    assert 'bin "mycli"' in kdl
    assert 'about "A complex CLI tool"' in kdl
    assert "<files>..." in kdl
    assert "[options]..." in kdl
    assert "cmd build" in kdl
    assert "cmd test" in kdl


def test_optional_positional():
    """Test optional positional argument."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Arg(name="required", help="Required arg", required=True))
    spec.children.append(Arg(name="optional", help="Optional arg", required=False))

    kdl = spec.to_kdl()

    assert 'arg "<required>"' in kdl
    assert 'arg "[optional]"' in kdl


def test_exactly_n_positional():
    """Test positional with exact count."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Arg(name="coords", help="Three coordinates", var=True, var_min=3, var_max=3)
    )

    kdl = spec.to_kdl()

    assert 'arg "<coords>..."' in kdl
    assert "var_min=3" in kdl
    assert "var_max=3" in kdl


def test_store_true_flag():
    """Test store_true action flag."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(long="--force", help="Force operation", default=False))

    kdl = spec.to_kdl()

    assert 'flag "--force"' in kdl
    assert "default=#false" in kdl


def test_count_flag():
    """Test count action flag."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(short="-v", long="--verbose", count=True, default=0))

    kdl = spec.to_kdl()

    assert 'flag "-v --verbose"' in kdl
    assert "count=#true" in kdl


def test_flag_with_default():
    """Test flag with default value."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(long="--output", default="output.txt", help="Output file", takes_arg=True)
    )

    kdl = spec.to_kdl()

    assert 'flag "--output"' in kdl
    assert 'default "output.txt"' in kdl
    assert "arg <output>" in kdl


def test_custom_bin_name():
    """Test custom binary name."""
    spec = Spec(name="mycli", bin="my-custom-cli", about="A simple CLI tool")

    kdl = spec.to_kdl()

    assert 'bin "my-custom-cli"' in kdl


def test_epilog():
    """Test epilog (after_help) generation."""
    spec = Spec(name="mycli", bin="mycli", about="A CLI")
    spec.children.append(Arg(name="file", help="Input file"))

    kdl = spec.to_kdl()

    assert kdl is not None
    assert 'name "mycli"' in kdl


def test_string_flag_with_argument():
    """Test that string flags have arg children."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(long="--output", help="Output file", takes_arg=True))

    kdl = spec.to_kdl()

    assert "arg <output>" in kdl
    assert 'flag "--output" {' in kdl


def test_int_flag_with_argument():
    """Test that integer flags have arg children."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(long="--port", help="Port number", takes_arg=True))

    kdl = spec.to_kdl()

    assert "arg <port>" in kdl


def test_bool_flag_no_argument():
    """Test that bool flags do NOT have arg children."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(long="--force", help="Force operation"))

    kdl = spec.to_kdl()

    assert 'arg "<force>"' not in kdl
    lines = kdl.split("\n")
    force_lines = [line for line in lines if 'flag "--force"' in line]
    assert len(force_lines) == 1
    assert "{" not in force_lines[0]


def test_count_flag_no_argument():
    """Test that count flags do NOT have arg children."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(short="-v", long="--verbose", help="Increase verbosity", count=True)
    )

    kdl = spec.to_kdl()

    assert 'arg "<verbose>"' not in kdl
    assert "count=#true" in kdl


def test_flag_with_choices_has_arg():
    """Test that flags with choices have arg children with choices."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(
            long="--format",
            help="Output format",
            choices=["json", "yaml", "xml"],
            takes_arg=True,
        )
    )

    kdl = spec.to_kdl()

    assert "arg <format> {" in kdl
    assert "choices" in kdl
    assert "json" in kdl
    assert "yaml" in kdl
    assert "xml" in kdl


def test_flag_with_variadic_args():
    """Test flags that accept multiple arguments."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(long="--tags", help="Tags", var=True, var_min=0, takes_arg=True)
    )

    kdl = spec.to_kdl()

    assert "arg <tags>" in kdl
    assert "var #true" in kdl


def test_flag_with_exact_nargs():
    """Test flags that accept exact number of arguments."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(
            long="--coords",
            help="Two coordinates",
            var=True,
            var_min=2,
            var_max=2,
            takes_arg=True,
        )
    )

    kdl = spec.to_kdl()

    assert "arg <coords>" in kdl
    assert "var_min 2" in kdl
    assert "var_max 2" in kdl


def test_multiple_flags_mixed():
    """Test multiple flags with different types."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(Flag(long="--config", help="Config file", takes_arg=True))
    spec.children.append(Flag(long="--force", help="Force"))
    spec.children.append(Flag(short="-v", long="--verbose", help="Verbose", count=True))
    spec.children.append(Flag(long="--port", default=8080, help="Port", takes_arg=True))

    kdl = spec.to_kdl()

    assert "arg <config>" in kdl
    assert 'arg "<force>"' not in kdl
    assert 'arg "<verbose>"' not in kdl
    assert "arg <port>" in kdl
    assert 'default "8080"' in kdl


def test_block_attribute_format():
    """Test that attributes inside blocks use space not equals sign."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(
            long="--format",
            help="Output format",
            choices=["json", "yaml"],
            takes_arg=True,
        )
    )

    kdl = spec.to_kdl()

    assert 'help "Output format"' in kdl


def test_subparser_with_bool_flag():
    """Test subparser with bool flag."""
    spec = Spec(name="mycli", bin="mycli")
    add_cmd = Cmd(name="add", help="Add something")
    add_cmd.children.append(Flag(long="--force", help="Force add"))
    spec.children.append(add_cmd)

    kdl = spec.to_kdl()

    assert "cmd add" in kdl
    assert 'flag "--force" help="Force add"' in kdl
    assert "arg <force>" not in kdl


def test_subparser_with_flag_arg():
    """Test subparser with flag that accepts an argument."""
    spec = Spec(name="mycli", bin="mycli")
    build_cmd = Cmd(name="build", help="Build project")
    build_cmd.children.append(
        Flag(long="--output", help="Output directory", takes_arg=True)
    )
    spec.children.append(build_cmd)

    kdl = spec.to_kdl()

    assert "cmd build" in kdl
    lines = kdl.split("\n")
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
    assert 'flag "--output" {' in build_spec
    assert "arg <output>" in build_spec


def test_subparser_help_from_help_parameter():
    """Test that subparser help text is taken from help parameter, not description."""
    spec = Spec(name="mycli", bin="mycli")
    add_cmd = Cmd(name="add", help="Add something")
    add_cmd.children.append(Flag(long="--name", help="Item name", takes_arg=True))
    spec.children.append(add_cmd)

    kdl = spec.to_kdl()

    assert "cmd add" in kdl
    assert 'help "Add something"' in kdl


def test_subparser_help_fallback_to_description():
    """Test that subparser help falls back to description if help is not provided."""
    spec = Spec(name="mycli", bin="mycli")
    add_cmd = Cmd(name="add", help="Add something else")
    add_cmd.children.append(Flag(long="--name", help="Item name", takes_arg=True))
    spec.children.append(add_cmd)

    kdl = spec.to_kdl()

    assert "cmd add" in kdl
    assert 'help "Add something else"' in kdl


def test_nested_subparser_help():
    """Test that nested subparsers also get help text from help parameter."""
    spec = Spec(name="mycli", bin="mycli")
    config_cmd = Cmd(name="config", help="Manage config")
    get_cmd = Cmd(name="get", help="Get a config value")
    get_cmd.children.append(Arg(name="key", help="Config key"))
    config_cmd.children.append(get_cmd)
    spec.children.append(config_cmd)

    kdl = spec.to_kdl()

    assert "cmd config" in kdl
    assert "cmd get" in kdl
    assert 'help "Manage config"' in kdl
    assert 'help "Get a config value"' in kdl


def test_help_text_with_default_placeholder():
    """Test that %(default)s placeholder is replaced with actual default value."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(
            long="--type",
            default="default",
            help="Item type (default: default)",
            takes_arg=True,
        )
    )
    spec.children.append(
        Flag(
            long="--limit",
            default="20",
            help="Max results (default: 20)",
            takes_arg=True,
        )
    )

    kdl = spec.to_kdl()

    assert 'help "Item type (default: default)"' in kdl
    assert 'help "Max results (default: 20)"' in kdl
    assert "%(default)s" not in kdl


def test_help_text_with_prog_placeholder():
    """Test that %(prog)s placeholder is replaced with program name."""
    spec = Spec(name="myprog", bin="myprog")
    spec.children.append(
        Flag(long="--config", help="Config file (prog: myprog)", takes_arg=True)
    )

    kdl = spec.to_kdl()

    assert 'help "Config file (prog: myprog)"' in kdl
    assert "%(prog)s" not in kdl


def test_help_text_in_subcommand():
    """Test that placeholders are expanded in subcommand arguments."""
    spec = Spec(name="mycli", bin="mycli")
    create_cmd = Cmd(name="create", help="Create an item")
    create_cmd.children.append(
        Flag(
            long="--type",
            default="default",
            help="Item type (default: default)",
            takes_arg=True,
        )
    )
    spec.children.append(create_cmd)

    kdl = spec.to_kdl()

    assert 'help "Item type (default: default)"' in kdl
    assert "%(default)s" not in kdl


def test_argument_defaults_help_formatter():
    """Test argparse.ArgumentDefaultsHelpFormatter."""
    spec = Spec(name="mycli", bin="mycli")
    spec.children.append(
        Flag(
            long="--type",
            default="default",
            help="Item type (default: default)",
            takes_arg=True,
        )
    )
    spec.children.append(
        Flag(
            long="--limit",
            default="20",
            help="Max results (default: 20)",
            takes_arg=True,
        )
    )

    kdl = spec.to_kdl()

    assert 'help "Item type (default: default)"' in kdl
    assert 'help "Max results (default: 20)"' in kdl
    assert "%(default)s" not in kdl
