"""Generate usage specs from argparse.ArgumentParser."""

import argparse
from collections.abc import Iterator
from typing import Any

from argparse_usage.kdl_utils import escape_string, format_arg, format_flag


def _get_all_actions(parser: argparse.ArgumentParser) -> Iterator[argparse.Action]:
    """Yield all actions from parser and its parent parsers."""
    # Get parent parsers first
    parents = getattr(parser, "_parents", None)
    if parents:
        for parent in parents:
            yield from _get_all_actions(parent)

    # Then get actions from this parser
    for action in parser._actions:
        yield action


def _is_positional(action: argparse.Action) -> bool:
    """Check if action is a positional argument."""
    return len(action.option_strings) == 0


def _is_flag(action: argparse.Action) -> bool:
    """Check if action is a flag (optional argument)."""
    return len(action.option_strings) > 0


def _get_flag_names(action: argparse.Action) -> tuple[str | None, str | None]:
    """Extract short and long flag names from an action."""
    short = None
    long = None

    for opt in action.option_strings:
        if opt.startswith("--"):
            long = opt
        elif opt.startswith("-"):
            short = opt

    return short, long


def _get_var_info(nargs: Any) -> tuple[bool, int | None, int | None]:
    """Extract variadic information from nargs."""
    if nargs in ("*", "+"):
        return True, 1 if nargs == "+" else 0, None
    elif isinstance(nargs, int) and nargs > 1:
        return True, nargs, nargs
    elif nargs is None:
        return False, None, None
    else:
        return False, None, None


def _convert_action_to_spec(action: argparse.Action) -> str | None:
    """Convert an argparse Action to usage spec KDL."""
    # Skip help action
    if isinstance(action, argparse._HelpAction):
        return None

    # Skip subparsers action (handled separately)
    if isinstance(action, argparse._SubParsersAction):
        return None

    if _is_flag(action):
        return _convert_flag_to_spec(action)
    elif _is_positional(action):
        return _convert_positional_to_spec(action)

    return None


def _convert_flag_to_spec(action: argparse.Action) -> str:
    """Convert a flag action to usage spec KDL."""
    short, long = _get_flag_names(action)
    help_text = getattr(action, "help", None)
    required = getattr(action, "required", False)
    default = getattr(action, "default", None)
    choices = getattr(action, "choices", None)

    # Determine action type
    is_count = isinstance(action, argparse._CountAction)
    is_store_true = isinstance(action, argparse._StoreTrueAction)
    is_store_false = isinstance(action, argparse._StoreFalseAction)

    # Get variadic info
    nargs = getattr(action, "nargs", None)
    var, var_min, var_max = _get_var_info(nargs)

    # For count actions, default is typically 0
    if is_count and default is None:
        default = 0

    # For store_true/false, default is opposite of what would happen
    if is_store_true and default is None:
        default = False
    if is_store_false and default is None:
        default = True

    # Determine if flag takes an argument
    # Flags that DON'T take arguments: store_true, store_false, count
    takes_arg = not (is_store_true or is_store_false or is_count)

    # Handle ellipsis notation for variadic flags
    if var and long:
        if long.endswith("..."):
            long = long[:-3]
        elif nargs in ("*", "+"):
            # Add ellipsis to long form for variadic
            long = f"{long}..."

    return format_flag(
        short=short,
        long=long,
        help_text=help_text,
        required=required,
        default=default,
        count=is_count,
        var=var,
        var_min=var_min,
        var_max=var_max,
        choices=choices,
        takes_arg=takes_arg,
    )


def _convert_positional_to_spec(action: argparse.Action) -> str:
    """Convert a positional argument to usage spec KDL."""
    name = action.dest
    help_text = getattr(action, "help", None)
    required = getattr(action, "required", False)
    default = getattr(action, "default", None)
    choices = getattr(action, "choices", None)

    # Get variadic info
    nargs = getattr(action, "nargs", None)
    var, var_min, var_max = _get_var_info(nargs)

    # Handle optional positionals (nargs='?')
    if nargs == "?":
        required = False

    return format_arg(
        name=name,
        help_text=help_text,
        required=required,
        default=default,
        var=var,
        var_min=var_min,
        var_max=var_max,
        choices=choices,
    )


def _format_subcommand(name: str, parser: argparse.ArgumentParser) -> str:
    """Format a subcommand with its spec."""
    lines = [f"cmd {name} {{"]

    # Add help text if available
    # Prefer help (stored in _help_text) over description
    help_text = getattr(parser, "_help_text", None) or getattr(
        parser, "description", None
    )
    if help_text:
        lines.append(f"  help {escape_string(help_text)}")

    # Process all actions (skip help and subparsers)
    for action in parser._actions:
        if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue

        spec = _convert_action_to_spec(action)
        if spec:
            # Indent each line
            for line in spec.split("\n"):
                lines.append(f"  {line}")

    # Handle sub-subcommands
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            # Build a map of help text from _choices_actions
            help_map = {}
            if hasattr(action, "_choices_actions"):
                for ca in action._choices_actions:
                    help_map[ca.dest] = ca.help

            for sub_name, sub_parser in action.choices.items():
                # Store the help text on the parser if available
                if sub_name in help_map and help_map[sub_name]:
                    sub_parser._help_text = help_map[sub_name]
                # Indent each line of the sub-subcommand block
                for line in _format_subcommand(sub_name, sub_parser).split("\n"):
                    lines.append(f"  {line}")

    lines.append("}")
    return "\n".join(lines)


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
    lines = []

    lines.append("// @generated by argparse-usage from Python argparse")
    lines.append("")

    if name:
        lines.append(f"name {escape_string(name)}")
    elif parser.prog:
        lines.append(f"name {escape_string(parser.prog)}")
    elif parser.description:
        # Try to extract name from description
        import re

        match = re.match(r"^(\w+)", parser.description)
        if match:
            lines.append(f"name {escape_string(match.group(1))}")

    bin_value = bin_name or parser.prog or "cli"
    lines.append(f"bin {escape_string(bin_value)}")

    if version:
        lines.append(f"version {escape_string(version)}")

    if author:
        lines.append(f"author {escape_string(author)}")

    if parser.description:
        lines.append(f"about {escape_string(parser.description)}")

    lines.append("")

    # Process all actions (skip help and subparsers)
    for action in parser._actions:
        if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
            continue

        spec = _convert_action_to_spec(action)
        if spec:
            lines.append(spec)

    # Handle subcommands
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            # Build a map of help text from _choices_actions
            help_map = {}
            if hasattr(action, "_choices_actions"):
                for ca in action._choices_actions:
                    help_map[ca.dest] = ca.help

            for name, sub_parser in action.choices.items():
                # Store the help text on the parser if available
                if name in help_map and help_map[name]:
                    sub_parser._help_text = help_map[name]
                lines.append(_format_subcommand(name, sub_parser))

    return "\n".join(lines)
