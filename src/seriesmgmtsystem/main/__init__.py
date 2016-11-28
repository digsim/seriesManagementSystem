import sys
from .mainImpl import MainImpl


def main():
    """Entry point for the application script"""
    main = MainImpl()
    main.getArguments(sys.argv[1:])