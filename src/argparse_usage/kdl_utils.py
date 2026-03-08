"""KDL formatting utilities for usage spec generation."""

import argparse


def escape_string(value: str) -> str:
    """Escape a string value for KDL format."""
    if not value:
        return '""'

    value = str(value)

    # If string contains special characters, use raw string format r#"..."#
    needs_raw = any(c in value for c in ['"', "\n", "\r", "\t", "\\"])

    if needs_raw:
        # Use raw string format to avoid escaping
        return f'r#"{value}"#'
    else:
        return f'"{value}"'


def format_flag(
    short: str | None,
    long: str | None,
    help_text: str | None = None,
    required: bool = False,
    default: str | bool | int | None = None,
    count: bool = False,
    var: bool = False,
    var_min: int | None = None,
    var_max: int | None = None,
    choices: list[str] | None = None,
    long_help: str | None = None,
    takes_arg: bool = False,
) -> str:
    """Format a flag definition for KDL spec."""
    parts = []

    if short is None and long is None:
        raise ValueError("neither 'short' nor 'long' provided")

    flag_names = []
    if short:
        flag_names.append(short)
    if long:
        flag_names.append(long)
    flag_str = " ".join(flag_names)

    # Use block if takes_arg OR has complex attributes
    needs_block = (
        takes_arg or choices is not None or (long_help and len(long_help) > 50)
    )

    if needs_block:
        # Block format: all attributes use `key value` (space, no =)
        parts.append(f"flag {escape_string(flag_str)} {{")
        if help_text:
            parts.append(f"  help {escape_string(help_text)}")
        if required:
            parts.append("  required #true")
        if default is not None and default != argparse.SUPPRESS:
            if isinstance(default, bool):
                parts.append(f"  default #{str(default).lower()}")
            else:
                parts.append(f"  default {escape_string(str(default))}")
        if count:
            parts.append("  count #true")
        if var or var_min is not None or var_max is not None:
            parts.append("  var #true")
            if var_min is not None:
                parts.append(f"  var_min {var_min}")
            if var_max is not None:
                parts.append(f"  var_max {var_max}")
        if long_help:
            parts.append(f"  long_help={escape_string(long_help)}")
        if choices:
            arg_name = long.lstrip("-") if long else "value"
            # Strip ellipsis from arg name if present
            arg_name = arg_name.rstrip("...")
            parts.append(f"  arg <{arg_name}> {{")
            # Inside blocks, choices are bare values (not quoted)
            parts.append(f"    choices {' '.join(c for c in choices)}")
            parts.append("  }")
        elif takes_arg:
            arg_name = long.lstrip("-") if long else "value"
            # Strip ellipsis from arg name if present
            arg_name = arg_name.rstrip("...")
            # Inside flag blocks, arg names are not quoted
            parts.append(f"  arg <{arg_name}>")
        parts.append("}")
    else:
        # Inline format: attributes use `key=value` (=, no space)
        line = f"flag {escape_string(flag_str)}"
        attrs = []
        if help_text:
            attrs.append(f"help={escape_string(help_text)}")
        if required:
            attrs.append("required=#true")
        if default is not None and default != argparse.SUPPRESS:
            if isinstance(default, bool):
                attrs.append(f"default=#{str(default).lower()}")
            else:
                attrs.append(f"default={escape_string(str(default))}")
        if count:
            attrs.append("count=#true")
        if var or var_min is not None or var_max is not None:
            attrs.append("var=#true")
            if var_min is not None:
                attrs.append(f"var_min={var_min}")
            if var_max is not None:
                attrs.append(f"var_max={var_max}")
        if attrs:
            line += " " + " ".join(attrs)
        parts.append(line)

    return "\n".join(parts)


def format_arg(
    name: str,
    help_text: str | None = None,
    required: bool = True,
    default: str | None = None,
    var: bool = False,
    var_min: int | None = None,
    var_max: int | None = None,
    choices: list[str] | None = None,
    long_help: str | None = None,
) -> str:
    """Format an argument definition for KDL spec."""
    parts = []

    # Build arg name (e.g., "<file>" or "[file]" or "<file>..." or "[file]...")
    if not var and not var_min and not var_max:
        arg_name = f"[{name}]" if not required else f"<{name}>"
    else:
        # Variadic argument
        if var_min == 0:
            # Zero or more -> optional
            arg_name = f"[{name}]..."
        else:
            # One or more -> required
            arg_name = f"<{name}>..."

    # Check if we need a block (for complex attributes like choices or long_help)
    needs_block = choices is not None or (long_help and len(long_help) > 50)

    if needs_block:
        # Block format: attributes use `key value` (space, no =)
        parts.append(f"arg {escape_string(arg_name)} {{")
        if help_text:
            parts.append(f"  help {escape_string(help_text)}")
        if not required:
            parts.append("  required #false")
        if default is not None and default != argparse.SUPPRESS:
            parts.append(f"  default {escape_string(str(default))}")
        if var:
            parts.append("  var #true")
        if var_min is not None:
            parts.append(f"  var_min {var_min}")
        if var_max is not None:
            parts.append(f"  var_max {var_max}")
        if long_help:
            parts.append(f"  long_help={escape_string(long_help)}")
        if choices:
            # Inside blocks, choices are bare values (not quoted)
            parts.append(f"  choices {' '.join(c for c in choices)}")
            parts.append("}")
    else:
        # Inline format: attributes use `key=value` (=, no space)
        line = f"arg {escape_string(arg_name)}"
        attrs = []
        if help_text:
            attrs.append(f"help={escape_string(help_text)}")
        if not required:
            attrs.append("required=#false")
        if default is not None and default != argparse.SUPPRESS:
            attrs.append(f"default={escape_string(str(default))}")
        if var:
            attrs.append("var=#true")
        if var_min is not None:
            attrs.append(f"var_min={var_min}")
        if var_max is not None:
            attrs.append(f"var_max={var_max}")
        if attrs:
            line += " " + " ".join(attrs)
        parts.append(line)

    return "\n".join(parts)
