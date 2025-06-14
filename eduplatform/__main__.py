#!/usr/bin/env python3
"""
EduPlatform - Main module entry point.
"""

def main():
    """Run the EduPlatform CLI application."""
    from .cli.main import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()
