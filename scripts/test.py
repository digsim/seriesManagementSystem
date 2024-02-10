import sys

from seriesmgmtsystem.main.mainImpl import MainImpl


def main():
    """Entry point for the application script"""
    main = MainImpl()
    main.getArguments(sys.argv[1:])


if __name__ == "__main__":
    main()
