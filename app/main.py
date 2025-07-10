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
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install an application")
    install_parser.add_argument("app_name", help="Application name")
    install_parser.add_argument("-c", "--compile", action="store_true", 
                               help="Compile the application to binary using Bazel")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove an application")
    remove_parser.add_argument("app_name", help="Application name")
    
    # List command
    subparsers.add_parser("list", help="List installed applications")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade an application")
    upgrade_parser.add_argument("app_name", help="Application name")
    upgrade_parser.add_argument("-c", "--compile", action="store_true", 
                               help="Compile the application to binary using Bazel")
    
    args = parser.parse_args()
    
    if args.command == "install":
        success = install_app(args.app_name, compile_binary=args.compile)
        if not success:
            sys.exit(1)
    
    elif args.command == "remove":
        remove_app(args.app_name)
    
    elif args.command == "upgrade":
        success = upgrade_app(args.app_name, compile_binary=args.compile)
        if not success:
            sys.exit(1)
    
    elif args.command == "list":
        list_apps()
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 