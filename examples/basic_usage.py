"""Example usage of argparse-usage library."""

import argparse

import argparse_usage


def main():
    """Generate a usage spec for a sample CLI."""
    parser = argparse.ArgumentParser(
        prog="example-cli",
        description="An example CLI tool",
        epilog="For more info, visit https://example.com",
    )

    # Add flags
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    parser.add_argument("-o", "--output", default="output.txt", help="Output file")

    # Add flags
    parser.add_argument("-f", "--file", help="Input file")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")

    # Add positional arguments
    parser.add_argument("files", nargs="+", help="Files to process")

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command")

    build_cmd = subparsers.add_parser("build", help="Build project")
    build_cmd.add_argument("--debug", action="store_true", help="Debug build")

    test_cmd = subparsers.add_parser("test", help="Run tests")
    test_cmd.add_argument("--verbose", action="count", help="Test verbosity")
    test_cmd.add_argument("tests", nargs="*", help="Specific tests to run")

    # Generate usage spec
    spec = argparse_usage.generate(
        parser,
        name="Example CLI",
        version="1.0.0",
        author="Example Author",
    )

    print(spec)


if __name__ == "__main__":
    main()
