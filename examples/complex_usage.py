#!/usr/bin/env -S uv run
"""Example usage of argparse-usage library with nested subparsers."""

import argparse
import sys

import argparse_usage


def cmd_config_get(args):
    print(f"Getting config key '{args.key}'")


def cmd_config_set(args):
    print(f"Setting config key '{args.key}' = '{args.value}'")


def cmd_config_list(args):
    print(f"Listing all config (prefix={args.prefix})")


def cmd_database_migrate(args):
    print(f"Migrating database (steps={args.steps}, dry_run={args.dry_run})")


def cmd_database_backup(args):
    print(f"Backing up database to '{args.path}' (compress={args.compress})")


def cmd_database_restore(args):
    print(f"Restoring database from '{args.path}' (force={args.force})")


def cmd_deploy_init(args):
    print(f"Initializing deployment (env={args.env})")


def cmd_deploy_status(args):
    print(f"Deployment status (verbose={args.verbose})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mycli",
        description="Example CLI with nested subcommands",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--config",
        default="~/.config/mycli/config.yaml",
        help="Path to config file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # --- config (with nested subcommands) ---
    p_config = subparsers.add_parser("config", help="Manage configuration")
    p_config.add_argument(
        "--global", "-g", action="store_true", help="Operate on global config"
    )

    config_subparsers = p_config.add_subparsers(
        dest="config_command", metavar="CONFIG_COMMAND"
    )
    config_subparsers.required = True

    # config get
    p_config_get = config_subparsers.add_parser("get", help="Get a config value")
    p_config_get.add_argument("key", help="Config key to retrieve")
    p_config_get.set_defaults(func=cmd_config_get)

    # config set
    p_config_set = config_subparsers.add_parser("set", help="Set a config value")
    p_config_set.add_argument("key", help="Config key to set")
    p_config_set.add_argument("value", help="Value to set")
    p_config_set.add_argument(
        "--type",
        choices=["string", "int", "bool", "float"],
        default="string",
        help="Value type (default: %(default)s)",
    )
    p_config_set.set_defaults(func=cmd_config_set)

    # config list
    p_config_list = config_subparsers.add_parser("list", help="List all config values")
    p_config_list.add_argument("--prefix", default=None, help="Filter by key prefix")
    p_config_list.set_defaults(func=cmd_config_list)

    # --- database (with nested subcommands) ---
    p_db = subparsers.add_parser("database", help="Manage database")
    p_db.add_argument(
        "--db-name", default="mydb", help="Database name (default: %(default)s)"
    )

    db_subparsers = p_db.add_subparsers(dest="db_command", metavar="DB_COMMAND")
    db_subparsers.required = True

    # database migrate
    p_db_migrate = db_subparsers.add_parser("migrate", help="Run database migrations")
    p_db_migrate.add_argument(
        "--steps",
        type=int,
        default=-1,
        help="Number of migration steps (-1 for all, default: %(default)s)",
    )
    p_db_migrate.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    p_db_migrate.add_argument(
        "--direction",
        choices=["up", "down"],
        default="up",
        help="Migration direction (default: %(default)s)",
    )
    p_db_migrate.set_defaults(func=cmd_database_migrate)

    # database backup
    p_db_backup = db_subparsers.add_parser("backup", help="Backup database")
    p_db_backup.add_argument("path", help="Backup file path")
    p_db_backup.add_argument(
        "--compress", "-c", action="store_true", help="Compress backup"
    )
    p_db_backup.add_argument(
        "--format",
        choices=["sql", "dump"],
        default="sql",
        help="Backup format (default: %(default)s)",
    )
    p_db_backup.set_defaults(func=cmd_database_backup)

    # database restore
    p_db_restore = db_subparsers.add_parser("restore", help="Restore database")
    p_db_restore.add_argument("path", help="Backup file path")
    p_db_restore.add_argument(
        "--force", "-f", action="store_true", help="Restore even if database exists"
    )
    p_db_restore.set_defaults(func=cmd_database_restore)

    # --- deploy (with nested subcommands) ---
    p_deploy = subparsers.add_parser("deploy", help="Manage deployments")
    p_deploy.add_argument(
        "--cluster",
        default="default",
        help="Target cluster (default: %(default)s)",
    )

    deploy_subparsers = p_deploy.add_subparsers(
        dest="deploy_command", metavar="DEPLOY_COMMAND"
    )
    deploy_subparsers.required = True

    # deploy init
    p_deploy_init = deploy_subparsers.add_parser("init", help="Initialize a deployment")
    p_deploy_init.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        required=True,
        help="Environment to deploy to",
    )
    p_deploy_init.add_argument(
        "--region", default="us-east-1", help="AWS region (default: %(default)s)"
    )
    p_deploy_init.add_argument(
        "--instance-type",
        default="t3.micro",
        help="EC2 instance type (default: %(default)s)",
    )
    p_deploy_init.set_defaults(func=cmd_deploy_init)

    # deploy status
    p_deploy_status = deploy_subparsers.add_parser(
        "status", help="Check deployment status"
    )
    p_deploy_status.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed status"
    )
    p_deploy_status.add_argument(
        "--watch", "-w", action="store_true", help="Watch status in real-time"
    )
    p_deploy_status.set_defaults(func=cmd_deploy_status)

    return parser


def dispatch(args):
    """Dispatch to the appropriate command handler."""
    if args.command == "config":
        if args.config_command == "get":
            cmd_config_get(args)
        elif args.config_command == "set":
            cmd_config_set(args)
        elif args.config_command == "list":
            cmd_config_list(args)
    elif args.command == "database":
        if args.db_command == "migrate":
            cmd_database_migrate(args)
        elif args.db_command == "backup":
            cmd_database_backup(args)
        elif args.db_command == "restore":
            cmd_database_restore(args)
    elif args.command == "deploy":
        if args.deploy_command == "init":
            cmd_deploy_init(args)
        elif args.deploy_command == "status":
            cmd_deploy_status(args)


def main():
    parser = build_parser()

    if len(sys.argv) > 1 and sys.argv[1] == "--usage":
        spec = argparse_usage.generate(
            parser,
            name="Complex CLI",
            version="2.0.0",
            author="Example Author",
        )
        print(spec)
        return

    args = parser.parse_args()

    if args.verbose:
        print(f"[verbose] Running command: {args.command}")

    dispatch(args)


if __name__ == "__main__":
    main()
