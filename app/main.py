#!/usr/bin/env python3

import sys
import argparse
from core.package_manager import (
    install_app,
    remove_app,
    list_apps,
    upgrade_app
)


def main():
    parser = argparse.ArgumentParser(description="pget - Pure Python Package Manager")
    parser.add_argument("command", choices=["install", "remove", "list", "upgrade"], help="Command to execute")
    parser.add_argument("app_name", nargs="?", help="Application name")
    
    args = parser.parse_args()
    
    if args.command == "install":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for install command.\n")
            sys.exit(1)
        success = install_app(args.app_name)
        if not success:
            sys.exit(1)
    
    elif args.command == "remove":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for remove command.\n")
            sys.exit(1)
        remove_app(args.app_name)
    
    elif args.command == "upgrade":
        if not args.app_name:
            sys.stderr.write("ERROR: Application name required for upgrade command.\n")
            sys.exit(1)
        success = upgrade_app(args.app_name)
        if not success:
            sys.exit(1)
    
    elif args.command == "list":
        list_apps()


if __name__ == "__main__":
    main() 