#!/usr/bin/env -S uv run
"""Example usage of argparse-usage library."""

import argparse
import sys

import argparse_usage


def cmd_create(args):
    print(f"Creating '{args.name}' (type={args.type}, force={args.force})")


def cmd_delete(args):
    print(f"Deleting '{args.name}' (dry_run={args.dry_run})")


def cmd_list(args):
    print(f"Listing items (filter={args.filter}, limit={args.limit})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="Example CLI with subcommands",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True  # Enforce that a subcommand must be provided

    # --- create ---
    p_create = subparsers.add_parser("create", help="Create a new item")
    p_create.add_argument("name", help="Name of the item")
    p_create.add_argument(
        "--type", "-t", default="default", help="Item type (default: %(default)s)"
    )
    p_create.add_argument(
        "--force", "-f", action="store_true", help="Overwrite if exists"
    )
    p_create.set_defaults(func=cmd_create)

    # --- delete ---
    p_delete = subparsers.add_parser("delete", help="Delete an item")
    p_delete.add_argument("name", help="Name of the item to delete")
    p_delete.add_argument(
        "--dry-run", action="store_true", help="Simulate deletion without changes"
    )
    p_delete.set_defaults(func=cmd_delete)

    # --- list ---
    p_list = subparsers.add_parser("list", help="List all items")
    p_list.add_argument("--filter", default=None, help="Filter by keyword")
    p_list.add_argument(
        "--limit", type=int, default=20, help="Max results (default: %(default)s)"
    )
    p_list.set_defaults(func=cmd_list)

    return parser


def main():
    parser = build_parser()

    if len(sys.argv) > 1 and sys.argv[1] == "--usage":
        # Generate usage spec
        spec = argparse_usage.generate(
            parser,
            name="Example CLI",
            version="1.0.0",
            author="Example Author",
        )

        print(spec)
        return

    args = parser.parse_args()

    if args.verbose:
        print(f"[verbose] Running command: {args.command}")

    args.func(args)  # Dispatch to the appropriate handler


if __name__ == "__main__":
    main()
