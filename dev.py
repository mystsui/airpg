#!/usr/bin/env python3
"""
Development helper script for the combat system.
Run with --help to see available commands.
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_tests(args):
    """Run test suite with specified options."""
    cmd = ["pytest"]
    
    if args.coverage:
        cmd.extend(["--cov=combat", "--cov-report=term-missing"])
    
    if args.verbose:
        cmd.append("-v")
        
    if args.parallel:
        cmd.append("-n=auto")
        
    if args.test_path:
        cmd.append(args.test_path)
    else:
        cmd.append("tests/combat/")
        
    if args.performance:
        cmd.append("tests/combat/test_system_health.py::TestTimingPerformance")
        
    subprocess.run(cmd, check=True)

def format_code(args):
    """Format code using black and isort."""
    print("Formatting code...")
    subprocess.run(["black", "combat/", "tests/"], check=True)
    subprocess.run(["isort", "combat/", "tests/"], check=True)

def lint_code(args):
    """Run linting checks."""
    print("Running pylint...")
    subprocess.run(["pylint", "combat/", "tests/"], check=True)
    
    print("\nRunning mypy...")
    subprocess.run(["mypy", "combat/", "tests/"], check=True)

def check_all(args):
    """Run all checks: format, lint, test."""
    format_code(args)
    lint_code(args)
    run_tests(args)

def main():
    parser = argparse.ArgumentParser(description="Combat System Development Helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("-c", "--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    test_parser.add_argument("-p", "--parallel", action="store_true", help="Run tests in parallel")
    test_parser.add_argument("--performance", action="store_true", help="Run performance tests")
    test_parser.add_argument("test_path", nargs="?", help="Specific test path to run")
    
    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    
    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting")
    
    # Check all command
    check_parser = subparsers.add_parser("check", help="Run all checks")
    
    args = parser.parse_args()
    
    if args.command == "test":
        run_tests(args)
    elif args.command == "format":
        format_code(args)
    elif args.command == "lint":
        lint_code(args)
    elif args.command == "check":
        check_all(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
