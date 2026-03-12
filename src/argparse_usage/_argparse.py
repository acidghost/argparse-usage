"""Internal module to transform an argparse.ArgumentParser into an Usage spec object."""

import argparse
from collections.abc import Iterator

from argparse_usage._usage import Arg, Cmd, Flag, Spec


def _generate_spec(
    parser: argparse.ArgumentParser,
    name: str | None = None,
    version: str | None = None,
    author: str | None = None,
    bin_name: str | None = None,
) -> Spec:
    """Generate an Usage spec object from an ArgumentParser."""
    spec = Spec(
        name=name or parser.prog,
        bin=bin_name or parser.prog,
        version=version,
        author=author,
        about=parser.description,
    )

    for action in _get_all_actions(parser):
        node = _action_to_node(action)
        if node:
            spec.children.append(node)

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
                spec.children.append(_subcommand_to_node(sub_name, sub_parser))

    return spec


def _get_all_actions(parser: argparse.ArgumentParser) -> Iterator[argparse.Action]:
    """Yield all actions from parser and its parent parsers."""
    parents = getattr(parser, "_parents", None)
    if parents:
        for parent in parents:
            yield from _get_all_actions(parent)

    for action in parser._actions:
        yield action


def _action_to_node(action: argparse.Action) -> Flag | Arg | None:
    """Convert an argparse Action to an AST node."""
    if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
        return None

    if _is_flag(action):
        return _flag_to_node(action)
    elif _is_positional(action):
        return _positional_to_node(action)

    return None


def _is_flag(action: argparse.Action) -> bool:
    """Check if action is a flag (optional argument)."""
    return len(action.option_strings) > 0


def _is_positional(action: argparse.Action) -> bool:
    """Check if action is a positional argument."""
    return len(action.option_strings) == 0


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


def _get_var_info(nargs) -> tuple[bool, int | None, int | None]:
    """Extract variadic information from nargs."""
    if nargs in ("*", "+"):
        return True, 1 if nargs == "+" else 0, None
    elif isinstance(nargs, int) and nargs > 1:
        return True, nargs, nargs
    elif nargs is None:
        return False, None, None
    else:
        return False, None, None


def _flag_to_node(action: argparse.Action) -> Flag:
    """Convert a flag action to Flag node."""
    short, long = _get_flag_names(action)
    var, var_min, var_max = _get_var_info(getattr(action, "nargs", None))

    is_count = isinstance(action, argparse._CountAction)
    is_store_true = isinstance(action, argparse._StoreTrueAction)
    is_store_false = isinstance(action, argparse._StoreFalseAction)

    default = getattr(action, "default", None)
    if is_count and default is None:
        default = 0
    if is_store_true and default is None:
        default = False
    if is_store_false and default is None:
        default = True

    takes_arg = not (is_store_true or is_store_false or is_count)

    # Handle ellipsis notation for variadic flags
    if var and long:
        if long.endswith("..."):
            long = long[:-3]

    return Flag(
        short=short,
        long=long,
        help=getattr(action, "help", None),
        required=getattr(action, "required", False),
        default=default,
        count=is_count,
        var=var,
        var_min=var_min,
        var_max=var_max,
        choices=getattr(action, "choices", None),
        takes_arg=takes_arg,
    )


def _positional_to_node(action: argparse.Action) -> Arg:
    """Convert a positional argument to Arg node."""
    var, var_min, var_max = _get_var_info(getattr(action, "nargs", None))

    # Handle optional positionals (nargs='?')
    required = True
    nargs = getattr(action, "nargs", None)
    if nargs == "?":
        required = False

    return Arg(
        name=action.dest,
        help=getattr(action, "help", None),
        required=required,
        default=getattr(action, "default", None),
        var=var,
        var_min=var_min,
        var_max=var_max,
        choices=getattr(action, "choices", None),
    )


def _subcommand_to_node(name: str, parser: argparse.ArgumentParser) -> Cmd:
    """Convert subparser to Cmd node."""
    help_text = getattr(parser, "_help_text", None) or getattr(
        parser, "description", None
    )

    cmd = Cmd(name=name, help=help_text)

    for action in parser._actions:
        node = _action_to_node(action)
        if node:
            cmd.children.append(node)

    # Handle nested subcommands
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
                cmd.children.append(_subcommand_to_node(sub_name, sub_parser))

    return cmd
